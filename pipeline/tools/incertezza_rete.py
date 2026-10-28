"""Propagazione dell'errore di estrazione alle statistiche di rete (punto 17).

Uso: python3 tools/incertezza_rete.py [n_repliche]
Per ogni replica: (1) si tengono tutti gli emendamenti (un ricampionamento con reinserimento duplicherebbe gli atti e
sottostimerebbe i legami distinti: la parte di incertezza dovuta al recall, circa due terzi degli emendamenti stampati,
non si simula e va detta a parte); (2) si toglie ogni emendamento con 2+ firmatari con probabilita'
0,042 (falsi positivi misurati sui 216 pluri-firmati verificati); (3) si toglie ogni firma con probabilita' 0,043
(firmatari sbagliati misurati sugli stessi). Si calcolano le statistiche sulla rete risultante e si riportano media e
intervallo al 95% (percentili 2,5-97,5), accanto al valore osservato e a quello della versione conservativa.
Scrive extraction/incertezza_rete.csv."""
import os, sys
import numpy as np, pandas as pd
QUI = os.path.dirname(os.path.abspath(__file__)); RADICE = os.path.dirname(os.path.dirname(QUI))
IT = os.path.join(RADICE, 'data', 'it'); OUT = os.path.join(os.path.dirname(QUI), 'extraction', 'incertezza_rete.csv')
R = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
C = pd.read_csv(os.path.join(IT, 'costituenti_nodi.csv')); n = len(C)
idx = {d: i for i, d in enumerate(C.id_dep)}; gruppo = C.gruppo_finale.fillna('?').values
L = pd.read_csv(os.path.join(IT, 'edgelist_emendamenti.csv')); M = pd.read_csv(os.path.join(IT, 'menzioni_discorso.csv'), dtype=str).fillna('')
P_FP, P_FIRMA = 0.042, 0.043
p_g = pd.Series(gruppo).value_counts(normalize=True)
atteso_stesso = float((p_g ** 2).sum())

def statistiche(liste, ruoli):
    """liste: elenchi di indici dei firmatari; ruoli: per ogni elenco l'indice del presentatore (o -1)."""
    coppie = set(); diretti = set()
    for f, pr in zip(liste, ruoli):
        f = sorted(set(f))
        for a in range(len(f)):
            for b in range(a + 1, len(f)): coppie.add((f[a], f[b]))
        if pr >= 0:
            for x in f:
                if x != pr: diretti.add((x, pr))
    deg = np.zeros(n)
    for a, b in coppie: deg[a] += 1; deg[b] += 1
    m = len(coppie)
    stesso = sum(gruppo[a] == gruppo[b] for a, b in coppie) / m if m else np.nan
    recip = sum((b, a) in diretti for a, b in diretti) / len(diretti) if diretti else np.nan
    return dict(densita=2 * m / (n * (n - 1)), grado_medio=deg.mean(), centralizzazione=(deg.max() - deg).sum() / ((n - 1) * (n - 2)),
                quota_legami_stesso_gruppo=stesso, omofilia_rapporto_atteso=stesso / atteso_stesso, reciprocita_firmatario_presentatore=recip)

def da_edgelist(Ld):
    g = Ld.groupby('id_emendamento')
    liste = [[idx[d] for d in x.id_dep if d in idx] for _, x in g]
    ruoli = [next((idx[d] for d, r in zip(x.id_dep, x.ruolo) if r == 'presentatore' and d in idx), -1) for _, x in g]
    return liste, ruoli

liste, ruoli = da_edgelist(L)
oss = statistiche(liste, ruoli)
cons = statistiche(*da_edgelist(L[L.abbinamento.isin(['esatto', 'esatto+partito', 'correzione manuale'])]))
# reciprocita' delle menzioni nei discorsi: osservata e bootstrap sulle menzioni
Mm = M[(M.id_parlante != '') & (M.id_menzionato != '')]
def recip_menz(df):
    s = set(zip(df.id_parlante, df.id_menzionato)); s = {x for x in s if x[0] != x[1]}
    return sum((b, a) in s for a, b in s) / len(s)
rng = np.random.default_rng(1947)
rep = []
for _ in range(R):
    k = range(len(liste))
    l2, r2 = [], []
    for j in k:
        f = liste[j]
        if len(f) >= 2 and rng.random() < P_FP: continue
        f2 = [x for x in f if rng.random() >= P_FIRMA] if len(f) >= 2 else f
        if f2: l2.append(f2); r2.append(ruoli[j] if ruoli[j] in f2 else -1)
    st = statistiche(l2, r2)
    st['reciprocita_menzioni'] = np.nan   # menzionato giusto in 40/40, parlante in 31/31: nessun errore da propagare
    rep.append(st)
Rp = pd.DataFrame(rep)
oss['reciprocita_menzioni'] = recip_menz(Mm); cons['reciprocita_menzioni'] = np.nan
righe = [dict(statistica=k, osservato=round(oss[k], 4), versione_conservativa=round(cons[k], 4) if pd.notna(cons[k]) else '',
              media_repliche=round(Rp[k].mean(), 4), ic95_basso=round(Rp[k].quantile(.025), 4), ic95_alto=round(Rp[k].quantile(.975), 4))
         for k in oss]
O = pd.DataFrame(righe); O.to_csv(OUT, index=False); print(O.to_string(index=False))
