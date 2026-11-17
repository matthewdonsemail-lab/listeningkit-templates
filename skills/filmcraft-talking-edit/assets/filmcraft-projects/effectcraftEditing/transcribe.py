"""AssemblyAI word-timed transcript of matt's EffectCraft editing walkthrough (Cap, 2026-11-16 03.27 PM, raw mic).

Usage: python transcribe.py submit | poll | wait
Reads ASSEMBLY_AI_KEY from ../../.env.local without printing it. Never overwrites an existing transcript.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import assemblyai as aai

ROOT = Path(__file__).resolve().parent
REC = Path(r"C:\Users\0\AppData\Roaming\so.cap.desktop\recordings\Generic PnP Monitor (Display) 2026-11-16 03.27 PM.cap")
JOBS = {"Mic": REC / "content/segments/segment-0/audio-input.m4a"}
TERMS = ["EffectCraft", "FilmCraft", "ArtCraft", "Claude Code", "Hermes", "numpy", "precomp", "precomps", "Excalidraw",
         "cyberpsycho", "thermogram", "CRT", "VHS", "After Effects", "ExtendScript", "JSX", "Nous Research", "Log",
         "ListeningKit", "track matte", "keyframes", "J-cut", "Cap", "AssemblyAI", "TikTok", "The Big Short",
         "Cyberpunk", "GrabCut", "OpenCV", "Python", "render", "LUT", "Codex", "craic"]


def key() -> str:
    for line in (ROOT.parents[1] / ".env.local").read_text(encoding="utf-8").splitlines():
        name, _, value = line.partition("=")
        if name.strip() == "ASSEMBLY_AI_KEY":
            return value.strip().strip('"').strip("'")
    raise SystemExit("ASSEMBLY_AI_KEY missing")


def main() -> None:
    aai.settings.api_key = key()
    mode = sys.argv[1] if len(sys.argv) > 1 else "poll"
    for name, audio in JOBS.items():
        id_file, out = ROOT / f"transcript{name}-id.txt", ROOT / f"transcript{name}.json"
        if mode == "submit":
            if id_file.exists():
                print(name, "already submitted"); continue
            config = aai.TranscriptionConfig(language_code="en", punctuate=True, format_text=True,
                                             speaker_labels=True, keyterms_prompt=TERMS)
            result = aai.Transcriber().submit(str(audio), config=config)
            id_file.write_text(result.id + "\n", encoding="utf-8")
            print(name, "submitted", result.id)
            continue
        result = aai.Transcript.get_by_id(id_file.read_text(encoding="utf-8").strip())
        while mode == "wait" and result.status in (aai.TranscriptStatus.queued, aai.TranscriptStatus.processing):
            time.sleep(10)
            result = aai.Transcript.get_by_id(result.id)
        print(name, "status:", result.status)
        if result.status == aai.TranscriptStatus.error:
            raise SystemExit(f"AssemblyAI failed on {name}: {result.error}")
        if result.status == aai.TranscriptStatus.completed and not out.exists():
            out.write_text(json.dumps(result.json_response, ensure_ascii=False, indent=2), encoding="utf-8")
            print("saved:", out.name, "words:", len(result.words or []))


if __name__ == "__main__":
    main()
