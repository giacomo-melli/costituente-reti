# =====================================================================
# Estrazione degli emendamenti e dei firmatari dai testi OCR
#
# Da lanciare DOPO che ocr_costituente.R ha finito.
# In Spyder: apri questo file e premi Run (F5). Non serve modificare nulla.
#
# Produce la cartella "extraction" con:
#   emendamenti.csv            un emendamento per riga (firmatari, seduta, pagina, fonte)
#   edgelist_emendamenti.csv   rete two-mode costituente x emendamento
#   menzioni.csv, menzioni_nomi.csv   tutte le occorrenze trovate, per il controllo
#   VERIFICA.csv               tutti gli emendamenti, con link al PDF
#   VERIFICA_campione.csv      40 emendamenti estratti a caso da controllare a mano
#   esiti.csv                  esito di ogni emendamento (approvato, respinto, ritirato, decaduto, assorbito)
#   voti.csv, voti_nominali.csv, edgelist_voti.csv   voti per appello nominale (chi ha votato sì, no, astenuto)
# =====================================================================
import os, sys, subprocess
import pandas as pd

QUI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(QUI, 'extraction')
S = os.path.join(QUI, 'tools')

for script in ['estrai_emendamenti.py', 'esito_emendamenti.py', 'controllo_articolo.py', 'prepara_verifica.py', 'estrai_voti.py']:
    r = subprocess.run([sys.executable, os.path.join(S, script), QUI, OUT], capture_output=True, text=True)
    print(r.stdout)
    if r.returncode != 0:
        print('ERRORE in', script, '\n', r.stderr)
        raise SystemExit

V = pd.read_csv(os.path.join(OUT, 'VERIFICA.csv'))
V.sample(min(40, len(V)), random_state=1947).sort_values(['prima_seduta', 'pagina']) \
 .to_csv(os.path.join(OUT, 'VERIFICA_campione.csv'), index=False, encoding='utf-8-sig')

E = pd.read_csv(os.path.join(OUT, 'emendamenti.csv'))
print('Sedute trascritte:', len({f.split('_')[0] for f in os.listdir(os.path.join(QUI, 'testi_colonne')) if f.endswith('.txt')}))
print('Emendamenti:', len(E), '| con 2+ firmatari:', int((E.n_firmatari >= 2).sum()),
      '| da blocchi di firma:', int((E.fonte == 'firma').sum()), '| con «ed altri»:', int((E.completo == 0).sum()))
print('\nFatto. Controlla VERIFICA_campione.csv nella cartella "extraction".')
