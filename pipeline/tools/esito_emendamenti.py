"""Esito di ogni emendamento: approvato, respinto, ritirato, decaduto (assente), assorbito, o non determinato.

Uso: python3 tools/esito_emendamenti.py [cartella_pipeline] [cartella_estrazione]
Legge extraction/emendamenti.csv e i testi OCR; scrive extraction/esiti.csv (id_emendamento, esito, pagina_esito, prova).
Si cerca, dalla pagina in cui l'emendamento compare e per le due sedute successive, il primo evento che nomina il
primo firmatario: la messa ai voti («Pongo in votazione l'emendamento dell'onorevole X») seguita dalla didascalia
«(È approvato)» / «(Non è approvato)»; il ritiro detto dal firmatario nel proprio turno («X. Lo ritiro», «Non insisto»);
la rinuncia per assenza («Non essendo presente l'onorevole X, si intende che abbia rinunziato»); l'assorbimento."""
import os, re, sys
import pandas as pd
QUI = os.path.dirname(os.path.abspath(__file__)); PIPE = os.path.dirname(QUI)
EST = sys.argv[-1] if len(sys.argv) > 1 else os.path.join(PIPE, 'extraction')   # come gli altri script: [cartella_pipeline] cartella_estrazione
src = open(os.path.join(QUI, 'estrai_emendamenti.py'), encoding='utf-8').read()
_argv = sys.argv; sys.argv = ['x', PIPE, EST]; os.chdir(QUI)
exec(src[:src.index('recs = []')])                 # flatten, page_at, nomi dall'estrattore
sys.argv = _argv
E = pd.read_csv(os.path.join(EST, 'emendamenti.csv'))
cogn = nomi.set_index('id_dep').cognome
sedute = sorted({os.path.basename(f).split('_')[0] for f in glob.glob(os.path.join(TXT, 'sed*_p*.txt'))})
cache = {}
def comune(tn, finestra, n=25):
    f = norm_t(finestra)
    return any(tn[j:j + n] in f for j in range(0, max(1, len(tn) - n), 8))
norm_t = lambda x: re.sub(r'[^a-z]', '', unicodedata.normalize('NFKD', str(x) if isinstance(x, str) else '').encode('ascii', 'ignore').decode().lower())
def testo(s):
    if s not in cache: cache[s] = flatten(s)
    return cache[s]
APPROV = re.compile(r"\(\s*(?:L['’]\s?emendamento\s+|L['’]\s?articolo\s+aggiuntivo\s+|Dopo\s+prova\s+e\s+controprova,\s*)?(?:(?P<no>non\s+è|Non\s+è|non\s+e|Non\s+e)\s+|(?:È|E|é)\s+)?approvat", re.I)
def esito_per(r):
    c = str(cogn.get(str(r.primo) if isinstance(r.primo, str) and r.primo else str(r.firmatari).split('|')[0], ''))
    if not c: return 'non determinato', '', ''
    sur = re.escape(c.split()[0]).replace("'", "['’]?")
    i0 = sedute.index(r.prima_seduta) if r.prima_seduta in sedute else -1
    for k, s in enumerate(sedute[i0:i0 + 3] if i0 >= 0 else []):
        t, pm = testo(s)
        start = 0
        if k == 0:
            start = next((a for a, p in pm if p == r.pagina), 0)
        seg = t[start:start + 60000]
        tn = norm_t(r.testo)
        ev = []
        for m in re.finditer(r"(?:[Pp]ongo|[Mm]etto)\s+(?:ora\s+|quindi\s+|allora\s+)?(?:in\s+votazione|ai\s+voti)\b[^.¶]{0,120}?(?:emendament|articolo\s+aggiuntiv|propost|formul)\w*[^.¶]{0,80}?\b" + sur + r"\b", seg):
            a = APPROV.search(seg, m.end(), m.end() + 900)
            if a and (len(tn) < 30 or comune(tn, seg[m.start():a.end()])):
                ev.append((m.start(), 'respinto' if a.group('no') else 'approvato', s, pm, start))
        for m in re.finditer(r"(?:¶|[.?!)]\s)\s*" + sur.upper() + r"[A-ZÀ-Ý '’]{0,25}\.\s+(?:[^¶]{0,400}?)\b(?:[Ll]o\s+ritiro|[Ll]i\s+ritiro|[Rr]itir\w*\b[^.¶]{0,25}emendament|[Nn]on\s+insist|[Rr]inunzio(?!\s+a\s+svolger)|[Rr]inuncio(?!\s+a\s+svolger))", seg):
            dom = seg[max(0, m.start() - 700):m.start() + 1]
            if not re.search(r"[Oo]norevole\s+" + sur + r"\b[^¶]{0,160}?(?:mant\w+|insist\w*|ritir\w*)[^¶]{0,60}\?", dom): continue
            if len(tn) >= 30 and re.search(r"[Ss]egue|emendament", dom) and not comune(tn, seg[max(0, m.start() - 2500):m.start()]): continue
            ev.append((m.start(), 'ritirato', s, pm, start))
        for m in re.finditer(r"(?:[Nn]on\s+essendo\s+present\w\s+(?:l['’]\s?onorevole\s+)?" + sur + r"|" + sur + r"[^.¶]{0,40}non\s+(?:è|essendo)\s+present)[^¶]{0,160}?(?:rinunzi|rinunci|decad)(?![^.¶]{0,30}\bsvolger)", seg):
            ev.append((m.start(), 'decaduto (assente)', s, pm, start))
        for m in re.finditer(r"emendament\w+[^.¶]{0,60}\b" + sur + r"\b[^.¶]{0,80}(?:è|e|resta|rimane|s['’]intende)\s+assorbit", seg):
            ev.append((m.start(), 'assorbito', s, pm, start))
        if ev and k > 0:
            # in una seduta successiva lo stesso firmatario ha spesso altri emendamenti: l'evento vale solo se
            # nelle righe vicine ricorre un pezzo del testo di questo («LO RITIRO» di Arata si riferiva a un altro)
            ev = [e for e in ev if len(tn) >= 30 and any(tn[j:j + 25] in norm_t(seg[max(0, e[0] - 1500):e[0] + 1500]) for j in range(0, len(tn) - 25, 10))]
        if ev:
            pos, es, s_, pm_, st = min(ev)
            return es, f'{s_} p{page_at(pm_, st + pos)}', re.sub(r'\s+', ' ', seg[max(0, pos - 80):pos + 260]).replace('¶', '/')
    return 'non determinato', '', ''
out = []
for r in E.itertuples():
    es, dove, prova = esito_per(r)
    out.append(dict(id_emendamento=r.id_emendamento, esito=es, dove_esito=dove, prova=prova))
O = pd.DataFrame(out); O.to_csv(os.path.join(EST, 'esiti.csv'), index=False)
print('esiti:', O.esito.value_counts().to_dict())
