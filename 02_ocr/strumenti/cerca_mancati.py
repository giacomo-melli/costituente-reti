"""Cerca nei testi OCR frasi che parlano di emendamenti e contengono 2+ cognomi di costituenti,
ma non sono state estratte: servono a trovare formule non ancora riconosciute."""
import re, glob, os, collections, pandas as pd, unicodedata
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
nomi = pd.read_csv(os.path.join(D, 'strumenti', 'costituenti_nomi.csv'))
COG = {c for c in nomi.cognome if len(c) >= 4}
pat = re.compile(r'\b(' + '|'.join(sorted(map(re.escape, COG), key=len, reverse=True)) + r')\b')
M = pd.read_csv(os.path.join(D, 'estrazione', 'menzioni.csv'))
presi = set(zip(M.seduta, M.pagina))
out = []
for f in sorted(glob.glob(os.path.join(D, 'testi_colonne', 'sed*_p*.txt'))):
    s, p = os.path.basename(f)[:6], int(f[-7:-4])
    t = re.sub(r'-\s*\n\s*', '', open(f, encoding='utf-8', errors='ignore').read()).replace('\n', ' ')
    for fr in re.split(r'(?<=[.:])\s+(?=[A-Z«])', t):
        if not re.search(r'emendament|articolo aggiuntivo|proposto|presentat|firmat', fr, re.I): continue
        if re.search(r'interrog|interpell|ordine del giorno|mozion|appello nominale', fr, re.I): continue
        c = set(pat.findall(fr))
        if len(c) >= 2 and (s, p) not in presi:
            out.append((s, p, re.sub(r'\s+', ' ', fr)[:220]))
print('frasi candidate su pagine senza estrazioni:', len(out))
# formule: le 4 parole prima del primo cognome
form = collections.Counter()
for s, p, fr in out:
    m = pat.search(fr)
    if not m: continue
    form[' '.join(fr[:m.start()].lower().split()[-4:])] += 1
for k, v in form.most_common(25): print(v, '|', k)
pd.DataFrame(out, columns=['seduta', 'pagina', 'frase']).to_csv(os.path.join(D, 'estrazione', 'candidati_mancati.csv'), index=False)
