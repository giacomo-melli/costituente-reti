"""Controllo incrociato fra l'articolo che un emendamento dice di modificare e l'articolo in discussione (punto 23).

Uso: python3 tools/controllo_articolo.py [cartella_pipeline] [cartella_estrazione]
Per ogni seduta si segue l'ordine dei lavori stampato dal Presidente («Passiamo all'articolo 31», «Si riprende
la discussione dell'articolo 7»): ogni pagina ha cosi' l'articolo in discussione all'inizio e quelli annunciati
sulla pagina. Un emendamento con `articolo_menzionato` che non e' fra questi e' una discordanza da guardare:
numero letto male dall'OCR, articolo citato di passaggio o record attribuito alla seduta sbagliata.
Scrive extraction/controllo_articolo.csv."""
import os, re, sys, glob
import pandas as pd
QUI = os.path.dirname(os.path.abspath(__file__)); PIPE = os.path.dirname(QUI)
EST = sys.argv[-1] if len(sys.argv) > 1 else os.path.join(PIPE, 'extraction')
src = open(os.path.join(QUI, 'estrai_emendamenti.py'), encoding='utf-8').read()
_a = sys.argv; sys.argv = ['x', PIPE, EST]; os.chdir(QUI); exec(src[:src.index('recs = []')]); sys.argv = _a
ORDINE = re.compile(r"(?:[Ss]i\s+dia\s+lettura|[Dd]o\s+lettura|[Pp]assiamo|[Pp]assare|[Ss]i\s+riprende\s+(?:la\s+discussione|l['’]esame)|[Rr]iprendiamo|[Ss]egue|[Ee]saminiamo|[Pp]rocediamo)\b[^.¶]{0,60}?\barticol[oi]\s+(\d{1,3})(?:[\s-]*(bis|ter|quater))?", re.I)
E = pd.read_csv(os.path.join(EST, 'emendamenti.csv'))
base = lambda x: re.sub(r'\D.*', '', x)
T = pd.read_csv(os.path.join(EST, 'menzioni_tutte.csv'))
CTX = T.dropna(subset=['id_emendamento']).groupby('id_emendamento').contesto.apply(list)
def posizione(t, eid, a0, a1):
    """Posizione nel testo della prima menzione dell'emendamento (dal contesto salvato dall'estrattore)."""
    for c in CTX.get(eid, []):
        m = re.search(r"\[\[\s*(.{4,60}?)\s*\]\]", str(c), re.S)
        if not m: continue
        parole = [re.escape(w) for w in m.group(1).replace('/', ' ').split() if w]
        if not parole: continue
        k = re.compile(r"[\s¶]+".join(parole)).search(t, max(0, a0 - 3000), min(len(t), a1 + 3000))
        if k: return k.start()
    return None
righe = []
for s, g in E.groupby('prima_seduta'):
    t, pm = flatten(s)
    eventi = [(m.start(), m.group(1) + ('-' + m.group(2).lower() if m.group(2) else '')) for m in ORDINE.finditer(t)]
    # numeri letti male dall'OCR («195» per 95, «441» per 11): il progetto ha 139 articoli e l'ordine dei lavori
    # procede per passi brevi, quindi si scarta un numero oltre 140 o lontano da entrambi i vicini che fra loro concordano
    n = [int(base(e[1])) for e in eventi]
    eventi = [e for i, e in enumerate(eventi) if n[i] <= 140 and not (0 < i < len(n) - 1 and abs(n[i] - n[i - 1]) > 15
              and abs(n[i] - n[i + 1]) > 15 and abs(n[i - 1] - n[i + 1]) <= 15)]
    for r in g.itertuples():
        art = str(r.articolo_menzionato).replace('.0', '') if pd.notna(r.articolo_menzionato) and str(r.articolo_menzionato) else ''
        a0 = next((a for a, p in pm if p == r.pagina), 0); a1 = next((a for a, p in pm if p == r.pagina + 1), len(t))
        prima = [x for x in eventi if x[0] < a0]
        cand = ([prima[-1][1]] if prima else []) + [x[1] for x in eventi if a0 <= x[0] < a1]
        cand = list(dict.fromkeys(cand))
        # posizione esatta della prima menzione: l'articolo in discussione e' l'ultimo annunciato prima di essa
        pos = posizione(t, r.id_emendamento, a0, a1)
        if pos is not None:
            pr = [x for x in eventi if x[0] < pos]
            disc_pos = pr[-1][1] if pr else ''
        else:
            disc_pos = None
        if art and art in cand: disc = art            # l'articolo nominato vicino all'emendamento e annunciato sulla pagina
        elif disc_pos: disc = disc_pos
        elif len(cand) == 1: disc = cand[0]
        elif art and base(art) in [base(c) for c in cand]: disc = next(c for c in cand if base(c) == base(art))
        else: disc = ''
        stato = ('senza articolo' if not art else 'senza ordine dei lavori' if not cand else
                 'coerente' if art in cand or base(art) in {base(c) for c in cand} else 'discordante')
        righe.append(dict(id_emendamento=r.id_emendamento, seduta=s, pagina=r.pagina, articolo_menzionato=art,
                          articoli_in_discussione=';'.join(cand), articolo_in_discussione=disc, controllo=stato))
O = pd.DataFrame(righe); O.to_csv(os.path.join(EST, 'controllo_articolo.csv'), index=False)
print('controllo:', O.controllo.value_counts().to_dict(), '| articolo in discussione assegnato:', int((O.articolo_in_discussione != '').sum()), 'su', len(O))
