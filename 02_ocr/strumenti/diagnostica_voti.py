"""Diagnostica dei voti per appello nominale con scarto grande rispetto ai totali ufficiali
(tipicamente una colonna persa dall'OCR, ~30 nomi).

In Spyder: apri questo file e premi Run (F5). Non serve modificare nulla.

Fa tre cose, nell'ordine:
  1. LOCALIZZA  per ogni voto sospetto, conta i nomi abbinati pagina per pagina e colonna
                per colonna dentro il segmento deficitario (es. l'elenco dei «no»):
                la pagina/colonna con pochi nomi è quella sospetta.
  2. RI-OCR     scarica il PDF della seduta (se manca in pdf/) e riprova le pagine del
                segmento con parametri diversi: split colonne a 400 dpi, split a metà
                pagina, pagina intera con psm 4. Per ogni variante conta i nomi abbinati
                e mostra i nomi NUOVI rispetto al testo attuale.
  3. APPLICA    (facoltativo) sostituisce il testo di una pagina con la variante scelta,
                dopo aver salvato una copia .bak. Poi rilancia esegui_estrazione.py per
                ricontrollare i totali.

Per applicare una variante: in fondo al file, compila APPLICA e ripremi Run.
Riusa le funzioni di estrai_voti.py (norm, scomponi, nomi_da...) senza duplicarle.
"""
import os, re, sys, glob, shutil, subprocess, tempfile, urllib.request

QUI = os.path.dirname(os.path.abspath(__file__))          # .../02_ocr/strumenti
D = os.path.dirname(QUI)                                  # .../02_ocr
TXT = os.path.join(D, 'testi_colonne')
OUT = os.path.join(D, 'estrazione')

VOTI_SOSPETTI = [7, 27]       # id_voto in estrazione/voti.csv (da riga di comando: python3 diagnostica_voti.py 7)
# Varianti che preservano l'ordine di lettura (colonna sinistra poi destra) e possono
# quindi essere applicate; 'psm4_300' legge la pagina intera ed è solo diagnostica.
VARIANTI = ['colonne_400', 'meta_300', 'meta_400', 'psm4_300']

# Per applicare una variante dopo averla scelta, ad esempio:
# APPLICA = [('sed102', 16, 'meta_400')]
APPLICA = []

# ---------- importa la logica di estrai_voti.py senza eseguirne l'estrazione ----------
src = open(os.path.join(QUI, 'estrai_voti.py'), encoding='utf-8').read()
src = src.split('voti, righe = [], []')[0]                # tutto tranne il ciclo finale
_args = [a for a in sys.argv[1:] if a.isdigit()]          # prima che argv venga riassegnato
sys.argv = ['estrai_voti.py', D, OUT]
ev = {'__name__': 'estrai_voti_funzioni'}
exec(compile(src, 'estrai_voti.py', 'exec'), ev)
norm, match, scomponi, nomi_da = ev['norm'], ev['match'], ev['scomponi'], ev['nomi_da']
PROSA = ev['PROSA']
M_SI, M_NO, M_AST, M_CONG, M_END = ev['M_SI'], ev['M_NO'], ev['M_AST'], ev['M_CONG'], ev['M_END']
date, nomi = ev['date'], ev['nomi']
pd = ev['pd']

ROSTER = nomi.set_index('id_dep')

def leggi_pagina(f):
    cols = open(f, encoding='utf-8', errors='ignore').read().split('<<<COLONNA_DESTRA>>>')
    return cols + [''] * (2 - len(cols))

def flatten_cols(seduta, sostituzioni=None):
    """Come flatten() di estrai_voti.py, ma la mappa ricorda anche la colonna (0=sx, 1=dx)
    e si può sostituire il testo di singole pagine: sostituzioni={pagina: (sx, dx)}."""
    text, pm = '', []
    for f in sorted(glob.glob(os.path.join(TXT, f'{seduta}_p*.txt'))):
        p = int(re.search(r'_p(\d+)', f).group(1))
        cols = leggi_pagina(f)
        if sostituzioni and p in sostituzioni:
            cols = list(sostituzioni[p])
        for ci, col in enumerate(cols):
            pm.append((len(text), p, ci))
            col = col.replace('î', 'i').replace('Î', 'I').replace('ì ', 'i ')
            text += ' ' + re.sub(r'\s*\n\s*', ' ', col)
    return text, pm

def dove(pm, pos):
    p, c = pm[0][1], pm[0][2]
    for start, pg, ci in pm:
        if start <= pos: p, c = pg, ci
        else: break
    return p, c

def segmenti_voto(text, occorrenza):
    """Rifà la segmentazione di estrai_voti.py per la n-esima occorrenza nella seduta.
    Ritorna {'sì': (ini, fine), 'no': ...} come posizioni assolute nel testo."""
    ms = list(M_SI.finditer(text))
    m = ms[occorrenza]
    win = text[m.end():m.end() + 30000]
    mn = M_NO.search(win)
    ma = M_AST.search(win, mn.end()); mc = M_CONG.search(win, mn.end()); me = M_END.search(win, mn.end())
    stops = sorted(x.start() for x in [ma, mc, me] if x)
    end_no = stops[0] if stops else len(win)
    off = m.end()
    seg = {'sì': (off, off + mn.start()), 'no': (off + mn.end(), off + end_no)}
    if ma and ma.start() == end_no:
        nxt = min([x.start() for x in [mc, me] if x and x.start() > ma.start()] or [len(win)])
        seg['astenuto'] = (off + ma.end(), off + nxt)
    return seg

def abbinati(testo, data):
    """Insieme degli id_dep abbinati in un pezzo di testo (stessa pulizia di estrai_voti.py).
    nomi_da() si ferma alla prima riga di prosa: qui il testo viene prima spezzato sui
    tratti di prosa, così si contano anche i nomi che vengono dopo (serve per confrontare
    pagine intere, dove l'elenco può seguire il dibattito)."""
    ids = set()
    for chunk in PROSA.split(testo):
        for piece in nomi_da(chunk):
            for nm, r, how in scomponi(piece, data):
                if r is not None:
                    ids.add(r.id_dep)
    return ids

def chi(ids):
    return ', '.join(sorted(f"{ROSTER.loc[i, 'cognome']} {ROSTER.loc[i, 'nome']}" for i in ids))

# ---------- ri-OCR ----------
def tessdata():
    """Copia ita.traineddata in una cartella temporanea leggibile (come ocr_pagina.sh);
    se /tmp/td appartiene a un altro utente, ne usa una propria; male che vada legge
    direttamente da strumenti/."""
    for td in ('/tmp/td', os.path.join(tempfile.gettempdir(), f'td_{os.getuid()}')):
        dst = os.path.join(td, 'ita.traineddata')
        try:
            os.makedirs(td, exist_ok=True)
            if not os.path.exists(dst):
                shutil.copy(os.path.join(QUI, 'ita.traineddata'), dst)
            with open(dst, 'rb') as fh:
                fh.read(1)
            return td
        except OSError:
            continue
    return QUI

def scarica_pdf(seduta):
    os.makedirs(os.path.join(D, 'pdf'), exist_ok=True)
    pdf = os.path.join(D, 'pdf', f'{seduta}.pdf')
    if not os.path.exists(pdf):
        url = f'https://documenti.camera.it/_dati/costituente/lavori/Assemblea/{seduta}/{seduta}nc.pdf'
        print(f'  scarico {url}')
        urllib.request.urlretrieve(url, pdf)
    return pdf

def rendi(pdf, pagina, dpi, w):
    subprocess.run(['pdftoppm', '-r', str(dpi), '-f', str(pagina), '-l', str(pagina),
                    '-gray', '-png', pdf, os.path.join(w, f'pg{dpi}')], check=True)
    return glob.glob(os.path.join(w, f'pg{dpi}-*.png'))[0]

def ocr(png, w, psm, dpi, td):
    base = os.path.join(w, f'ocr_{os.path.basename(png)}_{psm}')
    subprocess.run(['tesseract', png, base, '-l', 'ita', '--tessdata-dir', td,
                    '--psm', str(psm), '--dpi', str(dpi)],
                   check=True, env={**os.environ, 'OMP_THREAD_LIMIT': '1'},
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return open(base + '.txt', encoding='utf-8', errors='ignore').read()

def split_colonne(png, w, modo):
    """Ritorna (png_sx, png_dx). modo='auto' usa colonne.py; 'meta' taglia a metà."""
    pre = os.path.join(w, f'c_{modo}_{os.path.basename(png)}')
    if modo == 'auto':
        r = subprocess.run([sys.executable, os.path.join(QUI, 'colonne.py'), png, pre],
                           capture_output=True)
        if r.returncode == 0:
            return pre + '_L.png', pre + '_R.png'
        modo = 'meta'
    from PIL import Image
    im = Image.open(png).convert('L'); W, H = im.size
    im.crop((0, 0, W // 2, H)).save(pre + '_L.png')
    im.crop((W // 2, 0, W, H)).save(pre + '_R.png')
    return pre + '_L.png', pre + '_R.png'

CACHE = os.path.join(OUT, 'diagnostica_cache')

def varianti_pagina(seduta, pagina, w, td):
    """Ritorna {nome_variante: (testo_sx, testo_dx)}; per psm4 tutto in sx.
    Le varianti già in diagnostica_cache/ vengono rilette, non ricalcolate:
    si può interrompere e rilanciare senza perdere il lavoro fatto."""
    os.makedirs(CACHE, exist_ok=True)
    out, mancanti = {}, []
    for nome in VARIANTI:
        fc = os.path.join(CACHE, f'{seduta}_p{pagina:03d}_{nome}.txt')
        if os.path.exists(fc):
            cols = open(fc, encoding='utf-8', errors='ignore').read().split('<<<COLONNA_DESTRA>>>')
            out[nome] = (cols[0], cols[1] if len(cols) > 1 else '')
        else:
            mancanti.append(nome)
    if not mancanti:
        return out
    pdf = scarica_pdf(seduta)
    img300 = rendi(pdf, pagina, 300, w) if {'meta_300', 'psm4_300'} & set(mancanti) else None
    img400 = rendi(pdf, pagina, 400, w) if {'colonne_400', 'meta_400'} & set(mancanti) else None
    for nome, img, dpi, modo in [('colonne_400', img400, 400, 'auto'),
                                 ('meta_300', img300, 300, 'meta'),
                                 ('meta_400', img400, 400, 'meta')]:
        if nome not in mancanti: continue
        L, R = split_colonne(img, w, modo)
        out[nome] = (ocr(L, w, 6, dpi, td), ocr(R, w, 6, dpi, td) if os.path.getsize(R) else '')
    if 'psm4_300' in mancanti:
        out['psm4_300'] = (ocr(img300, w, 4, 300, td), '')
    for nome in mancanti:
        sx, dx = out[nome]
        with open(os.path.join(CACHE, f'{seduta}_p{pagina:03d}_{nome}.txt'), 'w', encoding='utf-8') as fh:
            fh.write(sx + '\n<<<COLONNA_DESTRA>>>\n' + dx)
    return out

# ---------- programma ----------
if _args:                                            # in Spyder non ce ne sono: usa il default
    VOTI_SOSPETTI = [int(a) for a in _args]
V = pd.read_csv(os.path.join(OUT, 'voti.csv'))
V['occorrenza'] = V.groupby('seduta').cumcount()

for _, voto in V[V.id_voto.isin(VOTI_SOSPETTI)].iterrows():
    s, data = voto.seduta, voto.data
    print(f"\n{'=' * 70}\nVOTO {voto.id_voto}  {s}  {data}  —  {voto.controllo}")
    print(f"  sì: {voto.si_abbinati} abbinati / {voto.si_ufficiali} ufficiali  (scarto {voto.scarto_si})")
    print(f"  no: {voto.no_abbinati} abbinati / {voto.no_ufficiali} ufficiali  (scarto {voto.scarto_no})")
    text, pm = flatten_cols(s)
    segs = segmenti_voto(text, int(voto.occorrenza))

    # 1. LOCALIZZA: conta i nomi per pagina/colonna nel segmento deficitario
    deficit = [k for k, sc in [('sì', voto.scarto_si), ('no', voto.scarto_no)]
               if pd.notna(sc) and sc < -5] or ['sì', 'no']
    pagine_da_provare = set()
    for quale in deficit:
        ini, fine = segs[quale]
        print(f"\n  elenco dei «{quale}» (mancano {abs(int(voto['scarto_' + ('si' if quale == 'sì' else 'no')]))} nomi):")
        bordi = [b for b in pm if ini <= b[0] < fine]
        bordi = [(ini, *dove(pm, ini))] + bordi + [(fine, None, None)]
        for (a, pg, ci), (b, _, _) in zip(bordi, bordi[1:]):
            n = len(abbinati(text[a:b], data))
            print(f"    pag. {pg:>3} col. {'sx' if ci == 0 else 'dx'}  caratteri {b - a:>5}  nomi abbinati {n:>3}")
            pagine_da_provare.add(pg)

    # 2. RI-OCR delle pagine del segmento
    td = tessdata()
    for pg in sorted(pagine_da_provare):
        print(f"\n  ri-OCR di {s} pagina {pg}:")
        f_attuale = os.path.join(TXT, f'{s}_p{pg:03d}.txt')
        base_ids = abbinati(' '.join(leggi_pagina(f_attuale)), data)
        print(f"    attuale                nomi sulla pagina {len(base_ids):>3}")
        with tempfile.TemporaryDirectory() as w:
            try:
                vv = varianti_pagina(s, pg, w, td)
            except Exception as e:
                print(f"    ERRORE nel ri-OCR: {e}"); continue
            for nome, (sx, dx) in vv.items():
                ids = abbinati(sx + ' ' + dx, data)
                nuovi = ids - base_ids
                persi = base_ids - ids
                print(f"    {nome:<22} nomi sulla pagina {len(ids):>3}  nuovi {len(nuovi):>2}  persi {len(persi):>2}")
                if nuovi: print(f"      + {chi(nuovi)}")
                if persi: print(f"      - {chi(persi)}")

# 3. APPLICA (se richiesto)
for s, pg, nome in APPLICA:
    if nome == 'psm4_300':
        print(f"\n{nome} legge la pagina intera e può mescolare le colonne: solo diagnostica, non applicabile."); continue
    src_f = os.path.join(CACHE, f'{s}_p{pg:03d}_{nome}.txt')
    dst_f = os.path.join(TXT, f'{s}_p{pg:03d}.txt')
    shutil.copy(dst_f, dst_f.replace('.txt', '.bak'))
    shutil.copy(src_f, dst_f)
    print(f"\napplicata {nome} a {s} p.{pg} (copia di riserva in .bak). Rilancia esegui_estrazione.py.")

print('\nFatto.')
