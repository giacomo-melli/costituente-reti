"""Rielezione alla Camera nel 1948 (punto 26): `eletto_camera_1948`.

Fonte: elenco degli eletti alla Camera nelle elezioni del 18 aprile 1948 per circoscrizione, da Wikipedia
(pipeline/fonti/eletti_camera_1948_wikipedia.txt, con l'indirizzo e la data di consultazione). Esclusi i subentrati.
Abbinamento: stesso cognome in fondo al nome e nome proprio compatibile (uguale, contenuto nell'altro
— Raimondo/Pierraimondo — o molto simile — Ferdinando/Fernando —, ma non lo stesso nome al maschile e al femminile).
Giudice esterno: ogni eletto abbinato deve risultare deputato della Repubblica nei dati della Camera (`deputato_rep`).
Il Senato del 1948 (eletti e senatori di diritto) non e' coperto: manca una fonte completa raggiungibile."""
import os, re, unicodedata, difflib
import pandas as pd
QUI = os.path.dirname(os.path.abspath(__file__)); RADICE = os.path.dirname(os.path.dirname(QUI))
n = lambda s: re.sub(r'\s+', ' ', re.sub(r'[^a-z ]', ' ', unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower())).strip()
L = [n(l) for l in open(os.path.join(os.path.dirname(QUI), 'fonti', 'eletti_camera_1948_wikipedia.txt'), encoding='utf-8') if l.strip() and not l.startswith('#')]
def simile(a, b):
    if a[:-1] == b[:-1] and a != b: return False          # Mario / Maria
    return a in b or b in a or difflib.SequenceMatcher(None, a, b).ratio() >= 0.75
def eletto(cognome, nome):
    cg = n(cognome); nm = n(nome).split()
    return int(any(l.endswith(' ' + cg) and nm and any(simile(nm[0], p) for p in l[:-len(cg) - 1].split()) for l in L))
if __name__ == '__main__':
    C = pd.read_csv(os.path.join(RADICE, 'data', 'it', 'costituenti_nodi.csv'))
    e = [eletto(c, x) for c, x in zip(C.cognome, C.nome)]
    print('eletti alla Camera nel 1948:', sum(e), '| di cui non deputati della Repubblica nei dati Camera:', sum(1 for a, d in zip(e, C.deputato_rep) if a and d == 0))
