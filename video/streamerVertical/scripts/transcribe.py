"""Transcribe a clip with AssemblyAI: word timings (ms) + speaker labels.

    python transcribe.py CLIP.mp4 [--out assembly_CLIP.json]

Key: $ASSEMBLYAI_API_KEY, else ~/.buzz/.secrets/assemblyai.key. Never printed.

How it works
1. Extracts the audio to a 16 kHz mono WAV with ffmpeg (uploads stay small).
2. Uploads it (POST /v2/upload), starts a transcript with `speaker_labels: true` and
   `format_text: true` (POST /v2/transcript), polls every 3 s until `completed`.
3. Saves the whole response: `words` = [{text, start, end, confidence, speaker}] in ms of the
   SOURCE clip, `utterances` = speaker turns. build.py reads `words`.

This is the first-pass transcript only. After the cut, captions are re-timed from the cut's own
dialogue (resync_captions.py), because a full-clip transcript segments repeated words differently
and counts game sounds as words.
"""
import json, os, subprocess, sys, tempfile, time, urllib.request

API = "https://api.assemblyai.com/v2"


def key():
    k = os.environ.get("ASSEMBLYAI_API_KEY")
    if not k:
        k = open(os.path.expanduser("~/.buzz/.secrets/assemblyai.key")).read()
    return k.strip()


def call(method, path, body=None, raw=None):
    req = urllib.request.Request(API + path, method=method, data=raw if raw is not None else (json.dumps(body).encode() if body else None),
                                 headers={"authorization": key(), "content-type": "application/octet-stream" if raw is not None else "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read())


def main():
    clip = sys.argv[1]
    out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else os.path.join(
        os.path.dirname(os.path.abspath(clip)), "assembly_" + os.path.splitext(os.path.basename(clip))[0] + ".json")
    wav = os.path.join(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")), "a.wav")
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", clip, "-vn", "-ac", "1", "-ar", "16000", wav], check=True)
    url = call("POST", "/upload", raw=open(wav, "rb").read())["upload_url"]
    os.remove(wav)
    tid = call("POST", "/transcript", {"audio_url": url, "speaker_labels": True, "format_text": True, "punctuate": True})["id"]
    while True:
        t = call("GET", f"/transcript/{tid}")
        if t["status"] in ("completed", "error"):
            break
        time.sleep(3)
    if t["status"] == "error":
        raise SystemExit("AssemblyAI error: " + t.get("error", "?"))
    json.dump(t, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{out}: {len(t['words'])} words, speakers {sorted({u['speaker'] for u in t.get('utterances') or []})}")
    for u in t.get("utterances") or []:
        print(f"  {u['speaker']} {u['start']/1000:6.2f}-{u['end']/1000:6.2f}  {u['text'][:110]}")


if __name__ == "__main__":
    main()
