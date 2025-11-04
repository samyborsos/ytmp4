import streamlit as st
from yt_dlp import YoutubeDL
import tempfile
import os

st.title("YouTube Downloader")

# YouTube URL input
url = st.text_input("YouTube video link:")

if url.strip():
    try:
        # Get video info
        ydl_opts = {}
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])

        # Separate formats
        video_formats = []
        audio_formats = []

        for f in formats:
            if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                # Video + audio combined formats
                resolution = f.get('height') or f.get('format_note') or "Unknown"
                fmt_id = f.get('format_id')
                video_formats.append((fmt_id, f"{resolution}p"))
            elif f.get('vcodec') == 'none' and f.get('acodec') != 'none':
                # Audio only
                fmt_id = f.get('format_id')
                abr = f.get('abr')  # audio bitrate
                audio_formats.append((fmt_id, f"{abr} kbps"))

        # User choice: video or audio
        choice = st.radio("Download type:", ["Video + Audio", "Audio only"])

        if choice == "Video + Audio":
            # Show resolutions
            resolution_options = {res: fid for fid, res in video_formats}
            selected_res = st.selectbox("Select resolution:", list(resolution_options.keys()))
            fmt_id = resolution_options[selected_res]
        else:
            # Show audio options
            audio_options = {res: fid for fid, res in audio_formats}
            selected_audio = st.selectbox("Select audio quality:", list(audio_options.keys()))
            fmt_id = audio_options[selected_audio]

        # Download button
        if st.button("Download"):
            with tempfile.TemporaryDirectory() as tmpdir:
                ydl_opts = {
                    'format': fmt_id,
                    'outtmpl': os.path.join(tmpdir, '%(title)s.%(ext)s'),
                    'merge_output_format': 'mp4'  # ignored for audio only
                }

                st.info("Downloading...")
                with YoutubeDL(ydl_opts) as ydl:
                    info_downloaded = ydl.extract_info(url)

                filename = ydl.prepare_filename(info_downloaded)
                with open(filename, "rb") as f:
                    file_bytes = f.read()

                # Set file name and mime type
                if choice == "Video + Audio":
                    file_name = f"{info_downloaded.get('title')}.mp4"
                    mime_type = "video/mp4"
                else:
                    file_name = f"{info_downloaded.get('title')}.mp3"
                    mime_type = "audio/mpeg"

                st.success("Download ready!")
                st.download_button(
                    label="Download",
                    data=file_bytes,
                    file_name=file_name,
                    mime=mime_type
                )

    except Exception as e:
        st.error(f"An error occurred:\n{str(e)}")
