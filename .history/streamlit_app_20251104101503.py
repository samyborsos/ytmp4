import streamlit as st
from yt_dlp import YoutubeDL
import tempfile
import os

st.title("YouTube Downloader with Quality")

# YouTube URL input
url = st.text_input("YouTube video link:")

if url.strip():
    try:
        # Get video info
        ydl_opts = {}
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])

        # Build a list of quality options
        options = []
        for f in formats:
            # Only video+audio formats or video-only if you want
            if f.get('vcodec') != 'none':
                resolution = f.get('format_note') or f.get('height')
                filesize = f.get('filesize') or f.get('filesize_approx')
                ext = f.get('ext')
                fmt_id = f.get('format_id')
                size_mb = round(filesize / (1024*1024), 2) if filesize else "Unknown"
                options.append(f"{fmt_id} - {resolution} - {ext} - {size_mb} MB")

        # Let user select quality
        quality_choice = st.selectbox("Choose video quality:", options)

        # Download button
        if st.button("Download"):
            # Extract format ID from selected option
            fmt_id = quality_choice.split(" - ")[0]

            with tempfile.TemporaryDirectory() as tmpdir:
                ydl_opts = {
                    'format': fmt_id,
                    'outtmpl': os.path.join(tmpdir, '%(title)s.%(ext)s'),
                    'merge_output_format': 'mp4'
                }
                st.info("Downloading...")
                with YoutubeDL(ydl_opts) as ydl:
                    info_downloaded = ydl.extract_info(url)

                filename = ydl.prepare_filename(info_downloaded)
                with open(filename, "rb") as f:
                    video_bytes = f.read()

                st.success(f"Downloaded: {info_downloaded.get('title')}")
                st.download_button(
                    label="Download Video",
                    data=video_bytes,
                    file_name=f"{info_downloaded.get('title')}.mp4",
                    mime="video/mp4"
                )

    except Exception as e:
        st.error(f"An error occurred:\n{str(e)}")
