# Le reti dell'Assemblea Costituente (1946–1948)
### The networks of the Italian Constituent Assembly (1946–1948)

[![DOI](https://zenodo.org/badge/1433417579.svg)](https://doi.org/10.5281/zenodo.23646592)
[![Data: CC BY-SA 4.0](https://img.shields.io/badge/data-CC%20BY--SA%204.0-blue.svg)](https://creativecommons.org/licenses/by-sa/4.0/)
[![Code: MIT](https://img.shields.io/badge/code-MIT-green.svg)](LICENSE)

Un dataset di reti sui 581 membri dell'Assemblea Costituente italiana, per la
ricerca e per l'insegnamento dell'analisi delle reti sociali.
Oltre alla rete formale dell'appartenenza agli organi, contiene reti di
interazione ricostruite dall'attività quotidiana in Aula: temi di discussione
condivisi, co-presenza nei resoconti, emendamenti firmati insieme e votazioni
per appello nominale. Le ultime due sono estratte con l'OCR dai resoconti a
stampa, e la loro accuratezza è misurata e dichiarata.

*A network dataset on the 581 members of the Italian Constituent Assembly, for
research and for teaching social network analysis. Alongside
the formal network of membership of the Assembly's bodies, it contains
interaction networks reconstructed from day-to-day activity in the chamber:
shared discussion topics, co-presence in the proceedings, co-signed amendments
and roll-call votes. The last two are extracted from the printed records by
OCR, and their accuracy is measured and reported.*

---

## Cosa c'è qui / What is here

| Cartella | Contenuto | Contents |
|---|---|---|
| `data/it/` | I file finali, in italiano, con il codebook | The final files, in Italian, with the codebook |
| `data/en/` | Gli stessi file, in inglese | The same files, in English |
| `pipeline/` | Il codice che ricostruisce emendamenti e voti dai resoconti | The code that rebuilds amendments and votes from the records |

Le due cartelle `data/it` e `data/en` contengono gli stessi dati:
cambiano i nomi dei file, delle colonne e delle etichette, e il codebook.
Ogni cartella è autosufficiente.

*The two folders hold the same data: file names, column names, labels and the
codebook differ. Each folder stands on its own.*

**Cominciare dal codebook.** `data/it/codebook.md` (o `data/en/codebook.md`)
descrive ogni file, ogni variabile, come sono state costruite le reti e quali
errori contengono. — *Start from the codebook.*

---

## Caricare i dati / Loading the data

```r
# R — rete two-mode costituente × organo
library(igraph)

base  <- "data/it/"
nodi  <- read.csv(paste0(base, "costituenti_nodi.csv"))
archi <- read.csv(paste0(base, "edgelist.csv"))     # id_dep, id_organo, ruolo, inizio, fine

g <- graph_from_data_frame(archi[, c("id_dep", "id_organo")], directed = FALSE)
V(g)$type <- V(g)$name %in% archi$id_organo          # two-mode
costituenti <- bipartite_projection(g)$proj1         # chi condivide un organo
```

```python
# Python
import pandas as pd, networkx as nx

base = "data/en/"
edges = pd.read_csv(base + "edgelist_amendments.csv")   # id_member, id_amendment
G = nx.from_pandas_edgelist(edges, "id_member", "id_amendment")
```

I file sono CSV con intestazione, codifica UTF-8 (con BOM nei file di verifica),
separatore virgola. Gli identificativi dei costituenti (`id_dep`) sono quelli
della Camera dei deputati e permettono di agganciare altre fonti.

*CSV with a header row, UTF-8, comma-separated. Member identifiers (`id_dep`)
are the Chamber of Deputies' own, so other sources can be joined on them.*

---

## Rifare tutto da zero / Reproducing the data

I PDF dei resoconti non sono in questo repository: gli script li scaricano dal
sito della Camera (sono atti ufficiali, non coperti da diritto d'autore).
Servono R con i pacchetti `tesseract`, `pdftools` e `magick`, Python 3 con
`pandas`, `numpy` e `pillow`, e Tesseract con la lingua italiana.

*The record PDFs are not in this repository: the scripts download them from the
Chamber's site. You need R with `tesseract`, `pdftools` and `magick`, Python 3
with `pandas`, `numpy` and `pillow`, and Tesseract with the Italian language.*

Tutto in un comando, da qualunque cartella (gli script trovano da soli la cartella del repository):
*Everything in one command, from any folder:*

```bash
caffeinate -i bash ~/Documents/Papers/SNA-Dataset/Costituenti/aggiorna_dati.sh   # --senza-ocr per saltare l'OCR
```

Oppure i singoli passi, dalla cartella del repository / *or step by step, from the repository folder*:

```bash
# 1. OCR a 300 dpi di tutte le sedute (lungo: molte ore)
Rscript pipeline/ocr_costituente.R

# 2. Rilettura a 400 dpi delle pagine difficili
Rscript pipeline/ocr_400dpi.R

# 3. Estrazione di emendamenti e voti
python3 pipeline/tools/estrai_emendamenti.py pipeline
python3 pipeline/tools/estrai_voti.py pipeline

# 3b. Test di non-regressione delle regole (un secondo; da lanciare dopo ogni modifica all'estrattore)
python3 pipeline/tools/test_regole.py

# 4. File finali, correzioni manuali, etichette e misure di accuratezza
python3 pipeline/esporta_dataset.py
```

Gli script si possono interrompere e rilanciare: riprendono da dove erano
arrivati. Il passo 1 è quello che costa; i passi 3 e 4 durano pochi minuti.

*The scripts can be stopped and restarted: they resume where they left off.
Step 1 is the expensive one; steps 3 and 4 take a few minutes.*

---

## Quanto sono accurati emendamenti e voti / How accurate are the amendments and votes

Gli emendamenti non esistono come dato strutturato: sono ricavati dal testo dei
resoconti, e contengono errori. Sono stati misurati su campioni letti a mano
sull'immagine della pagina.

*Amendments do not exist as structured data: they are derived from the text of
the records and contain errors. They were measured on samples read by hand
against the page image.*

Le stime qui sotto vengono da un campione di 80 record estratto a caso **dopo**
le correzioni all'estrattore, fra record mai esaminati prima: è indipendente
dalla taratura. In tutto sono stati verificati a mano 219 record.

*The estimates below come from a sample of 80 records drawn at random **after**
the fixes to the extractor, among records never examined before: it is
independent of the tuning. 219 records have been verified by hand in all.*

- **Falsi positivi** (record che non sono emendamenti con quei firmatari):
  2 su 80 = 2,5% (IC 95%: 0,7–8,7). — *False positives: 2 of 80.*
- **Firmatari mancanti o errati**: 6 su 78 = 7,7% (IC 95%: 3,6–15,8); 13,2% fra
  gli emendamenti con due o più firmatari. — *Missing or wrong signatories.*

Quattro dei sei elenchi incompleti sono stati corretti dopo la misura, che è
quindi una stima conservativa. — *Four of the six incomplete lists were fixed
after the measurement, so the figure is conservative.*

Il codebook spiega come sono stati costruiti i campioni, quali errori restano e
perché. I voti hanno un controllo diverso: il confronto fra i nomi estratti e i
totali ufficiali annunciati in Aula, riportato in `voti_nodi.csv`.

*The codebook explains how the samples were drawn, which errors remain and why.
Votes are checked differently: extracted names against the official totals
announced in the chamber, reported in `voti_nodi.csv`.*

---

## Limiti noti / Known limitations

- Gli emendamenti coprono le sedute dell'Aula, non i lavori delle commissioni.
- Gli elenchi di firmatari chiusi da «ed altri» sono marcati `completo = 0`:
  i firmatari successivi non sono noti.
- Interrogazioni, interpellanze, mozioni, ordini del giorno e richieste di
  votazione non entrano nella rete degli emendamenti: formano uno strato a parte
  (`altri_atti_nodi.csv`, `edgelist_altri_atti.csv`).
- Il dataset contiene circa due terzi degli emendamenti stampati nelle sedute
  trascritte, nove su dieci di quelli con più firmatari (gli unici che creano
  legami): le misure di volume della rete sono limiti inferiori.
- Il riconoscimento dei nomi è ottimo ma non perfetto: il codebook riporta la
  distribuzione dei tipi di abbinamento.

*Amendments cover sittings of the chamber, not committee work. Signatory lists
ending in «ed altri» (and others) are flagged `complete = 0`. Parliamentary
questions, interpellations, motions, orders of the day and vote requests are kept
out of the amendment network and form a separate layer (`other_acts_nodes.csv`).
The dataset holds about two thirds of the amendments printed in the transcribed
sittings, nine in ten of the multi-signatory ones: network volume measures are
lower bounds. Name matching is good but
not perfect; the codebook reports the distribution of match types.*

---

## Fonti / Sources

| Fonte | Licenza |
|---|---|
| Camera dei deputati — [dati.camera.it](https://dati.camera.it), [costituente.camera.it](https://costituente.camera.it) | CC BY-SA 3.0 |
| Senato della Repubblica — [dati.senato.it](https://dati.senato.it) | CC BY 3.0 |
| Resoconti dell'Assemblea Costituente | Atti ufficiali, art. 5 l. 633/1941 |
| Wikidata | CC0 |
| Wikipedia italiana | CC BY-SA 4.0 |

## Licenze / Licences

Dati (`data/`): **CC BY-SA 4.0**. Codice (`pipeline/`): **MIT**.
Il vincolo ShareAlike sui dati deriva dalle fonti, non è una scelta.
Vedi [LICENSE](LICENSE).

*Data: CC BY-SA 4.0. Code: MIT. The ShareAlike condition on the data comes from
the sources, not from a preference.*

## Citazione / Citation

Melli, G. (2026). *The networks of the Italian Constituent Assembly (1946–1948)*
[Data set]. Zenodo. https://doi.org/10.5281/zenodo.23646592

Vedi [CITATION.cff](CITATION.cff) per il formato leggibile dalle macchine.

## Contatti / Contact

Giacomo Melli — Department of Sociology, University of Oxford
[giacomo.melli@sociology.ox.ac.uk](mailto:giacomo.melli@sociology.ox.ac.uk) ·
[www.giacomomelli.com](https://www.giacomomelli.com)

Segnalazioni di errori nei dati sono benvenute: apri una *issue* indicando il
file, la riga e la pagina del resoconto. — *Reports of errors in the data are
welcome: open an issue giving the file, the row and the page of the record.*
