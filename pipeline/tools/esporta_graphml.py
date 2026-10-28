"""Le reti del dataset in GraphML (punto 19), per Gephi, igraph, networkx, Pajek… Solo librerie standard + pandas.

Uso: python3 pipeline/tools/esporta_graphml.py      -> scrive data/graphml/*.graphml
  cofirma_bipartita      costituenti × emendamenti (ruolo presentatore/firmatario)
  cofirma_proiezione     costituente — costituente, peso = emendamenti firmati insieme
  presentatore_diretta   firmatario -> presentatore, peso = emendamenti
  voti_bipartita         costituenti × votazioni, segno +1 sì, -1 no, 0 astenuto
  menzioni_diretta       chi parla -> chi e' menzionato, peso = menzioni
  altri_atti_bipartita   costituenti × altri atti co-firmati (interrogazioni, ordini del giorno…)
Gli attributi dei nodi costituente sono cognome, nome, gruppo_iniziale, gruppo_finale, lista_partito, donna."""
import os, itertools
from xml.sax.saxutils import escape
import pandas as pd
RADICE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
IT = os.path.join(RADICE, 'data', 'it'); OUT = os.path.join(RADICE, 'data', 'graphml'); os.makedirs(OUT, exist_ok=True)
C = pd.read_csv(os.path.join(IT, 'costituenti_nodi.csv'))
ATTR = ['cognome', 'nome', 'gruppo_iniziale', 'gruppo_finale', 'lista_partito', 'donna']
def scrivi(nome, nodi, archi, diretto, attr_nodi, attr_archi):
    """nodi: dict id -> dict attributi; archi: lista (u, v, dict attributi)."""
    tipo = lambda v: 'double' if isinstance(v, float) else 'int' if isinstance(v, int) else 'string'
    righe = ['<?xml version="1.0" encoding="UTF-8"?>', '<graphml xmlns="http://graphml.graphdrawing.org/xmlns">']
    for k in attr_nodi: righe.append(f'<key id="n_{k}" for="node" attr.name="{k}" attr.type="string"/>')
    for k, t in attr_archi.items(): righe.append(f'<key id="e_{k}" for="edge" attr.name="{k}" attr.type="{t}"/>')
    righe.append(f'<graph id="{nome}" edgedefault="{"directed" if diretto else "undirected"}">')
    for i, a in nodi.items():
        righe.append(f'<node id="{escape(str(i))}">' + ''.join(f'<data key="n_{k}">{escape(str(a.get(k, "")))}</data>' for k in attr_nodi if str(a.get(k, '')) not in ('', 'nan')) + '</node>')
    for u, v, a in archi:
        righe.append(f'<edge source="{escape(str(u))}" target="{escape(str(v))}">' + ''.join(f'<data key="e_{k}">{escape(str(x))}</data>' for k, x in a.items()) + '</edge>')
    righe += ['</graph>', '</graphml>']
    open(os.path.join(OUT, nome + '.graphml'), 'w', encoding='utf-8').write('\n'.join(righe))
    print(nome, len(nodi), 'nodi', len(archi), 'archi')
cost = {r.id_dep: dict(tipo='costituente', **{k: getattr(r, k) for k in ATTR}) for r in C.itertuples()}
L = pd.read_csv(os.path.join(IT, 'edgelist_emendamenti.csv')); E = pd.read_csv(os.path.join(IT, 'emendamenti_nodi.csv'), dtype=str).fillna('')
em = {r.id_emendamento: dict(tipo='emendamento', seduta=r.prima_seduta, data=r.data, tipo_emendamento=r.tipo_emendamento, esito=r.esito, materia=r.materia) for r in E.itertuples()}
scrivi('cofirma_bipartita', {**cost, **em}, [(r.id_dep, r.id_emendamento, dict(ruolo=r.ruolo, abbinamento=r.abbinamento)) for r in L.itertuples()],
       False, ATTR + ['tipo', 'seduta', 'data', 'tipo_emendamento', 'esito', 'materia'], dict(ruolo='string', abbinamento='string'))
peso = {}
for _, g in L.groupby('id_emendamento'):
    for a, b in itertools.combinations(sorted(set(g.id_dep)), 2): peso[(a, b)] = peso.get((a, b), 0) + 1
scrivi('cofirma_proiezione', cost, [(a, b, dict(peso=w)) for (a, b), w in peso.items()], False, ATTR, dict(peso='int'))
dir_ = {}
for _, g in L.groupby('id_emendamento'):
    p = g[g.ruolo == 'presentatore'].id_dep
    if len(p):
        for x in g[g.ruolo == 'firmatario'].id_dep: dir_[(x, p.iloc[0])] = dir_.get((x, p.iloc[0]), 0) + 1
scrivi('presentatore_diretta', cost, [(a, b, dict(peso=w)) for (a, b), w in dir_.items()], True, ATTR, dict(peso='int'))
Vn = pd.read_csv(os.path.join(IT, 'voti_nodi.csv')); Ev = pd.read_csv(os.path.join(IT, 'edgelist_voti.csv'))
vot = {r.id_voto: dict(tipo='votazione', seduta=r.seduta, data=r.data) for r in Vn.itertuples()}
scrivi('voti_bipartita', {**cost, **vot}, [(r.id_dep, r.id_voto, dict(segno={'sì': 1, 'no': -1}.get(r.voto, 0), voto=r.voto)) for r in Ev.itertuples()],
       False, ATTR + ['tipo', 'seduta', 'data'], dict(segno='int', voto='string'))
M = pd.read_csv(os.path.join(IT, 'menzioni_discorso.csv'), dtype=str).fillna('')
M = M[(M.id_parlante != '') & (M.id_menzionato != '') & (M.id_parlante != M.id_menzionato)]
mz = M.groupby(['id_parlante', 'id_menzionato']).size()
scrivi('menzioni_diretta', cost, [(a, b, dict(peso=int(w))) for (a, b), w in mz.items()], True, ATTR, dict(peso='int'))
A = pd.read_csv(os.path.join(IT, 'altri_atti_nodi.csv'), dtype=str).fillna(''); LA = pd.read_csv(os.path.join(IT, 'edgelist_altri_atti.csv'))
att = {r.id_atto: dict(tipo=r.tipo_atto, seduta=r.seduta, data=r.data) for r in A.itertuples()}
scrivi('altri_atti_bipartita', {**cost, **att}, [(r.id_dep, r.id_atto, {}) for r in LA.itertuples()], False, ATTR + ['tipo', 'seduta', 'data'], {})
