"""Gruppo parlamentare alla data (punto 11), dalle adesioni pubblicate dalla Camera (pipeline/fonti/camera_adesioni_gruppi.csv,
scaricato da tools/scarica_fonti_esterne.py dall'endpoint dati.camera.it).

Scrive data/it/gruppi_periodi.csv (id_dep, gruppo, inizio, fine, motivo_termine) e data/en/group_spells.csv.
Funzione gruppo_alla_data(id_dep, data): il gruppo a cui il costituente aderiva quel giorno; prima della prima adesione
(i gruppi si costituirono nelle settimane successive alla prima seduta) vale la prima."""
import os, re
import pandas as pd
QUI = os.path.dirname(os.path.abspath(__file__)); PIPE = os.path.dirname(QUI); RADICE = os.path.dirname(PIPE)
A = pd.read_csv(os.path.join(PIPE, 'fonti', 'camera_adesioni_gruppi.csv')).drop_duplicates()
A['id_dep'] = A.deputato.str.extract(r'deputato\.rdf/(d\d+)_')[0]
A['p'] = A.proprieta.str.extract(r'([^/#]+)$')[0]
W = A.pivot_table(index=['id_dep', 'adesione'], columns='p', values='valore', aggfunc='first').reset_index()
d = lambda x: f'{str(x)[:4]}-{str(x)[4:6]}-{str(x)[6:8]}' if pd.notna(x) and len(str(x)) >= 8 else ''
P = pd.DataFrame({'id_dep': W.id_dep, 'gruppo': W.label.str.replace(r'\s*\(.*\)\s*$', '', regex=True).str.strip(),
                  'inizio': W.startDate.map(d), 'fine': W.endDate.map(d), 'motivo_termine': W.motivoTermine.fillna('')})
P = P.sort_values(['id_dep', 'inizio']).reset_index(drop=True)
PER = {k: list(zip(g.inizio, g.fine, g.gruppo)) for k, g in P.groupby('id_dep')}
def gruppo_alla_data(id_dep, data):
    per = PER.get(id_dep, [])
    if not per or not isinstance(data, str): return ''
    for a, b, g in per:
        if a <= data <= (b or '9999'): return g
    return per[0][2] if data < per[0][0] else per[-1][2]
if __name__ == '__main__':
    IT = os.path.join(RADICE, 'data', 'it'); EN = os.path.join(RADICE, 'data', 'en')
    P.to_csv(os.path.join(IT, 'gruppi_periodi.csv'), index=False)
    P.rename(columns={'id_dep': 'id_member', 'gruppo': 'group', 'inizio': 'start', 'fine': 'end', 'motivo_termine': 'end_reason'}) \
     .to_csv(os.path.join(EN, 'group_spells.csv'), index=False)
    C = pd.read_csv(os.path.join(IT, 'costituenti_nodi.csv'))
    primo = P.groupby('id_dep').gruppo.first(); ultimo = P.groupby('id_dep').gruppo.last(); n = P.groupby('id_dep').gruppo.nunique()
    print('periodi:', len(P), '| costituenti:', P.id_dep.nunique(), 'su', len(C))
    print('primo gruppo = gruppo_iniziale:', int((C.id_dep.map(primo) == C.gruppo_iniziale).sum()),
          '| ultimo = gruppo_finale:', int((C.id_dep.map(ultimo) == C.gruppo_finale).sum()),
          '| n gruppi = n_gruppi:', int((C.id_dep.map(n) == C.n_gruppi).sum()))
