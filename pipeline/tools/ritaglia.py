"""Ritaglia dalla scansione la parte di pagina che contiene un passo, per il controllo a vista.

Uso: python3 ritaglia.py SEDUTA PAGINA "parola chiave" [margine]
La colonna e l'altezza approssimativa del passo si ricavano dal testo OCR della pagina
(posizione della riga fra le righe della colonna); il ritaglio prende una fascia attorno.
Scrive pipeline/extraction/crops_notte/SEDUTA_pPAGINA_PAROLA.png e stampa il percorso."""
import os, re, sys, subprocess, glob
QUI = os.path.dirname(os.path.abspath(__file__)); PIPE = os.path.dirname(QUI)
sed, pag, chiave = sys.argv[1], int(sys.argv[2]), sys.argv[3]
marg = float(sys.argv[4]) if len(sys.argv) > 4 else 0.16
OUT = os.path.join(PIPE, 'extraction', 'crops_notte'); os.makedirs(OUT, exist_ok=True)
txt = None
for d in ('testi_colonne_400', 'testi_colonne'):
    f = os.path.join(PIPE, d, f'{sed}_p{pag:03d}.txt')
    if os.path.exists(f) and chiave.lower() in open(f, encoding='utf-8', errors='ignore').read().lower(): txt = f; break
col, frac = 0, 0.5
if txt:
    cols = open(txt, encoding='utf-8', errors='ignore').read().split('<<<COLONNA_DESTRA>>>')
    for ci, c in enumerate(cols):
        righe = c.split('\n')
        for li, r in enumerate(righe):
            if chiave.lower() in r.lower():
                col, frac = ci, li / max(1, len(righe)); break
        else: continue
        break
else:
    print('  parola non trovata nel testo OCR: pagina intera', file=sys.stderr); col = -1
base = os.path.join(OUT, f'_tmp_{sed}_{pag}')
if not os.path.exists(base + '.png'):
    subprocess.run(['pdftoppm', '-f', str(pag), '-l', str(pag), '-r', '220', '-png', '-singlefile', os.path.join(PIPE, 'pdf', f'{sed}.pdf'), base], check=True)
w, h = map(int, subprocess.run(['identify', '-format', '%w %h', base + '.png'], capture_output=True, text=True).stdout.split())
nome = re.sub(r'\W+', '_', chiave)[:20]
dest = os.path.join(OUT, f'{sed}_p{pag}_{nome}.png')
if col < 0:
    geo = f'{w}x{h}+0+0'
else:
    x0 = 0 if col == 0 else w // 2 - w // 40
    y0 = max(0, int((frac - marg) * h)); y1 = min(h, int((frac + marg) * h))
    geo = f'{w // 2 + w // 40}x{y1 - y0}+{x0}+{y0}'
subprocess.run(['convert', base + '.png', '-crop', geo, '+repage', '-colorspace', 'Gray', dest], check=True)
print(dest)
