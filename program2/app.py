import streamlit as st
import os
import smtplib
import zipfile
import subprocess
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from yt_dlp import YoutubeDL
from moviepy.editor import VideoFileClip

# --- CONFIGURATION ---
FFMPEG_BIN_PATH = r'C:\Users\himan\Downloads\ffmpeg-8.0.1-essentials_build\ffmpeg-8.0.1-essentials_build\bin'
FFMPEG_EXE_PATH = os.path.join(FFMPEG_BIN_PATH, 'ffmpeg.exe')

# --- 1. MASHUP LOGIC ---
def download_videos(singer, number):
    if not os.path.exists("videos"):
        os.makedirs("videos")
    for f in os.listdir("videos"):
        os.remove(os.path.join("videos", f))

    ydl_opts = {
        'format': 'worstvideo+bestaudio/best',
        'outtmpl': 'videos/%(id)s.%(ext)s',
        'quiet': True,
        'ffmpeg_location': FFMPEG_BIN_PATH
    }

    search_query = f"ytsearch{number}:{singer} songs"
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([search_query])

def convert_to_audio():
    if not os.path.exists("audios"):
        os.makedirs("audios")
    for f in os.listdir("audios"):
        os.remove(os.path.join("audios", f))
    for file in os.listdir("videos"):
        if file.endswith((".mp4", ".mkv", ".webm", ".m4a")):
            video_path = os.path.join("videos", file)
            audio_path = os.path.join("audios", file.rsplit(".", 1)[0] + ".mp3")
            try:
                video = VideoFileClip(video_path)
                video.audio.write_audiofile(audio_path, logger=None)
                video.close()
            except Exception as e:
                st.error(f"Error converting {file}: {e}")

def cut_and_merge(duration, output_file):
    trimmed_files = []
    if not os.path.exists("audios"):
        return None
    for file in os.listdir("audios"):
        if file.endswith(".mp3") and not file.startswith("trimmed_"):
            input_path = os.path.join("audios", file)
            trimmed_path = os.path.join("audios", "trimmed_" + file)
            subprocess.run([
                FFMPEG_EXE_PATH, "-y", "-i", input_path, "-ss", "0", "-t", str(duration), trimmed_path
            ], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            trimmed_files.append(trimmed_path)
    if not trimmed_files:
        return None
    merge_command = [FFMPEG_EXE_PATH, "-y"]
    for file in trimmed_files:
        merge_command.extend(["-i", file])
    merge_command.extend([
        "-filter_complex", f"concat=n={len(trimmed_files)}:v=0:a=1", output_file
    ])
    subprocess.run(merge_command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    return output_file

# --- 2. ZIP AND EMAIL LOGIC ---
def create_zip(output_file):
    zip_filename = output_file.replace(".mp3", ".zip")
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        zipf.write(output_file, arcname=os.path.basename(output_file))
    return zip_filename

def send_email(receiver_email, zip_file, sender_email, sender_password):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = "Your Mashup Result"
    body = "Here is the mashup you requested."
    msg.attach(MIMEText(body, 'plain'))
    try:
        with open(zip_file, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(zip_file)}")
        msg.attach(part)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)  # Must be App Password
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        return str(e)

# --- 3. STREAMLIT INTERFACE ---
st.title("🎵 Mashup Generator")

with st.form("mashup_form"):
    singer_name = st.text_input("Singer Name", placeholder="e.g., Sharry Maan")
    num_videos = st.number_input("Number of Videos", min_value=11, value=11, help="Must be > 10")
    duration = st.number_input("Duration (seconds)", min_value=21, value=21, help="Must be > 20")
    email_id = st.text_input("Receiver Email", placeholder="example@gmail.com")
    submitted = st.form_submit_button("Submit")

st.sidebar.header("Email Configuration")
st.sidebar.info("""
⚠️ To send the mashup via email, enter:

1. **Sender Email:** Your Gmail address  
2. **Sender App Password:** A Gmail App Password (NOT your Gmail login)  

Steps to create an App Password:  
https://support.google.com/mail/answer/185833?hl=en
""")
sender_email = st.sidebar.text_input("Sender Email")
sender_password = st.sidebar.text_input("Sender App Password", type="password")

if submitted:
    if not singer_name or not email_id:
        st.error("Please provide all details (Singer Name and Receiver Email).")
    elif not sender_email or not sender_password:
        st.error("Provide Sender Email and App Password in sidebar to send results.")
    else:
        st.success(f"Starting Mashup for {singer_name}...")
        output_filename = "mashup_output.mp3"
        try:
            with st.spinner("Downloading videos..."):
                download_videos(singer_name, int(num_videos))
            with st.spinner("Converting to Audio..."):
                convert_to_audio()
            with st.spinner("Cutting and Merging..."):
                result = cut_and_merge(int(duration), output_filename)
            if result:
                st.info("Zipping the file...")
                zip_path = create_zip(result)
                with st.spinner("Sending Email..."):
                    email_status = send_email(email_id, zip_path, sender_email, sender_password)
                    if email_status is True:
                        st.success(f"Done! Mashup sent to {email_id}")
                        st.info("✅ Use a Gmail App Password, NOT your Gmail login password.")
                    else:
                        st.error(f"Failed to send email: {email_status}")
                        st.warning("⚠️ Check that you entered the correct App Password in the sidebar.")
            else:
                st.error("Mashup generation failed.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
