#!/usr/bin/env python3
"""
Burn a millisecond clock onto the footage WITHOUT altering a single pixel of
the original picture.

WHY IT IS BUILT THIS WAY. Three separate ways to lose information, all avoided:

  1. Overwriting pixels.  The text goes into a black band PADDED ON below the
     picture, not drawn over it. Every original pixel survives untouched, so
     the annotated file is still valid for measurement.
  2. Re-encoding loss.  -qp 0 is mathematically lossless H.264. The decoded
     frames are bit-identical to the source, verified by framemd5 (--verify).
  3. Frame rate resampling.  -fps_mode passthrough keeps every one of the
     source's frames at its original timestamp. No fps filter anywhere: an
     earlier version of this analysis resampled to 30 fps and silently threw
     away half the real information.

THE TIME BASE. The CCTV overlay ticks in whole seconds, useless for timing a
one-second event, but the tick EDGES are visible and fall at video t = n+0.100
(measured gaps of 3.033, 0.967 and 2.000 s between digit changes, all within
35 ms of exact integers, confirming real-time recording). That pins:

    video t = 0  ==  10:59:25.900 Beijing  ==  08:44:25.900 Nepal

good to about +/-35 ms. Nepal is UTC+5:45, Beijing UTC+8. Seismic origin
08:37:10 NPT (USGS/GFZ), so "T+" is the elapsed time the border-clock argument
turns on.

Usage:
    annotate.py <in.mp4> [out.mkv] [--from S] [--to S] [--verify]
"""
import argparse, os, subprocess, sys

BJ0 = 10*3600 + 59*60 + 25.9
OFFSET_NPT = 2*3600 + 15*60
COLLAPSE = 8*3600 + 37*60 + 10
PAD = 132                                    # black band height, in pixels


def _hms(s):
    return f"{int(s)//3600:02d}:{int(s)%3600//60:02d}:{s%60:06.3f}"


def _clock(base, label):
    e = lambda x: x.replace(",", "\\,")
    h  = e(f"floor(mod(({base}+t)/3600,24))")
    m  = e(f"floor(mod(({base}+t)/60,60))")
    s  = e(f"floor(mod({base}+t,60))")
    ms = e(f"floor(mod(({base}+t)*1000,1000))")
    return (f"{label} %{{eif\\:{h}\\:d\\:2}}\\:%{{eif\\:{m}\\:d\\:2}}"
            f"\\:%{{eif\\:{s}\\:d\\:2}}.%{{eif\\:{ms}\\:d\\:3}}")


def _elapsed(label, shift=0.0):
    base = BJ0 - OFFSET_NPT - COLLAPSE + shift
    e = lambda x: x.replace(",", "\\,")
    m  = e(f"floor(({base}+t)/60)")
    s  = e(f"floor(mod({base}+t,60))")
    ms = e(f"floor(mod(({base}+t)*1000,1000))")
    return (f"{label} %{{eif\\:{m}\\:d\\:1}}\\:%{{eif\\:{s}\\:d\\:2}}"
            f".%{{eif\\:{ms}\\:d\\:3}}")


def build(src, out, t0=None, t1=None, verify=False):
    # WINDOWING BUG, fixed 6 Sept. With -ss, ffmpeg resets the output's
    # timestamps to zero, so drawtext's `t` is CLIP-relative. The clock bases
    # below are SOURCE-relative, so every windowed clip came out slow by
    # exactly the window start (a 24 s window read 10:59:26.6 where the CCTV's
    # own overlay read 10:59:50). Caught by comparing the burnt-in clock
    # against the station clock in the same frame - which is the check that
    # should have been in here from the start, and now is (see the self-test
    # printed at the end).
    shift = t0 or 0.0
    probe = subprocess.run(
        ["ffprobe","-v","error","-select_streams","v:0","-show_entries",
         "stream=width,height","-of","csv=p=0", src],
        capture_output=True, text=True, check=True).stdout.strip()
    w, h = (int(v) for v in probe.split(","))

    F = "fontcolor=yellow:fontsize=26:x=14"
    fps = _fps(src)
    f0 = int(round(shift * fps))
    rows = [(f"src frame %{{eif\\:n+{f0}\\:d}}    src t %{{eif\\:t+{shift}\\:d\\:2}}."
             f"%{{eif\\:mod((t+{shift})*1000\\,1000)\\:d\\:3}} s", h + 8),
            (_clock(BJ0 + shift, "Beijing"), h + 40),
            (_clock(BJ0 - OFFSET_NPT + shift, "Nepal  "), h + 72),
            (_elapsed("T+     ", shift), h + 104)]
    vf = (f"pad={w}:{h+PAD}:0:0:black,"
          + ",".join(f"drawtext=text='{txt}':{F}:y={y}" for txt, y in rows))

    cmd = ["ffmpeg", "-v", "error", "-y"]
    if t0 is not None: cmd += ["-ss", str(t0)]
    if t1 is not None: cmd += ["-to", str(t1)]
    cmd += ["-i", src, "-vf", vf,
            "-c:v", "libx264", "-qp", "0", "-preset", "medium",
            "-pix_fmt", "yuv420p",   # SOURCE format: converting to 444 recovers
            "-fps_mode", "passthrough", "-an", out]
    subprocess.run(cmd, check=True)

    n_in = _count(src); n_out = _count(out)
    print(f"wrote {out}  ({os.path.getsize(out)/1e6:.1f} MB)")
    print(f"  frames: {n_in} in -> {n_out} out"
          + ("  (windowed)" if t0 is not None else
             ("  OK, none lost" if n_in == n_out else "  !! MISMATCH")))
    print(f"  picture {w}x{h} untouched; text sits in a {PAD}px band below it")
    if shift:
        print(f"  windowed from {shift:g} s: clocks shifted by +{shift:g} s and "
              f"frames numbered from {f0} so they stay SOURCE-relative")
    print(f"  SELF-CHECK: at clip t=0 the burnt-in Beijing clock should read "
          f"{_hms(BJ0 + shift)}")
    print(f"              compare it against the station's own overlay in the "
          f"same frame; they must agree to the second")

    if verify:
        a, b = _md5(src, w, h), _md5(out, w, h)
        same = a == b
        print(f"  framemd5 of the picture area: "
              f"{'IDENTICAL - bit-for-bit lossless' if same else 'DIFFER'}")


def _fps(p):
    r = subprocess.run(["ffprobe","-v","error","-select_streams","v:0",
                        "-show_entries","stream=r_frame_rate","-of","csv=p=0",p],
                       capture_output=True, text=True).stdout.strip()
    a, b = r.split("/"); return float(a)/float(b)


def _count(p):
    r = subprocess.run(["ffprobe","-v","error","-select_streams","v:0",
                        "-count_frames","-show_entries","stream=nb_read_frames",
                        "-of","csv=p=0",p], capture_output=True, text=True)
    return r.stdout.strip()


def _md5(p, w, h):
    """md5 of the ORIGINAL picture region only, so padding is excluded"""
    # -an -map 0:v:0 matters: framemd5 otherwise emits AUDIO lines too, and
    # comparing a file that has audio against one that does not silently
    # misaligns every row.
    r = subprocess.run(["ffmpeg","-v","error","-i",p,"-an","-map","0:v:0",
                        "-vf",f"crop={w}:{h}:0:0","-f","framemd5","-"],
                       capture_output=True, text=True)
    return [l.split(",")[-1].strip() for l in r.stdout.splitlines()
            if not l.startswith("#")]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("out", nargs="?", default="annotated_lossless.mkv")
    ap.add_argument("--from", dest="t0", type=float); ap.add_argument("--to", dest="t1", type=float)
    ap.add_argument("--verify", action="store_true")
    a = ap.parse_args()
    build(a.src, a.out, a.t0, a.t1, a.verify)
