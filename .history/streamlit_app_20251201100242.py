import streamlit as st
from yt_dlp import YoutubeDL
import tempfile
import os
import time

# ----- Custom CSS -----
st.markdown("""
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
    .centered { display: flex; flex-direction: column; align-items: center; }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; text-align: center;
              font-size: 12px; color: #888; padding: 5px 0; background-color: rgba(255,255,255,0.8); }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="centered">', unsafe_allow_html=True)

# ----- App Title -----
st.title("YouTube & Video Downloader")

# ----- Input URL -----
url = st.text_input("Paste YouTube or video link:",
                    placeholder="https://www.youtube.com/watch?v=dQw4w9WgXcQ")

if url.strip():
    try:
        # Extract metadata only
        with YoutubeDL({"quiet": True}) as ydl:
            info = ydl.extract_info(url, download=False)

        # Display info
        st.subheader(info.get("title", ""))
        if info.get("thumbnail"):
            st.image(info["thumbnail"], width=400)
        st.caption(info.get("uploader", "Unknown"))

        # Choose Video or Audio
        choice = st.radio("Download type:", ["Video", "Audio"], index=0, horizontal=True)

        # On Download
        if st.button("Download"):
            progress_bar = st.progress(0)
            status_text = st.empty()

            def progress_hook(d):
                if d["status"] == "downloading":
                    downloaded = d.get("downloaded_bytes", 0)
                    total = d.get("total_bytes") or d.get("total_bytes_estimate")
                    if total:
                        percent = downloaded / total
                        progress_bar.progress(percent)
                        status_text.text(f"Downloading… {percent*100:.1f}%")
                elif d["status"] == "finished":
                    status_text.text("Finalizing…")

            with tempfile.TemporaryDirectory() as tmpdir:

                # -------- NO-FFMPEG VIDEO (MP4 ONLY) --------
                if choice == "Video":
                    ydl_opts = {
                        "format": "best[ext=mp4]/best",  # ALWAYS a combined MP4
                        "outtmpl": os.path.join(tmpdir, "%(title)s.%(ext)s"),
                        "progress_hooks": [progress_hook]
                    }

                # -------- NO-FFMPEG AUDIO (M4A ONLY) --------
                else:
                    ydl_opts = {
                        "format": "bestaudio[ext=m4a]/bestaudio",
                        "outtmpl": os.path.join(tmpdir, "%(title)s.%(ext)s"),
                        "progress_hooks": [progress_hook]
                    }

                with YoutubeDL(ydl_opts) as ydl:
                    downloaded_info = ydl.extract_info(url)

                filepath = ydl.prepare_filename(downloaded_info)

                # Load file
                with open(filepath, "rb") as f:
                    data = f.read()

                st.success("✅ Download ready!")

                # Download button
                if choice == "Video":
                    st.download_button("Download Video",
                        data=data,
                        file_name=f"{downloaded_info['title']}.mp4",
                        mime="video/mp4")
                else:
                    st.download_button("Download Audio",
                        data=data,
                        file_name=f"{downloaded_info['title']}.m4a",
                        mime="audio/mp4")

    except Exception as e:
        st.error(f"An error occurred:\n{str(e)}")

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer">
    This downloader uses <strong>yt-dlp</strong> for video extraction.
    All site logos and icons are property of their respective owners.
</div>
""", unsafe_allow_html=True)
