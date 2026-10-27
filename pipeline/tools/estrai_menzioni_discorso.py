"""Menzioni di costituenti nei discorsi: chi, parlando in Aula, nomina chi.

Ogni «l'onorevole X», «dell'/dall'/all'onorevole X», «il collega X», «on. X» detto da un oratore diventa una
riga: seduta, data, pagina, chi parla (il nome in testa al turno di parola), chi è nominato, la forma stampata
e il contesto. Sono esclusi i turni del Presidente dell'Assemblea, quasi sempre procedurali («Ha facoltà di
parlare l'onorevole X»), e le autocitazioni.
Le regole di testo (lettura delle pagine, abbinamento dei nomi, atti di parola) sono quelle dell'estrattore
degli emendamenti, caricate dal suo file perché le due estrazioni restino coerenti.
Uso: python3 estrai_menzioni_discorso.py CARTELLA_pipeline [file_output]"""
import os, re, sys, glob
import pandas as pd

D = sys.argv[1] if len(sys.argv) > 1 else '.'
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(D, 'extraction', 'menzioni_discorso.csv')
src = open(os.path.join(D, 'tools', 'estrai_emendamenti.py'), encoding='utf-8').read()
ns = {}
argv, sys.argv = sys.argv, ['estrai_emendamenti.py', D]
exec(compile(src[:src.index('recs = []')], 'estrai_emendamenti.py', 'exec'), ns)
sys.argv = argv
flatten, page_at, candidates, NAME = ns['flatten'], ns['page_at'], ns['candidates'], ns['NAME']
atto_di_parola, INTESTA = ns['atto_di_parola'], ns['INTESTA']
nomi, date = ns['nomi'], ns['date']

NON_NOMI = r"(?!(?:Presidente|Ministro|Sottosegretario|Relatore|Commissione|Assemblea|Governo|Collega|Colleghi|Segretario|Questore)\b)"
MENZ = re.compile(r"(?:\b(?:[LlDdAaNnSs](?:ell|all|ull)?['’]\s?|[Ll]['’]\s?)?onorevole|\b(?:il|del|al|dal|col|nel|sul)\s+collega(?:\s+onorevole)?|\bon\.)[\s‘'’]+"
                  + NON_NOMI + "(" + NAME + ")")
RUOLO = re.compile(r"Presidente|Relatore|Ministro|Sottosegretario")


# intestazione di turno anche in linea, non solo a capo: «…(Approvazioni). PRESIDENTE. Pongo in votazione…»;
# senza, le parole del Presidente finivano nel turno dell'oratore precedente
INTESTA_LINEA = re.compile(r"(?:¶|[.!?)»;:]\s|^)\s*[.,'‘’|:°\s]*([A-ZÀ-Ý]{3,}(?:['’ ][A-ZÀ-Ý]{2,}){0,3})(,\s*[A-Z][a-zà-ÿ][^.¶]{0,70})?[.,]\s+(?=[A-ZÀ-Ý(«]|\.{2,}|…)")
NON_TURNO = {'ART', 'ARTICOLO', 'TITOLO', 'PARTE', 'SEZIONE', 'CAPO', 'INDICE', 'ASSEMBLEA', 'COSTITUENTE', 'SEDUTA', 'RESOCONTO'}


def turni(text):
    """(inizio, nome, ruolo) di ogni turno di parola, in ordine."""
    return [(t.start(1), t.group(1).strip(), (t.group(2) or '').strip(' ,')) for t in INTESTA_LINEA.finditer(text)
            if t.group(1).strip().split()[0] not in NON_TURNO and (len(t.group(1).strip()) >= 4)]


def abbina(nome, data, presenti):
    """id del costituente; per gli omonimi vale chi parla nella stessa seduta, altrimenti resta vuoto."""
    c, how, _ = candidates(nome, data)
    if len(c) == 1: return c[0].id_dep, how
    if len(c) > 1:
        p = [x for x in c if x.id_dep in presenti]
        if len(p) == 1: return p[0].id_dep, how + '+seduta'
        return '', 'ambiguo'
    return '', 'non trovato'


righe = []
sedute = sorted({os.path.basename(f).split('_')[0] for f in glob.glob(os.path.join(D, 'testi_colonne', 'sed*_p*.txt'))})
for s in sedute:
    text, pm = flatten(s)
    data = date.get(s)
    T = turni(text)
    # chi parla almeno una volta nella seduta: serve a sciogliere gli omonimi
    presenti = set()
    for _, nm, _ in T:
        if not nm.startswith('PRESIDENTE'):
            i, how = abbina(nm.title(), data, set())
            if i: presenti.add(i)
    k = 0
    for m in MENZ.finditer(text):
        while k + 1 < len(T) and T[k + 1][0] < m.start(): k += 1
        if not T or T[k][0] > m.start(): continue
        nome_parl, ruolo = T[k][1], T[k][2]
        if nome_parl.startswith('PRESIDENTE'): continue                      # turni del Presidente: procedurali
        id_parl, _ = abbina(nome_parl.title(), data, presenti)
        forma = m.group(1).strip()
        id_men, how = abbina(forma, data, presenti)
        if id_men and id_men == id_parl: continue                          # autocitazione
        before = text[max(0, m.start() - 300):m.start()]
        dopo = text[m.end():m.end() + 160]
        # didascalia del resoconto fra parentesi («(Interruzione dell'onorevole X)», «(Commenti a sinistra)»):
        # registra un'interazione, ma non sono parole dell'oratore
        if re.search(r"\([^()]{0,60}$", before[-60:]) and re.match(r"[^()]{0,60}\)", dopo):
            tipo = 'didascalia'
        elif re.search(r"emendament|propost[ao]\s+(?:di|presentat)|articolo aggiuntivo", before[-120:] + dopo[:80], re.I):
            tipo = 'su un emendamento'
        elif atto_di_parola(before, m.group(0)[:1]):
            tipo = 'atto di parola'
        else:
            tipo = 'altro'
        righe.append(dict(seduta=s, data=data, pagina=page_at(pm, m.start()), id_parlante=id_parl, parlante_stampato=nome_parl.title(),
                          ruolo_parlante=('' if not RUOLO.search(ruolo) else ruolo), id_menzionato=id_men, forma_stampata=forma,
                          abbinamento=how, tipo_menzione=tipo,
                          contesto=(before[-160:] + ' [[' + m.group(0) + ']] ' + dopo[:120]).replace('¶', '/')))

R = pd.DataFrame(righe)
R.to_csv(OUT, index=False)
ok = R[(R.id_parlante != '') & (R.id_menzionato != '')]
print(f"menzioni {len(R)}; con parlante e menzionato abbinati {len(ok)}; coppie distinte {ok.groupby(['id_parlante','id_menzionato']).ngroups}")
print('tipo:', R.tipo_menzione.value_counts().to_dict())
print('abbinamento del menzionato:', R.abbinamento.value_counts().to_dict())
print('parlante non abbinato:', int((R.id_parlante == '').sum()))
