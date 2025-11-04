import streamlit as st
from yt_dlp import YoutubeDL
import tempfile
import os
import time

# ----- Custom CSS -----
st.markdown("""
    <style>
    .centered {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .supported-sites {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 20px;
        margin-top: 20px;
    }
    .supported-sites img {
        width: 50px;
        height: 50px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="centered">', unsafe_allow_html=True)

# ----- App Title -----
st.title("YouTube & Video Downloader")

# ----- Input URL -----
url = st.text_input("Paste YouTube or video link:")

# ----- Supported Sites Section -----
st.subheader("Supported Platforms")
st.markdown("""
<div class="supported-sites">
    <img src="https://upload.wikimedia.org/wikipedia/commons/4/42/YouTube_icon_%282013-2017%29.png" alt="YouTube" title="YouTube">
    <img src="https://upload.wikimedia.org/wikipedia/en/6/6b/TikTok_logo.png" alt="TikTok" title="TikTok">
    <img src="https://upload.wikimedia.org/wikipedia/commons/e/e7/Instagram_logo_2016.svg" alt="Instagram" title="Instagram">
    <img src="https://upload.wikimedia.org/wikipedia/commons/5/51/Facebook_f_logo_%282019%29.svg" alt="Facebook" title="Facebook">
    <img src="https://upload.wikimedia.org/wikipedia/commons/4/4f/Twitter-logo.svg" alt="Twitter" title="Twitter">
    <img src="https://upload.wikimedia.org/wikipedia/en/8/82/Reddit_logo_and_wordmark.svg" alt="Reddit" title="Reddit">
    <img src="https://upload.wikimedia.org/wikipedia/en/5/5e/Twitch_logo.svg" alt="Twitch" title="Twitch">
    <img src="https://upload.wikimedia.org/wikipedia/commons/2/23/SoundCloud_logo.svg" alt="SoundCloud" title="SoundCloud">
</div>
""", unsafe_allow_html=True)
st.caption("yt-dlp supports hundreds of sites. Support may vary depending on site changes, region restrictions, or DRM.")

# ----- Video Info and Download -----
if url.strip():
    try:
        ydl_opts = {}
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])

        best_video = None
        best_audio = None
        for f in formats:
            if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                if not best_video or f.get('height', 0) > best_video.get('height', 0):
                    best_video = f
            elif f.get('vcodec') == 'none' and f.get('acodec') != 'none':
                if not best_audio or (f.get('abr') or 0) > (best_audio.get('abr') or 0):
                    best_audio = f

        st.subheader(info.get('title'))
        if info.get('thumbnail'):
            st.image(info.get('thumbnail'), width=400)
        st.caption(info.get('uploader'))

        choice = st.radio("Download type:", ["Video", "Audio"], index=0, horizontal=True)

        if st.button("Download"):
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Mutable state for smoothing ETA
            progress_state = {
                "last_update": 0,
                "speed_history": []
            }

            def progress_hook(d):
                if d['status'] == 'downloading':
                    now = time.time()
                    if now - progress_state["last_update"] < 0.2:
                        return

                    downloaded_bytes = d.get('downloaded_bytes', 0)
                    total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
                    speed = d.get('speed') or 0

                    if total_bytes:
                        percent = downloaded_bytes / total_bytes
                        progress_bar.progress(min(percent, 1.0))

                        # Smooth ETA
                        progress_state["speed_history"].append(speed)
                        if len(progress_state["speed_history"]) > 5:
                            progress_state["speed_history"].pop(0)
                        avg_speed = sum(progress_state["speed_history"]) / len(progress_state["speed_history"]) if progress_state["speed_history"] else 0
                        eta = (total_bytes - downloaded_bytes) / avg_speed if avg_speed else 0

                        status_text.text(f"Downloading... {percent*100:.1f}% | Time Left: {int(eta)}s")

                    progress_state["last_update"] = now

            with tempfile.TemporaryDirectory() as tmpdir:
                if choice == "Video":
                    fmt_id = best_video['format_id']
                    ydl_opts = {
                        'format': fmt_id,
                        'outtmpl': os.path.join(tmpdir, '%(title)s.%(ext)s'),
                        'merge_output_format': 'mp4',
                        'progress_hooks': [progress_hook]
                    }
                else:
                    fmt_id = best_audio['format_id']
                    ydl_opts = {
                        'format': fmt_id,
                        'outtmpl': os.path.join(tmpdir, '%(title)s.%(ext)s'),
                        'progress_hooks': [progress_hook]
                    }

                with YoutubeDL(ydl_opts) as ydl:
                    downloaded_info = ydl.extract_info(url)

                filename = ydl.prepare_filename(downloaded_info)
                with open(filename, "rb") as f:
                    file_bytes = f.read()

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
