#!/bin/bash
# uso: ocr_pagina.sh CARTELLA sedNNN PAGINA
D="$1"; s="$2"; p="$3"; TD=/tmp/td
out=$(printf "%s/testi_colonne/%s_p%03d.txt" "$D" "$s" "$p"); [ -s "$out" ] && exit 0
W=$(mktemp -d)
pdftoppm -r 300 -f $p -l $p -gray -png "$D/pdf/$s.pdf" $W/pg >/dev/null 2>&1
img=$(ls $W/pg-*.png | head -1)
python3 "$D/strumenti/colonne.py" "$img" $W/c >/dev/null 2>&1 || { cp "$img" $W/c_L.png; : > $W/c_R.png; }
OMP_THREAD_LIMIT=1 tesseract $W/c_L.png $W/L -l ita --tessdata-dir $TD --psm 6 --dpi 300 >/dev/null 2>&1
[ -s $W/c_R.png ] && OMP_THREAD_LIMIT=1 tesseract $W/c_R.png $W/R -l ita --tessdata-dir $TD --psm 6 --dpi 300 >/dev/null 2>&1
{ cat $W/L.txt; echo "<<<COLONNA_DESTRA>>>"; cat $W/R.txt 2>/dev/null; } > "$out.tmp" && mv "$out.tmp" "$out"
rm -rf $W
