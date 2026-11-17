#!/usr/bin/env bash
# Max-quality render of a FilmCraft project (matt, 2026-11-17: FilmCraft's own H.264 encoder came out blocky at ~2 Mbps).
# The picture goes out of FilmCraft as ProRes LT in 4 pieces (C: has ~45 GB free; the whole film would be ~35 GB),
# each piece is encoded with x264 (CRF 16) and deleted, then the pieces are joined and muxed with the full mix from
# FilmCraft (WAV -> AAC 320k). No burned-in captions; the .srt goes next to it.
#   bash render_hq.sh effectcraftEditing-20min-v15.fcproj renders/effectcraftEditing-20min-v15-hq.mp4 1254.1
set -euo pipefail
cd "$(dirname "$0")"
PROJ=$1; OUT=$2; DUR=$3
CLI=../../target/release/filmcraft-cli.exe
W=renders/_hq_work; mkdir -p "$W"
export WGPU_POWER_PREF=low WGPU_BACKEND=dx12
CUTS=(0 315 630 945 "$DUR")
: > "$W/list.txt"
for i in 0 1 2 3; do
  a=${CUTS[$i]}; b=${CUTS[$((i+1))]}
  if [ ! -s "$W/p$i.mp4" ]; then
    echo "$(date +%H:%M:%S) piece $((i+1))/4: FilmCraft ProRes ${a}-${b} s"
    "$CLI" --project "$PROJ" export "$W/p$i.mov" --format prores --start "$a" --end "$b" --settings '{"proresProfile":"lt"}' > "$W/p$i.log" 2>&1
    echo "$(date +%H:%M:%S) piece $((i+1))/4: x264"
    ffmpeg -v error -stats -y -i "$W/p$i.mov" -an -c:v libx264 -preset medium -crf 16 -pix_fmt yuv420p -threads 6 "$W/p$i.mp4"
    rm -f "$W/p$i.mov"
  fi
  echo "file 'p$i.mp4'" >> "$W/list.txt"
done
echo "$(date +%H:%M:%S) audio"
"$CLI" --project "$PROJ" export "$W/mix.wav" --format wav > "$W/mix.log" 2>&1
echo "$(date +%H:%M:%S) join"
ffmpeg -v error -y -f concat -safe 0 -i "$W/list.txt" -i "$W/mix.wav" -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -shortest -movflags +faststart "$OUT"
ffprobe -v error -show_entries format=duration,size,bit_rate -of compact "$OUT"
echo "$(date +%H:%M:%S) done"
