"""Valuta un'estrazione degli emendamenti sui campioni verificati (verità registrata a mano).
Uso: python3 valuta_campioni.py CARTELLA_ESTRAZIONE"""
import sys, os, pandas as pd, unicodedata, re
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EST = sys.argv[1] if len(sys.argv) > 1 else os.path.join(D, 'extraction')
nomi = pd.read_csv(os.path.join(D, 'tools', 'costituenti_nomi.csv')).set_index('id_dep')
k = lambda s: re.sub(r'[^A-Z]', '', unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().upper())
# verità: (seduta, pagina) -> insieme di cognomi; None = non è un emendamento con quei firmatari
V1 = pd.read_csv(os.path.join(D, 'extraction', 'VERIFICA_campione_verificato.csv'))
V2 = pd.read_csv(os.path.join(D, 'extraction', 'VERIFICA_campione2_verificato.csv'))
# campione 3: estratto a caso DOPO le correzioni, su record mai guardati prima.
# E' l'unico indipendente dalla taratura, quindi i suoi tassi si stampano anche a parte.
V3 = pd.read_csv(os.path.join(D, 'extraction', 'VERIFICA_campione3_verificato.csv'))
# campione 4: 80 record estratti a caso dopo le correzioni del 25.10, anch'essi mai guardati.
V4 = pd.read_csv(os.path.join(D, 'extraction', 'VERIFICA_campione4_verificato.csv'))
V = pd.concat([V1.assign(campione=1), V2.assign(campione=2), V3.assign(campione=3), V4.assign(campione=4)])
cg = lambda f: frozenset(k(nomi.loc[i, 'cognome']) for i in str(f).split('|') if i in nomi.index)
E0 = pd.read_csv(os.path.join(D, 'extraction', 'emendamenti_estrazione_v1_verificata.csv')).set_index('id_emendamento')   # estrazione verificata
E = pd.read_csv(os.path.join(EST, 'emendamenti.csv'))
E['cogn'] = E.firmatari.map(lambda x: frozenset(k(nomi.loc[i, 'cognome']) for i in str(x).split('|') if i in nomi.index))
res = []
for r in V.itertuples():
    vero = str(getattr(r, '_11')).strip().lower()   # emendamento_vero_(s/n)
    if vero not in ('s', 'n'): continue
    # gli id del campione 3 vengono dall'estrazione corrente, non da quella di riferimento:
    # in quel caso l'insieme dei cognomi si ricava dai nomi gia' abbinati nel file di verifica.
    if r.id_emendamento in E0.index:
        old = cg(E0.loc[r.id_emendamento, 'firmatari'])
    else:
        old = frozenset(k(max((c for c in nomi.cognome if str(x).startswith(str(c))), key=len, default=x))
                        for x in [y.strip() for y in str(r.firmatari_abbinati).split(',') if y.strip()])
    truth = frozenset(k(x) for x in str(r.verita).split(';')) if isinstance(r.verita, str) and r.verita.strip() else None
    near = E   # stesso insieme di firmatari ovunque (la prima menzione può cambiare tra versioni)
    if vero == 'n':
        ok = not any(c == old for c in near.cogn)          # il falso positivo è sparito?
    else:
        t = truth if truth else old
        ok = any(c == t for c in near.cogn) or any(t <= c for c in near.cogn)
    res.append(dict(id=r.id_emendamento, campione=r.campione, vero=vero, ok=ok, n2=len(truth or old) >= 2))
R = pd.DataFrame(res)
print('verificati:', len(R))
print('falsi positivi ancora presenti:', int(((R.vero == 'n') & ~R.ok).sum()), 'su', int((R.vero == 'n').sum()))
print('emendamenti veri estratti correttamente:', int(((R.vero == 's') & R.ok).sum()), 'su', int((R.vero == 's').sum()))
print('errati:', list(R[(R.vero == 's') & ~R.ok].id)); print('FP residui:', list(R[(R.vero == 'n') & ~R.ok].id))
# Il campione 3 e' estratto DALL'estrazione corrente, quindi il test «il record e' ancora
# presente» sarebbe vero per costruzione: qui contano i verdetti letti a mano sulla pagina.
v3 = V3['emendamento_vero_(s/n)'].astype(str).str.strip().str.lower()
f3 = V3['firmatari_corretti_(s/n)'].astype(str).str.strip().str.lower()
if (v3.isin(['s', 'n'])).any():
    import math
    def wilson(k, n, z=1.96):
        p = k / n; d = 1 + z * z / n
        c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
        return f'{k}/{n} = {100 * p:.1f}% (IC 95%: {100 * max(0, c - h):.1f}-{100 * min(1, c + h):.1f}%)'
    for et, Vx in [('campione 3 (estrazione del 24.10)', V3), ('campione 4 (estrazione del 25.10)', V4)]:
        vv = Vx['emendamento_vero_(s/n)'].astype(str).str.strip().str.lower()
        ff = Vx['firmatari_corretti_(s/n)'].astype(str).str.strip().str.lower()
        if not vv.isin(['s', 'n']).any(): continue
        veri = (vv == 's'); due = veri & (Vx.n_firmatari >= 2)
        print(f'--- {et}: record mai guardati prima, verdetti letti sull\'immagine')
        print('  falsi positivi:', wilson(int((vv == 'n').sum()), int(vv.isin(['s', 'n']).sum())))
        print('  firmatari mancanti o errati:', wilson(int((veri & (ff == 'n')).sum()), int(veri.sum())))
        if int(due.sum()):
            print('    fra i soli emendamenti con 2+ firmatari:', wilson(int((due & (ff == 'n')).sum()), int(due.sum())))
