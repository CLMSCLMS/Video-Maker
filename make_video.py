#!/usr/bin/env python3
"""Build the music video from project.json, the media/ folder and the song.

Usage:
  python3 make_video.py            # full 1080p render  -> out/music_video.mp4
  python3 make_video.py --preview  # fast 720p render   -> out/preview.mp4
  python3 make_video.py --list     # show which shots still need a file

Missing shots are rendered as storyboard cards, so you can preview the
whole video before you have every photo or clip.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import textwrap
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent
MEDIA = ROOT / "media"
BUILD = ROOT / "build"
OUT = ROOT / "out"

IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".bmp", ".tif", ".tiff"}
VIDEO_EXT = {".mp4", ".mov", ".m4v", ".avi", ".mkv", ".webm", ".mts"}
FONT_SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FONT_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"ffmpeg failed:\n{' '.join(map(str, cmd))}\n{r.stderr[-2000:]}")


def probe_duration(path):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(path)], capture_output=True, text=True)
    return float(r.stdout.strip())


def find_media(shot_id):
    for p in sorted(MEDIA.glob(shot_id + ".*")):
        if p.suffix.lower() in IMAGE_EXT | VIDEO_EXT:
            return p
    return None


# ---------- timeline ----------

def build_timeline(proj, total):
    """Give every shot and lyric line an absolute start/end time."""
    secs = proj["sections"]
    if secs[-1]["start"] >= total - 5:
        # Planned timings run past the song: stretch them to fit.
        k = total / proj["length_if_no_audio"]
        print(f"Section starts don't fit a {total:.0f}s song - scaling them by {k:.2f}.")
        secs = [{**s, "start": s["start"] * k} for s in secs]
    shots, lines = [], []
    for i, sec in enumerate(secs):
        start = sec["start"]
        end = secs[i + 1]["start"] if i + 1 < len(secs) else total
        dur = end - start
        weights = [s.get("weight", 1) for s in sec["shots"]]
        t = start
        for s, w in zip(sec["shots"], weights):
            d = dur * w / sum(weights)
            shots.append({**s, "section": sec["name"], "t0": t, "t1": t + d})
            t += d
        # lyric lines: a string (spread evenly) or {"t": seconds, "text": ...}
        n = len(sec["lyrics"])
        for j, ln in enumerate(sec["lyrics"]):
            if isinstance(ln, dict):
                lines.append(ln)
            else:
                lines.append({"t": start + 1 + (dur - 2) * j / max(n, 1), "text": ln})
    for k, ln in enumerate(lines):
        nxt = lines[k + 1]["t"] if k + 1 < len(lines) else total
        ln["end"] = ln.get("end", min(nxt - 0.15, ln["t"] + 7))
    return shots, lines


# ---------- images ----------

def fit_canvas(img, w, h):
    """Fill a w x h frame. Photos that don't match (e.g. phone portrait)
    sit on a blurred copy of themselves instead of being cropped."""
    img = ImageOps.exif_transpose(img).convert("RGB")
    ratio = img.width / img.height
    if abs(ratio - w / h) < 0.25:
        return ImageOps.fit(img, (w, h), Image.LANCZOS)
    bg = ImageOps.fit(img, (w, h), Image.LANCZOS).filter(ImageFilter.GaussianBlur(w // 40))
    bg = Image.blend(bg, Image.new("RGB", (w, h)), 0.35)
    fg = ImageOps.contain(img, (w, h), Image.LANCZOS)
    bg.paste(fg, ((w - fg.width) // 2, (h - fg.height) // 2))
    return bg


def storyboard_card(shot, w, h):
    """Placeholder frame for a shot that has no photo/clip yet."""
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):  # warm dusk gradient
        f = y / h
        d.line([(0, y), (w, y)], fill=(int(40 + 50 * f), int(30 + 25 * f), int(22 + 10 * f)))
    s = w / 1920
    small = ImageFont.truetype(FONT_SANS, int(30 * s))
    big = ImageFont.truetype(FONT_SERIF_BOLD, int(52 * s))
    d.text((90 * s, 60 * s), shot["section"].upper() + f"   ·   add media/{shot['id']}.jpg or .mp4",
           font=small, fill=(230, 190, 120))
    y = 120 * s
    for line in textwrap.wrap(shot["note"], 48):
        d.text((90 * s, y), line, font=big, fill=(245, 238, 225))
        y += 76 * s
    return img


MOVES = ["in", "out", "right", "in", "left", "out"]


def render_still(img, shot, idx, w, h, fps, frames, dst, card=False):
    big_w, big_h = w * 2, h * 2  # upscale first so the slow zoom is smooth
    src = BUILD / f"{dst.stem}_src.png"
    fit_canvas(img, big_w, big_h).save(src)
    move = "in" if card else shot.get("move", MOVES[idx % len(MOVES)])
    n = max(frames - 1, 1)
    z, x, y = {
        "in":    (f"1+0.10*on/{n}", "(iw-iw/zoom)/2", "(ih-ih/zoom)/2"),
        "out":   (f"1.10-0.10*on/{n}", "(iw-iw/zoom)/2", "(ih-ih/zoom)/2"),
        "right": ("1.08", f"(iw-iw/zoom)*on/{n}", "(ih-ih/zoom)/2"),
        "left":  ("1.08", f"(iw-iw/zoom)*(1-on/{n})", "(ih-ih/zoom)/2"),
        "none":  ("1", "0", "0"),
    }[move]
    vf = (f"zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={w}x{h}:fps={fps},"
          f"setsar=1,format=yuv420p")
    run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-vf", vf,
         "-frames:v", str(frames), "-c:v", "libx264", "-preset", "veryfast",
         "-crf", "18", "-r", str(fps), str(dst)])
    src.unlink()


def render_clip(path, shot, w, h, fps, frames, dst):
    speed = shot.get("speed", 1)
    vf = (f"[0:v]setpts=PTS/{speed},fps={fps},split[a][b];"
          f"[a]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},"
          f"boxblur=30,eq=brightness=-0.08[bg];"
          f"[b]scale={w}:{h}:force_original_aspect_ratio=decrease[fg];"
          f"[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1,format=yuv420p")
    run(["ffmpeg", "-y", "-v", "error", "-stream_loop", "-1",
         "-ss", str(shot.get("in", 0)), "-i", str(path), "-filter_complex", vf,
         "-an", "-frames:v", str(frames), "-c:v", "libx264", "-preset", "veryfast",
         "-crf", "18", str(dst)])


def render_shot(args):
    idx, shot, w, h, fps = args
    f0, f1 = round(shot["t0"] * fps), round(shot["t1"] * fps)
    frames = max(f1 - f0, 1)
    dst = BUILD / f"seg_{idx:03d}.mp4"
    path = find_media(shot["id"])
    if path and path.suffix.lower() in VIDEO_EXT:
        render_clip(path, shot, w, h, fps, frames, dst)
    else:
        img = Image.open(path) if path else storyboard_card(shot, w * 2, h * 2)
        render_still(img, shot, idx, w, h, fps, frames, dst, card=not path)
    return dst


# ---------- lyrics ----------

def ass_time(t):
    t = max(t, 0)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def write_subtitles(proj, lines, w, h):
    s = h / 1080
    ass = [
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {w}", f"PlayResY: {h}", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, "
        "Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV",
        f"Style: Lyric,DejaVu Serif,{int(54*s)},&H00F5F5FA,&H00101010,&H80000000,"
        f"1,0,1,{max(2*s,1):.1f},{max(2*s,1):.1f},2,{int(160*s)},{int(160*s)},{int(70*s)}",
        f"Style: Title,DejaVu Serif,{int(96*s)},&H00F0F5FA,&H00101010,&H80000000,"
        f"1,0,1,{3*s:.1f},{3*s:.1f},5,60,60,60",
        f"Style: Sub,DejaVu Sans,{int(36*s)},&H00B4D2E6,&H00101010,&H80000000,"
        f"0,1,1,{2*s:.1f},{2*s:.1f},5,60,60,60", "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        f"Dialogue: 0,{ass_time(1.5)},{ass_time(10)},Title,,0,0,0,,"
        f"{{\\fad(1200,900)\\pos({w//2},{int(h*0.44)})}}{proj['title']}",
        f"Dialogue: 0,{ass_time(2.5)},{ass_time(10)},Sub,,0,0,0,,"
        f"{{\\fad(1200,900)\\pos({w//2},{int(h*0.56)})}}{proj.get('subtitle','')}",
    ]
    srt = []
    if proj.get("show_lyrics", True):
        for i, ln in enumerate(lines, 1):
            ass.append(f"Dialogue: 0,{ass_time(ln['t'])},{ass_time(ln['end'])},Lyric,,0,0,0,,"
                       f"{{\\fad(350,350)}}{ln['text']}")
    for i, ln in enumerate(lines, 1):
        a, b = (ass_time(x).replace(".", ",") + "0" for x in (ln["t"], ln["end"]))
        srt += [str(i), f"0{a} --> 0{b}", ln["text"], ""]
    (BUILD / "lyrics.ass").write_text("\n".join(ass) + "\n")
    OUT.mkdir(exist_ok=True)
    (OUT / "lyrics.srt").write_text("\n".join(srt))


# ---------- main ----------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true", help="fast 720p render")
    ap.add_argument("--list", action="store_true", help="list missing shots and exit")
    ap.add_argument("--project", default=str(ROOT / "project.json"))
    a = ap.parse_args()

    proj = json.loads(Path(a.project).read_text())
    all_shots = [s for sec in proj["sections"] for s in sec["shots"]]
    if a.list:
        have = 0
        for s in all_shots:
            p = find_media(s["id"])
            have += bool(p)
            print(("  ok   " if p else "  --   ") + s["id"] + ("" if p else f"   {s['note']}"))
        print(f"\n{have}/{len(all_shots)} shots have media.")
        return

    w, h = proj["resolution"]
    if a.preview:
        w, h = 1280, 720
    fps = proj["fps"]
    audio = ROOT / proj["audio"]
    has_audio = audio.exists()
    total = probe_duration(audio) if has_audio else proj["length_if_no_audio"]
    if not has_audio:
        print(f"No song at {proj['audio']} - rendering silent at {total}s with planned timings.")

    shutil.rmtree(BUILD, ignore_errors=True)
    BUILD.mkdir()
    OUT.mkdir(exist_ok=True)
    shots, lines = build_timeline(proj, total)

    jobs = [(i, s, w, h, fps) for i, s in enumerate(shots)]
    with ThreadPoolExecutor(max(os.cpu_count() // 2, 1)) as ex:
        for n, seg in enumerate(ex.map(render_shot, jobs), 1):
            print(f"\rRendering shots {n}/{len(jobs)}", end="", flush=True)
    print()

    (BUILD / "list.txt").write_text(
        "".join(f"file 'seg_{i:03d}.mp4'\n" for i in range(len(shots))))
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
         "-i", str(BUILD / "list.txt"), "-c", "copy", str(BUILD / "joined.mp4")])

    write_subtitles(proj, lines, w, h)
    fade_out = max(total - 3, 0)
    audio_in = (["-i", str(audio)] if has_audio else
                ["-f", "lavfi", "-t", str(total), "-i", "anullsrc=r=48000:cl=stereo"])
    dst = OUT / ("preview.mp4" if a.preview else "music_video.mp4")
    print("Adding lyrics and audio...")
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", "joined.mp4", *audio_in,
         "-vf", f"subtitles=lyrics.ass,fade=in:st=0:d=1.5,fade=out:st={fade_out}:d=3",
         "-af", f"afade=out:st={fade_out}:d=3",
         "-map", "0:v", "-map", "1:a", "-shortest",
         "-c:v", "libx264", "-preset", "medium", "-crf", "20" if a.preview else "17",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k",
         "-movflags", "+faststart", str(dst.resolve())],
        cwd=BUILD, check=True)
    print(f"Done: {dst.relative_to(ROOT)}  (lyrics file for YouTube: out/lyrics.srt)")


if __name__ == "__main__":
    main()
