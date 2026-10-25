"""Estrae dai testi OCR i voti per appello nominale: chi ha risposto sì, no, chi si è astenuto
e chi era in congedo. Ogni voto è controllato con i totali ufficiali annunciati dal Presidente
(«Hanno risposto sì ... 350»).
Uso: python3 estrai_voti.py CARTELLA_02_ocr [cartella_output]"""
import re, os, sys, glob, unicodedata, difflib
import pandas as pd

D = sys.argv[1] if len(sys.argv) > 1 else '.'
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(D, 'estrazione')
TXT = os.path.join(D, 'testi_colonne')
nomi = pd.read_csv(os.path.join(D, 'strumenti', 'costituenti_nomi.csv'))
date = dict(pd.read_csv(os.path.join(D, 'strumenti', 'sedute_date.csv')).values)

# ---------- abbinamento dei nomi (come in estrai_emendamenti.py) ----------
def norm(s):
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().upper()
    return re.sub(r"\s+", ' ', re.sub(r"[^A-Z ]", ' ', s)).strip()
ALIAS = {'SILONE': 'TRANQUILLI', 'DE UNTERRICHTER JERVOLINO': 'JERVOLINO MARIA', 'DE UNTERRICHTER': 'JERVOLINO MARIA'}
nomi['k_cogn'] = nomi.cognome.map(lambda x: norm(x).replace(' ', ''))
nomi['k_nome'] = nomi.nome.map(lambda x: norm(x).replace(' ', ''))
IDX = {}
for r in nomi.itertuples():
    IDX.setdefault(r.k_cogn, []).append(r)
KEYS = list(IDX)
NOMI_PROPRI = {t for x in nomi.nome for t in norm(x).split()}

def match(name, data):
    n = norm(name)
    for a, b in ALIAS.items():
        n = re.sub(r'\b' + a + r'\b', b, n)
    if n == 'JERVOLINO':          # nei resoconti Maria è stampata come «De Unterrichter»: «Jervolino» è Angelo Raffaele
        n = 'JERVOLINO ANGELO'
    toks = n.split()
    if not toks or len(''.join(toks)) < 3:
        return None, 'scartato'
    cands, how, rest = [], '', ''
    for k in range(len(toks), 0, -1):
        key = ''.join(toks[:k])
        if key in IDX:
            cands, how, rest = IDX[key], 'esatto', ''.join(toks[k:]); break
    if not cands:
        for k in range(len(toks), 0, -1):
            key = ''.join(toks[:k])
            close = difflib.get_close_matches(key, KEYS, n=1, cutoff=0.8)
            if close:
                cands, how, rest = IDX[close[0]], 'approssimato', ''.join(toks[k:]); break
    if data and len(cands) > 1:
        cands = [c for c in cands if c.inizio_mandato <= data <= c.fine_mandato] or cands
    if len(cands) > 1 and rest:
        cands = [c for c in cands if rest[:4] in c.k_nome] or cands
    if not cands:
        return None, 'non trovato'
    if len(cands) > 1:
        return None, 'ambiguo'
    return cands[0], how

def scomponi(piece, data):
    """Un pezzo può contenere più nomi fusi dall'OCR («Villani Zanardi»): li separa cercando,
    da sinistra, il cognome più lungo che esiste tra i costituenti, seguito dal nome proprio se c'è."""
    n = norm(piece).replace('DE UNTERRICHTER JERVOLINO', 'JERVOLINO MARIA').replace('DE UNTERRICHTER', 'JERVOLINO MARIA').replace('SILONE', 'TRANQUILLI').replace('GALLICO SPANO NADIA', 'GALLICO NADIA').replace('SPANO NADIA', 'GALLICO NADIA').replace('GURBI', 'CORBI').replace('GUIDI CINGOLANI ANGELA', 'GUIDI ANGELA').replace('CINGOLANI ANGELA', 'GUIDI ANGELA')   # cognomi da sposate (forma completa per prima, per non raddoppiare); GURBI: OCR di «Corbi» in sed180
    toks = [t for t in n.split() if t]
    toks = [('C' + t[1:]) if (t.startswith('G') and t not in IDX and t not in NOMI_PROPRI and
             (('C' + t[1:]) in IDX or ('C' + t[1:]) in NOMI_PROPRI)) else t for t in toks]   # OCR: «Gairo» per «Cairo»
    j = 0                                                       # «D' Amico» -> «DAMICO» (apostrofo staccato dall'OCR)
    while j < len(toks) - 1:
        if len(toks[j]) == 1 and toks[j] in 'DL': toks[j:j + 2] = [toks[j] + toks[j + 1]]
        j += 1
    toks = ['IOTTI' if t in ('JOTTI', 'TOTTI') else t for t in toks]
    toks = [t[1:] if (t.startswith('G') and len(t) > 4 and t not in IDX and t not in NOMI_PROPRI and
                      (t[1:] in IDX or t[1:] in NOMI_PROPRI)) else t for t in toks]     # «GCARLO», «GCASSIANI»: G spuria
    out, i = [], 0
    while i < len(toks):
        found = None
        for k in (3, 2, 1):
            key = ''.join(toks[i:i + k])
            if i + k <= len(toks) and key in IDX:
                found = (k, IDX[key]); break
        if found:
            k, cands = found; j = i + k
            key = ''.join(toks[i:i + k])
            composti = [c for kk in KEYS if kk != key and (kk.startswith(key) or kk.endswith(key)) for c in IDX[kk]]   # «Rodinò» -> «Rodinò di Miglione»
            if composti and j < len(toks) and any(toks[j][:4] in c.k_nome for c in composti + list(cands)):
                cands = list(cands) + composti
            if data and len(cands) > 1:
                cands = [c for c in cands if c.inizio_mandato <= data <= c.fine_mandato] or cands
            if j < len(toks):                                   # nome proprio dopo il cognome?
                byname = [c for c in cands if c.k_nome.startswith(toks[j][:4]) or toks[j][:4] in c.k_nome]
                if byname and len(toks[j]) >= 3:
                    nn = byname[0].k_nome; jj = j
                    while jj < len(toks) and toks[jj] in nn: jj += 1      # consuma tutto il nome («VITTORIO EMANUELE»)
                    cands, j = byname, max(jj, j + 1)
            r = cands[0] if len(cands) == 1 else None
            if r is None and len(cands) > 1 and ' '.join(toks[i:i + k]) == 'JERVOLINO':
                r = [c for c in cands if c.k_nome.startswith('ANGELO')][0]
            out.append((' '.join(toks[i:j]), r, 'esatto' if r is not None else 'ambiguo')); i = j
        else:
            t = toks[i]
            pref = [k for k in KEYS if len(t) >= 5 and k.startswith(t)]                    # «Tambroni» -> «Tambroni Armaroli»
            if t.startswith('G') and len(t) > 5 and t not in IDX and t[1:] in IDX: pref = [t[1:]]    # «GCOCCIA»: G spuria dell'OCR
            close = pref if len(pref) == 1 else difflib.get_close_matches(t, KEYS, n=1, cutoff=0.8)
            if t in NOMI_PROPRI or len(t) < 4: close = []                                   # «Maria», «Pietro», «Michele»: nomi propri staccati, non cognomi
            if close and len(IDX[close[0]]) == 1:
                out.append((toks[i], IDX[close[0]][0], 'approssimato'))
            elif len(toks[i]) >= 4 and toks[i] not in ('DEPUTATI', 'CONGEDO', 'SONO', 'ASTENUTI'):
                out.append((toks[i], None, 'non trovato'))
            i += 1
    return out

# ---------- testo continuo per seduta ----------
def flatten(seduta):
    text, pagemap = '', []
    for f in sorted(glob.glob(os.path.join(TXT, f'{seduta}_p*.txt'))):
        p = int(re.search(r'_p(\d+)', f).group(1))
        for col in open(f, encoding='utf-8', errors='ignore').read().split('<<<COLONNA_DESTRA>>>'):
            pagemap.append((len(text), p))
            col = col.replace('î', 'i').replace('Î', 'I').replace('ì ', 'i ')
            text += ' ' + re.sub(r'\s*\n\s*', ' ', col)
    return text, pagemap

def page_at(pm, pos):
    p = pm[0][1]
    for start, pg in pm:
        if start <= pos: p = pg
        else: break
    return p

M_SI = re.compile(r'Rispond[oe]no\s+s[iìl1]\s*[:;.]?', re.I)
M_NO = re.compile(r'Rispond[oe]no\s+no\s*[:;.]?', re.I)
M_AST = re.compile(r'Si\s+(?:sono\s+)?astengono\s*[:;.]?|Si\s+sono\s+astenuti\s*[:;.]?|Si\s+[èe]\s+astenut[oa]\s*[:;.]?|Astenut[oi]\s*[:;]', re.I)   # anche l'intestazione secca «Astenuti:» (coi due punti: quella del riquadro dei totali non li ha)
M_CONG = re.compile(r"(?:Sono|Deputati|[EÈ])\s+in\s+congedo\s*[:;.]?|In\s+congedo\s*[:;.]?", re.I)
M_END = re.compile(r'Risultato\s+della\s+votazione|Hanno\s+risposto\s+s|Comunico\s+il\s+risultato|Annuncio\s+il\s+risultato', re.I)

PROSA = re.compile(r"(?:\b[a-zàèéìòù’']{3,}\b[\s,.;:]+){4,}")   # 4+ parole minuscole di fila: è testo, non un elenco
def nomi_da(seg):
    seg = re.sub(r"PRESIDENZA\s+DEL\s+(?:VICE\s*)?PRESIDENTE(?:[\s.,|']+[A-ZÀ-Ý']{3,})*", ' ', seg)   # cambio di presidenza durante la chiama (ammette rumore OCR tra le parole)
    mp = PROSA.search(seg)
    if mp: seg = seg[:mp.start()]
    seg = re.split(r"PRESIDENTE\s*\.|Hanno risposto|Risultato", seg)[0]
    s = re.sub(r"[|©°“”\"«»‘_~*]", ' ', seg)
    s = re.sub(r"(\w)-\s+([a-zàèéìòù])", r"\1\2", s)                 # sillabazione «Al- berti»
    parts = re.split(r'\s*[—–]+\s*-?\s*|\s+-\s+|\s*-{2,}\s*|\s*\.\s*(?=[A-Z][a-z])', s)
    out = []
    for p in parts:
        p = re.sub(r"[^A-Za-zÀ-ÿ' ]", ' ', p)
        p = re.sub(r"\b(?!di\b|de\b)[a-z]{1,2}\b", ' ', p)                # rumore OCR (n, o...), ma non «di»
        p = re.sub(r"\s+", ' ', p).strip(" '")
        if len(re.sub(r"[^A-Za-zÀ-ÿ]", '', p)) >= 3 and p[0].isupper():
            out.append(p)
    return out

def totale(after, pat):
    m = re.search(pat + r"[^0-9]{0,25}(\d{1,4})", after, re.I)
    if not m: return None
    v = int(m.group(1))
    return v % 1000 if v > 556 else v          # errori di OCR come «4173» per «173»

# Totali ufficiali stampati nel resoconto ma letti male dall'OCR («1» scambiato per «4»),
# corretti dopo verifica sull'immagine del PDF. In entrambi i casi l'aritmetica del
# riquadro conferma il valore giusto: presenti - astenuti = votanti = sì + no.
TOTALI_CORRETTI = {('sed102', 'si', 147): 117,   # p. 18: 404 - 3 = 401 = 117 + 284
                   ('sed332', 'no', 246): 216}   # p. 19: 331 - 4 = 327 = 111 + 216

# Nomi stampati spezzati dal cambio pagina e abbinati alla persona sbagliata:
# ricodifica manuale verificata sull'immagine del PDF.
CORREZIONI_NOMI = {('sed270', 'no', 'RICI'): 'CLERICI'}   # «Cle- / rici» a cavallo delle pp. 18-19 (Ricci Giuseppe votò sì)

# Voti controllati a mano sull'immagine del PDF: lo scarto residuo non è un errore di
# estrazione ma una discrepanza del resoconto stesso tra elenco stampato e totali annunciati.
VERIFICATI = {('sed180', 16): 'verificato: elenco stampato con meno nomi dei totali (163 sì, 164 no)',
              ('sed270', 18): 'verificato: elenco stampato con più nomi dei totali (91 sì, 266 no)'}

voti, righe = [], []
sedute = sorted({os.path.basename(f).split('_')[0] for f in glob.glob(os.path.join(TXT, 'sed*_p*.txt'))})
for s in sedute:
    text, pm = flatten(s)
    if not M_SI.search(text): continue
    data = date.get(s)
    for m in M_SI.finditer(text):
        win = text[m.end():m.end() + 30000]
        mn = M_NO.search(win)
        if not mn: continue
        ma = M_AST.search(win, mn.end()); mc = M_CONG.search(win, mn.end()); me = M_END.search(win, mn.end())
        stops = sorted(x.start() for x in [ma, mc, me] if x)
        end_no = stops[0] if stops else len(win)
        segs = {'sì': win[:mn.start()], 'no': win[mn.end():end_no]}
        if ma and ma.start() == end_no:
            nxt = min([x.start() for x in [mc, me] if x and x.start() > ma.start()] or [len(win)])
            segs['astenuto'] = win[ma.end():nxt]
        if mc:
            nxt = min([x.start() for x in [me] if x and x.start() > mc.start()] or [mc.end() + 3000])
            segs['congedo'] = win[mc.end():nxt]
        after = win[me.start():me.start() + 800] if me else ''
        before = text[max(0, m.start() - 2500):m.start()]
        k = before.lower().rfind('appello nominale')
        oggetto = before[max(0, k - 500):k + 200] if k >= 0 else before[-600:]
        vid = len(voti) + 1
        cnt = {}
        for voto, seg in segs.items():
            names = nomi_da(seg)
            cnt[voto] = 0
            for piece in names:
                for nm, r, how in scomponi(piece, data):
                    fix = CORREZIONI_NOMI.get((s, voto, nm))
                    if fix:
                        r, how = IDX[fix][0], 'correzione manuale'
                    righe.append(dict(id_voto=vid, voto=voto, nome_stampato=nm, id_dep=r.id_dep if r is not None else '',
                                      cognome=r.cognome if r is not None else '', abbinamento=how))
                    cnt[voto] += r is not None
        voti.append(dict(id_voto=vid, seduta=s, data=data, pagina=page_at(pm, m.start()),
                         si_ufficiali=TOTALI_CORRETTI.get((s, 'si', t_si := totale(after, r'Hanno\s+risposto\s+s[iìl1]')), t_si),
                         no_ufficiali=TOTALI_CORRETTI.get((s, 'no', t_no := totale(after, r'Hanno\s+risposto\W{0,3}n[o0]')), t_no),
                         astenuti_ufficiali=totale(after, r'Si\s+sono\s+astenuti'),
                         si_abbinati=cnt.get('sì', 0), no_abbinati=cnt.get('no', 0), astenuti_abbinati=cnt.get('astenuto', 0),
                         congedo_abbinati=cnt.get('congedo', 0), oggetto=re.sub(r'\s+', ' ', oggetto).strip(),
                         url_pdf=f'https://documenti.camera.it/_dati/costituente/lavori/Assemblea/{s}/{s}nc.pdf#page={page_at(pm, m.start())}'))

V = pd.DataFrame(voti); R = pd.DataFrame(righe)
V['scarto_si'] = V.si_abbinati - V.si_ufficiali
V['scarto_no'] = V.no_abbinati - V.no_ufficiali
V['controllo'] = ['senza totali' if pd.isna(a) or pd.isna(b) else ('ok' if abs(a) <= 3 and abs(b) <= 3 else 'da verificare')
                  for a, b in zip(V.scarto_si, V.scarto_no)]
V['controllo'] = [VERIFICATI.get((sed, pag), c) for sed, pag, c in zip(V.seduta, V.pagina, V.controllo)]
os.makedirs(OUT, exist_ok=True)
V.to_csv(os.path.join(OUT, 'voti.csv'), index=False)
R.to_csv(os.path.join(OUT, 'voti_nominali.csv'), index=False)
ok = R[(R.id_dep != '') & R.voto.isin(['sì', 'no', 'astenuto'])].copy()
# stesso costituente in due elenchi dello stesso voto: se uno solo dei due abbinamenti è esatto si tiene
# quello (l'altro è un abbinamento approssimato sbagliato); se lo sono entrambi è un errore della fonte
# (es. Zappelli in v16, stampato tra i sì e tra i no) e il voto di quel costituente si lascia mancante
ok['esatto'] = ok.abbinamento.isin(['esatto', 'correzione manuale'])
conf = ok.groupby(['id_voto', 'id_dep']).voto.transform('nunique') > 1
ok = pd.concat([ok[~conf], ok[conf & ok.esatto & (ok.groupby(['id_voto', 'id_dep']).esatto.transform('sum') == 1)]])
ok = ok.drop_duplicates(['id_voto', 'id_dep'])
ok[['id_voto', 'id_dep', 'voto']].to_csv(os.path.join(OUT, 'edgelist_voti.csv'), index=False)
print('voti per appello nominale:', len(V))
print('controllo con i totali ufficiali:', V.controllo.value_counts().to_dict())
print('abbinamento dei nomi:', R.abbinamento.value_counts().to_dict())
