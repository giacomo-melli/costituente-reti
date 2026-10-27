# Changelog

Cosa cambia in ogni versione del dataset, così chi cita una versione sa che cosa ha in mano.
*What changes in each version, so that whoever cites a version knows what it contains.*

## 1.1.0 — in preparazione / in preparation

### Emendamenti / Amendments

- **Recall misurato per la prima volta.** 14 sedute estratte a caso sono state lette per intero sull'immagine, contando ogni emendamento stampato. Sul campione di convalida il recall è del 67% (IC 95% 49–81) per tutti gli emendamenti e del 90% per quelli con più firmatari, che sono gli unici a produrre legami. Nella versione 1.0.0 era del 57%.
  *Recall measured for the first time on 14 randomly drawn sittings read in full: 67% on the validation sample (90% for multi-signatory amendments, which alone produce edges), up from 57% in 1.0.0.*
- **Correzioni generali all'estrattore**, tutte documentate nel codebook: la formula «L'onorevole X ha presentato il seguente emendamento», le forme «dall'onorevole», «della onorevole», «dal collega», «unitamente agli onorevoli», le proposte di chi parla, la sillabazione con segni spuri, il consolidamento che fondeva emendamenti diversi dello stesso firmatario, e diverse famiglie di falsi positivi (elenchi di oratori, atti distinti, interrogazioni, richieste di votazione).
  *General fixes to the extractor (see the codebook): new presentation formulas, hyphenation with stray marks, consolidation that merged different amendments by the same signatory, and several false-positive families.*
- **Tutti i 388 emendamenti con più firmatari controllati sull'immagine** almeno una volta (216 per la prima volta): falsi positivi 4,2%, firmatari errati 4,3%. Una seconda lettura cieca di 50 record concorda con la prima in tutti i casi decidibili (kappa 1,00).
  *All 388 multi-signatory amendments checked against the image; a blind second reading of 50 records agrees in every decidable case.*
- **Emendamenti a firma singola**: due campioni ciechi sull'immagine (60 + 50). Nel secondo, dopo le correzioni del primo, gli errori veri sono 2/48 (4,2%), più 4 record nati da una citazione nel discorso di un altro, che corrispondono comunque a un emendamento vero di quella persona. Corrette tre nuove famiglie, recuperati due elenchi pluri-firmati (sed124, sed343).
  *Singles: two blind image samples; in the second, 2/48 true errors (4.2%) plus 4 records born from a citation of a real amendment. Three more families fixed, two multi-signatory lists recovered.*
- Emendamenti 718 → 1.385; con 2+ firmatari 329 → 388; legami di co-firma 2.269 → 3.176.

### Variabili nuove / New variables

- `emendamenti_nodi.csv`: `testo` (testo stampato dell'emendamento), `tipo_emendamento` (sostituire, sopprimere, aggiungere, inserire), `id_presentatore`, `presentatore_fonte`. EN: `text_it`, `amendment_type`, `id_proposer`, `proposer_source`.
- `edgelist_emendamenti.csv`: `ruolo` (presentatore / firmatario), per la rete diretta di chi raccoglie e chi concede firme. EN: `role`.

### File nuovi / New files

- `menzioni_discorso.csv` (EN `speech_mentions.csv`): rete diretta delle menzioni nei discorsi, chi nomina chi in Aula; 9.194 menzioni, 3.743 coppie dirette.
- `pipeline/tools/test_regole.py`: test di non-regressione delle regole di estrazione (57 passi veri, 58 controlli).
- `pipeline/tools/estrai_menzioni_discorso.py`, `pipeline/tools/coesione_voto.py`, `pipeline/tools/ritaglia.py`, `pipeline/tools/qualita_ocr.py` (qualità dell'OCR per pagina, `pipeline/extraction/qualita_pagine.csv`).
- File di verifica in `pipeline/extraction/VERIFICA_*`: recall, precisione, pluri-firmati, kappa, menzioni.

### Voti / Votes

- 27 votazioni. Aggiunto il controllo di validità con l'indice di Rice per gruppo: PCI 0,996, DC 0,983.
  *Added a Rice-index validity check (PCI 0.996, DC 0.983).*
- Le cinque votazioni «senza totali» sono state lette sull'immagine. Quattro (v4, v10, v13, v23) sono nulle per mancanza del numero legale: nuova variabile `numero_legale_mancato` (EN `quorum_failed`). La quinta (v24) aveva i totali stampati nella formula «Voti favorevoli / contrari», ora letta, con due cifre storpiate dall'OCR corrette dall'aritmetica del riquadro. Controllo: 21 ok, 2 verificati, 4 nulle, 0 senza totali.
  *The five votes «without totals» were read on the image: four are void for lack of quorum (new variable `quorum_failed`); the fifth had its totals printed as «Voti favorevoli / contrari», now read.*
- L'ordine alfabetico degli elenchi controlla ora anche gli abbinamenti approssimati: sei nomi attribuiti alla persona sbagliata sono stati corretti (Vanoni, Iotti, Pella, Marina, Massini, Montini tolti; Giolitti, Preti, Cassiani aggiunti), e sono stati recuperati Carpano Maglioli (v24) e Maria Jervolino (v7, v14). Legami: sei tolti e sei aggiunti, totale invariato (9.119).
  *Alphabetical order now also checks approximate matches: six wrong attributions fixed, three members recovered.*

## 1.0.0 — 25.10.2026

Prima versione pubblica. *First public version.* DOI 10.5281/zenodo.23646593.
