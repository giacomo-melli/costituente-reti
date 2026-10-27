# Changelog

Cosa cambia in ogni versione del dataset, così chi cita una versione sa che cosa ha in mano.
*What changes in each version, so that whoever cites a version knows what it contains.*

## 1.1.0 — in preparazione / in preparation

### Emendamenti / Amendments

- **Recall misurato per la prima volta.** 14 sedute estratte a caso sono state lette per intero sull'immagine, contando ogni emendamento stampato. Sul campione di convalida il recall è del 67% (IC 95% 49–81) per tutti gli emendamenti e del 90% per quelli con più firmatari, che sono gli unici a produrre legami. Nella versione 1.0.0 era del 57%.
  *Recall measured for the first time on 14 randomly drawn sittings read in full: 67% on the validation sample (90% for multi-signatory amendments, which alone produce edges), up from 57% in 1.0.0.*
- **Correzioni generali all'estrattore**, tutte documentate nel codebook: la formula «L'onorevole X ha presentato il seguente emendamento», le forme «dall'onorevole», «della onorevole», «dal collega», «unitamente agli onorevoli», le proposte di chi parla, la sillabazione con segni spuri, il consolidamento che fondeva emendamenti diversi dello stesso firmatario, e diverse famiglie di falsi positivi (elenchi di oratori, atti distinti, interrogazioni, richieste di votazione).
  *General fixes to the extractor (see the codebook): new presentation formulas, hyphenation with stray marks, consolidation that merged different amendments by the same signatory, and several false-positive families.*
- **Tutti i 386 emendamenti con più firmatari controllati sull'immagine** almeno una volta (216 per la prima volta): falsi positivi 4,2%, firmatari errati 4,3%. Una seconda lettura cieca di 50 record concorda con la prima in tutti i casi decidibili (kappa 1,00).
  *All 386 multi-signatory amendments checked against the image; a blind second reading of 50 records agrees in every decidable case.*
- Emendamenti 718 → 1.397; con 2+ firmatari 329 → 386; legami di co-firma 2.269 → 3.180.

### Variabili nuove / New variables

- `emendamenti_nodi.csv`: `testo` (testo stampato dell'emendamento), `tipo_emendamento` (sostituire, sopprimere, aggiungere, inserire), `id_presentatore`, `presentatore_fonte`. EN: `text_it`, `amendment_type`, `id_proposer`, `proposer_source`.
- `edgelist_emendamenti.csv`: `ruolo` (presentatore / firmatario), per la rete diretta di chi raccoglie e chi concede firme. EN: `role`.

### File nuovi / New files

- `menzioni_discorso.csv` (EN `speech_mentions.csv`): rete diretta delle menzioni nei discorsi, chi nomina chi in Aula; 9.194 menzioni, 3.743 coppie dirette.
- `pipeline/tools/test_regole.py`: test di non-regressione delle regole di estrazione (46 passi veri).
- `pipeline/tools/estrai_menzioni_discorso.py`, `pipeline/tools/coesione_voto.py`, `pipeline/tools/ritaglia.py`.
- File di verifica in `pipeline/extraction/VERIFICA_*`: recall, precisione, pluri-firmati, kappa, menzioni.

### Voti / Votes

- Invariati (27 votazioni, 9.119 legami). Aggiunto il controllo di validità con l'indice di Rice per gruppo: PCI 0,996, DC 0,983.
  *Unchanged; added a Rice-index validity check (PCI 0.996, DC 0.983).*

## 1.0.0 — 25.10.2026

Prima versione pubblica. *First public version.* DOI 10.5281/zenodo.23646593.
