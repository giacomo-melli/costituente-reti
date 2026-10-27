"""Estrae dai testi OCR dei resoconti gli emendamenti e i loro firmatari.

Due fonti nel testo:
  A. blocchi di firma « COGNOME, COGNOME, ... » che chiudono il testo di un emendamento
     quando il Presidente li elenca (lista completa dei firmatari);
  B. formule di presentazione «emendamento degli onorevoli X, Y e Z» (complete, salvo «ed altri»).
I nomi sono abbinati ai 581 costituenti usando la data della seduta (chi era in carica),
il nome proprio quando stampato e, per gli omonimi, il partito degli altri firmatari.
Uso: python3 estrai_emendamenti.py CARTELLA_pipeline [cartella_output]"""
import re, os, sys, glob, unicodedata, difflib
from collections import Counter
import pandas as pd

D = sys.argv[1] if len(sys.argv) > 1 else '.'
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(D, 'extraction')
TXT = os.path.join(D, 'testi_colonne')
nomi = pd.read_csv(os.path.join(D, 'tools', 'costituenti_nomi.csv'))
date = dict(pd.read_csv(os.path.join(D, 'tools', 'sedute_date.csv')).values)

def norm(s):
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().upper()
    return re.sub(r"\s+", ' ', re.sub(r"[^A-Z ]", ' ', s)).strip()

ALIAS = {'RODNO': 'RODINO', 'SILONE': 'TRANQUILLI', 'NATOLI': 'NATOLI LAMANTEA', 'DE UNTERRICHTER MARIA': 'JERVOLINO MARIA', 'DE UNTERRICHTER': 'JERVOLINO MARIA',
         'RODINO MARIO': 'RODINO DI MIGLIONE MARIO', 'VASSALLO': 'PASQUALINO VASSALLO ROSARIO',
         # refusi ricorrenti dell'OCR sui cognomi
         'TECA': 'TEGA', 'TONCILO': 'TONELLO', 'GABRIELE': 'GABRIELI'}
STOP = {'PRESIDENTE', 'DEPUTATI', 'COMMISSIONE', 'ASSEMBLEA', 'ONOREVOLE', 'ONOREVOLI', 'ALTRI', 'COLLEGHI', 'GOVERNO', 'MINISTRO', 'RELATORE'}
nomi['k_cogn'] = nomi.cognome.map(lambda x: norm(x).replace(' ', ''))
nomi['k_nome'] = nomi.nome.map(lambda x: norm(x).replace(' ', ''))
NOMI_PROPRI = {t for x in nomi.nome for t in norm(x).split()} - set(nomi.cognome.map(lambda x: norm(x).replace(' ', '')))
IDX = {}
for r in nomi.itertuples():
    IDX.setdefault(r.k_cogn, []).append(r)
KEYS = list(IDX)

def candidates(name, data):
    n = norm(name)
    for a, b in ALIAS.items():
        n = re.sub(r'\b' + a + r'\b', b, n)
    toks = [t for t in n.split() if t not in STOP]
    if not toks or len(''.join(toks)) < 3:
        return [], 'scartato', ''
    cands, how, rest = [], '', ''
    for k in range(len(toks), 0, -1):                       # cognome = prime k parole
        key = ''.join(toks[:k])
        if key in IDX:
            cands, how, rest = IDX[key], 'esatto', ''.join(toks[k:]); break
    if not cands and len(toks) >= 2:                         # nome prima del cognome («Sandro Pertini», «Vittorio Emanuele Orlando»)
        for j in range(1, len(toks)):
            key = ''.join(toks[j:])
            if key in IDX:
                cands, how, rest = IDX[key], 'esatto', ''.join(toks[:j]); break
    if not cands:                                            # cognome composto troncato (es. NATOLI)
        pre = [k for k in KEYS if k.startswith(''.join(toks)) and len(''.join(toks)) >= 5]
        if len(pre) == 1:
            cands, how = IDX[pre[0]], 'prefisso'
    if not cands:                                            # errori di OCR
        for k in range(len(toks), 0, -1):
            key = ''.join(toks[:k])
            if len(key) < 5 or toks[0] in NOMI_PROPRI: continue   # frammenti («CARI», «Med») e nomi propri («Bianca»)
            close = difflib.get_close_matches(key, KEYS, n=1, cutoff=0.8)
            if close:
                cands, how, rest = IDX[close[0]], 'approssimato', ''.join(toks[k:]); break
    if data and len(cands) > 1:
        att = [c for c in cands if c.inizio_mandato <= data <= c.fine_mandato]
        cands = att or cands
    if len(cands) > 1 and rest:
        f = [c for c in cands if rest[:4] in c.k_nome]
        cands = f or cands
    return cands, how, rest

def resolve_group(names, data):
    """Abbina un gruppo di firmatari; per gli omonimi sceglie il candidato del partito prevalente nel gruppo."""
    uniti, i = [], 0                                          # «CARI-» + «GNANI» -> «CARIGNANI» (cognome spezzato dall'OCR)
    while i < len(names):
        if i + 1 < len(names) and norm(names[i] + names[i + 1]).replace(' ', '') in IDX and candidates(names[i], data)[1] != 'esatto':
            uniti.append(names[i] + names[i + 1]); i += 2
        else:
            uniti.append(names[i]); i += 1
    names = uniti
    # due cognomi senza la virgola in mezzo («Targetti Amadei e Bordon»): si separano se il resto non
    # e' il nome proprio del primo ma e' a sua volta il cognome di un costituente
    sep = []
    for nm in names:
        toks = [t for t in norm(nm).split() if t not in STOP]
        diviso = False
        if len(toks) >= 2 and ''.join(toks) not in IDX:
            for j in range(1, len(toks)):
                a, b = ''.join(toks[:j]), ''.join(toks[j:])
                if a in IDX and b in IDX and toks[j] not in NOMI_PROPRI \
                        and not any(c.k_nome.startswith(b[:4]) for c in IDX[a]):
                    sep += [' '.join(toks[:j]), ' '.join(toks[j:])]; diviso = True; break
        if not diviso: sep.append(nm)
    names = sep
    res = [(nm,) + candidates(nm, data) for nm in names]
    parties = Counter(c[0].lista_partito for _, c, _, _ in res if len(c) == 1)
    out = []
    for nm, c, how, _ in res:
        if len(c) > 1:
            best = [x for x in c if parties and x.lista_partito == parties.most_common(1)[0][0]]
            if len(best) == 1:
                c, how = best, how + '+partito'
        if not c:
            out.append(dict(nome_stampato=nm, id_dep='', cognome='', nome='', abbinamento=how or 'non trovato'))
        elif len(c) > 1:
            out.append(dict(nome_stampato=nm, id_dep='', cognome=' / '.join(x.cognome + ' ' + x.nome for x in c), nome='', abbinamento='ambiguo',
                            candidati='|'.join(x.id_dep for x in c)))
        else:
            out.append(dict(nome_stampato=nm, id_dep=c[0].id_dep, cognome=c[0].cognome, nome=c[0].nome, abbinamento=how))
    return out

def split_names(s):
    s = re.sub(r'\b(ed|e)\s+altri\b', '', s, flags=re.I)
    s = re.sub(r"\b(?:dell['’]\s?|della\s+|dall['’]\s?)onorevole\b", '', s, flags=re.I)   # elenco che ripete «dell'onorevole»
    s = re.sub(r'(\w)-\s+(\w)', r'\1\2', s)
    s = re.sub(r'(\w)[|¶]\s*(\w)', r'\1\2', s)   # cognome spezzato dall'a capo: Ma|glioli
    s = re.sub(r'\b(?!(?:e|ed)\.)([A-Za-z]{1,3})\.\s+(?=[A-Z])', r'\1', s)   # sillabe spezzate dall'OCR (DE Mr. CHELIS), non la congiunzione «e.»
    parts = re.split(r",|;|\.\s+(?=[A-ZÀ-Ý])|\s\bed?\b(?:['’.]?\s|-\s*(?=[A-ZÀ-Ý]))", s)   # anche «e-Carboni»   # anche «e'» ed «e.» con il segno spurio dell'OCR
    return [p.strip(" .:-'’\"|°_") for p in parts if len(re.sub(r'[^A-Za-zÀ-ÿ]', '', p)) >= 3]

# ---------- testo continuo per seduta ----------
COGN_RE = re.compile(r'\b(' + '|'.join(sorted({re.escape(c) for c in nomi.cognome if len(c) >= 4}, key=len, reverse=True)) + r')\b', re.I)
def qualita(f):
    """Cognomi di costituenti riconosciuti nella pagina: misura grezza della qualità dell'OCR."""
    return len(COGN_RE.findall(open(f, encoding='utf-8', errors='ignore').read()))

def flatten(seduta):
    text, pagemap = '', []
    for f in sorted(glob.glob(os.path.join(TXT, f'{seduta}_p*.txt'))):
        p = int(re.search(r'_p(\d+)', f).group(1))
        f400 = os.path.join(D, 'testi_colonne_400', os.path.basename(f))     # seconda lettura a 400 dpi, se c'è
        if os.path.exists(f400) and os.path.getsize(f400) > 0 and qualita(f400) > qualita(f): f = f400   # tiene la lettura migliore
        for col in open(f, encoding='utf-8', errors='ignore').read().split('<<<COLONNA_DESTRA>>>'):
            lines = col.strip('\n').split('\n')
            if lines and len(re.findall(r'[a-z]', lines[0])) < 10:   # residuo di intestazione
                lines = lines[1:]
            c = '\n'.join(lines)
            # sillabazione, anche con righe vuote o sporche in mezzo, e con un segno spurio fra il
            # trattino e l'a capo o all'inizio della riga dopo («MARAZ-'» / «- ZA», «Cle-.» / «rici»):
            # senza, il blocco di firma si spezza e l'emendamento va perso per intero
            c = re.sub(r'-{1,3}[ \t]*[|.,\'‘’°"`´]{0,2}[ \t]*\n(?:[^\S\n]*[|.,\'‘’°-]*[^\S\n]*\n)*[^\S\n]*[-|.,\'‘’°]{0,2}[^\S\n]*', '', c)
            c = re.sub(r'\bo\W{0,3}n\W{0,2}o\W{0,2}[rt]\W{0,2}e\W{0,2}v\W{0,2}o\W{0,2}l\W{0,2}([ei])\b', r'onorevol\1', c)
            c = re.sub(r'\bonorevo[!|1I]([ei])\b', r'onorevol\1', c)
            c = re.sub(r'(\w)-[:;]\s+(\w)', r'\1\2', c)                       # «sostan-: ziali»
            c = re.sub(r"\b(De|Di|Da|Del|Della|Lo|La)['’]?\s*[:.|]\s+(?=[A-ZÀ-Ý][a-zà-ÿ])", r'\1 ', c)   # «De' : Palma»
            c = re.sub(r'\b([Oo])n[oòóô][eéè]?r[eéè]vol([ei])\b', r'\1norevol\2', c)   # «onòérevole»        # «onorevo!e»: la l letta come punto esclamativo   # «ono“revoli», «o- norevoli»
            # cognome spezzato a fine riga con un apice o una barra al posto del trattino
            # («Carpano Ma ‘glioli», «For-‘nara»): senza ricucirlo, l'elenco dei firmatari
            # si interrompe li'. Richiede 2-4 lettere prima, per non toccare «L'onorevole».
            c = re.sub(r"\b([A-ZÀ-Ý][a-zà-ÿ]{1,3})\s*[‘'’|-]+\s*\n?\s*([a-zà-ÿ]{2,})\b", r"\1\2", c)
            c = re.sub(r'\n\s*\n', ' ¶ ', c)
            c = re.sub(r'\s*\n\s*', ' ', c)
            pagemap.append((len(text), p))
            text += ' ' + c
    return text, pagemap

def page_at(pm, pos):
    p = pm[0][1] if pm else 0
    for start, pg in pm:
        if start <= pos: p = pg
        else: break
    return p

SIG = re.compile(r'[«<]{1,2}\s*([^«»¶]{3,400}?)\s*[\'’"‘]?\s*[»>]')
def is_signature(c):
    c2 = re.sub(r'\b(ed|e)\s+altri\b', '', c, flags=re.I)
    letters = [ch for ch in c2 if ch.isalpha()]
    if len(letters) < 4: return False
    up = sum(ch.isupper() for ch in letters) / len(letters)
    parts = split_names(c2)
    return bool(parts) and all(len(x.split()) <= 4 for x in parts) and up >= 0.6

# «|» e «¶» compaiono dentro i cognomi quando l'OCR spezza la riga («Carpano Ma|glioli»):
# se non si ammettono, l'elenco dei firmatari si interrompe li' e tutti i nomi successivi vanno persi.
NAME = r"[A-ZÀ-Ý][\w'’À-ÿ:|¶]+(?:\.\s(?=[a-z])\w+)?(?:\s+[A-ZÀ-Ý][\w'’À-ÿ:|¶]+){0,3}"   # ammette «Miccol:s», «Bo. nino» (rumore OCR)
PRES = re.compile(r"(?:dell['’]\s?onorevole|[Dd]all['’]?\s?onorevole|della\s+onorevole|de\s?gli onorevoli|dagli onorevoli|dalle onorevoli|dell['’]\s?on\.|insie\w{1,3}\s+con\s+gli\s+onorevoli|unitamente\s+(?:agli|con\s+gli|ai)\s+(?:onorevoli|colleghi)|dal\s+collega(?:\s+onorevole)?|dai\s+colleghi(?:\s+onorevoli)?|firm\w+\s+(?:anche\s+)?(?:dei|degli|dai)\s+colleghi)[\s‘'’]+(" + NAME +
                  r"(?:[\s·]*(?:,\s*(?:ed|e)\b|,|;|\be\b|\bed\b|\s*-\s*)[\s¶\-·.‘’'\"“”|$*!:]*(?:(?:dell['’]\s?|della\s+)onorevole[\s‘'’]+)?" + NAME + r")*(?:,?\s*(?:ed|e)\s+altri)?)")
# Il segno ¶ (riga vuota nel testo appiattito) e' ammesso fra separatore e nome:
# senza, elenchi come «Marinaro e ¶ Rodi» si interrompevano prima dell'ultimo firmatario.
# «Gli onorevoli X, Y e Z hanno presentato il seguente emendamento»
PRES2 = re.compile(r"\b[Gg]li\W{0,2}\s*onorevoli[\s\-–]+(" + NAME + r"(?:[\s·]*(?:,\s*(?:ed|e)\b|,|;|\be\b|\bed\b|\s*-\s*)[\s¶\-·.‘’'\"“”|$*!:]*" + NAME +
                   r")*(?:,?\s*(?:ed|e)\s+altri)?)[\s,.’'‘\"“”*!$]+ha\w{1,3}o[\s’'‘\",.]+(?:pres[ea]\w{2,5}ato|proposto|ripresentato)\b")
ART = re.compile(r"articol[oi]\s+(\d+(?:-bis)?)", re.I)
# «L'onorevole X ha presentato il seguente emendamento:» e' la formula con cui il Presidente legge un
# emendamento a firma singola; prima serviva solo ad aggiungere il presentatore ai «firmato anche dagli».
# Il recall misurato su cinque sedute lette per intero sull'immagine mostra che senza questa formula si
# perdevano la maggior parte degli emendamenti a firma singola.
PRES3 = re.compile(r"[Ll]['’]\W{0,2}onorevole[\s.,‘'’]+(" + NAME + r")(?:,\s*[a-zà-ÿ][^,.;¶]{1,30},)?[\s.,]+ha[\s,]+(?:(?:ora|anche|pure|gia|già|poi|inoltre|altresì)[\s,.]+){0,2}"
                   r"(?:presentato|proposto|ripresentato)[\s,.¶|]+(?:(?:anche|pure|inoltre)\s+)?(?:(?:a|al|alla|all['’]|per|su|sul|sull['’])\s*(?:quest\w+\s+)?(?:articolo|comma|testo)(?:\s+\d+)?\s+)?(?:il|un|l['’]\s?|uno|questo|altro|gli|i|due)?\s*(?:seguent\w+\s+|altro\s+|nuovo\s+)?"
                   r"(?:emendament\w+|articol\w+\s+(?:\d+[-\s]?b[iî]s\W{0,3}\s*)?aggiuntiv\w*|articolo\s+\d+[-\s]?b[iî]s|comma\s+aggiuntiv\w*|nuovo\s+testo|"
                   r"di\s+(?:sopprimere|sostituire|aggiungere|inserire)|(?<=proposto )che\s+(?:si\s+|il\s+|la\s+|l['’]|facciano|sia|venga|vengano))")
# chi parla propone un proprio testo («CRISPO. ... Propongo che l'articolo 4 sia redatto nel modo seguente: «...»»,
# «ho presentato il seguente emendamento»): il proponente e' il nome in testa al turno di parola
PROPONGO = re.compile(r"\b(?:[Ii]o\s+)?(?:[Pp]ropongo|[Pp]roporrei)\b(?P<mid>[^«]{0,170})«|\b[Hh]o\s+(?:gi[aà]\s+|anche\s+)?(?:presentato|proposto)\s+(?:il\s+seguente\s+|un\s+|questo\s+|l['’]\s?|altro\s+|un\s+altro\s+)?emendamento")
INTESTA = re.compile(r"¶\s*[.,'‘’|:\s]*([A-ZÀ-Ý][A-ZÀ-Ý'’ ]{2,30}?)(,\s*[A-Z][a-zà-ÿ][^.¶]{0,70})?[.,]\s+(?=[A-ZÀ-Ý(«]|\.{2,}|…)")
def chi_parla(text, pos):
    """Nome in testa al turno di parola in cui cade `pos` (None per il Presidente o per chi parla per la Commissione)."""
    t = list(INTESTA.finditer(text, max(0, pos - 15000), pos + 3))
    if not t: return None
    nome, ruolo = t[-1].group(1).strip(), t[-1].group(2) or ''
    if nome.startswith('PRESIDENTE') or re.search(r'Presidente|Relatore|Ministro|Sottosegretario', ruolo): return None
    return nome.title()
COFIRMA_DOPO = re.compile(r"firmat\w*\s+anche|insie\w{1,3}\s+con|con\s+gli\s+onorevoli|e\s+dagli\s+onorevoli|altri\s+colleghi|a\s+firma", re.I)


def pulisci(t):
    t = re.sub(r'\s*¶\s*', ' / ', t)
    return re.sub(r'\s+', ' ', t).strip(' /')[:2000]


TURNO = re.compile(r"¶\s*[.,'‘’|:\s]*(?:PRESIDENTE|[A-ZÀ-Ý]{3,}[A-ZÀ-Ý'’ ]{0,26})[.,]\s")


FINE_TESTO = re.compile(r"(?:L['’]\s?onorevole\s+[A-ZÀ-Ý]\S*(?:\s+[A-ZÀ-Ý]\S*){0,2}\s+ha\s+fac\w{2,5}|Ha\s+fac\w{2,5}\s+di\s+svolger|"
                        r"Non\s+essendo\s+present|\((?:È|E|Non\s+è)\s+approvat|PRESIDENTE\.|Onorevole\s+[A-ZÀ-Ý]\S*(?:\s+[A-ZÀ-Ý]\S*)?,\s+(?:lo|la|li)\s+mant|"
                        r"[A-ZÀ-Ý]{4,}(?:\s+[A-ZÀ-Ý]{2,}){0,2}[.,]\s+(?:[A-ZÀ-Ý][a-zà-ÿ]|Presidente|Relatore))")
def testo_dopo(text, pos, finestra=160):
    """Testo dell'emendamento stampato fra virgolette subito dopo la formula di presentazione.
    Fra la formula e la virgoletta sono ammessi solo raccordi («così formulato», «del seguente tenore:»):
    se in mezzo comincia una frase nuova o un turno di parola, il testo non e' quello dell'emendamento."""
    k = text.find('«', pos, pos + finestra)
    if k < 0: return ''
    inter = text[pos:k]
    if re.search(r"[.?!][\s¶]+[(«]?[A-ZÀ-Ý][a-zà-ÿ]", inter) or TURNO.search(inter): return ''
    depth, i, fine = 0, k, min(len(text), k + 2500)
    while i < fine:
        ch = text[i]
        if ch == '«': depth += 1
        elif ch == '»':
            depth -= 1
            if depth <= 0: return pulisci(text[k:i + 1])
        elif ch == '¶' and i > k + 20 and TURNO.match(text, i):
            break                       # virgolette non chiuse: ci si ferma al turno di parola
        elif i > k + 20 and (ch.isupper() or ch == '(') and FINE_TESTO.match(text, i):
            break                       # ... o alla formula che segue la lettura
        i += 1
    return pulisci(text[k:i])


def testo_prima(text, pos, finestra=1500):
    """Per un blocco di firma: il testo fra virgolette che lo precede (anche se l'OCR non chiude le virgolette)."""
    seg = text[max(0, pos - finestra):pos]
    depth, j, start = 0, len(seg) - 1, -1
    while j >= 0:
        ch = seg[j]
        if ch == '»': depth += 1
        elif ch == '«':
            depth -= 1
            if depth <= 0: start = j; break
        elif ch == '¶' and TURNO.match(seg, j): break
        j -= 1
    if start < 0: return ''
    for _ in range(3):              # «Sostituirlo col seguente: ¶ «testo»: si risale al « esterno
        prima = seg[max(0, start - 300):start]
        q = prima.rfind('«')
        if q < 0 or '»' in prima[q:] or TURNO.search(prima[q:]): break
        start = start - len(prima) + q
    return pulisci(seg[start:])


VERBI_TIPO = [(r"soppri\w*|sopprime\w*|soppress\w*", 'sopprimere'), (r"sostitu\w*", 'sostituire'),
              (r"inseri\w*|premett\w*|far precedere", 'inserire'), (r"aggiung\w*|aggiuntiv\w*|far seguire", 'aggiungere')]


def tipo_emendamento(testo, formula=''):
    """sostituire / sopprimere / aggiungere / inserire, dalla formula d'apertura del testo; se il testo non
    la stampa, dall'aggettivo della presentazione («emendamento soppressivo», «articolo aggiuntivo»)."""
    for fonte in (testo[:220], formula):
        hit = [(m.start(), lab) for pat, lab in VERBI_TIPO for m in [re.search(pat, fonte, re.I)] if m]
        if hit: return min(hit)[1]
    return 'non determinato'


# «le proposte / gli emendamenti degli onorevoli X, Y e Z»: atti DISTINTI elencati insieme,
# non una firma congiunta. Il nome plurale deve reggere direttamente l'elenco: il varco fra i
# due non può contenere due punti, punto e virgola o una fine di frase (punto + maiuscola).
# Punti e virgolette isolati sono tollerati perché l'OCR li inserisce a fine riga
# («assorbiti gli emendamenti. « degli onorevoli...»).
PLUR_NOME = r"(?:emendame\w{0,3}ti|propost[ae]|osservazion[ie]|istanz[ae]|articoli aggiuntivi)"
# niente re.I sull'intero schema: renderebbe [A-ZÀ-Ý] insensibile al caso e ogni punto
# sembrerebbe una fine di frase. Il nome plurale resta insensibile al caso con (?i:...).
# Fra il punto e la maiuscola possono esserci ¶ (il segno di paragrafo del testo appiattito),
# barre e virgolette: senza, una vera fine di frase passerebbe per un elenco di atti.
PLURALE = re.compile(r"(?i:" + PLUR_NOME + r")\b(?![^;:]{0,70}?\.[\s¶/«(\[»·‘’'\"“”|_-]*[A-ZÀ-Ý])[^;:]{0,70}$")
QUELLI = re.compile(r"quel-?\s*li\s+(?:\w+\s+){0,2}$", re.I)

# «le parole / le dichiarazioni dell'onorevole X»: il nome e' l'autore di un intervento,
# non il presentatore di un emendamento. Stessa logica del plurale: il sostantivo deve reggere
# direttamente il nome, senza due punti, punto e virgola o fine di frase nel mezzo.
# «proposta» resta fuori di proposito: «la proposta dell'onorevole X» e' spesso un emendamento.
ATTO_PAROLA = r"(?:parol[ae]|dichiarazion[ei]|osservazion[ei]|intervent[oi]|discors[oi]|relazion[ei]|chiariment[oi]|argoment[oi]|tes[ie]|affermazion[ei]|rilievi|considerazion[ei]|pensiero|parere|critich[ea]|obiezion[ei]|richiest[ae]|domand[ae]|suggeriment[oi]|spiegazion[ei]|eccezion[ei]|avvertenz[ae]|raccomandazion[ei]|preghier[ae]|avviso|cortesia|interruzion[ei]|opinion[ei]|esposizion[ei]|valutazion[ei]|competenz[ae])"
PAROLA_DI = re.compile(r"(?i:" + ATTO_PAROLA + r")\b(?![^;:]{0,40}?\.[\s¶/«(\[»·‘’'\"“”|_-]*[A-ZÀ-Ý])[^;:]{0,40}$")


def atto_di_parola(before, nxt=''):
    """True se la menzione e' retta da un sostantivo di atto linguistico (parole, dichiarazioni...).
    `nxt` è il primo carattere della menzione: una maiuscola dopo il punto è una fine di frase
    («…pervenute. Gli onorevoli»), una minuscola no («dichiarazioni . dell'onorevole», rumore OCR)."""
    return bool(PAROLA_DI.search((before + nxt)[-70:]))


RISPETTIV = re.compile(r"rispettivamente\W{0,4}$", re.I)   # «presentati rispettivamente dagli onorevoli X e Y»
def elenco_di_atti_distinti(before, nxt=''):
    """True se la menzione è preceduta da un plurale che regge l'elenco (vedi atto_di_parola per `nxt`)."""
    # il sostantivo piu' vicino decide: «degli emendamenti Treves e Cappi valgono anche per
    # l'emendamento degli onorevoli Basso, Giua... ed altri» e' un emendamento solo
    if re.search(r"\bemendamento(?:\s+(?:aggiuntivo|sostitutivo|soppressivo|modificativo|concordato))?\W{0,4}$", before[-45:], re.I):
        return False
    # «due emendamenti, dei quali uno ... presentato dall'onorevole X»: il pronome singolare riporta a un atto solo
    if re.search(r"(?i:" + PLUR_NOME + r")\b[^;:]{0,40}\b(?:uno|il\s+primo|il\s+secondo|l['’]altro|l['’]ultimo)\b[^;:]{0,60}$", before[-110:]):
        return False
    # `nxt` serve solo al plurale: QUELLI e RISPETTIV sono ancorati allo spazio prima della menzione
    return bool(PLURALE.search((before + nxt)[-90:]) or QUELLI.search(before[-90:]) or RISPETTIV.search(before[-40:]))

EMEND_VERB = re.compile(r"sostitu|aggiung|soppri|sopprime|inseri|premett|trasferi|far precedere|far seguire|dopo le parole|dopo la parola|alle parole|alla parola|\bcomma\b|all['’]articolo|articolo aggiuntivo|nuovo testo|testo della Commissione", re.I)
NON_EMEND = re.compile(r"interrog|interpell|per\s+sapere\b|se\s+non\s+(?:ritenga|ravvisi|creda)|quali\s+provvedimenti|ordin\w*\W{0,4}del\W{0,4}giorno|risoluzion|mozion|lettera aperta|telegramma|impegna il Governo|invita il Governo|fiducia|appello nominale|scrutinio segreto|chiede d['’]\s?interrogare|chiedono d['’]\s?interrogare|\bAl(?:la)?\s+Ministr|\bAi\s+Ministri|Al\s+Presidente\s+del\s+Consiglio", re.I)
def tipo_testo(seg):
    if NON_EMEND.search(seg): return 'altro atto'
    return 'emendamento' if EMEND_VERB.search(seg) else 'non classificato'
URL = 'https://documenti.camera.it/_dati/costituente/lavori/Assemblea/{s}/{s}nc.pdf#page={p}'

recs = []
sedute = sorted({os.path.basename(f).split('_')[0] for f in glob.glob(os.path.join(TXT, 'sed*_p*.txt'))})
for s in sedute:
    text, pm = flatten(s)
    data = date.get(s)
    last_end = 0
    for m in SIG.finditer(text):
        firma = m.group(1)
        if not is_signature(firma): continue
        prev = text[max(0, m.start() - 160):m.start()]                     # «MEDA, ..., BAL- «.. DUZZI; ...»:
        k = prev.rfind('«')                                                # « spuria a metà del blocco
        if k >= 0 and '»' not in prev[k:] and len(prev[k + 1:].strip()) > 3 and is_signature(prev[k + 1:]):
            firma = prev[k + 1:] + ' ' + firma
        before = text[max(0, m.start() - 1200):m.start()]
        seg = text[max(last_end, m.start() - 1500):m.start()]
        last_end = m.end()
        tipo = tipo_testo(seg)
        if tipo != 'emendamento': continue
        arts = ART.findall(before)
        t_em = testo_prima(text, m.start())
        # la formula d'apertura e' subito prima del testo («Sostituirlo col seguente: «...»»), non in coda al blocco
        k_t = text.rfind('«', 0, m.start() - len(t_em) + 5) if t_em else -1
        formula = text[max(0, k_t - 160):k_t] if k_t > 0 else seg[-200:]
        recs.append(dict(seduta=s, data=data, pagina=page_at(pm, m.start()), fonte='firma', tipo=tipo, testo_stampato=firma.strip(),
                         testo_emendamento=t_em, tipo_emendamento=tipo_emendamento(t_em, formula),
                         altri=int(bool(re.search(r'altri', firma, re.I))), articolo_menzionato=arts[-1] if arts else '',
                         contesto=before[-350:].replace('¶', '/'), pos=m.start()))
    for m in PRES.finditer(text):
        after = text[m.end():m.end() + 120]
        before = text[max(0, m.start() - 1200):m.start()]
        # solo se il contesto immediato parla di un emendamento o di una proposta di testo
        vicino = before[-150:] + ' ' + m.group(0) + ' ' + text[m.end():m.end() + 300]
        if not re.search(r"emendament|sostitutiv|aggiuntiv|soppressiv|a firma|firmat[oa] dagli|insie\w{1,3}\s+con|propost[ao]\s+presentat|propost[ao] (?:aggiuntiv|sostitutiv|di)", before[-100:] + ' ' + after[:60], re.I):
            continue
        if NON_EMEND.search(before[-150:] + ' ' + re.split(r"\.[\s¶/]*(?=[A-ZÀ-Ý«])|¶", after[:80])[0]):
            continue
        # escluse: interrogazioni, interpellanze, mozioni e richieste di votazione (appello nominale, scrutinio segreto).
        # La spia puo' trovarsi anche DOPO i nomi: «...hanno chiesto la votazione per appello nominale»,
        # «Essa porta le firme anche degli onorevoli X, Y, Z» riferito a una richiesta annunciata prima.
        NON_EM = r"interrogazion|interpellanz|mozion|ordin\w*\W{0,4}del\W{0,4}giorno|risoluzion|appello\W{0,4}nominale|scrutinio segreto|(?:chiest|richiest)\w*\W+(?:la\W+)?votazione|s\w?rutinio|verifica del numero legale|risoluzion"
        # dopo l'elenco la spia vale solo nella stessa frase: «Identico emendamento è stato presentato
        # dagli onorevoli X, Y. ¶ È stata chiesta la votazione per appello nominale...» e' un emendamento
        stessa_frase = re.split(r"\.[\s¶/]*(?=[A-ZÀ-Ý«])|¶", after[:160])[0]
        if re.search(NON_EM, before[-120:], re.I) or re.search(NON_EM, stessa_frase, re.I):
            continue
        # «dall'onorevole X» dopo un participio di discorso («l'inconveniente accennato dall'onorevole X»)
        # o di adozione («fatto proprio dall'onorevole X»: l'emendamento e' di un altro), oppure riferito
        # a una proposta fatta in Commissione: X non e' il presentatore di un emendamento in Aula
        if re.match(r"dall", m.group(0), re.I) and (
                re.search(r"(?:accennat|rilevat|osservat|dett|ricordat|sostenut|espress|citat|richiamat|lamentat|affermat|dichiarat|"
                          r"pres[oa]\s+in\s+considerazione|fatt[oa]\s+propri)\w*[\s,]*$", before[-40:], re.I)
                or re.match(r"[\s,]*(?:nella|in|in\s+sede\s+di)\s+(?:\w+\s+)?(?:Sotto)?[Cc]ommissione", after)):
            continue
        # «gli emendamenti degli onorevoli X, Y e Z»: emendamenti distinti, non firme congiunte
        if elenco_di_atti_distinti(before, m.group(0)[:1]) or atto_di_parola(before, m.group(0)[:1]):
            continue
        testo = m.group(1).strip()
        # «L'onorevole X ha presentato il seguente emendamento, firmato anche dagli onorevoli...»:
        # il presentatore non è nell'elenco e va aggiunto
        if (re.search(r"firmat[oa]\s+anche|firme\s+anche|firme\s+de", before[-70:], re.I)
                or re.match(r"(?:insie|firm|unitam)", m.group(0), re.I)):
            # due forme: «L'onorevole X ha presentato ... firmato anche dagli onorevoli Y, Z»
            # e «Segue l'emendamento dell'onorevole X, firmato anche dagli onorevoli Y, Z»
            mp = (re.search(r"[Ll]['’]\s?onorevole[\s.,]+(" + NAME + r")[\s.,]+ha[\s,]+(?:(?:ora|anche|pure|gia|già|poi|inoltre)[\s,]+){0,2}(?:presentato|proposto|sostituito)", before[-400:])
                  or re.search(r"emendamento[\s,]+dell['’]\s?onorevole[\s.,]+(" + NAME + r")[\s,]*(?:che\s+)?(?:reca\s+anche\s+le\s*|firmat)", before[-250:]))
            # terza forma: il presentatore è il nome in testa al turno di parola
            # («LACONI. Presento all'Assemblea il seguente emendamento firmato anche dai colleghi X, Y»)
            if not mp:
                mp = re.search(r"(?:^|[.¶/]\s*)([A-ZÀ-Ý][A-ZÀ-Ý'’ ]{3,28})\.\s+(?:Presento|Ho\s+presentato|Abbiamo\s+presentato|Propongo)",
                               before[-400:])
            # quarta forma: «insieme con gli onorevoli» ha sempre un soggetto, l'ultimo
            # «l'onorevole X» prima dell'elenco («ha facolta' di svolgerlo l'onorevole Merlin Angelina,
            # la quale, insieme con gli onorevoli...»; «l'onorevole Laconi svolgere il seguente
            # emendamento presentato insieme con gli onorevoli...»)
            if not mp and (re.match(r"insie|unitam", m.group(0), re.I) or re.search(r"firmat[oa]\s+anche", before[-70:], re.I)):
                tutti = list(re.finditer(r"[Ll]['’]\s?onorevole[\s.,]+(" + NAME + r")", before[-200:]))
                mp = tutti[-1] if tutti else None
            if mp: testo = mp.group(1).strip().title() + ', ' + testo
        # «presentato dagli onorevoli X, Y e da me» / «da me e dagli onorevoli X, Y»: si aggiunge chi parla,
        # cioe' il nome in testa al turno di parola
        if (re.match(r"[\s.,]*e\s*[.,]?\s*da\s+me\b", after) or re.search(r"\bda\s+me\s+e\s*$", before[-20:])
                or re.match(r"[\s.,]*(?:e\s+)?(?:firmat\w+\s+)?anche\s+da\s+me\b", after)):
            turni = [t for t in re.finditer(r"(?:^|[.¶/]\s*)([A-ZÀ-Ý][A-ZÀ-Ý'’ ]{3,28})\.\s", before[-1500:])
                     if not t.group(1).strip().startswith('PRESIDENTE')]
            if turni: testo = turni[-1].group(1).strip().title() + ', ' + testo
        arts = ART.findall(before + m.group(0) + after[:60])
        t_em = testo_dopo(text, m.end())
        recs.append(dict(seduta=s, data=data, pagina=page_at(pm, m.start()), fonte='presentazione', tipo='emendamento', testo_stampato=testo,
                         testo_emendamento=t_em, tipo_emendamento=tipo_emendamento(t_em, before[-150:] + m.group(0) + after[:80]),
                         altri=int(bool(re.search(r'altri', m.group(1)))), articolo_menzionato=arts[-1] if arts else '',
                         contesto=(before[-200:] + ' [[' + m.group(0) + ']] ' + after).replace('¶', '/'), pos=m.start()))

    for m in PRES2.finditer(text):
        before = text[max(0, m.start() - 1200):m.start()]; after = text[m.end():m.end() + 300]
        # «hanno proposto ciascuno un identico emendamento», «hanno presentato due emendamenti ... in
        # formulazioni diverse»: atti distinti, uno per firmatario
        if re.match(r"[\s,]*(?:il\s+)?(?:ciascuno|rispettivamente|separatamente|(?:due|tre|quattro)\s+emendament)", after, re.I): continue
        if NON_EMEND.search(after[:150]): continue
        if elenco_di_atti_distinti(before, m.group(0)[:1]) or atto_di_parola(before, m.group(0)[:1]): continue
        arts = ART.findall(before[-300:] + after[:200])
        t_em = testo_dopo(text, m.end())
        recs.append(dict(seduta=s, data=data, pagina=page_at(pm, m.start()), fonte='presentazione', tipo='emendamento', testo_stampato=m.group(1).strip(),
                         testo_emendamento=t_em, tipo_emendamento=tipo_emendamento(t_em, m.group(0) + after[:80]),
                         altri=int(bool(re.search(r'altri', m.group(1)))), articolo_menzionato=arts[-1] if arts else '',
                         contesto=(before[-200:] + ' [[' + m.group(0) + ']] ' + after).replace('¶', '/'), pos=m.start()))

    for m in PROPONGO.finditer(text):
        if m.group('mid') is not None and TURNO.search(m.group('mid')): continue
        if m.group('mid') is not None and not re.search(r"articol|comma|formul|redatt|dire|sostitu|aggiun|soppri|emendament|modo seguente|seguente", m.group('mid'), re.I):
            continue                                       # «propongo di rinviare la seduta»: proposta di procedura
        oratore = chi_parla(text, m.start())
        if not oratore: continue
        before = text[max(0, m.start() - 1200):m.start()]; after = text[m.end():m.end() + 300]
        if NON_EMEND.search(m.group(0) + re.split(r"\.[\s¶/]*(?=[A-ZÀ-Ý«])|¶", after[:150])[0]): continue
        t_em = testo_dopo(text, m.end() - 1) if m.group(0).endswith('«') else testo_dopo(text, m.end())
        if m.group('mid') is not None and len(t_em) < 20: continue
        arts = ART.findall(before[-300:] + m.group(0) + after[:200])
        recs.append(dict(seduta=s, data=data, pagina=page_at(pm, m.start()), fonte='presentazione', tipo='emendamento', testo_stampato=oratore,
                         testo_emendamento=t_em, tipo_emendamento=tipo_emendamento(t_em, m.group(0) + after[:80]),
                         altri=0, articolo_menzionato=arts[-1] if arts else '',
                         contesto=(before[-200:] + ' [[' + m.group(0) + ']] ' + after).replace('¶', '/'), pos=m.start()))

    for m in PRES3.finditer(text):
        before = text[max(0, m.start() - 1200):m.start()]; after = text[m.end():m.end() + 300]
        if COFIRMA_DOPO.search(after[:220]): continue          # elenco di cofirmatari: lo prende PRES con il presentatore
        if NON_EMEND.search(re.split(r"\.[\s¶/]*(?=[A-ZÀ-Ý«])|¶", after[:150])[0]): continue
        arts = ART.findall(before[-300:] + m.group(0) + after[:200])
        t_em = testo_dopo(text, m.end())
        recs.append(dict(seduta=s, data=data, pagina=page_at(pm, m.start()), fonte='presentazione', tipo='emendamento', testo_stampato=m.group(1).strip(),
                         testo_emendamento=t_em, tipo_emendamento=tipo_emendamento(t_em, m.group(0) + after[:80]),
                         altri=0, articolo_menzionato=arts[-1] if arts else '',
                         contesto=(before[-200:] + ' [[' + m.group(0) + ']] ' + after).replace('¶', '/'), pos=m.start()))

R = pd.DataFrame(recs)
if R.empty:                                   # nessun record (succede solo su corpora di prova minimi)
    os.makedirs(OUT, exist_ok=True)
    for f in ('menzioni', 'menzioni_nomi', 'emendamenti', 'edgelist_emendamenti'):
        open(os.path.join(OUT, f + '.csv'), 'w').write('')
    print('menzioni 0'); sys.exit(0)
rows = []
for i, r in R.iterrows():
    for o, x in enumerate(resolve_group(split_names(r.testo_stampato), r.data), 1):
        rows.append(dict(id_menzione=i, ordine=o, **x))
F = pd.DataFrame(rows)
# omonimi rimasti ambigui (Gullo Fausto/Rocco, Mastino Pietro/Gesumino, Pajetta Gian Carlo/Giuliano...):
# si sceglie il candidato che ha firmato più spesso, altrove, con gli altri firmatari dello stesso gruppo
ris = F[F.id_dep.astype(str).str.startswith('d')]
coppie = Counter()
for _, g in ris.groupby('id_menzione'):
    ids = sorted(set(g.id_dep))
    for a_ in ids:
        for b_ in ids:
            if a_ != b_: coppie[(a_, b_)] += 1
if 'candidati' in F:
    for i, r in F[F.abbinamento == 'ambiguo'].iterrows():
        altri = set(ris[ris.id_menzione == r.id_menzione].id_dep)
        punti = {c: sum(coppie[(c, o)] for o in altri) for c in str(r.candidati).split('|')}
        top = sorted(punti.values(), reverse=True)
        if top and top[0] > 0 and (len(top) == 1 or top[0] > top[1]):
            c = max(punti, key=punti.get); x = nomi.set_index('id_dep').loc[c]
            F.loc[i, ['id_dep', 'cognome', 'nome', 'abbinamento']] = [c, x.cognome, x.nome, 'ambiguo+cofirme']
# ancora ambigui (il cognome citato da solo, senza cofirmatari che aiutino): si sceglie il
# candidato che in quella stessa seduta risulta abbinato con certezza altrove. Un omonimo
# assente dalla seduta non puo' aver presentato l'emendamento; se i candidati presenti sono
# due, si lascia ambiguo.
sed_di = R.seduta.to_dict()
attivi = {}
for _, r in F[F.id_dep.astype(str).str.startswith('d')].iterrows():
    attivi.setdefault(sed_di.get(r.id_menzione), set()).add(r.id_dep)
if 'candidati' in F:
    for i, r in F[F.abbinamento == 'ambiguo'].iterrows():
        pres = attivi.get(sed_di.get(r.id_menzione), set())
        c = [x for x in str(r.candidati).split('|') if x in pres]
        if len(c) == 1:
            x = nomi.set_index('id_dep').loc[c[0]]
            F.loc[i, ['id_dep', 'cognome', 'nome', 'abbinamento']] = [c[0], x.cognome, x.nome, 'ambiguo+seduta']

ok = F[F.id_dep.astype(str).str.startswith('d')]
R['ids'] = R.index.map(ok.groupby('id_menzione').id_dep.apply(lambda x: '|'.join(sorted(set(x))))).fillna('')
R['n_nomi'] = R.index.map(F.groupby('id_menzione').size()).fillna(0).astype(int)
# primo firmatario stampato: il resoconto chiama un emendamento col nome del primo («l'emendamento Fanfani»)
R['primo'] = R.index.map(ok.sort_values('ordine').groupby('id_menzione').id_dep.first()).fillna('')
R['n_abbinati'] = R.ids.map(lambda x: len(x.split('|')) if x else 0)
R['url_pdf'] = [URL.format(s=s, p=p) for s, p in zip(R.seduta, R.pagina)]

# ---------- consolidamento in emendamenti ----------
# Ogni blocco di firma è un emendamento; lo stesso emendamento riletto più volte (stessi firmatari,
# stesso articolo) è contato una volta. Le formule di presentazione con almeno un nome sono
# assorbite da un blocco se i loro firmatari ne sono un sottoinsieme (stessa seduta o le 3 vicine);
# altrimenti diventano un emendamento a sé (completo se senza «ed altri»).
R = R[R.n_abbinati > 0].copy()
R['snum'] = R.seduta.str[3:].astype(int)
def _n(t): return re.sub(r'[^a-z ]', '', unicodedata.normalize('NFKD', str(t)).encode('ascii', 'ignore').decode().lower())[:250]
def stesso_testo(a, b):
    """Due menzioni con lo stesso firmatario sono lo stesso emendamento salvo che entrambe stampino un testo e
    i testi siano diversi: chi presenta molti emendamenti (Nitti, Colitto, Caronia...) ne ha spesso piu' d'uno
    in sedute vicine, e senza il testo venivano fusi in uno solo."""
    if not isinstance(a, str) or not isinstance(b, str) or len(a) < 25 or len(b) < 25: return True
    # una ripresa che cita solo un pezzo del testo («e tecnico-professionale») e' lo stesso emendamento
    ca, cb = (_n(x).replace(' ', '') for x in (a[:2000], b[:2000]))
    corto, lungo = sorted((ca, cb), key=len)
    if len(corto) >= 10 and corto in lungo: return True
    blocco = difflib.SequenceMatcher(None, corto, lungo, autojunk=False).find_longest_match(0, len(corto), 0, len(lungo)).size
    if blocco >= 0.8 * len(corto): return True
    return difflib.SequenceMatcher(None, _n(a), _n(b)).ratio() >= 0.5
blocks = R[R.fonte == 'firma'].sort_values(['snum', 'pos'])
em, key2id, EMS = [], {}, {}
for i, r in blocks.iterrows():
    k = r.ids
    if k in key2id and abs(int(EMS[key2id[k]]) - r.snum) <= 3 and stesso_testo(em[key2id[k] - 1]['testo'], r.testo_emendamento):
        R.loc[i, 'id_emendamento'] = key2id[k]; continue
    eid = len(em) + 1; key2id[k] = eid; EMS[eid] = r.snum; R.loc[i, 'id_emendamento'] = eid
    em.append(dict(id_emendamento=eid, firmatari=r.ids, n_firmatari=r.n_abbinati, completo=1 - r.altri, articolo_menzionato=r.articolo_menzionato,
                   prima_seduta=r.seduta, data=r.data, pagina=r.pagina, fonte='firma', url_pdf=r.url_pdf, primo=r.primo,
                   testo=r.testo_emendamento, tipo_emendamento=r.tipo_emendamento))
EM = pd.DataFrame(em, columns=['id_emendamento', 'firmatari', 'n_firmatari', 'completo', 'articolo_menzionato', 'prima_seduta', 'data',
                               'pagina', 'fonte', 'url_pdf', 'primo', 'testo', 'tipo_emendamento'])
for i, r in R[R.fonte == 'presentazione'].sort_values(['snum', 'pos']).iterrows():
    s = set(r.ids.split('|'))
    near = EM[(EM.prima_seduta.str[3:].astype(int) - r.snum).abs() <= 3] if len(EM) else EM
    # un elenco di 2+ nomi e' assorbito da un emendamento che li contiene tutti; un nome solo
    # soltanto se ne e' il primo firmatario: «Segue l'emendamento dell'onorevole Bubbio» e' un atto
    # a se', non la ripresa dell'elenco di 28 firme in cui Bubbio e' tredicesimo
    hit = [e for e in near.itertuples() if s <= set(e.firmatari.split('|')) and (len(s) > 1 or e.primo == r.ids)
           and stesso_testo(e.testo, r.testo_emendamento)]
    if not hit:
        hit = [e for e in near.itertuples() if e.firmatari == r.ids and stesso_testo(e.testo, r.testo_emendamento)] if len(near) else []
    if hit:
        R.loc[i, 'id_emendamento'] = hit[0].id_emendamento
        j = EM.index[EM.id_emendamento == hit[0].id_emendamento][0]
        if (not isinstance(EM.at[j, 'testo'], str) or not EM.at[j, 'testo']) and r.testo_emendamento:   # testo dalla menzione che lo stampa
            EM.at[j, 'testo'] = r.testo_emendamento; EM.at[j, 'tipo_emendamento'] = r.tipo_emendamento
        elif EM.at[j, 'tipo_emendamento'] == 'non determinato' and r.tipo_emendamento != 'non determinato':
            EM.at[j, 'tipo_emendamento'] = r.tipo_emendamento
        continue
    eid = len(EM) + 1
    EM = pd.concat([EM, pd.DataFrame([dict(id_emendamento=eid, firmatari=r.ids, n_firmatari=r.n_abbinati, completo=1 - r.altri,
                     articolo_menzionato=r.articolo_menzionato, prima_seduta=r.seduta, data=r.data, pagina=r.pagina, fonte='presentazione', url_pdf=r.url_pdf,
                     primo=r.primo, testo=r.testo_emendamento, tipo_emendamento=r.tipo_emendamento)])],
                   ignore_index=True)
    R.loc[i, 'id_emendamento'] = eid

# una citazione che precede la lettura formale («non possiamo aderire all'emendamento dell'onorevole Laconi»,
# letto due pagine dopo con le firme di Laconi, Grieco e Gullo) crea un record a firma singola: se il nome e' il
# primo firmatario di un emendamento con piu' firme nelle sedute vicine e i testi non sono diversi, e' lo stesso
EM['snum'] = EM.prima_seduta.str[3:].astype(int)
fusi = {}
for e in EM[EM.n_firmatari == 1].itertuples():
    cand = EM[(EM.n_firmatari >= 2) & (EM.primo == e.firmatari) & ((EM.snum - e.snum).abs() <= 3)]
    cand = [c for c in cand.itertuples() if stesso_testo(c.testo, e.testo)]
    if cand: fusi[e.id_emendamento] = cand[0].id_emendamento
if fusi:
    R['id_emendamento'] = R.id_emendamento.map(lambda x: fusi.get(x, x))
    EM = EM[~EM.id_emendamento.isin(fusi)]
EM = EM.drop(columns='snum')
print('citazioni singole assorbite nell\'emendamento a piu\' firme:', len(fusi))

os.makedirs(OUT, exist_ok=True)
R.drop(columns=['pos', 'snum']).to_csv(os.path.join(OUT, 'menzioni.csv'), index=False)
F.to_csv(os.path.join(OUT, 'menzioni_nomi.csv'), index=False)
EM.to_csv(os.path.join(OUT, 'emendamenti.csv'), index=False)
two = EM.assign(id_dep=EM.firmatari.str.split('|')).explode('id_dep')[['id_emendamento', 'id_dep']]
two.to_csv(os.path.join(OUT, 'edgelist_emendamenti.csv'), index=False)
print(f"menzioni {len(R)} (firme {int((R.fonte=='firma').sum())}, presentazioni {int((R.fonte=='presentazione').sum())})")
print(f"emendamenti {len(EM)}; con 2+ firmatari {int((EM.n_firmatari>=2).sum())}; completi {int(EM.completo.sum())}")
print('abbinamento dei nomi:', F.abbinamento.value_counts().to_dict())
