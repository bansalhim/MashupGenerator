import sys
import os
import subprocess
from yt_dlp import YoutubeDL
from moviepy.editor import VideoFileClip

# NOTE: FFMPEG_PATH removed. Requires ffmpeg to be in system PATH (standard for grading).

def download_videos(singer, number):
    if not os.path.exists("videos"):
        os.makedirs("videos")

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': 'videos/%(id)s.%(ext)s',
        'quiet': False,
        # 'ffmpeg_location' removed to allow running on any computer
    }

    search_query = f"ytsearch{number}:{singer} songs"

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([search_query])


def convert_to_audio():
    if not os.path.exists("audios"):
        os.makedirs("audios")

    for file in os.listdir("videos"):
        if file.endswith((".mp4", ".mkv", ".webm")):
            video_path = os.path.join("videos", file)
            audio_path = os.path.join("audios", file.rsplit(".", 1)[0] + ".mp3")

            if os.path.exists(audio_path):
                continue

            # This part remains exactly the same as your working code
            video = VideoFileClip(video_path)
            video.audio.write_audiofile(audio_path)
            video.close()


def cut_and_merge(duration, output_file):
    trimmed_files = []

    # Trim each audio file
    for file in os.listdir("audios"):
        if file.endswith(".mp3") and not file.startswith("trimmed_"): # Added safety check
            input_path = os.path.join("audios", file)
            trimmed_path = os.path.join("audios", "trimmed_" + file)

            # CHANGED: Uses 'ffmpeg' directly instead of hardcoded path
            subprocess.run([
                "ffmpeg", 
                "-y",
                "-i", input_path,
                "-t", str(duration),
                trimmed_path
            ])

            trimmed_files.append(trimmed_path)

    if len(trimmed_files) == 0:
        print("No audio files found to merge.")
        return

    # Merge all trimmed files
    # CHANGED: Uses 'ffmpeg' directly
    merge_command = ["ffmpeg", "-y"]

    for file in trimmed_files:
        merge_command.extend(["-i", file])

    merge_command.extend([
        "-filter_complex",
        f"concat=n={len(trimmed_files)}:v=0:a=1",
        output_file
    ])

    subprocess.run(merge_command)


def main():
    if len(sys.argv) != 5:
        print("Usage: python <RollNumber>.py <SingerName> <NumberOfVideos> <AudioDuration> <OutputFileName>")
        sys.exit(1)

    singer = sys.argv[1]

    try:
        number = int(sys.argv[2])
        duration = int(sys.argv[3])
    except ValueError:
        print("NumberOfVideos and AudioDuration must be integers.")
        sys.exit(1)

    output_file = sys.argv[4]

    if number <= 10:
        print("Number of videos must be greater than 10.")
        sys.exit(1)

    if duration <= 20:
        print("Audio duration must be greater than 20 seconds.")
        sys.exit(1)

    try:
        # Check if videos folder exists and has content
        if not os.path.exists("videos") or len(os.listdir("videos")) == 0:
            print(f"Downloading {number} videos of {singer}...")
            download_videos(singer, number)
        else:
            print("Videos already downloaded. Skipping download...")

        print("Converting videos to audio...")
        convert_to_audio()

        print(f"Cutting first {duration} seconds and merging...")
        cut_and_merge(duration, output_file)

        print("Mashup created successfully:", output_file)

    except Exception as e:
        print("Error occurred:", e)


if __name__ == "__main__":
    main()