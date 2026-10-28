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
        # votazione per appello nominale: l'esito e' la didascalia «(L'Assemblea approva / non approva)» dopo il risultato,
        # e l'emendamento e' l'ultimo nominato prima dell'intestazione «Votazione nominale» (sed073 Cosattini, sed187
        # Scoccimarro-Veroni, sed311 Lami Starnuti: prima restavano «non determinato»)
        TESTA = r"Votazione\s+(?:per\s+appello\s+)?nominale\s*[.°]|(?:Ind[iì]co|Procediamo\s+alla|Si\s+proceda\W{0,3}\s?alla|Pongo[^.¶]{0,40}?in\s+vota\W{0,3}\s?zione[^.¶]{0,30}?per)\s+(?:la\s+)?(?:vota\W{0,3}\s?zione\s+)?(?:per\s+)?(?:appello\s+)?no\W{0,3}\s?minal"
        NOME = r"([A-Z][a-zà-ÿ'’]+(?:\s[A-Z][a-zà-ÿ'’]+)?)"
        for m in re.finditer(TESTA, seg):
            pre = seg[max(0, m.start() - 4000):m.start()]
            dopo = t[start + m.end():start + m.end() + 40000]     # dal testo intero: l'elenco della chiama e' lungo
            # l'emendamento e' quello nominato nell'annuncio del voto («Indico la votazione nominale sull'emendamento La Rocca»,
            # «Pongo in votazione, per appello nominale, l'emendamento aggiuntivo degli onorevoli Corbino, Marchesi»);
            # se l'annuncio non lo nomina, l'ultimo emendamento nominato prima, esclusa la richiesta di appello nominale
            ann = re.search(r"emendament\w*\s+(?:aggiuntiv\w+\s+|soppressiv\w+\s+|sostitutiv\w+\s+)?(?:(?:presen\W{0,3}\s?tat\w+|propost\w+)\s+(?:dal\W{0,3}\s?l?['’]?\s?onorevole\s+|dagli\W{0,3}\s?onorevoli\s+))?(?:dell['’]\s?onorevole\s+|degli\W{0,3}\s?o\w*revoli\s+)?" + NOME, seg[m.start():m.end() + 400])
            if ann: chi = ann.group(1)
            else:
                men = [x for x in re.finditer(r"emendament\w*\s+(?:(?:presentat\w+|propost\w+|firmat\w+)\s+)?(?:dal|dell|degli|dagli)?\W{0,3}\s?(?:onorevol\w\s+)?" + NOME, pre)
                       if not re.search(r"appello\s+nominale|chiest", pre[max(0, x.start() - 80):x.end() + 20])]
                if not men: continue
                chi = men[-1].group(1)
            tutti_c = {str(cogn.get(x, '')).split()[0] for x in str(r.firmatari).split('|') if cogn.get(x, '')}
            # l'emendamento e' chiamato col nome del primo firmatario, ma talvolta con quello di chi lo ha svolto
            # («emendamento Ravagnan» per l'elenco Laconi, Ravagnan, Grieco): vale anche un altro firmatario se il testo coincide
            if not re.match(sur, chi) and not (chi.split()[0] in tutti_c and len(tn) >= 30 and comune(tn, seg[max(0, m.start() - 6000):m.end() + 800])): continue
            # con piu' firmatari, l'elenco dell'annuncio non deve nominare altri («degli onorevoli Scoccimarro e Veroni» non
            # e' l'emendamento Scoccimarro-Pesenti-Lombardi citato poco prima)
            el = re.search(r"emendament\w*\s+(?:aggiuntiv\w+\s+)?degli\W{0,3}\s?o\w*revoli\s+([^:.;«]{3,200})", seg[m.start():m.end() + 400])
            if el and any(n not in tutti_c and n not in ('Presidente',) for n in re.findall(r"\b([A-Z][a-zà-ÿ'’]{2,})", el.group(1))): continue
            nx = re.search(TESTA, dopo)
            a = re.search(r"\(\s*L\W{0,3}\s?Assemblea\s+(?P<no>non\s+)?approva", dopo[:nx.start() if nx else len(dopo)])
            if a: ev.append((m.start(), 'respinto' if a.group('no') else 'approvato', s, pm, start))
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
