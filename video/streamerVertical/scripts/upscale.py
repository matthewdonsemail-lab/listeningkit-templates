"""AI upscaling with Real-ESRGAN (x4plus, ncnn-vulkan: runs on any Vulkan GPU, incl. the AMD 780M iGPU).

Two modes:

  Close-up crop (what build.py does per face beat): upscale just the webcam crop, 4x.
    python upscale.py crop CLIP.mp4 --rect X,Y,W,H --range START,END --out closeup_x4.mp4

  Full frame, only the seconds the cut uses: a full-length 2x video, same frame count and timing as
  the source, so it drops in as a replacement source (`file.replaceWithPrecomp`) without re-cutting.
    python upscale.py full CLIP.mp4 --ranges "0,1.04;4.83,8.1" --out CLIP_x2.mp4 [--work DIR]

How it works
- Frames are pulled with ffmpeg as PNG (exact frame numbers: `select=between(n,a,b)`), run through
  `realesrgan-ncnn-vulkan -n realesrgan-x4plus`, then encoded back at 30 fps (x264 CRF 14).
- ALWAYS 4x, then downscale. `-s 2` with this model scrambles tiles (we lost a 25-minute run to it).
  Full mode upscales 4x then Lanczos-downscales to 2x as each batch finishes.
- Frames OUTSIDE the used ranges are Lanczos-scaled 2x (cheap), so the file stays frame-exact.
- Full mode is resumable: work happens in batches of 60 frames, finished batches are listed in
  WORK/done.json, and a rerun after a crash or restart skips them.
- Speed on the 780M: ~7 s per 1280x720 frame at 4x; a 224x312 webcam crop is ~0.8 s per frame.
- Real-ESRGAN lives in %LOCALAPPDATA%/listeningkit/realesrgan/ (realesrgan-ncnn-vulkan-20220424-windows.zip
  from github.com/xinntao/Real-ESRGAN releases, unzipped).
"""
import json, os, shutil, subprocess, sys, tempfile

RE = os.path.join(os.environ.get("LOCALAPPDATA", ""), "listeningkit", "realesrgan", "realesrgan-ncnn-vulkan.exe")
FPS = 30
FF = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]


def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def esrgan(i, o):
    r = subprocess.run([RE, "-i", i, "-o", o, "-n", "realesrgan-x4plus", "-s", "4", "-f", "png"], capture_output=True, text=True)
    if r.returncode or not os.listdir(o):
        raise SystemExit("realesrgan failed: " + r.stderr[-400:])


def frames(clip, f0, f1, d, vf=None):
    os.makedirs(d, exist_ok=True)
    chain = f"select='between(n\\,{f0}\\,{f1})'" + (f",{vf}" if vf else "")
    subprocess.run(FF + ["-i", clip, "-vf", chain, "-fps_mode", "passthrough", "-start_number", str(f0), os.path.join(d, "%06d.png")], check=True)


def encode(pattern, start, out, vf=None):
    subprocess.run(FF + ["-framerate", str(FPS), "-start_number", str(start), "-i", pattern] + (["-vf", vf] if vf else []) +
                   ["-c:v", "libx264", "-crf", "14", "-preset", "medium", "-pix_fmt", "yuv420p", out], check=True)


def crop():
    clip, out = sys.argv[2], arg("--out")
    x, y, w, h = map(int, arg("--rect").split(","))
    a, b = map(float, arg("--range").split(","))
    tmp = tempfile.mkdtemp(dir=os.environ.get("TMPDIR"))
    f0, f1 = int(round(a * FPS)), int(round(b * FPS))
    frames(clip, f0, f1, tmp + "/i", f"crop={w}:{h}:{x}:{y}")
    os.makedirs(tmp + "/o")
    esrgan(tmp + "/i", tmp + "/o")
    encode(tmp + "/o/%06d.png", f0, out)
    shutil.rmtree(tmp)
    print(f"{out}: frames {f0}-{f1} of the source, crop {w}x{h}@{x},{y} -> {w*4}x{h*4}")


def full():
    clip, out = sys.argv[2], arg("--out")
    ranges = [tuple(map(float, r.split(","))) for r in arg("--ranges").split(";")]
    work = arg("--work", os.path.splitext(out)[0] + "_work")
    os.makedirs(work + "/up", exist_ok=True)
    pr = subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0", "-show_entries", "stream=nb_read_packets,width,height",
                         "-of", "json", clip], capture_output=True, text=True)
    st = json.loads(pr.stdout)["streams"][0]
    n, W, H = int(st["nb_read_packets"]), st["width"] * 2, st["height"] * 2
    used = sorted({f for a, b in ranges for f in range(int(a * FPS), min(n, int(round(b * FPS)) + 1))})
    done_f = work + "/done.json"
    done = set(json.load(open(done_f))) if os.path.exists(done_f) else set()
    batches = [used[i:i + 60] for i in range(0, len(used), 60)]
    for k, bt in enumerate(batches):
        if bt[0] in done:
            continue
        tmp = tempfile.mkdtemp(dir=work)
        # contiguous runs inside the batch
        runs, s = [], bt[0]
        for p, q in zip(bt, bt[1:] + [None]):
            if q != p + 1:
                runs.append((s, p)); s = q
        for a, b in runs:
            frames(clip, a, b, tmp + "/i")
        os.makedirs(tmp + "/o")
        esrgan(tmp + "/i", tmp + "/o")
        for f in os.listdir(tmp + "/o"):  # 4x -> 2x, Lanczos
            subprocess.run(FF + ["-i", f"{tmp}/o/{f}", "-vf", f"scale={W}:{H}:flags=lanczos", "-q:v", "2", f"{work}/up/{f[:-4]}.jpg"], check=True)
        shutil.rmtree(tmp)
        done.add(bt[0]); json.dump(sorted(done), open(done_f, "w"))
        print(f"batch {k+1}/{len(batches)} ({bt[0]}-{bt[-1]})", flush=True)
    # every source frame: the upscaled one if it exists, else a Lanczos 2x of the original
    allf = work + "/all"
    os.makedirs(allf, exist_ok=True)
    subprocess.run(FF + ["-i", clip, "-vf", f"scale={W}:{H}:flags=lanczos", "-q:v", "2", "-start_number", "0", allf + "/%06d.jpg"], check=True)
    for f in os.listdir(work + "/up"):
        shutil.copy(f"{work}/up/{f}", f"{allf}/{f}")
    encode(allf + "/%06d.jpg", 0, out + ".noaudio.mp4")
    subprocess.run(FF + ["-i", out + ".noaudio.mp4", "-i", clip, "-map", "0:v", "-map", "1:a?", "-c", "copy", out], check=True)
    os.remove(out + ".noaudio.mp4")
    shutil.rmtree(work)
    print(f"{out}: {n} frames at {W}x{H}, {len(used)} upscaled with Real-ESRGAN")


if __name__ == "__main__":
    {"crop": crop, "full": full}[sys.argv[1]]()
