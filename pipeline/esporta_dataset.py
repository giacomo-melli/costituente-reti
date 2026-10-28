# =====================================================================
# Esporta emendamenti e voti nominali nel dataset finale (IT ed EN)
#
# Da lanciare DOPO esegui_estrazione.py e la verifica a campione.
# In Spyder: apri questo file e premi Run (F5). Non serve modificare nulla.
#
# Legge  pipeline/extraction/  (emendamenti, voti, campione verificato)
# Scrive data/it e data/en
# Stampa i tassi di errore stimati dal campione verificato a mano.
# =====================================================================
import os, math
import pandas as pd

QUI = os.path.dirname(os.path.abspath(__file__))
EST = os.path.join(QUI, 'extraction')
DS = os.path.join(os.path.dirname(QUI), 'data')
IT, EN = os.path.join(DS, 'it'), os.path.join(DS, 'en')
nomi = pd.read_csv(os.path.join(QUI, 'tools', 'costituenti_nomi.csv'))

# ---------- correzioni manuali dalla verifica a campione ----------
# Individuate per seduta e cognomi (gli id cambiano tra un'estrazione e l'altra).
FALSI_POSITIVI = [('sed072', ['Perassi']),                               # proposta citata nel dibattito
                  ('sed073', ['Dozza', 'Cosattini']),   # «il criterio proposto dagli onorevoli Dozza e Cosattini»: due emendamenti distinti, citati insieme
                  ('sed189', ['Arcaini']),      # p20 e p23 citano l'emendamento Arcaini-Scoca-Cappi di p18, non un atto a se'
                  ('sed075', ['Della Seta', 'Calamandrei', 'Lami Starnuti']),   # tre emendamenti distinti
                  ('sed299', ['Ruini']),                                # parla come Presidente della Commissione
                  # secondo campione (verifica dei 26 casi residui): gli altri FP individuati
                  # non sono piu' prodotti dall'estrattore corrente e non richiedono correzione
                  ('sed128', ['Togliatti', 'Marchesi']),                 # valutazioni in un intervento, non presentazione
                  ('sed308', ['Nobile', "Dominedo'"]),                  # osservazioni, non emendamento
                  # terzo campione (40 record estratti a caso dopo le correzioni)
                  ('sed089', ['Tupini']),                                # parla come Presidente della prima Sottocommissione
                  ('sed170', ['Lami Starnuti', 'Preti']),                # due emendamenti distinti; il record nasce da una formula di interpello
                  ('sed262', ['Ruini']),                                 # parla come Presidente della Commissione
                  # --- verifica sull'immagine della pagina dopo le correzioni dell'estrattore (ottobre 2026) ---
                  ('sed120', ['Moro']),          # «l'emendamento sostitutivo dell'onorevole Laconi, dell'onorevole Moro e di altri
                                                 # colleghi»: ripresa dell'emendamento Laconi (sed119), non un atto nuovo
                  ('sed105', ['Martino', 'Labriola', 'Della Seta', 'Caronia', 'Lucifero']),   # ripresa dell'emendamento
                                                 # presentato in sed104 (vedi FIRMATARI_CORRETTI): elenco ristampato dal Presidente
                  ('sed310', ['Nitti', 'Bertone'])]   # «eguale emendamento, prima di me, era stato proposto dall'onorevole
                                                 # Nitti» (Bertone): due emendamenti identici di autori diversi, non una co-firma
FIRMATARI_CORRETTI = [                       # elenco stampato, verificato sul PDF: (seduta, cognomi presenti, elenco giusto, completo)
    ('sed102', ['Guerrieri', 'Zotta', 'Bovetti'], ['Guerrieri Filippo', 'Zotta', 'Carignani', 'Bovetti', 'Cremaschi Carlo'], 1),
    ('sed119', ['Cevolotto', 'Targetti', 'Moro', 'Taviani'],
           ['Laconi', 'Cevolotto', 'Targetti', 'Moro', 'Taviani'], 1),   # «presentato insieme con gli onorevoli...»: manca il presentatore
    ('sed186', ['Nobile', 'Porzio'], ['Nobile', 'Porzio', 'Di Gloria', 'Persico', 'Bernini', 'Veroni', 'Morelli Renato',
           'Gasparotto', 'Lami Starnuti', 'Corsi', 'Finocchiaro Aprile', 'Giannini', 'Massini'], 0),
    # --- verificati sull'immagine della pagina (ottobre 2026): elenchi interrotti dall'OCR ---
    # sed189 p18: «L'onorevole Arcaini ha fatto pervenire un emendamento anche a firma degli onorevoli Scoca, Cappi ed altri»:
    # manca il presentatore, l'elenco resta troncato
    ('sed189', ['Scoca', 'Cappi'], ['Arcaini', 'Scoca', 'Cappi'], 0, 18),
    # sed196 p5: «proposto dagli onorevoli Mastino Pietro, Lussu, Corsi, Schiavetti, Mannironi, De Vita, Mastino Ge-/sumino,
    # Abozzi, Simonini, Bruni»: l'OCR spezza «Ge-/sumino» e perde gli ultimi quattro nomi
    ('sed196', ['Lussu', 'Corsi', 'Schiavetti'], ['Mastino Pietro', 'Lussu', 'Corsi', 'Schiavetti', 'Mannironi', 'De Vita',
           'Mastino Gesumino', 'Abozzi', 'Simonini', 'Bruni'], 1, 5),
    # sed106 (Mattarella, Zerbi, Lazzati... 10 firme): dall'ottobre 2026 l'estrattore produce l'elenco completo da solo
    # (prima menzione in sed105 p25, formula «Abbiamo presentato ... firmato anche dagli onorevoli»)
    ('sed119', ['Vischioni', 'Merighi', 'Barbareschi', 'Carmagnola', 'Costantini', 'De Michelis'],
           ['Merlin Angelina', 'Barbareschi', 'Carmagnola', 'Vischioni', 'De Michelis', 'Costantini', 'Merighi'], 1),   # «Mariani» resta omonimo irrisolto
    ('sed188', ['Carpano Maglioli', 'Dugoni', 'Tega', 'Vernocchi', 'Priolo', 'Amadei', 'Jacometti'],
           ['Amadei', 'Jacometti', 'Carpano Maglioli', 'Dugoni', 'Tega', 'Priolo', 'Vernocchi', 'Fornara', 'Cacciatore', 'Mariani Enrico', 'Bonomelli'], 1),
    ('sed261', ['Rossi Paolo', 'Lucifero', 'Persico', 'Buffoni', 'Cosattini', 'Carpano Maglioli'],
           ['Rossi Paolo', 'Lucifero', 'Persico', 'Buffoni', 'Cosattini', 'Carpano Maglioli', 'Bianchi Bianca',
            'Morelli Renato', 'Lami Starnuti', 'Preti', 'Condorelli'], 1),
    ('sed301', ['Covelli'], ['Covelli', 'Benedettini'], 1),      # «ella ha firmato anche l'emendamento Covelli»
    ('sed318', ['Rescigno', 'Adonnino', 'Cimenti', 'Lizier', 'Micheli', 'Carbonari', 'Tozzi Condivi'],
           ['Adonnino', 'Coccia', 'Borsellino', 'De Maria', 'Angelucci', 'Carbonari', 'Cimenti', 'Tozzi Condivi',
            'Lizier', 'Cremaschi Carlo', 'Rescigno'], 1),        # «Micheli» apparteneva all'emendamento precedente
    # --- verificati sull'immagine della pagina (ottobre 2026, seconda tornata) ---
    # INCERTO: due stampe dello stesso emendamento. In sed104 p23 Martino Gaetano lo dice «presentato dagli
    # onorevoli Labriola, Della Seta, Lucifero, Corbino e da me»; in sed105 p8 il Presidente lo ristampa come
    # «degli onorevoli Martino Gaetano, Labriola, Della Seta, Caronia, Lucifero e [a capo di colonna] Corbino».
    # Si tiene l'elenco piu' lungo, che e' quello letto dalla presidenza; Caronia e' stampato, non dedotto.
    ('sed104', ['Martino', 'Labriola', 'Della Seta', 'Corbino', 'Lucifero'],
           ['Martino Gaetano', 'Labriola', 'Della Seta', 'Caronia', 'Lucifero', 'Corbino'], 1),
    ('sed120', ['Medi'], ['Medi', 'Federici Maria'], 1, 12),   # p12: «l'emendamento degli onorevoli Medi -e Federici Maria»
    # --- verifica dei pluri-firmati (blocchi 3-4): elenchi che proseguono oltre la colonna o la pagina ---
    ('sed122', ['Benvenuti', 'Belotti', 'Castelli Avolio', "Dominedo'", 'Cremaschi Carlo', 'Biagioni'],
           ['Clerici', 'Belotti', "Dominedo'", 'Benvenuti', 'Chatrian', 'Castelli Avolio', 'Biagioni', 'Cremaschi Carlo',
            'Tosi', 'Balduzzi', 'Mortati', 'Bonomi Paolo'], 1, 34),     # seconda formulazione dell'emendamento Clerici
    ('sed118', ['Montagnana Mario', 'Pajetta Gian Carlo', 'Foa'],
           ['Montagnana Mario', 'Foa', 'Pajetta Gian Carlo', 'Pesenti', 'Grieco', 'Laconi'], 1, 1),   # p1 col. destra -> p2 col. sinistra
    # INCERTO: la pagina stampa «Massa», che non e' un costituente; l'abbinamento approssimato dava Massola (PCI) in un
    # elenco liberale e qualunquista. Si attribuisce a Mazza Crescenzo (Uomo Qualunque), il cognome piu' vicino coerente
    # con i cofirmatari (Colitto, Perrone Capano, Condorelli, Rodino' Mario).
    ('sed322', ['Martino', 'Massola', 'Villabruna'],
           ['Martino Gaetano', 'Villabruna', 'Morelli Renato', 'Bonino', 'Colitto', 'Perrone Capano', 'Condorelli',
            'Colonna Di Paliano', 'Mazza', "Rodino' Di Miglione", 'Cifaldi'], 1, 17),
]

# Oggetto dei voti (in inglese). Quelli non elencati restano «to be labelled».
ETICHETTE = {
    ('sed072', 16): "Art. 1: 'a democratic Republic of workers'", ('sed075', 50): 'Art. 7: the Lateran Pacts',
    ('sed084', 4): 'Ravagnan-Laconi-Grieco amendment: right of asylum',
    ('sed084', 13): 'Della Seta amendment: definition of secret associations',
    ('sed086', 17): 'Amendment on the equality of religious confessions',
    ('sed088', 24): 'Ghidini amendment: only the judiciary may seize the press',
    ('sed102', 16): 'Orlando motion: leave schools out of the Constitution', ('sed102', 54): 'Zotta amendment: equality of spouses',
    ('sed104', 21): 'Rossi amendment: private schools', ('sed104', 26): 'Dossetti amendment: right to found private schools',
    ('sed105', 15): "Corbino-Marchesi amendment: private schools 'at no cost to the State'",
    ('sed129', 35): 'Cairo amendment: military service not compulsory', ('sed177', 17): 'Motion on currency exchange',
    ('sed178', 16): 'Nobile: deletion of a whole paragraph (regional powers)',
    ('sed180', 13): "Regional powers: 'agriculture and forests'", ('sed180', 16): "Regional powers: 'trade'",
    ('sed188', 15): 'Laconi amendment', ('sed229', 8): 'Piccioni-Moro motion on parliamentary democracy',
    ('sed260', 13): 'Deletion of Art. 72, para. 2 (abrogative referendum)',
    ('sed269', 18): 'Bozzi amendment, para. 2 (absolute majority)',
    ('sed270', 18): 'La Rocca amendment: composition of the Government',
    ('sed277', 7): 'Schiavetti amendment: temporary limits on voting rights for fascist responsibilities',
    ('sed296', 27): 'Benedettini motion (bill against fascist and monarchist activity)',
    ('sed301', 7): 'Gullo article: powers of the Minister of the Interior',
    ('sed311', 29): 'Lami Starnuti amendment: composition of the Senate',
    ('sed315', 25): 'Gullo proposal: delete para. 1 of draft Art. 128',
    ('sed332', 17): 'Nenni: commission of inquiry (not on the Constitution)',
    ('sed073', 20): 'Cosattini amendment: municipal pharmacies (bill, not on the Constitution)',
    ('sed187', 16): 'Scoccimarro-Veroni amendment: extraordinary property tax (bill, not on the Constitution)',
}
NON_COSTITUZIONE = {('sed177', 17), ('sed296', 27), ('sed332', 17), ('sed073', 20), ('sed187', 16)}   # chiave: (seduta, pagina), stabile se si aggiungono votazioni

# ---------- funzioni ----------
def trova(nome, data):
    """Cognome (+ eventuale nome) stampato -> id_dep, tra i costituenti in carica alla data."""
    parti = nome.split()
    for k in range(len(parti), 0, -1):
        c = nomi[nomi.cognome.str.lower() == ' '.join(parti[:k]).lower()]
        c = c[(c.inizio_mandato <= data) & (data <= c.fine_mandato)] if len(c) > 1 else c
        if len(c) > 1 and k < len(parti):
            c = c[c.nome.str.lower().str.startswith(parti[k].lower()[:4])]
        if len(c) == 1:
            return c.id_dep.iloc[0]
        if len(c) > 1:
            print(f'  ATTENZIONE: «{nome}» ambiguo ({", ".join(c.nome)}): escluso'); return None
    print(f'  ATTENZIONE: «{nome}» non trovato: escluso'); return None

def testi_compatibili(a, b):
    """Stesso criterio dell'estrattore: due testi diversi sono due emendamenti diversi."""
    import difflib, re, unicodedata
    if not isinstance(a, str) or not isinstance(b, str) or len(a) < 25 or len(b) < 25: return True
    n = lambda t: re.sub(r'[^a-z]', '', unicodedata.normalize('NFKD', t).encode('ascii', 'ignore').decode().lower())
    c, l = sorted((n(a), n(b)), key=len)
    return c in l or difflib.SequenceMatcher(None, c[:250], l[:250]).ratio() >= 0.5

def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return f'{k}/{n} = {100 * p:.1f}% (IC 95%: {100 * max(0, c - h):.1f}–{100 * min(1, c + h):.1f}%)'

# ---------- accuratezza sui campioni verificati ----------
import subprocess, sys
print(subprocess.run([sys.executable, os.path.join(QUI, 'tools', 'valuta_campioni.py'), EST], capture_output=True, text=True).stdout)

# ---------- decisioni prese a mano sul foglio CASI_APERTI.xlsx (tools/prepara_casi_aperti.py) ----------
DEC = {}
f_dec = os.path.join(QUI, 'CASI_APERTI.xlsx')
if os.path.exists(f_dec):
    for foglio, df in pd.read_excel(f_dec, sheet_name=None, dtype=str).items():
        if 'DECISIONE' in df:
            DEC[foglio] = df[df.DECISIONE.notna() & (df.DECISIONE.str.strip() != '')]
    print('Decisioni a mano lette:', {k: len(v) for k, v in DEC.items() if len(v)})
_sd = pd.read_csv(os.path.join(QUI, 'tools', 'sedute_date.csv')); sedute_date = dict(zip(_sd.iloc[:, 0], _sd.iloc[:, 1]))
NESSUNO = ('nessuno', 'non è un emendamento', 'nessun elenco completo stampato', 'giusto')
def id_da_etichetta(t, data=None):
    """«Cognome Nome» scelto dal menu -> id_dep (anche solo il cognome, se univoco alla data)."""
    t = str(t).strip()
    c = nomi[(nomi.cognome + ' ' + nomi.nome) == t]
    if len(c) == 1: return c.id_dep.iloc[0]
    x = trova(t, data or '1947-06-01')
    return x
def dec(foglio, chiave):
    d = DEC.get(foglio)
    if d is None or d.empty: return None
    x = d[d.chiave == chiave]
    return x.DECISIONE.iloc[0].strip() if len(x) else None
_m = dec('incerti', 'sed322_massa')
if _m:
    for k, voce in enumerate(FIRMATARI_CORRETTI):
        if voce[0] == 'sed322':
            lista = [x for x in voce[2] if x != 'Mazza'] + ([] if _m.startswith('nessuno') else [_m])
            FIRMATARI_CORRETTI[k] = (voce[0], voce[1], lista) + tuple(voce[3:])
_m = dec('incerti', 'sed104_martino')
if _m and 'senza Caronia' in _m:
    for k, voce in enumerate(FIRMATARI_CORRETTI):
        if voce[0] == 'sed104':
            FIRMATARI_CORRETTI[k] = (voce[0], voce[1], [x for x in voce[2] if x != 'Caronia']) + tuple(voce[3:])

# ---------- emendamenti ----------
E = pd.read_csv(os.path.join(EST, 'emendamenti.csv'))
L = pd.read_csv(os.path.join(EST, 'edgelist_emendamenti.csv'))
cogn = nomi.set_index('id_dep').cognome
E['cogn'] = E.firmatari.map(lambda f: {cogn.get(x, '') for x in str(f).split('|')})
via = [i for sed, cc in FALSI_POSITIVI for i in E[(E.prima_seduta == sed) & (E.cogn == set(cc))].id_emendamento]
E = E[~E.id_emendamento.isin(via)].copy(); L = L[~L.id_emendamento.isin(via)]
def presente(k, cset):
    """«Rossi Paolo» nella chiave vale per il cognome «Rossi»: la chiave puo' riportare il nome proprio."""
    return any(k == c or k.startswith(c + ' ') for c in cset)
corretti = set()
for sed, cc, lista, completo, *pag in FIRMATARI_CORRETTI:      # quinto elemento facoltativo: la pagina
    hit = E[(E.prima_seduta == sed) & E.cogn.map(lambda c: all(presente(k, c) for k in cc))]
    if pag: hit = hit[hit.pagina == pag[0]]
    if len(hit) > 1:   # piu' record contengono quei nomi: vale quello che ha esattamente quei nomi
        hit = hit[hit.cogn.map(lambda c: len(c) == len(cc))]
    if len(hit) != 1: print('  ATTENZIONE: correzione non applicata', sed, cc, len(hit)); continue
    i = hit.id_emendamento.iloc[0]; data = hit.data.iloc[0]
    ids = [x for x in (trova(n, data) for n in lista) if x]
    L = pd.concat([L[L.id_emendamento != i], pd.DataFrame({'id_emendamento': i, 'id_dep': ids})])
    E.loc[E.id_emendamento == i, ['firmatari', 'n_firmatari', 'completo', 'primo', 'presentatore_formula']] = ['|'.join(ids), len(ids), completo, ids[0], 0]
    corretti.add(i)
# firmatari aggiunti o emendamenti creati dalle decisioni del foglio
n_dec = 0
d_em = DEC.get('emendamenti_nomi', pd.DataFrame())
for r in d_em.itertuples():
    if str(r.DECISIONE).startswith(NESSUNO): continue
    sed, pag = r.seduta, int(float(r.pagina))
    if isinstance(r.chiave_emendamento, str) and r.chiave_emendamento:
        s0, p0, f0 = r.chiave_emendamento.split('|', 2)
        hit = E[(E.prima_seduta == s0) & (E.pagina == int(p0)) & E.firmatari.map(lambda f: set(f0.split('|')) <= set(str(f).split('|')))]
        if len(hit) != 1: print('  ATTENZIONE: decisione non applicata', r.caso, len(hit)); continue
        i = hit.id_emendamento.iloc[0]; x = id_da_etichetta(r.DECISIONE, hit.data.iloc[0])
        if not x or x in str(hit.firmatari.iloc[0]).split('|'): continue
        E.loc[E.id_emendamento == i, ['firmatari', 'n_firmatari']] = [hit.firmatari.iloc[0] + '|' + x, hit.n_firmatari.iloc[0] + 1]
        L = pd.concat([L, pd.DataFrame({'id_emendamento': [i], 'id_dep': [x]})]); corretti.add(i); n_dec += 1
    else:
        data = sedute_date.get(sed)
        x = id_da_etichetta(r.DECISIONE, data)
        if not x: continue
        i = int(E.id_emendamento.max()) + 1
        E = pd.concat([E, pd.DataFrame([dict(id_emendamento=i, firmatari=x, n_firmatari=1, completo=1, articolo_menzionato='',
                       prima_seduta=sed, data=data, pagina=pag, fonte='presentazione',
                       url_pdf=f'https://documenti.camera.it/_dati/costituente/lavori/Assemblea/{sed}/{sed}nc.pdf#page={pag}',
                       primo=x, testo='', tipo_emendamento='non determinato', presentatore_formula=1, cogn={cogn.get(x, '')})])], ignore_index=True)
        L = pd.concat([L, pd.DataFrame({'id_emendamento': [i], 'id_dep': [x]})]); n_dec += 1
for r in DEC.get('emendamenti_ed_altri', pd.DataFrame()).itertuples():
    if str(r.DECISIONE).startswith(NESSUNO): continue
    s0, p0, f0 = r.chiave.split('|', 2)
    hit = E[(E.prima_seduta == s0) & (E.pagina == int(p0)) & E.firmatari.map(lambda f: set(f0.split('|')) <= set(str(f).split('|')))]
    if len(hit) > 1: hit = hit[hit.firmatari == f0] if (hit.firmatari == f0).sum() == 1 else hit[hit.completo == 0]
    if len(hit) != 1: print('  ATTENZIONE: decisione non applicata', r.caso, len(hit)); continue
    i = hit.id_emendamento.iloc[0]; fs = str(hit.firmatari.iloc[0]).split('|')
    if str(r.DECISIONE).startswith('elenco già completo'):      # «ed altri» non stampato: l'elenco e' completo cosi'
        E.loc[E.id_emendamento == hit.id_emendamento.iloc[0], 'completo'] = 1; n_dec += 1; continue
    voci = [n.strip() for n in str(r.DECISIONE).split(';') if n.strip()]
    tronco = any(v.lower() in ('ed altri', 'e altri') for v in voci)      # nomi aggiunti, ma l'elenco stampato resta troncato
    nuovi = [x for x in (id_da_etichetta(n, hit.data.iloc[0]) for n in voci if n.lower() not in ('ed altri', 'e altri')) if x and x not in fs]
    E.loc[E.id_emendamento == i, ['firmatari', 'n_firmatari', 'completo']] = ['|'.join(fs + nuovi), len(fs) + len(nuovi), 0 if tronco else 1]
    L = pd.concat([L, pd.DataFrame({'id_emendamento': i, 'id_dep': nuovi})]); corretti.add(i); n_dec += 1
if DEC: print('Decisioni a mano applicate agli emendamenti:', n_dec)
print('Correzioni manuali: rimossi', len(via), 'falsi positivi')
# dopo le correzioni due record possono avere lo stesso elenco (stesso emendamento stampato due volte,
# la prima con l'elenco troncato): si tiene il primo, come fa l'estrattore per le riletture (±3 sedute).
# Vale solo per i gruppi che contengono un record corretto a mano: gli altri record con gli stessi
# firmatari sono emendamenti distinti, tenuti separati dall'estrattore perche' i testi sono diversi.
E['snum'] = E.prima_seduta.str[3:].astype(int)
doppi = []
for f, g in E.sort_values(['snum', 'pagina']).groupby(E.firmatari.map(lambda x: '|'.join(sorted(str(x).split('|'))))):
    tenuto = None
    if not set(g.id_emendamento) & corretti: continue
    for r in g.itertuples():
        if tenuto is not None and r.snum - tenuto[0] <= 3 and testi_compatibili(tenuto[1], r.testo): doppi.append(r.id_emendamento)
        else: tenuto = (r.snum, r.testo)
E = E[~E.id_emendamento.isin(doppi)].drop(columns='snum'); L = L[~L.id_emendamento.isin(doppi)]
print('Correzioni manuali: uniti', len(doppi), 'doppioni nati dalle correzioni')
# ---------- direzione del legame: presentatore e firmatari ----------
E['primo'] = E.primo.fillna('').astype(str)
E['id_presentatore'] = [p if p and p in str(f).split('|') else '' for p, f in zip(E.primo, E.firmatari)]
E['presentatore_fonte'] = ['non identificato' if not p else 'firma singola' if n == 1 else 'formula' if fm == 1 else 'primo dell\'elenco'
                           for p, n, fm in zip(E.id_presentatore, E.n_firmatari, E.presentatore_formula.fillna(0))]
print('Presentatore:', E.presentatore_fonte.value_counts().to_dict())
# esito (tools/esito_emendamenti.py): si cerca solo dove la formula e' univoca; il resto e' «non determinato»
_es = pd.read_csv(os.path.join(EST, 'esiti.csv')).set_index('id_emendamento').esito
E['esito'] = E.id_emendamento.map(_es).fillna('non determinato')
print('Esito:', E.esito.value_counts().to_dict())
_ca = pd.read_csv(os.path.join(EST, 'controllo_articolo.csv'), dtype=str).fillna('')
_ca['id_emendamento'] = _ca.id_emendamento.astype(int)
E['articolo_in_discussione'] = E.id_emendamento.map(_ca.set_index('id_emendamento').articolo_in_discussione).fillna('')
_tv = pd.read_csv(os.path.join(EST, 'articoli_tavola.csv'), dtype=str).fillna('')
_tv['id_emendamento'] = _tv.id_emendamento.astype(int); _tv = _tv.set_index('id_emendamento')
E['materia'] = E.id_emendamento.map(_tv.materia).fillna('')
E['articolo_costituzione'] = E.id_emendamento.map(_tv.articolo_costituzione).fillna('')
E['controllo_data'] = E.id_emendamento.map(_tv.tavola).fillna('')
# qualita' dell'abbinamento di ogni arco (punto 18): il criterio migliore con cui quel nome e' stato riconosciuto in una
# delle menzioni dell'emendamento; gli elenchi corretti a mano sono stati letti sull'immagine
RANGO = ['esatto', 'esatto+partito', 'prefisso', 'ambiguo+cofirme', 'ambiguo+seduta', 'approssimato', 'approssimato+partito']
_mt = pd.read_csv(os.path.join(EST, 'menzioni_tutte.csv'), usecols=['id_menzione', 'id_emendamento']).dropna()
_mn = pd.read_csv(os.path.join(EST, 'menzioni_nomi.csv'), usecols=['id_menzione', 'id_dep', 'abbinamento']).merge(_mt, on='id_menzione')
_mn = _mn[_mn.abbinamento.isin(RANGO)].assign(r=lambda d: d.abbinamento.map(RANGO.index))
_best = _mn.sort_values('r').drop_duplicates(['id_emendamento', 'id_dep']).set_index(['id_emendamento', 'id_dep']).abbinamento
L['abbinamento'] = ['correzione manuale' if e in corretti else _best.get((e, d), 'decisione manuale') for e, d in zip(L.id_emendamento, L.id_dep)]
CONSERVATIVO = {'esatto', 'esatto+partito', 'correzione manuale'}
print('Abbinamento degli archi di co-firma:', L.abbinamento.value_counts().to_dict())
E['id_emendamento'] = 'a' + E.id_emendamento.astype(str)
L['id_emendamento'] = 'a' + L.id_emendamento.astype(str)
L = L.drop_duplicates().sort_values(['id_emendamento', 'id_dep'])
pres = E.set_index('id_emendamento').id_presentatore
L['ruolo'] = ['presentatore' if pres.get(e, '') == d else 'firmatario' for e, d in zip(L.id_emendamento, L.id_dep)]

E_it = E.rename(columns={'firmatari': 'firmatari_id'})[['id_emendamento', 'firmatari_id', 'n_firmatari', 'completo',
        'articolo_menzionato', 'articolo_in_discussione', 'materia', 'articolo_costituzione', 'controllo_data', 'prima_seduta', 'data', 'pagina', 'fonte', 'url_pdf', 'id_presentatore', 'presentatore_fonte',
        'tipo_emendamento', 'esito', 'testo']]
E_it.to_csv(os.path.join(IT, 'emendamenti_nodi.csv'), index=False)
# gruppo parlamentare alla data della firma (punto 11), dalle adesioni della Camera
sys.path.insert(0, os.path.join(QUI, 'tools'))
if os.path.exists(os.path.join(QUI, 'fonti', 'camera_adesioni_gruppi.csv')):
    from gruppi_periodi import gruppo_alla_data, P as _GP
    _GP.to_csv(os.path.join(IT, 'gruppi_periodi.csv'), index=False)
    _GP.rename(columns={'id_dep': 'id_member', 'gruppo': 'group', 'inizio': 'start', 'fine': 'end', 'motivo_termine': 'end_reason'}).to_csv(os.path.join(EN, 'group_spells.csv'), index=False)
    _dt = E.set_index('id_emendamento').data
    L['gruppo_alla_data'] = [gruppo_alla_data(d, _dt.get(e)) for d, e in zip(L.id_dep, L.id_emendamento)]
    _gf = pd.read_csv(os.path.join(IT, 'costituenti_nodi.csv')).set_index('id_dep').gruppo_finale
    print('Firme con gruppo alla data diverso dal gruppo finale:', int((L.gruppo_alla_data != L.id_dep.map(_gf)).sum()), 'su', len(L))
else:
    L['gruppo_alla_data'] = ''
L[['id_dep', 'id_emendamento', 'ruolo', 'abbinamento', 'gruppo_alla_data']].to_csv(os.path.join(IT, 'edgelist_emendamenti.csv'), index=False)
L[L.abbinamento.isin(CONSERVATIVO)][['id_dep', 'id_emendamento', 'ruolo', 'abbinamento', 'gruppo_alla_data']].to_csv(os.path.join(IT, 'edgelist_emendamenti_conservativa.csv'), index=False)
E_en = E_it.drop(columns='firmatari_id').rename(columns={
    'id_emendamento': 'id_amendment', 'n_firmatari': 'n_signatories', 'completo': 'complete',
    'articolo_menzionato': 'article_mentioned', 'articolo_in_discussione': 'article_under_discussion', 'materia': 'subject_title',
    'articolo_costituzione': 'constitution_article', 'controllo_data': 'date_check', 'prima_seduta': 'sitting', 'data': 'date', 'pagina': 'pdf_page', 'fonte': 'source'})
E_en['source'] = E_en.source.map({'firma': 'signature block', 'presentazione': 'presentation formula'})
E_en['id_proposer'] = E_en.id_presentatore
E_en['proposer_source'] = E_en.presentatore_fonte.map({'formula': 'formula', 'firma singola': 'single signatory',
                                                      "primo dell'elenco": 'first in list', 'non identificato': 'not identified'})
E_en['amendment_type'] = E_en.tipo_emendamento.map({'sostituire': 'replace', 'sopprimere': 'delete', 'aggiungere': 'add',
                                                    'inserire': 'insert', 'non determinato': 'undetermined'})
E_en['date_check'] = E_en.date_check.map({'data coerente': 'date consistent', 'unico articolo discusso quel giorno': 'only article discussed that day',
    'giorno senza articoli del progetto': 'day without draft articles', 'data discordante': 'date inconsistent', 'non determinato': 'undetermined', '': ''})
E_en['subject_title'] = E_en.subject_title.str.replace('Disposizioni generali', 'General provisions').str.replace('Parte', 'Part').str.replace('Titolo', 'Title').str.replace('Sez.', 'Sect.')
E_en['outcome'] = E_en.esito.map({'approvato': 'approved', 'respinto': 'rejected', 'ritirato': 'withdrawn',
                                  'decaduto (assente)': 'lapsed (proposer absent)', 'assorbito': 'absorbed', 'non determinato': 'undetermined'})
E_en = E_en.rename(columns={'testo': 'text_it'})
E_en[['id_amendment', 'n_signatories', 'complete', 'source', 'sitting', 'date', 'pdf_page', 'article_mentioned', 'article_under_discussion', 'subject_title', 'constitution_article', 'date_check', 'url_pdf',
      'id_proposer', 'proposer_source', 'amendment_type', 'outcome', 'text_it']] \
    .to_csv(os.path.join(EN, 'amendments_nodes.csv'), index=False)
MATCH_EN = {'esatto': 'exact', 'esatto+partito': 'exact+party', 'prefisso': 'prefix', 'ambiguo+cofirme': 'namesake+cosignatures',
            'ambiguo+seduta': 'namesake+sitting', 'approssimato': 'approximate', 'approssimato+partito': 'approximate+party',
            'correzione manuale': 'manual correction', 'decisione manuale': 'manual decision', 'fascia alfabetica': 'alphabetical band',
            'omonimo risolto': 'namesake resolved', 'frammento': 'fragment'}
_Len = L.rename(columns={'gruppo_alla_data': 'group_at_date'}).assign(role=L.ruolo.map({'presentatore': 'proposer', 'firmatario': 'signatory'}), matching=L.abbinamento.map(MATCH_EN)) \
    .rename(columns={'id_dep': 'id_member', 'id_emendamento': 'id_amendment'})
_Len[['id_member', 'id_amendment', 'role', 'matching', 'group_at_date']].to_csv(os.path.join(EN, 'edgelist_amendments.csv'), index=False)
_Len[L.abbinamento.isin(CONSERVATIVO).values][['id_member', 'id_amendment', 'role', 'matching']].to_csv(os.path.join(EN, 'edgelist_amendments_conservative.csv'), index=False)

# ---------- menzioni nei discorsi (tools/estrai_menzioni_discorso.py) ----------
f_md = os.path.join(EST, 'menzioni_discorso.csv')
if os.path.exists(f_md):
    MD = pd.read_csv(f_md, dtype=str).fillna('')
    MD['url_pdf'] = [f'https://documenti.camera.it/_dati/costituente/lavori/Assemblea/{s}/{s}nc.pdf#page={p}' for s, p in zip(MD.seduta, MD.pagina)]
    col = ['seduta', 'data', 'pagina', 'url_pdf', 'id_parlante', 'parlante_stampato', 'ruolo_parlante', 'id_menzionato',
           'forma_stampata', 'abbinamento', 'tipo_menzione', 'contesto']
    MD[col].to_csv(os.path.join(IT, 'menzioni_discorso.csv'), index=False)
    MD_en = MD[col].rename(columns={'seduta': 'sitting', 'data': 'date', 'pagina': 'pdf_page', 'id_parlante': 'id_speaker',
        'parlante_stampato': 'speaker_printed', 'ruolo_parlante': 'speaker_role', 'id_menzionato': 'id_mentioned',
        'forma_stampata': 'printed_form', 'abbinamento': 'matching', 'tipo_menzione': 'mention_type', 'contesto': 'context_it'})
    MD_en['mention_type'] = MD_en.mention_type.map({'su un emendamento': 'on an amendment', 'atto di parola': 'speech act',
                                                    'didascalia': 'stage direction', 'altro': 'other'})
    MD_en['matching'] = MD_en.matching.str.replace('esatto', 'exact').str.replace('approssimato', 'approximate') \
        .str.replace('prefisso', 'prefix').str.replace('seduta', 'sitting').str.replace('ambiguo', 'ambiguous').str.replace('non trovato', 'not found')
    MD_en.to_csv(os.path.join(EN, 'speech_mentions.csv'), index=False)
    print('Menzioni nei discorsi:', len(MD), '| con parlante e menzionato:', int(((MD.id_parlante != '') & (MD.id_menzionato != '')).sum()))

# ---------- strato multiplex: altri atti co-firmati (interrogazioni, interpellanze, ordini del giorno, mozioni,
# richieste di votazione), riconosciuti dall'estrattore e tenuti fuori dagli emendamenti ----------
A = pd.read_csv(os.path.join(EST, 'altri_atti.csv'))
A[['id_atto', 'tipo_atto', 'seduta', 'data', 'pagina', 'fonte', 'n_firmatari', 'testo_stampato']].to_csv(os.path.join(IT, 'altri_atti_nodi.csv'), index=False)
LA = A.assign(id_dep=A.firmatari.str.split('|')).explode('id_dep')[['id_dep', 'id_atto']]
LA.to_csv(os.path.join(IT, 'edgelist_altri_atti.csv'), index=False)
TIPI = {'interrogazione': 'question', 'interpellanza': 'interpellation', 'ordine del giorno': 'order of the day',
        'mozione': 'motion', 'richiesta di votazione': 'vote request'}
A.assign(act_type=A.tipo_atto.map(TIPI), source=A.fonte.map({'firma': 'signature block', 'presentazione': 'presentation formula'})) \
 .rename(columns={'id_atto': 'id_act', 'seduta': 'sitting', 'data': 'date', 'pagina': 'pdf_page', 'n_firmatari': 'n_signatories', 'testo_stampato': 'printed_names'}) \
 [['id_act', 'act_type', 'sitting', 'date', 'pdf_page', 'source', 'n_signatories', 'printed_names']].to_csv(os.path.join(EN, 'other_acts_nodes.csv'), index=False)
LA.rename(columns={'id_dep': 'id_member', 'id_atto': 'id_act'}).to_csv(os.path.join(EN, 'edgelist_other_acts.csv'), index=False)
print('Altri atti:', len(A), A.tipo_atto.value_counts().to_dict(), '| legami:', len(LA))

# ---------- voti ----------
Vt = pd.read_csv(os.path.join(EST, 'voti.csv'))
Ev = pd.read_csv(os.path.join(EST, 'edgelist_voti.csv'))
n_dv = 0
import re as _re
_vid = {(a, int(b)): i for i, a, b in zip(Vt.id_voto, Vt.seduta, Vt.pagina)}
def vid_di(r):
    """numero della votazione dalla seduta e dalla pagina del collegamento: i numeri cambiano se si aggiungono sedute"""
    m_ = _re.search(r'/(sed\d+)/[^#]*#page=(\d+)', str(r.link_pagina))
    return _vid.get((m_.group(1), int(m_.group(2)))) if m_ else int(r.id_voto[1:])
for r in DEC.get('voti_nomi', pd.DataFrame()).itertuples():
    if str(r.DECISIONE).startswith(NESSUNO): continue
    vid = vid_di(r)
    if vid is None: print('  ATTENZIONE: votazione non trovata', r.caso); continue
    x = id_da_etichetta(r.DECISIONE, Vt.set_index('id_voto').data.get(vid))
    if x and not ((Ev.id_voto == vid) & (Ev.id_dep == x)).any() and r.voto in ('sì', 'no', 'astenuto'):
        Ev = pd.concat([Ev, pd.DataFrame([dict(id_voto=vid, id_dep=x, voto=r.voto)])], ignore_index=True); n_dv += 1
for r in DEC.get('voti_approssimati', pd.DataFrame()).itertuples():
    d = str(r.DECISIONE).strip()
    if d.startswith('giusto'): continue
    vid = vid_di(r); vecchio = r.chiave.split('|')[-1]
    if vid is None: continue
    Ev = Ev[~((Ev.id_voto == vid) & (Ev.id_dep == vecchio))]; n_dv += 1
    if not d.startswith('sbagliato'):
        x = id_da_etichetta(d, Vt.set_index('id_voto').data.get(vid))
        if x and r.voto in ('sì', 'no', 'astenuto'): Ev = pd.concat([Ev, pd.DataFrame([dict(id_voto=vid, id_dep=x, voto=r.voto)])], ignore_index=True)
if DEC: print('Decisioni a mano applicate ai voti:', n_dv)
_k = list(zip(Vt.seduta, Vt.pagina))
Vt['label_en'] = [ETICHETTE.get(k, 'to be labelled: see source page') for k in _k]
Vt['on_constitution'] = [int(k not in NON_COSTITUZIONE) for k in _k]
Vt['id_voto'] = 'v' + Vt.id_voto.astype(str); Ev['id_voto'] = 'v' + Ev.id_voto.astype(str)
Vt = Vt.rename(columns={'oggetto': 'excerpt_it'})
Vt.drop(columns=[]).to_csv(os.path.join(IT, 'voti_nodi.csv'), index=False)
_vn = pd.read_csv(os.path.join(EST, 'voti_nominali.csv'), keep_default_na=False)
_vn = _vn[_vn.id_dep != ''].assign(id_voto=lambda d: 'v' + d.id_voto.astype(str))
_RV = ['correzione manuale', 'esatto', 'omonimo risolto', 'fascia alfabetica', 'approssimato']
_vn = _vn[_vn.abbinamento.isin(_RV)].assign(r=lambda d: d.abbinamento.map(_RV.index)).sort_values('r').drop_duplicates(['id_voto', 'id_dep'])
_bv = _vn.set_index(['id_voto', 'id_dep']).abbinamento
Ev['abbinamento'] = [_bv.get((v, d), 'decisione manuale') for v, d in zip(Ev.id_voto, Ev.id_dep)]
print('Abbinamento degli archi di voto:', Ev.abbinamento.value_counts().to_dict())
_dv = Vt.set_index('id_voto').data
Ev['gruppo_alla_data'] = [gruppo_alla_data(d, _dv.get(v)) for d, v in zip(Ev.id_dep, Ev.id_voto)] if 'gruppo_alla_data' in globals() else ''
Ev[['id_dep', 'id_voto', 'voto', 'abbinamento', 'gruppo_alla_data']].to_csv(os.path.join(IT, 'edgelist_voti.csv'), index=False)
Ev[Ev.abbinamento.isin({'esatto', 'correzione manuale'})][['id_dep', 'id_voto', 'voto', 'abbinamento', 'gruppo_alla_data']].to_csv(os.path.join(IT, 'edgelist_voti_conservativa.csv'), index=False)
ctrl = lambda c: 'ok' if c == 'ok' else ('no official totals' if c == 'senza totali' else
       'void: quorum not reached, totals not announced' if str(c).startswith('votazione nulla') else
       ('verified: printed list differs from announced totals' if str(c).startswith('verificato') else 'to check'))
V_en = Vt.rename(columns={'id_voto': 'id_vote', 'seduta': 'sitting', 'data': 'date', 'pagina': 'pdf_page',
        'si_ufficiali': 'yes_official', 'si_abbinati': 'yes_matched', 'no_ufficiali': 'no_official', 'no_abbinati': 'no_matched',
        'astenuti_ufficiali': 'abstain_official', 'astenuti_abbinati': 'abstain_matched', 'congedo_abbinati': 'leave_matched',
        'controllo': 'check', 'numero_legale_mancato': 'quorum_failed'})
V_en['check'] = V_en.check.map(ctrl)
V_en[['id_vote', 'sitting', 'date', 'pdf_page', 'label_en', 'on_constitution', 'yes_official', 'yes_matched', 'no_official',
      'no_matched', 'abstain_matched', 'leave_matched', 'quorum_failed', 'check', 'excerpt_it', 'url_pdf']].to_csv(os.path.join(EN, 'votes_nodes.csv'), index=False)
_Ven = Ev.rename(columns={'gruppo_alla_data': 'group_at_date'}).assign(vote=Ev.voto.map({'sì': 'yes', 'no': 'no', 'astenuto': 'abstain'}), matching=Ev.abbinamento.map(MATCH_EN)) \
  .rename(columns={'id_dep': 'id_member', 'id_voto': 'id_vote'})
_Ven[['id_member', 'id_vote', 'vote', 'matching', 'group_at_date']].to_csv(os.path.join(EN, 'edgelist_votes.csv'), index=False)
_Ven[Ev.abbinamento.isin({'esatto', 'correzione manuale'}).values][['id_member', 'id_vote', 'vote', 'matching']].to_csv(os.path.join(EN, 'edgelist_votes_conservative.csv'), index=False)

print('\nEmendamenti:', len(E), '| con 2+ firmatari:', int((E.n_firmatari >= 2).sum()), '| legami:', len(L))
print('Voti:', len(Vt), '| controllo:', Vt.controllo.str.split(':').str[0].value_counts().to_dict(),
      '| da etichettare:', int((Vt.label_en.str.startswith('to be')).sum()), '| legami:', len(Ev))
# variabili dei costituenti ricavate dagli altri file (commissione, presenza agli appelli)
print(subprocess.run([sys.executable, os.path.join(QUI, 'tools', 'arricchisci_costituenti.py')], capture_output=True, text=True).stdout)
print('\nFatto. File scritti in', DS)
