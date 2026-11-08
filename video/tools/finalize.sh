#!/usr/bin/env bash
# Two-pass loudness normalisation to -14 LUFS / -1.5 dBTP, moov at the front for phones.
set -euo pipefail
f="$1"
J=$(ffmpeg -hide_banner -i "$f" -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g() { echo "$J" | python3 -c "import json,sys;print(json.load(sys.stdin)['$1'])"; }
ffmpeg -y -v error -i "$f" -c:v copy -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true" -c:a aac -b:a 192k -ar 48000 -movflags +faststart "${f%.mp4}.tmp.mp4"
mv "${f%.mp4}.tmp.mp4" "$f"
ffmpeg -i "$f" -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):"
