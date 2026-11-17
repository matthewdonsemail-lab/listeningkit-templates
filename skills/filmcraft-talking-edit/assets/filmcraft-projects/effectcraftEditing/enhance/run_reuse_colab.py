"""NVIDIA NemotronLabs RE-USE (huggingface.co/nvidia/NVIDIA-NemotronLabs-RE-USE) on Windows: the model's own chunked
inference (inference_chunk.py: 5 s chunks, 50% overlap, Hann overlap-add), with the shim/mamba_ssm stand-in instead of
the CUDA-only mamba_ssm. Reads/writes WAV with soundfile; output is the same length and rate as the input.
  python run_reuse.py in.wav out.wav [--chunk 5] [--bwe 48000]"""
import argparse
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, "reuse")]  # Colab: the real mamba_ssm is installed

import soundfile as sf  # noqa: E402
import torch  # noqa: E402
import torch.nn as nn  # noqa: E402
from safetensors.torch import load_file  # noqa: E402

from models.generator_SEMamba_time_d4 import SEMamba  # noqa: E402
from models.stfts import mag_phase_istft, mag_phase_stft  # noqa: E402
from utils.util import load_config, pad_or_trim_to_match  # noqa: E402

RELU = nn.ReLU()
make_even = lambda v: (lambda r: r if r % 2 == 0 else r + 1)(int(round(v)))

ap = argparse.ArgumentParser()
ap.add_argument("inp"); ap.add_argument("out")
ap.add_argument("--chunk", type=float, default=5.0); ap.add_argument("--hop", type=float, default=0.5)
args = ap.parse_args()

dev = torch.device("cuda")
cfg = load_config(os.path.join(HERE, "reuse", "recipes",
                               "USEMamba_30x1_lr_00002_norm_05_vq_065_nfft_320_hop_40_NRIR_012_pha_0005_com_04_early_001.yaml"))
model = SEMamba(cfg=cfg)
missing, unexpected = model.load_state_dict(load_file(os.path.join(HERE, "reuse", "model.safetensors")), strict=True), None
model = model.to(dev).eval()
n_fft, hop, win = cfg["stft_cfg"]["n_fft"], cfg["stft_cfg"]["hop_size"], cfg["stft_cfg"]["win_size"]
cf, base_sr = cfg["model_cfg"]["compress_factor"], cfg["stft_cfg"]["sampling_rate"]

wav, sr = sf.read(args.inp, dtype="float32", always_2d=True)
x = torch.from_numpy(wav.T.copy()).to(dev)  # [C, N]
cs = int(args.chunk * sr); hl = int(args.hop * cs)
window = torch.clamp(torch.hann_window(cs, device=dev), min=1e-7)
nf, hs, ws = make_even(n_fft * sr // base_sr), make_even(hop * sr // base_sr), make_even(win * sr // base_sr)
out = torch.zeros_like(x); wsum = torch.zeros_like(x)
n = max(1, math.ceil((x.shape[1] - cs) / hl) + 1)
t0 = time.time()
with torch.no_grad():
    for c in range(x.shape[0]):
        xc = x[c:c + 1]
        for i in range(n):
            seg = xc[:, i * hl:i * hl + cs] if i < n - 1 else xc[:, -cs:]
            mag, pha, _ = mag_phase_stft(seg, n_fft=nf, hop_size=hs, win_size=ws, compress_factor=cf, center=True,
                                         addeps=False)
            amp_g, pha_g, _ = model(mag, pha)
            m = torch.expm1(RELU(amp_g))
            zero = torch.sum(m == 0, 1) / m.shape[1]
            amp_g[:, :, (zero > 0.5)[0]] = 0  # the model's own "strange sweep artifact" fix
            y = pad_or_trim_to_match(seg, mag_phase_istft(amp_g, pha_g, nf, hs, ws, cf), pad_value=1e-8)
            w = window[:y.shape[1]]
            if i < n - 1:
                out[c:c + 1, i * hl:i * hl + cs] += y * w; wsum[c:c + 1, i * hl:i * hl + cs] += w
            else:
                out[c:c + 1, -cs:] += y * w; wsum[c:c + 1, -cs:] += w
            if i % 10 == 0 or i == n - 1:
                el = time.time() - t0
                left = el / (i + 1) * (n - i - 1)
                print(f"{os.path.basename(args.inp)}  chunk {i + 1}/{n}  {100 * (i + 1) / n:5.1f}%  "
                      f"elapsed {el / 60:4.1f} min  left ~{left / 60:4.1f} min", flush=True)
out = (out / wsum).cpu().numpy().T
sf.write(args.out, out, sr, subtype="PCM_16")
print(f"done {args.out}: {x.shape[1] / sr:.1f}s of audio in {time.time() - t0:.1f}s")
