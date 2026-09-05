#!/usr/bin/env bash
# Pull a clip and find out how much timing information is actually in it.
#
# WHY THE FIRST STEP MATTERS. A CCTV source recorded at 1 fps and re-uploaded
# at 30 fps has 30 fps in the container and one unique image per second. ffprobe
# reports 30 and is telling the truth about the container while being useless
# about the content. mpdecimate drops frames that are near-duplicates of their
# predecessor, so counting what survives gives the UNIQUE frame rate — the rate
# that actually sets how well a velocity can be measured. Everything downstream
# depends on this number, so it is measured, not assumed.
#
# Usage:  research/video/probe_and_extract.sh <url-or-file> <tag>
# Output: research/video/<tag>/  — frames as zero-padded PNGs
#
# NOTE ON WHAT IS KEPT. Frames and video are third-party material and do NOT go
# in the repository; research/video/ is gitignored. The MEASUREMENTS taken from
# them, with provenance, go in research/event-dossier.md. This is the same rule
# PUBLISHING.md already applies to the @vantortech stills.
set -euo pipefail

SRC="${1:?usage: probe_and_extract.sh <url-or-file> <tag>}"
TAG="${2:?usage: probe_and_extract.sh <url-or-file> <tag>}"
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="$HERE/$TAG"
mkdir -p "$OUT"

# Runs both on the server (repo venv) and on a laptop (system packages), because
# YouTube blocks datacentre IPs with a bot check and the download has to happen
# on a residential connection. Everything after the download is identical.
VENV="$HERE/../../.venv/bin"
if [ -x "$VENV/python" ]; then PY="$VENV/python"; else PY="$(command -v python3)"; fi
if [ -x "$VENV/yt-dlp" ]; then YTDLP="$VENV/yt-dlp"; else YTDLP="$(command -v yt-dlp || true)"; fi

VID="$OUT/source.mp4"
if [ -s "$VID" ]; then
  echo "== $VID already present, skipping download =="
elif [[ "$SRC" =~ ^https?:// ]]; then
  [ -n "$YTDLP" ] || { echo "yt-dlp not found (Arch: pacman -S yt-dlp)"; exit 1; }
  echo "== downloading (best quality available; resolution limits placement accuracy) =="
  # COOKIES env var lets you pass --cookies-from-browser NAME if a login is
  # needed. Prefer running this on the machine that already has the browser
  # rather than copying a Google session cookie onto a server.
  "$YTDLP" ${COOKIES:+--cookies-from-browser "$COOKIES"} \
      -f 'bestvideo[ext=mp4]+bestaudio/best/best' --merge-output-format mp4 \
      -o "$VID" "$SRC"
else
  cp "$SRC" "$VID"
fi

echo
echo "== container says =="
ffprobe -v error -select_streams v:0 \
  -show_entries stream=width,height,r_frame_rate,avg_frame_rate,nb_frames,duration \
  -of default=noprint_wrappers=1 "$VID"

echo
echo "== how many of those frames are actually different? =="
# mpdecimate drops near-duplicates; the survivors are the real information.
TOT=$(ffprobe -v error -count_frames -select_streams v:0 \
        -show_entries stream=nb_read_frames -of csv=p=0 "$VID")
UNIQ=$(ffmpeg -v error -i "$VID" -vf mpdecimate -f null - 2>&1 \
        | grep -c 'keep' || true)
if [ "${UNIQ:-0}" -eq 0 ]; then
  UNIQ=$(ffmpeg -v info -i "$VID" -vf mpdecimate -loglevel debug -f null - 2>&1 \
          | grep -c 'keep pts' || echo 0)
fi
DUR=$(ffprobe -v error -select_streams v:0 -show_entries format=duration \
        -of csv=p=0 "$VID" 2>/dev/null || echo 0)
echo "  total frames decoded : $TOT"
echo "  unique frames        : $UNIQ"
echo "  duration (s)         : $DUR"
"$PY" - "$TOT" "$UNIQ" "$DUR" <<'PY'
import sys
tot, uniq, dur = int(sys.argv[1] or 0), int(sys.argv[2] or 0), float(sys.argv[3] or 0)
if dur > 0:
    print(f"  container rate       : {tot/dur:6.2f} fps")
    if uniq:
        print(f"  UNIQUE rate          : {uniq/dur:6.2f} fps   <-- this is what counts")
        print(f"  duplication factor   : {tot/max(uniq,1):6.2f}x")
        n = uniq/dur
        print()
        if n < 1.5:
            print("  ~1 fps of real information. Position tracking across many stills")
            print("  still works (the time base is exact); occlusion timing does not.")
        else:
            print(f"  {n:.0f} distinct images per second — enough for a proper")
            print("  position-time fit and a curvature (deceleration) test.")
PY

echo
echo "== extracting unique frames to $OUT/frames =="
mkdir -p "$OUT/frames"
# CAREFUL. mpdecimate drops a VARIABLE number of duplicates: many while the
# scene is static, few once the flood is moving. So the surviving frames are
# NOT evenly spaced in time, and treating their sequence number as a clock
# would stretch the early part of the record and compress the fast part —
# biasing exactly the acceleration we want to measure. Write each survivor
# with its true presentation timestamp instead, and let the fit use that.
ffmpeg -v error -i "$VID" -vf mpdecimate -vsync 0 "$OUT/frames/f_%05d.png"
ffmpeg -hide_banner -nostats -i "$VID" -vf mpdecimate,showinfo -vsync 0 \
       -f null - 2>&1 \
  | "$PY" -c '
import re, sys
# showinfo emits  n:  0 pts:  0 pts_time:0  ... — the fields are NOT adjacent,
# so pull each one independently instead of matching them as a pair. Getting
# this wrong silently produces an empty file, which is worse than an error.
print("file,time_s")
for line in sys.stdin:
    if "pts_time:" not in line:
        continue
    n = re.search(r"\bn:\s*(\d+)", line)
    t = re.search(r"\bpts_time:([\d.]+)", line)
    if n and t:
        # image2 numbers its output from 1; showinfo numbers frames from 0
        print(f"f_{int(n.group(1))+1:05d}.png,{float(t.group(1)):.6f}")
' > "$OUT/frames/times.csv"
echo "  $(ls "$OUT/frames"/*.png 2>/dev/null | wc -l) unique frames written"
echo "  timestamps in $OUT/frames/times.csv ($(($(wc -l < "$OUT/frames/times.csv")-1)) rows)"
echo
echo "Next: pick the plume front in a spread of frames, note each frame's"
echo "time_s from times.csv and its distance along the flow path from Google"
echo "Earth landmarks, then feed time_s,distance_m to fit_speed.py."
