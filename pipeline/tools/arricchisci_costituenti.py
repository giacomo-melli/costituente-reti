"""Variabili dei costituenti ricavate dagli altri file del dataset (si rilancia da esporta_dataset.py).

- Commissione per la Costituzione (punto 10): `commissione_75`, `sottocommissione` (I, II, III; piu' d'una
  separate da «;»), `comitato_redazione`, `ruolo_commissione` (la carica piu' alta tenuta nella Commissione
  o nei suoi organi), da `edgelist.csv` (organi o621-o625).
- Presenza agli appelli nominali (punto 13): `voti_in_carica` (votazioni tenute mentre era in carica),
  `voti_presente` (ha risposto sì, no o si e' astenuto), `voti_congedo`, `voti_assente` (in carica, ne'
  presente ne' in congedo), `quota_presenza` = presente / in carica. Le votazioni nulle per mancanza del
  numero legale contano: la chiama c'e' stata. Un nome stampato ma non abbinato fa risultare assente chi
  ha votato: l'errore e' quello misurato sui totali ufficiali (scarto medio 2,3 nomi su ~350 per votazione).
Lo script toglie e riscrive solo le proprie colonne, quindi si puo' lanciare piu' volte."""
import os, sys
import pandas as pd
QUI = os.path.dirname(os.path.abspath(__file__)); RADICE = os.path.dirname(os.path.dirname(QUI))
IT = os.path.join(RADICE, 'data', 'it'); EN = os.path.join(RADICE, 'data', 'en'); EST = os.path.join(os.path.dirname(QUI), 'extraction')
NUOVE = ['commissione_75', 'sottocommissione', 'comitato_redazione', 'ruolo_commissione',
         'voti_in_carica', 'voti_presente', 'voti_congedo', 'voti_assente', 'quota_presenza', 'eletto_camera_1948', 'viaf_id']
EN_NOMI = dict(zip(NUOVE, ['committee_75', 'subcommittee', 'drafting_committee', 'committee_role',
                           'votes_in_office', 'votes_present', 'votes_on_leave', 'votes_absent', 'share_present', 'elected_chamber_1948', 'viaf_id']))
C = pd.read_csv(os.path.join(IT, 'costituenti_nodi.csv')).drop(columns=NUOVE, errors='ignore')
G = pd.read_csv(os.path.join(IT, 'edgelist.csv'))
com = G[G.id_organo.isin(['o621', 'o622', 'o623', 'o624', 'o625'])]
C['commissione_75'] = C.id_dep.isin(com[com.id_organo == 'o621'].id_dep).astype(int)
sotto = {'o622': 'I', 'o623': 'II', 'o624': 'III'}
s = com[com.id_organo.isin(sotto)].assign(s=lambda d: d.id_organo.map(sotto)).groupby('id_dep').s.apply(lambda x: ';'.join(sorted(set(x), key=['I', 'II', 'III'].index)))
C['sottocommissione'] = C.id_dep.map(s).fillna('')
C['comitato_redazione'] = C.id_dep.isin(com[com.id_organo == 'o625'].id_dep).astype(int)
rango = {'presidente': 3, 'vicepresidente': 2, 'segretario': 1, 'componente': 0}
def piu_alto(ruoli):
    r = [x for v in ruoli for x in str(v).split(';') if x in rango]
    return max(r, key=rango.get) if r else ''
C['ruolo_commissione'] = C.id_dep.map(com.groupby('id_dep').ruolo.apply(piu_alto)).fillna('')
# presenza
V = pd.read_csv(os.path.join(EST, 'voti.csv')); N = pd.read_csv(os.path.join(EST, 'voti_nominali.csv'), keep_default_na=False)
Ev = pd.read_csv(os.path.join(IT, 'edgelist_voti.csv')); Ev['id_voto'] = Ev.id_voto.str[1:].astype(int)
cong = N[(N.voto == 'congedo') & (N.id_dep != '')][['id_voto', 'id_dep']].drop_duplicates()
fine = C.fine_mandato.fillna('1948-01-31')
rows = []
for r, ini, fin in zip(C.id_dep, C.inizio_mandato, fine):
    vv = set(V[(V.data >= ini) & (V.data <= fin)].id_voto)
    pres = set(Ev[Ev.id_dep == r].id_voto) & vv
    cg = (set(cong[cong.id_dep == r].id_voto) & vv) - pres
    rows.append((len(vv), len(pres), len(cg), len(vv) - len(pres) - len(cg)))
C[['voti_in_carica', 'voti_presente', 'voti_congedo', 'voti_assente']] = rows
C['quota_presenza'] = (C.voti_presente / C.voti_in_carica.where(C.voti_in_carica > 0)).round(3)
sys.path.insert(0, QUI); from eletti_1948 import eletto
C['eletto_camera_1948'] = [eletto(c, x) for c, x in zip(C.cognome, C.nome)]
# VIAF da Wikidata (P214), scaricato da tools/scarica_fonti_esterne.py; piu' identificativi separati da «;»
fv = os.path.join(os.path.dirname(QUI), 'fonti', 'wikidata_viaf.csv')
if os.path.exists(fv):
    W = pd.read_csv(fv, dtype=str).dropna()
    C['viaf_id'] = C.qid.map(W.groupby('qid').viaf.apply(lambda x: ';'.join(sorted(set(x))))).fillna('')
else:
    C['viaf_id'] = ''
C.to_csv(os.path.join(IT, 'costituenti_nodi.csv'), index=False)
M = pd.read_csv(os.path.join(EN, 'members_nodes.csv')).drop(columns=list(EN_NOMI.values()), errors='ignore')
assert (M.id_member.values == C.id_dep.values).all()
M = pd.concat([M, C[NUOVE].rename(columns=EN_NOMI)], axis=1)
M['committee_role'] = M.committee_role.map({'presidente': 'chair', 'vicepresidente': 'vice-chair', 'segretario': 'secretary', 'componente': 'member', '': ''}).fillna('')
M.to_csv(os.path.join(EN, 'members_nodes.csv'), index=False)
print('Commissione dei 75:', int(C.commissione_75.sum()), '| sottocommissioni:', C.sottocommissione.value_counts().to_dict(),
      '| Comitato di redazione:', int(C.comitato_redazione.sum()), '| ruoli:', C.ruolo_commissione.value_counts().to_dict())
print('VIAF:', int((C.viaf_id != '').sum()), '| con qid:', int(C.qid.notna().sum()))
print('Eletti alla Camera nel 1948:', int(C.eletto_camera_1948.sum()))
print('Presenza media agli appelli:', round(C.quota_presenza.mean(), 3), '| mai presenti:', int((C.voti_presente == 0).sum()))
