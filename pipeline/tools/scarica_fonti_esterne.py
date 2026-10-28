"""Scarica dalle fonti ufficiali i dati che servono ai punti 11 (gruppo alla data) e 15 (VIAF).
Va lanciato sul computer, con la connessione a Internet (la macchina di lavoro della pipeline non la ha):

    python3 pipeline/tools/scarica_fonti_esterne.py

Scrive in pipeline/fonti/ i dati grezzi, senza interpretarli:
  camera_legislature.csv        le legislature dell'endpoint della Camera (per trovare quella della Costituente)
  camera_adesioni_gruppi.csv    per ogni deputato della Costituente, tutte le proprieta' delle sue adesioni ai gruppi
                                (gruppo, date di inizio e fine come le pubblica la Camera)
  wikidata_viaf.csv             qid -> identificativo VIAF (P214) per i costituenti che hanno un qid
L'interpretazione (gruppi_periodi.csv, viaf_id) si fa dopo, sui file scaricati, cosi' ogni passo resta verificabile.
Solo librerie standard di Python."""
import csv, json, os, sys, time, urllib.parse, urllib.request
QUI = os.path.dirname(os.path.abspath(__file__)); FONTI = os.path.join(os.path.dirname(QUI), 'fonti'); os.makedirs(FONTI, exist_ok=True)
RADICE = os.path.dirname(os.path.dirname(QUI))
UA = {'User-Agent': 'costituente-reti/1.1 (dataset accademico; contatto: bkupgime@gmail.com)', 'Accept': 'application/sparql-results+json'}

def sparql(endpoint, q):
    url = endpoint + '?' + urllib.parse.urlencode({'query': q, 'format': 'json'})
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
        d = json.load(r)
    v = d['head']['vars']
    return v, [[b.get(k, {}).get('value', '') for k in v] for b in d['results']['bindings']]

def salva(nome, v, righe):
    with open(os.path.join(FONTI, nome), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(v); w.writerows(righe)
    print(nome, len(righe), 'righe')

CAM = 'https://dati.camera.it/sparql'
v, leg = sparql(CAM, """PREFIX ocd: <http://dati.camera.it/ocd/> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?leg ?label WHERE { ?leg a ocd:legislatura . OPTIONAL { ?leg rdfs:label ?label } }""")
salva('camera_legislature.csv', v, leg)
cost = [l for l, lab in leg if 'ostituent' in (lab + l)]
if not cost: sys.exit('Legislatura della Costituente non trovata: guarda camera_legislature.csv')
print('Costituente:', cost[0])
v, ad = sparql(CAM, f"""PREFIX ocd: <http://dati.camera.it/ocd/>
SELECT ?deputato ?adesione ?proprieta ?valore WHERE {{
  ?deputato a ocd:deputato ; ocd:rif_leg <{cost[0]}> ; ocd:aderisce ?adesione .
  ?adesione ?proprieta ?valore }}""")
salva('camera_adesioni_gruppi.csv', v, ad)
# gruppi: etichette dei gruppi a cui le adesioni rimandano
gruppi = sorted({val for _, _, p, val in ad if val.startswith('http://dati.camera.it/ocd/gruppoParlamentare')})
righe = []
for i in range(0, len(gruppi), 40):
    vals = ' '.join(f'<{g}>' for g in gruppi[i:i + 40])
    v2, r = sparql(CAM, f"""SELECT ?gruppo ?proprieta ?valore WHERE {{ VALUES ?gruppo {{ {vals} }} ?gruppo ?proprieta ?valore }}""")
    righe += r; time.sleep(1)
if gruppi: salva('camera_gruppi.csv', ['gruppo', 'proprieta', 'valore'], righe)
# VIAF da Wikidata
qid = []
with open(os.path.join(RADICE, 'data', 'it', 'costituenti_nodi.csv'), encoding='utf-8') as f:
    for r in csv.DictReader(f):
        if r.get('qid'): qid.append(r['qid'])
WD = 'https://query.wikidata.org/sparql'; out = []
for i in range(0, len(qid), 150):
    vals = ' '.join('wd:' + q for q in qid[i:i + 150])
    v3, r = sparql(WD, f"SELECT ?item ?viaf WHERE {{ VALUES ?item {{ {vals} }} OPTIONAL {{ ?item wdt:P214 ?viaf }} }}")
    out += [[a.rsplit('/', 1)[-1], b] for a, b in r]; time.sleep(2)
salva('wikidata_viaf.csv', ['qid', 'viaf'], out)
print('Fatto. Riapri la sessione di lavoro: i file in pipeline/fonti/ si trasformano in variabili del dataset.')
