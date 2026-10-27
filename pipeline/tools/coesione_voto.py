"""Coesione di voto dei gruppi parlamentari (indice di Rice) sulle votazioni per appello nominale.

Controllo di validità dei voti estratti: se l'abbinamento dei nomi fosse rumoroso, i gruppi notoriamente
disciplinati (comunisti, democristiani) risulterebbero poco compatti. Rice = |sì − no| / (sì + no) per gruppo e
votazione; gli astenuti sono esclusi. Il gruppo è quello finale (`gruppo_finale`): la scissione socialista del
gennaio 1947 precede quasi tutte le votazioni, ma per chi ha cambiato gruppo l'attribuzione può essere sfasata.
Uso: python3 coesione_voto.py [cartella_data_it] → stampa la tabella e scrive extraction/coesione_voto.csv"""
import os, sys
import pandas as pd
QUI = os.path.dirname(os.path.abspath(__file__))
IT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.dirname(QUI)), 'data', 'it')
V = pd.read_csv(os.path.join(IT, 'edgelist_voti.csv')).merge(
    pd.read_csv(os.path.join(IT, 'costituenti_nodi.csv'))[['id_dep', 'gruppo_finale']], on='id_dep')
t = V[V.voto.isin(['sì', 'no'])].groupby(['gruppo_finale', 'id_voto', 'voto']).size().unstack(fill_value=0)
t['votanti'] = t['sì'] + t['no']
t = t[t.votanti >= 5].copy()                       # gruppi con almeno 5 voti espressi nella votazione
t['rice'] = (t['sì'] - t['no']).abs() / t.votanti
t.reset_index().to_csv(os.path.join(QUI, '..', 'extraction', 'coesione_voto.csv'), index=False)
g = t.groupby('gruppo_finale').agg(votazioni=('rice', 'size'), rice_medio=('rice', 'mean'), rice_minimo=('rice', 'min'),
                                     votanti_medi=('votanti', 'mean')).sort_values('votanti_medi', ascending=False)
g['dissenzienti_per_voto'] = t.assign(d=t[['sì', 'no']].min(axis=1)).groupby('gruppo_finale').d.mean()
pd.set_option('display.width', 200)
print(g.round(3).to_string())
