import streamlit as st
from yt_dlp import YoutubeDL
import tempfile
import os
import time

# ----- Custom CSS -----
st.markdown("""
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
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
        gap: 25px;
        margin-top: 20px;
        font-size: 50px;
        color: #555;
    }
    .supported-sites i {
        transition: transform 0.2s, color 0.2s;
        cursor: pointer;
    }
    .supported-sites i:hover {
        transform: scale(1.2);
        color: #1DB954;
    }
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        text-align: center;
        font-size: 12px;
        color: #888;
        padding: 5px 0;
        background-color: rgba(255, 255, 255, 0.8);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="centered">', unsafe_allow_html=True)

# ----- App Title -----
st.title("YouTube & Video Downloader")

# ----- Input URL -----
url = st.text_input(
    "Paste YouTube or video link:",
    placeholder="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
)

# ---- Extract Metadata Safely ----
if url.strip():
    try:
        with YoutubeDL({"quiet": True}) as ydl:
            info = ydl.extract_info(url, download=False)

        st.subheader(info.get("title", ""))
        if info.get("thumbnail"):
            st.image(info["thumbnail"], width=400)
        st.caption(info.get("uploader", "Unknown"))

        choice = st.radio("Download type:", ["Video", "Audio"], index=0, horizontal=True)

        # ---- When user clicks Download ----
        if st.button("Download"):
            progress_bar = st.progress(0)
            status_text = st.empty()

            def progress_hook(d):
                if d["status"] == "downloading":
                    downloaded = d.get("downloaded_bytes", 0)
                    total = d.get("total_bytes") or d.get("total_bytes_estimate")
                    if total:
                        percent = downloaded / total
                        progress_bar.progress(min(percent, 1.0))
                        status_text.text(f"Downloading... {percent*100:.1f}%")
                elif d["status"] == "finished":
                    status_text.text("Processing...")

            with tempfile.TemporaryDirectory() as tmpdir:

                # ---------- VIDEO OPTION ----------
                if choice == "Video":
                    ydl_opts = {
                        "format": "bestvideo+bestaudio/best",
                        "merge_output_format": "mp4",
                        "outtmpl": os.path.join(tmpdir, "%(title)s.%(ext)s"),
                        "progress_hooks": [progress_hook]
                    }

                # ---------- AUDIO OPTION ----------
                else:
                    ydl_opts = {
                        "format": "bestaudio/best",
                        "outtmpl": os.path.join(tmpdir, "%(title)s.%(ext)s"),
                        "progress_hooks": [progress_hook],
                        "postprocessors": [
                            {
                                "key": "FFmpegExtractAudio",
                                "preferredcodec": "mp3"
                            }
                        ]
                    }

                # ---- Download ----
                with YoutubeDL(ydl_opts) as ydl:
                    downloaded_info = ydl.extract_info(url)

                # ---- Prepare file ----
                filepath = ydl.prepare_filename(downloaded_info)

                # If audio: ext becomes .mp3, so correct name
                if choice == "Audio":
                    base = os.path.splitext(filepath)[0]
                    filepath = base + ".mp3"

                with open(filepath, "rb") as f:
                    file_bytes = f.read()

                # Download button
                st.success("✅ Download ready!")

                if choice == "Video":
                    st.download_button(
                        label="Click to Download Video",
                        data=file_bytes,
                        file_name=f"{downloaded_info['title']}.mp4",
                        mime="video/mp4"
                    )
                else:
                    st.download_button(
                        label="Click to Download Audio",
                        data=file_bytes,
                        file_name=f"{downloaded_info['title']}.mp3",
                        mime="audio/mpeg"
                    )

    except Exception as e:
        st.error(f"An error occurred:\n{str(e)}")

st.markdown('</div>', unsafe_allow_html=True)


# ========== COUNTER ==========

COUNTER_FILE = "counter.txt"

def increment_counter():
    if not os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, "w") as f:
            f.write("0")

    with open(COUNTER_FILE, "r+") as f:
        count = int(f.read().strip() or 0) + 1
        f.seek(0)
        f.write(str(count))
        f.truncate()
    return count

if "counted" not in st.session_state:
    st.session_state.counted = True
    total_uses = increment_counter()
else:
    with open(COUNTER_FILE, "r") as f:
        total_uses = int(f.read().strip() or 0)


# ----- Footer -----
st.markdown("""
<div class="footer">
    This downloader uses <strong>yt-dlp</strong> for video extraction. 
    All site logos and icons are property of their respective owners!
</div>
""", unsafe_allow_html=True)
