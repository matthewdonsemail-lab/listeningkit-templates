#!/bin/sh
# Dialogue for the timeline: the raw Cap mic (quiet laptop mic, speech median -42.5 dB) loudness-normalised, +4.9 dB,
# then peak-limited to -5.5 dBFS (audio skill). The first v1 mix with only the limiter came out at -35.2 LUFS; this
# one gives the edited mix -17.5 LUFS, -4.1 dBFS peak. The cut analysis stays on the raw mic.wav.
set -e
cd "$(dirname "$0")"
REC="/c/Users/0/AppData/Roaming/so.cap.desktop/recordings/Generic PnP Monitor (Display) 2026-11-16 03.27 PM.cap/content/segments/segment-0"
ffmpeg -v error -n -i "$REC/audio-input.m4a" -ac 1 -c:a pcm_s16le mic.wav
ffmpeg -v error -n -i mic.wav -af "loudnorm=I=-16:TP=-5.5:LRA=11,volume=4.9dB,alimiter=limit=0.5309:attack=3:release=60:asc=1:level=disabled" -ar 48000 -ac 2 -c:a pcm_s16le dialogue-limited.wav
