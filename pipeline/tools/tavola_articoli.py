"""Materia e articolo della Costituzione per ogni emendamento (punto 22), e controllo delle date (punto 23).

Uso: python3 tools/tavola_articoli.py [cartella_pipeline] [cartella_estrazione]
Legge la tavola della Camera (pipeline/fonti/tavola_progetto_costituzione.tsv: articolo del progetto -> articolo della
Costituzione, parte e titolo, date della discussione in Assemblea) e extraction/controllo_articolo.csv.
Per ogni emendamento con `articolo_in_discussione`:
- se la seduta cade in una delle date in cui la tavola dice che quell'articolo del progetto fu discusso, l'articolo e'
  confermato da un giudice esterno (`tavola` = `data coerente`);
- se no, si prova `articolo_menzionato`; se nemmeno quello torna con le date, si cerca l'unico articolo del progetto
  discusso quel giorno; altrimenti `data discordante` (spesso una seduta su un'altra legge).
Scrive extraction/articoli_tavola.csv: id_emendamento, articolo_progetto, articolo_costituzione, materia, tavola."""
import os, re, sys
import pandas as pd
QUI = os.path.dirname(os.path.abspath(__file__)); PIPE = os.path.dirname(QUI)
EST = sys.argv[-1] if len(sys.argv) > 1 else os.path.join(PIPE, 'extraction')
MESI = {m: i + 1 for i, m in enumerate('gennaio febbraio marzo aprile maggio giugno luglio agosto settembre ottobre novembre dicembre'.split())}
def date_di(txt):
    out = set()
    for blocco in str(txt).split(';'):
        m = re.search(r'([a-z]+)\s+(\d{4})\s*$', blocco.strip())
        if not m: continue
        mese, anno = MESI[m.group(1)], int(m.group(2))
        giorni = [int(g) for g in re.findall(r'\b(\d{1,2})\b', blocco[:m.start()])]
        for g in giorni: out.add(f'{anno}-{mese:02d}-{g:02d}')
    return out
T = pd.read_csv(os.path.join(PIPE, 'fonti', 'tavola_progetto_costituzione.tsv'), sep='\t', comment='#', dtype=str).fillna('')
T['date'] = T.date_assemblea.map(date_di)
T['materia'] = T.parte_titolo
TAV = T.set_index('articolo_progetto')
per_data = {}
for r in T.itertuples():
    for d in r.date: per_data.setdefault(d, []).append(r.articolo_progetto)
C = pd.read_csv(os.path.join(EST, 'controllo_articolo.csv'), dtype=str).fillna('')
E = pd.read_csv(os.path.join(EST, 'emendamenti.csv'), dtype=str).set_index('id_emendamento')
righe = []
for r in C.itertuples():
    d = E.data.get(r.id_emendamento, '')
    scelta, stato = '', ''
    for cand in (r.articolo_in_discussione, r.articolo_menzionato.replace('.0', '')):
        if cand in TAV.index and d in TAV.loc[cand, 'date']:
            scelta, stato = cand, 'data coerente'; break
    if not scelta and len(per_data.get(d, [])) == 1:
        scelta, stato = per_data[d][0], 'unico articolo discusso quel giorno'
    if not scelta:
        stato = 'giorno senza articoli del progetto' if d not in per_data else ('data discordante' if r.articolo_in_discussione else 'non determinato')
    righe.append(dict(id_emendamento=r.id_emendamento, articolo_progetto=scelta,
                      articolo_costituzione=TAV.loc[scelta, 'articolo_costituzione'] if scelta else '',
                      materia=TAV.loc[scelta, 'materia'] if scelta else '', tavola=stato))
O = pd.DataFrame(righe); O.to_csv(os.path.join(EST, 'articoli_tavola.csv'), index=False)
print('tavola:', O.tavola.value_counts().to_dict())
print('materia:', O.materia.value_counts().head(8).to_dict())
