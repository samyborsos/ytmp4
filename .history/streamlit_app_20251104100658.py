import streamlit as st
from yt_dlp import YoutubeDL
import tempfile
import os

st.title("YouTube Downloader")

# YouTube URL input
url = st.text_input("YouTube video link:")

# Download button
if st.button("Download"):
    if not url.strip():
        st.error("Please enter a YouTube link.")
    else:
        with tempfile.TemporaryDirectory() as tmpdir:
            ydl_opts = {
                'format': 'bestvideo+bestaudio/best',
                'outtmpl': os.path.join(tmpdir, '%(title)s.%(ext)s'),
                'merge_output_format': 'mp4'
            }

            try:
                st.info("Downloading... This may take a moment.")
                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url)
                    filename = ydl.prepare_filename(info)

                # Read file bytes for download button
                with open(filename, "rb") as f:
                    video_bytes = f.read()

                st.success(f"Downloaded: {info.get('title')}")
                st.download_button(
                    label="Download Video",
                    data=video_bytes,
                    file_name=f"{info.get('title')}.mp4",
                    mime="video/mp4"
                )

            except Exception as e:
                st.error(f"An error occurred:\n{str(e)}")
