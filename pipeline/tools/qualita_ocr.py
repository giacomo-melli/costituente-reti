"""Punteggio di qualita' dell'OCR per pagina, per sapere dove i dati sono piu' fragili.

Uso: python3 tools/qualita_ocr.py [cartella_testi] [file_uscita]
Per ogni pagina: quota delle parole (4+ lettere) che compaiono almeno 20 volte nell'intero
corpus (una parola storpiata dall'OCR e' quasi sempre rara), e quota di caratteri spuri
(segni che nel testo a stampa non stanno dentro le parole: | ° © ¢ ~ ^ e simili).
Il vocabolario si ricava dal corpus stesso: nessuna lista esterna."""
import os, re, sys, glob, collections, csv
QUI = os.path.dirname(os.path.abspath(__file__)); PIPE = os.path.dirname(QUI)
TXT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(PIPE, 'testi_colonne_400')
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(PIPE, 'extraction', 'qualita_pagine.csv')
PAROLA = re.compile(r"[A-Za-zÀ-ÿ]{4,}")
SPURI = re.compile(r"[|°©¢~^¬®§¦†‡•¤£€\\]")
pagine = {}
for f in sorted(glob.glob(os.path.join(TXT, 'sed*_p*.txt'))):
    t = open(f, encoding='utf-8', errors='ignore').read().replace('<<<COLONNA_DESTRA>>>', ' ')
    pagine[os.path.basename(f)[:-4]] = t
freq = collections.Counter(w.lower() for t in pagine.values() for w in PAROLA.findall(t))
righe = []
for k, t in pagine.items():
    ws = [w.lower() for w in PAROLA.findall(t)]
    car = sum(1 for c in t if not c.isspace())
    sed, pag = k.split('_p')
    righe.append(dict(seduta=sed, pagina=int(pag), parole=len(ws),
                      quota_parole_comuni=round(sum(freq[w] >= 20 for w in ws) / len(ws), 3) if ws else '',
                      quota_caratteri_spuri=round(len(SPURI.findall(t)) / car, 4) if car else ''))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(righe[0])); w.writeheader(); w.writerows(righe)
val = sorted(r['quota_parole_comuni'] for r in righe if r['parole'] >= 100)
print(f'pagine {len(righe)}; quota di parole comuni (pagine con 100+ parole): mediana {val[len(val)//2]}, '
      f'5° percentile {val[len(val)//20]}, minimo {val[0]}')
