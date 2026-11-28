"""Render an EffectCraft comp at full quality in chunks, then join them and mux the audio once.

    python render_chunks.py PROJECT.ecproj OUT.mp4 [--comp 1] [--chunk 4] [--gain 0]

Why chunks: a full-res render of a heavy comp (deep glows, 2560x1440 upscaled footage) built up memory
until it died ("memory allocation of ... failed", no moov atom). Each chunk is its own process, so memory
is freed between them, a failure costs one chunk, and a rerun skips finished chunks (resumable).

How it works
1. Reads the comp's duration from the .ecproj and renders [k*chunk, (k+1)*chunk) as h264 at 16 Mbit,
   audio off. Each chunk is retried up to 3 times.
2. Renders the comp audio once as WAV (a seam-free mix; chunk audio would click at each join).
3. Joins the chunks with ffmpeg's concat demuxer (stream copy, no re-encode) and muxes the WAV as AAC
   256k through `volume` + `alimiter=limit=0.79:level=disabled` (true peak <= -1 dBFS after AAC).
4. Check it: `python ../validate.py PROJECT --video OUT.mp4` (-16..-13 LUFS, peak <= -1 dB).
   If loudness is low, rerun with --gain (dB) and the chunks are reused.
"""
import json, os, shutil, subprocess, sys, time

CLI = "C:/Users/0/effectcraft/target/release/effectcraft-cli.exe"
T = 254016000000


def arg(n, d):
    return sys.argv[sys.argv.index(n) + 1] if n in sys.argv else d


P, OUT = sys.argv[1], sys.argv[2]
comp, step, gain = arg("--comp", "1"), float(arg("--chunk", 4)), float(arg("--gain", 0))
END = json.load(open(P, encoding="utf-8"))["items"][comp]["kind"]["duration"] / T
work = os.path.splitext(OUT)[0] + "_chunks/"
os.makedirs(work, exist_ok=True)
t0 = time.time()
starts = [round(i * step, 4) for i in range(int(END // step) + 1) if i * step < END - 1e-6]
for k, a in enumerate(starts):
    out = f"{work}c{k:03d}.mp4"
    if os.path.exists(out) and os.path.getsize(out) > 10000:
        continue
    for attempt in range(3):
        r = subprocess.run([CLI, "render", "--project", P, "--comp", comp, "--out", out, "--format", "h264", "--start", str(a),
                            "--end", str(min(END, a + step)), "--resolution", "full", "--quality", "best", "--audio", "off", "--bitrate", "16000"],
                           capture_output=True, text=True)
        if r.returncode == 0 and os.path.exists(out):
            break
        print(f"chunk {k} attempt {attempt + 1} failed: {r.stderr[-200:]}", flush=True)
        if os.path.exists(out):
            os.remove(out)
    else:
        raise SystemExit(f"chunk {k} failed 3 times")
    print(f"chunk {k + 1}/{len(starts)} done, {(time.time() - t0) / 60:.1f} min", flush=True)
subprocess.run([CLI, "render", "--project", P, "--comp", comp, "--out", work + "audio.wav", "--format", "wav"], capture_output=True, check=True)
open(work + "list.txt", "w").write("".join(f"file 'c{k:03d}.mp4'\n" for k in range(len(starts))))
subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", work + "list.txt", "-i", work + "audio.wav",
                "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-af", f"volume={gain}dB,alimiter=limit=0.79:level=disabled", "-c:a", "aac", "-b:a", "256k",
                "-movflags", "+faststart", "-shortest", OUT], check=True)
shutil.rmtree(work)
print(f"{OUT}: {os.path.getsize(OUT) // 1048576} MB, {END:.2f} s, {(time.time() - t0) / 60:.1f} min")
