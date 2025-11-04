import streamlit as st
from yt_dlp import YoutubeDL
import tempfile
import os

# ----- Custom CSS to center everything -----
st.markdown("""
    <style>
    .centered {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="centered">', unsafe_allow_html=True)
st.title("YouTube Downloader (Auto Best Format)")

# Input URL
url = st.text_input("Paste YouTube video link:")

if url.strip():
    try:
        # Get video info
        ydl_opts = {}
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])

        # Best video+audio & best audio-only
        best_video = None
        best_audio = None

        for f in formats:
            if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                if not best_video or f.get('height', 0) > best_video.get('height', 0):
                    best_video = f
            elif f.get('vcodec') == 'none' and f.get('acodec') != 'none':
                if not best_audio or (f.get('abr') or 0) > (best_audio.get('abr') or 0):
                    best_audio = f

        # Display video info
        st.subheader(info.get('title'))
        if info.get('thumbnail'):
            st.image(info.get('thumbnail'), width=400)
        st.caption(info.get('uploader'))

        # Video or Audio choice
        choice = st.radio("Download type:", ["Video", "Audio"], index=0, horizontal=True)

        # Download button
        if st.button("Download"):
            with tempfile.TemporaryDirectory() as tmpdir:
                if choice == "Video":
                    fmt_id = best_video['format_id']
                    ydl_opts = {
                        'format': fmt_id,
                        'outtmpl': os.path.join(tmpdir, '%(title)s.%(ext)s'),
                        'merge_output_format': 'mp4'
                    }
                else:
                    fmt_id = best_audio['format_id']
                    ydl_opts = {
                        'format': fmt_id,
                        'outtmpl': os.path.join(tmpdir, '%(title)s.%(ext)s'),
                    }

                # Loading spinner while downloading
                with st.spinner("Downloading... Please wait ⏳"):
                    with YoutubeDL(ydl_opts) as ydl:
                        downloaded_info = ydl.extract_info(url)

                filename = ydl.prepare_filename(downloaded_info)
                with open(filename, "rb") as f:
                    file_bytes = f.read()

                # Set file name and mime type
                if choice == "Video":
                    file_name = f"{downloaded_info.get('title')}.mp4"
                    mime_type = "video/mp4"
                else:
                    file_name = f"{downloaded_info.get('title')}.mp3"
                    mime_type = "audio/mpeg"

                st.success("✅ Download ready!")
                st.download_button(
                    label="Click to Download",
                    data=file_bytes,
                    file_name=file_name,
                    mime=mime_type
                )

    except Exception as e:
        st.error(f"An error occurred:\n{str(e)}")

st.markdown('</div>', unsafe_allow_html=True)
