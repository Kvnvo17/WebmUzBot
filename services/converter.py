import os
import uuid
import asyncio
import tempfile
from typing import Optional


async def _run(cmd: list) -> tuple[int, bytes, bytes]:
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, err = await proc.communicate()
    return proc.returncode, out, err


async def probe(path: str) -> Optional[dict]:
    code, out, err = await _run([
        "ffprobe", "-v", "error",
        "-print_format", "json",
        "-show_format", "-show_streams", path,
    ])
    if code != 0:
        return None
    import json
    try:
        return json.loads(out.decode("utf-8", errors="ignore"))
    except Exception:
        return None


async def get_video_info(path: str):
    """Return (width, height, duration) or None."""
    info = await probe(path)
    if not info:
        return None
    v = None
    for s in info.get("streams", []):
        if s.get("codec_type") == "video":
            v = s
            break
    if not v:
        return None
    w = int(v.get("width") or 0)
    h = int(v.get("height") or 0)
    dur = 0.0
    try:
        dur = float(v.get("duration") or info.get("format", {}).get("duration") or 0)
    except Exception:
        dur = 0.0
    return w, h, dur


def _tmp(suffix: str) -> str:
    d = tempfile.gettempdir()
    return os.path.join(d, f"{uuid.uuid4().hex}{suffix}")

async def mp4_to_webm(src: str) -> Optional[str]:
    dst = _tmp(".webm")
    code, _, err = await _run([
        "ffmpeg", "-y",
        "-i", src,
        "-vf", "scale=512:512:force_original_aspect_ratio=decrease,"
               "pad=512:512:(ow-iw)/2:(oh-ih)/2:color=black",
        "-c:v", "libvpx-vp9",
        "-b:v", "0", "-crf", "32",
        "-an",
        "-t", "3",
        dst,
    ])
    if code != 0 or not os.path.exists(dst):
        print("ffmpeg error:", err.decode("utf-8", errors="ignore"))
        return None
    return dst
    
async def webm_to_mp4(src: str) -> Optional[str]:
    dst = _tmp(".mp4")
    code, _, err = await _run([
        "ffmpeg", "-y",
        "-i", src,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-an",
        dst,
    ])
    if code != 0 or not os.path.exists(dst):
        print("ffmpeg error:", err.decode("utf-8", errors="ignore"))
        return None
    return dst


def safe_remove(*paths):
    for p in paths:
        try:
            if p and os.path.exists(p):
                os.remove(p)
        except Exception as e:
            print("remove error:", e)
