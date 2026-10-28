"""Scarica i PDF delle sedute non ancora trascritte (pipeline/sedute_non_trascritte.csv) in pipeline/pdf/.
Va lanciato sul computer, con la connessione a Internet:

    python3 pipeline/tools/scarica_pdf_mancanti.py            # solo le 16 sedute nei giorni di discussione del progetto
    python3 pipeline/tools/scarica_pdf_mancanti.py --tutte    # tutte le sedute non trascritte

Poi: OCR (pipeline/ocr_costituente.R e ocr_400dpi.R, come per le altre sedute), pipeline/esegui_estrazione.py,
pipeline/esporta_dataset.py. Solo librerie standard di Python."""
import csv, os, sys, time, urllib.request
QUI = os.path.dirname(os.path.abspath(__file__)); PIPE = os.path.dirname(QUI)
righe = list(csv.DictReader(open(os.path.join(PIPE, 'sedute_non_trascritte.csv'), encoding='utf-8')))
if '--tutte' not in sys.argv: righe = [r for r in righe if r['giorno_discussione_progetto'] == '1']
os.makedirs(os.path.join(PIPE, 'pdf'), exist_ok=True)
for r in righe:
    dest = os.path.join(PIPE, 'pdf', r['seduta'] + '.pdf')
    if os.path.exists(dest): continue
    req = urllib.request.Request(r['url_pdf'], headers={'User-Agent': 'costituente-reti/1.1 (dataset accademico)'})
    with urllib.request.urlopen(req, timeout=120) as f, open(dest, 'wb') as o: o.write(f.read())
    print(r['seduta'], r['data'], os.path.getsize(dest) // 1024, 'kB'); time.sleep(1)
print('Fatto:', len(righe), 'sedute')
