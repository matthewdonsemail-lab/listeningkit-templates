#!/usr/bin/env bash
# Find and download sound effects from YouTube with yt-dlp, the way the launch film's kit was made (2026-11-15).
#
#   bash youtube_sfx.sh search "glitch sound effect no copyright" "vhs tape glitch sound effect" ...
#       lists the top 5 results per query: id | seconds | title. Pick short, free "no copyright" / "free download"
#       packs (5-60 s); skip hour-long loops and ASMR. Show matt the list before downloading.
#   bash youtube_sfx.sh get <out_dir> name:VIDEO_ID [name:VIDEO_ID ...]
#       downloads each as <out_dir>/<name>.wav (audio only). These are the raw packs make_sfx_kit.py cuts up
#       (its SOURCES dict maps the same names to the same ids).
#
# The launch film's searches and picks, to start from:
#   search "glitch sound effect no copyright" "digital glitch transition sound effect" "ui beep blip sound effect" \
#          "whoosh sound effect no copyright" "tv static burst sound effect" "vhs tape glitch sound effect" \
#          "electric zap sound effect" "heartbeat sound effect" "sub bass drop impact sound effect" \
#          "cinematic riser sound effect" "cinematic logo hit impact sound effect" "scanner scan sound effect sci fi" \
#          "data glitch stutter sound effect" "reverse glitch sound effect"
#   get textAnimations/assets/sfx/raw glitch_pack:oys87TrYFbA glitch4:ziI1z21LQ6o glitch_cine:8zFB-ki2Gk4 \
#       glitch_free:CYcbnFL2HS4 blip_ui:9cNJyi8NtAw blip_text:CbnHrtjMAeo whoosh_pack:Hj7-pltIVng whoosh5:qP_iJ-yLi7c \
#       static_burst:dpC00rE6qfw static_pop:NpcPLL60e8w vhs:0GZ-td_LhgQ zap:Zfcaj7M0Qnk zap_circuit:MX3N550cq-0 \
#       heartbeat:9zw6eZEBp30 sub_drop:Yzq8c2Xv5IY bass_impact:7DYBjzrhdWw riser:Q8mYX1scq6I hit_cine:fo-ULy4Ty08 \
#       hit_sudden:img8cqU6owQ scanner:59igcK_WY3Y stutter:Rz-ZDtDKLkM reverse:_g4Wazm3cJc
set -euo pipefail
cmd=${1:-}; shift || true
case "$cmd" in
  search)
    for q in "$@"; do
      echo "== $q"
      yt-dlp --flat-playlist --print "%(id)s | %(duration)s | %(title)s" "ytsearch5:$q" 2>/dev/null | cut -c1-110
    done ;;
  get)
    out=$1; shift; mkdir -p "$out"
    for pair in "$@"; do
      name=${pair%%:*}; id=${pair##*:}
      [ -s "$out/$name.wav" ] && { echo "have $name"; continue; }
      yt-dlp -q -x --audio-format wav -o "$out/$name.%(ext)s" "https://www.youtube.com/watch?v=$id" 2>&1 | grep -v WARNING || true
      echo "got $name ($id)"
    done
    du -sh "$out" ;;
  *) sed -n 2,12p "$0"; exit 1 ;;
esac
