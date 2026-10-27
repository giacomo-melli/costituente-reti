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
]

# Oggetto dei voti (in inglese). Quelli non elencati restano «to be labelled».
ETICHETTE = {
    1: "Art. 1: 'a democratic Republic of workers'", 2: 'Art. 7: the Lateran Pacts',
    3: 'Ravagnan-Laconi-Grieco amendment: right of asylum',
    4: 'Della Seta amendment: definition of secret associations',
    5: 'Amendment on the equality of religious confessions',
    6: 'Ghidini amendment: only the judiciary may seize the press',
    7: 'Orlando motion: leave schools out of the Constitution', 8: 'Zotta amendment: equality of spouses',
    9: 'Rossi amendment: private schools', 10: 'Dossetti amendment: right to found private schools',
    11: "Corbino-Marchesi amendment: private schools 'at no cost to the State'",
    12: 'Cairo amendment: military service not compulsory', 13: 'Motion on currency exchange',
    14: 'Nobile: deletion of a whole paragraph (regional powers)',
    15: "Regional powers: 'agriculture and forests'", 16: "Regional powers: 'trade'",
    17: 'Laconi amendment', 18: 'Piccioni-Moro motion on parliamentary democracy',
    19: 'Deletion of Art. 72, para. 2 (abrogative referendum)',
    20: 'Bozzi amendment, para. 2 (absolute majority)',
    21: 'La Rocca amendment: composition of the Government',
    22: 'Schiavetti amendment: temporary limits on voting rights for fascist responsibilities',
    23: 'Benedettini motion (bill against fascist and monarchist activity)',
    24: 'Gullo article: powers of the Minister of the Interior',
    25: 'Lami Starnuti amendment: composition of the Senate',
    26: 'Gullo proposal: delete para. 1 of draft Art. 128',
    27: 'Nenni: commission of inquiry (not on the Constitution)',
}
NON_COSTITUZIONE = {13, 23, 27}

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
E['id_emendamento'] = 'a' + E.id_emendamento.astype(str)
L['id_emendamento'] = 'a' + L.id_emendamento.astype(str)
L = L.drop_duplicates().sort_values(['id_emendamento', 'id_dep'])
pres = E.set_index('id_emendamento').id_presentatore
L['ruolo'] = ['presentatore' if pres.get(e, '') == d else 'firmatario' for e, d in zip(L.id_emendamento, L.id_dep)]

E_it = E.rename(columns={'firmatari': 'firmatari_id'})[['id_emendamento', 'firmatari_id', 'n_firmatari', 'completo',
        'articolo_menzionato', 'prima_seduta', 'data', 'pagina', 'fonte', 'url_pdf', 'id_presentatore', 'presentatore_fonte',
        'tipo_emendamento', 'testo']]
E_it.to_csv(os.path.join(IT, 'emendamenti_nodi.csv'), index=False)
L[['id_dep', 'id_emendamento', 'ruolo']].to_csv(os.path.join(IT, 'edgelist_emendamenti.csv'), index=False)
E_en = E_it.drop(columns='firmatari_id').rename(columns={
    'id_emendamento': 'id_amendment', 'n_firmatari': 'n_signatories', 'completo': 'complete',
    'articolo_menzionato': 'article_mentioned', 'prima_seduta': 'sitting', 'data': 'date', 'pagina': 'pdf_page', 'fonte': 'source'})
E_en['source'] = E_en.source.map({'firma': 'signature block', 'presentazione': 'presentation formula'})
E_en['id_proposer'] = E_en.id_presentatore
E_en['proposer_source'] = E_en.presentatore_fonte.map({'formula': 'formula', 'firma singola': 'single signatory',
                                                      "primo dell'elenco": 'first in list', 'non identificato': 'not identified'})
E_en['amendment_type'] = E_en.tipo_emendamento.map({'sostituire': 'replace', 'sopprimere': 'delete', 'aggiungere': 'add',
                                                    'inserire': 'insert', 'non determinato': 'undetermined'})
E_en = E_en.rename(columns={'testo': 'text_it'})
E_en[['id_amendment', 'n_signatories', 'complete', 'source', 'sitting', 'date', 'pdf_page', 'article_mentioned', 'url_pdf',
      'id_proposer', 'proposer_source', 'amendment_type', 'text_it']] \
    .to_csv(os.path.join(EN, 'amendments_nodes.csv'), index=False)
L.assign(role=L.ruolo.map({'presentatore': 'proposer', 'firmatario': 'signatory'})) \
    .rename(columns={'id_dep': 'id_member', 'id_emendamento': 'id_amendment'})[['id_member', 'id_amendment', 'role']] \
    .to_csv(os.path.join(EN, 'edgelist_amendments.csv'), index=False)

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

# ---------- voti ----------
Vt = pd.read_csv(os.path.join(EST, 'voti.csv'))
Ev = pd.read_csv(os.path.join(EST, 'edgelist_voti.csv'))
Vt['label_en'] = Vt.id_voto.map(ETICHETTE).fillna('to be labelled: see source page')
Vt['on_constitution'] = (~Vt.id_voto.isin(NON_COSTITUZIONE)).astype(int)
Vt['id_voto'] = 'v' + Vt.id_voto.astype(str); Ev['id_voto'] = 'v' + Ev.id_voto.astype(str)
Vt = Vt.rename(columns={'oggetto': 'excerpt_it'})
Vt.drop(columns=[]).to_csv(os.path.join(IT, 'voti_nodi.csv'), index=False)
Ev[['id_dep', 'id_voto', 'voto']].to_csv(os.path.join(IT, 'edgelist_voti.csv'), index=False)
ctrl = lambda c: 'ok' if c == 'ok' else ('no official totals' if c == 'senza totali' else
       ('verified: printed list differs from announced totals' if str(c).startswith('verificato') else 'to check'))
V_en = Vt.rename(columns={'id_voto': 'id_vote', 'seduta': 'sitting', 'data': 'date', 'pagina': 'pdf_page',
        'si_ufficiali': 'yes_official', 'si_abbinati': 'yes_matched', 'no_ufficiali': 'no_official', 'no_abbinati': 'no_matched',
        'astenuti_ufficiali': 'abstain_official', 'astenuti_abbinati': 'abstain_matched', 'congedo_abbinati': 'leave_matched',
        'controllo': 'check'})
V_en['check'] = V_en.check.map(ctrl)
V_en[['id_vote', 'sitting', 'date', 'pdf_page', 'label_en', 'on_constitution', 'yes_official', 'yes_matched', 'no_official',
      'no_matched', 'abstain_matched', 'leave_matched', 'check', 'excerpt_it', 'url_pdf']].to_csv(os.path.join(EN, 'votes_nodes.csv'), index=False)
Ev.assign(vote=Ev.voto.map({'sì': 'yes', 'no': 'no', 'astenuto': 'abstain'})) \
  .rename(columns={'id_dep': 'id_member', 'id_voto': 'id_vote'})[['id_member', 'id_vote', 'vote']] \
  .to_csv(os.path.join(EN, 'edgelist_votes.csv'), index=False)

print('\nEmendamenti:', len(E), '| con 2+ firmatari:', int((E.n_firmatari >= 2).sum()), '| legami:', len(L))
print('Voti:', len(Vt), '| controllo:', Vt.controllo.str.split(':').str[0].value_counts().to_dict(),
      '| da etichettare:', int((Vt.label_en.str.startswith('to be')).sum()), '| legami:', len(Ev))
print('\nFatto. File scritti in', DS)
