"""RE-USE on a Colab T4 via the colab CLI (matt, 2026-11-16): builds mamba_ssm for the T4 only (sm_75) with C++20
(Colab's torch 2.14 headers need it), fetches nvidia/NVIDIA-NemotronLabs-RE-USE, then cleans /content/voice_part*.flac
into /content/out/voice_partN_clean.flac with run_reuse.py (5 s chunks, 50% overlap, same length and rate).
  colab exec -s reuse -f colab_job.py"""
import glob
import json
import os
import subprocess
import sys
import tarfile
import time
import urllib.request


def sh(cmd):
    print("$", cmd, flush=True)
    r = subprocess.run(cmd, shell=True)
    if r.returncode:
        raise SystemExit(f"failed: {cmd}")


try:
    import selective_scan_cuda  # noqa: F401
    print("mamba_ssm already built", flush=True)
except ImportError:
    t0 = time.time()
    os.makedirs("/content/src", exist_ok=True)
    meta = json.load(urllib.request.urlopen("https://pypi.org/pypi/mamba-ssm/json"))
    url = [u["url"] for u in meta["urls"] if u["packagetype"] == "sdist"][0]
    urllib.request.urlretrieve(url, "/content/src/mamba.tar.gz")
    with tarfile.open("/content/src/mamba.tar.gz") as tf:
        tf.extractall("/content/src", filter="data")
    src = sorted(glob.glob("/content/src/mamba_ssm-*/"))[0]
    p = os.path.join(src, "setup.py")
    s = open(p).read()
    a = s.index('        cc_flag.append("-gencode")\n        cc_flag.append("arch=compute_75,code=sm_75")')
    z = 'cc_flag.append("arch=compute_121,code=sm_121")'
    b = s.index(z) + len(z)
    s = s[:a] + '        cc_flag += ["-gencode", "arch=compute_75,code=sm_75"]  # T4 only' + s[b:]
    s = s.replace("-std=c++17", "-std=c++20")
    open(p, "w").write(s)
    sh("pip install -q ninja packaging einops")
    print("building mamba_ssm for the T4 (about 10-20 min)...", flush=True)
    r = subprocess.run(f"cd {src} && MAMBA_FORCE_BUILD=TRUE MAX_JOBS=4 pip install --no-build-isolation --no-deps . "
                       "> /content/mamba_build.log 2>&1", shell=True)
    if r.returncode:
        subprocess.run("grep -n -m5 -A4 ' error' /content/mamba_build.log | cut -c1-300", shell=True)
        raise SystemExit("mamba_ssm build failed, see /content/mamba_build.log")
    print(f"mamba_ssm built in {time.time() - t0:.0f}s", flush=True)

sh("pip install -q soundfile safetensors pyyaml einops huggingface_hub")
from huggingface_hub import snapshot_download  # noqa: E402

snapshot_download("nvidia/NVIDIA-NemotronLabs-RE-USE", local_dir="/content/reuse")
os.makedirs("/content/out", exist_ok=True)
for f in sorted(glob.glob("/content/voice_part*.flac")):
    out = "/content/out/" + os.path.basename(f).replace(".flac", "_clean.flac")
    if os.path.exists(out):
        print("done already:", out, flush=True)
        continue
    sh(f"{sys.executable} /content/run_reuse.py {f} {out}")
sh("ls -la /content/out")
