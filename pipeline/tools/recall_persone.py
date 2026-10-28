"""Recall a livello di persona (punto 24): chi non ha nessun emendamento, e' davvero assente dagli emendamenti?

Uso: python3 tools/recall_persone.py
Per ogni costituente senza legami di co-firma cerca nel corpus il cognome a meno di 200 caratteri dopo la parola
«emendamento» o dentro un blocco di firma in maiuscolo, e scrive extraction/recall_persone.csv con i passi trovati,
da guardare sulla pagina. Un passo trovato non e' un errore: spesso il nome e' citato, non firmatario."""
import os, re, sys, glob
import pandas as pd
QUI = os.path.dirname(os.path.abspath(__file__)); PIPE = os.path.dirname(QUI); RADICE = os.path.dirname(PIPE)
src = open(os.path.join(QUI, 'estrai_emendamenti.py'), encoding='utf-8').read()
_a = sys.argv; sys.argv = ['x', PIPE, os.path.join(PIPE, 'extraction')]; os.chdir(QUI); exec(src[:src.index('recs = []')]); sys.argv = _a
C = pd.read_csv(os.path.join(RADICE, 'data', 'it', 'costituenti_nodi.csv'))
L = pd.read_csv(os.path.join(RADICE, 'data', 'it', 'edgelist_emendamenti.csv'))
zero = C[~C.id_dep.isin(L.id_dep)]
omon = C.cognome.value_counts()
pat = {r.id_dep: re.compile(r"\b" + re.escape(r.cognome).replace("'", "['’]?") + r"\b") for r in zero.itertuples()}
up = {r.id_dep: re.compile(r"\b" + re.escape(r.cognome.upper()).replace("'", "['’]?") + r"\b") for r in zero.itertuples()}
righe = []
for s in sorted({os.path.basename(f).split('_')[0] for f in glob.glob(os.path.join(TXT, 'sed*_p*.txt'))}):
    t, pm = flatten(s)
    for m in re.finditer(r"emendament\w*", t):
        fin = t[m.end():m.end() + 200]
        for r in zero.itertuples():
            k = pat[r.id_dep].search(fin)
            if k and re.search(r"(?:onorevol\w|dagli|degli|dell['’]|dall['’])[^.¶]{0,60}$", fin[:k.start()]):
                righe.append(dict(id_dep=r.id_dep, cognome=r.cognome, nome=r.nome, omonimi=int(omon[r.cognome] > 1), seduta=s,
                                  pagina=page_at(pm, m.start()), passo=re.sub(r'\s+', ' ', t[m.start():m.end() + 200]).replace('¶', '/')))
O = pd.DataFrame(righe).drop_duplicates(['id_dep', 'seduta', 'pagina'])
O.to_csv(os.path.join(PIPE, 'extraction', 'recall_persone.csv'), index=False)
print('costituenti senza emendamenti:', len(zero), '| con almeno un passo da guardare:', O.id_dep.nunique() if len(O) else 0)
