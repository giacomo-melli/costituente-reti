"""Test di non-regressione delle regole di estrazione degli emendamenti.

Ogni caso in `test_regole_casi.json` e' un passo vero dei resoconti (testo OCR, a volte con le
interruzioni di riga originali) con l'esito atteso: gli elenchi di firmatari che l'estrattore deve
produrre su quella pagina, oppure nessuno. I casi con «controllato sull'immagine» nella nota sono
stati confrontati con la scansione.

Il test lancia l'estrattore vero su un corpus finto, un caso per pagina con testo neutro attorno
perche' i contesti non si tocchino, e confronta. Da lanciare dopo ogni modifica all'estrattore:

    python3 pipeline/tools/test_regole.py            # usa tools/estrai_emendamenti.py
    python3 pipeline/tools/test_regole.py ALTRO.py   # prova una versione modificata

Esce con codice 1 se un caso fallisce."""
import json, os, shutil, subprocess, sys, tempfile, time
from collections import Counter
import pandas as pd

QUI = os.path.dirname(os.path.abspath(__file__))
ESTR = sys.argv[1] if len(sys.argv) > 1 else os.path.join(QUI, 'estrai_emendamenti.py')
CASI = json.load(open(os.path.join(QUI, 'test_regole_casi.json'), encoding='utf-8'))
NEUTRO = 'Il seguito della discussione e rinviato ad altra seduta. ' * 30

nomi = pd.read_csv(os.path.join(QUI, 'costituenti_nomi.csv'))
omonimi = set(nomi.cognome[nomi.cognome.duplicated()])
etichetta = {r.id_dep: r.cognome + (' ' + r.nome.split()[0] if r.cognome in omonimi else '') for r in nomi.itertuples()}

t0 = time.time()
d = tempfile.mkdtemp(prefix='test_regole_')
try:
    os.symlink(QUI, os.path.join(d, 'tools'))
    os.makedirs(os.path.join(d, 'testi_colonne'))
    pagina_di, n = {}, Counter()
    for c in CASI:
        n[c['seduta']] += 1
        pagina_di[(c['seduta'], n[c['seduta']])] = c['nome']
        with open(os.path.join(d, 'testi_colonne', f"{c['seduta']}_p{n[c['seduta']]:03d}.txt"), 'w', encoding='utf-8') as f:
            f.write(NEUTRO + '\n\n' + c['testo'] + '\n\n' + NEUTRO)
    r = subprocess.run([sys.executable, ESTR, d, os.path.join(d, 'out')], capture_output=True, text=True)
    if r.returncode:
        print(r.stderr); sys.exit(2)
    M = pd.read_csv(os.path.join(d, 'out', 'menzioni.csv'))
    E = pd.read_csv(os.path.join(d, 'out', 'emendamenti.csv'))
finally:
    shutil.rmtree(d, ignore_errors=True)

ottenuto = {c['nome']: [] for c in CASI}
for m in M.itertuples():
    ottenuto[pagina_di[(m.seduta, m.pagina)]].append(sorted(etichetta[x] for x in str(m.ids).split('|') if x.startswith('d')))

falliti = 0
for c in CASI:
    att, ott = Counter(map(tuple, c['atteso'])), Counter(map(tuple, ottenuto[c['nome']]))
    if att == ott:
        print(f"  ok      {c['nome']}")
        continue
    falliti += 1
    print(f"  FALLITO {c['nome']} ({c['seduta']}): {c['nota']}")
    for x in att - ott: print('          manca:  ', ', '.join(x))
    for x in ott - att: print('          in piu\':', ', '.join(x))

# consolidamento: un nome solo non e' assorbito da un elenco in cui non e' il primo firmatario
ids_bubbio = set(nomi.id_dep[nomi.cognome == 'Bubbio'])
if not any(set(str(f).split('|')) == ids_bubbio for f in E.firmatari):
    falliti += 1; print('  FALLITO consolidamento: l\'emendamento di Bubbio e\' stato assorbito nell\'elenco di 28 firme')
else:
    print('  ok      consolidamento (emendamento singolo non assorbito)')

print(f"\n{len(CASI) + 1 - falliti}/{len(CASI) + 1} casi superati in {time.time() - t0:.1f} s")
sys.exit(1 if falliti else 0)
