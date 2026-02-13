# 🎵 Mashup Generator

This is a Streamlit web app that generates a **mashup of songs from your favorite singers**, converts videos to audio, merges them, and optionally sends the final mashup via email.

## **Features**

- Download songs from YouTube using `yt-dlp`.
- Convert videos to MP3 audio using `moviepy`.
- Cut audios to a specific duration and merge into one mashup.
- Send the final mashup as a **ZIP file via email**.
- Works with **multiple singers**.
- **Persistent downloads**: avoids re-downloading or re-converting if files already exist.

## **Installation**

1. Clone the repository or download the project.

2. **Create a virtual environment** (recommended):

```bash
python -m venv venv
Activate the virtual environment:

Windows:

.\venv\Scripts\activate
Mac/Linux:

source venv/bin/activate
Install all required packages:

pip install -r requirements.txt
Setup for Sending Email
To send the mashup via email from Streamlit:

Go to: Google App Passwords

Sign in to your Gmail account.

Select App Passwords.

Choose Other for the app and give it a name like MashupApp or Streamlit.

Copy the 16-character password.

Enter your Gmail address and this App Password in the Streamlit sidebar under Email Configuration.

⚠️ Do not use your normal Gmail password, only the App Password.

Running the App
streamlit run app.py
Open the provided URL in your browser.

Enter Singer Name, Number of Videos, Duration, and Receiver Email.

Enter your Gmail and App Password in the sidebar.

Click Submit to generate and send the mashup.

Notes
If you close VS Code or restart, you don’t need to re-download Python packages if you are using the same virtual environment.

Videos and audios will be downloaded into videos/ and audios/ folders. If files already exist, they won’t be re-downloaded.

For new singers, the app will download the required videos and create a new mashup.

Make sure your FFmpeg path is correctly set in app.py.




```
