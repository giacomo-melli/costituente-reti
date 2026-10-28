# Changelog

Cosa cambia in ogni versione del dataset, così chi cita una versione sa che cosa ha in mano.
*What changes in each version, so that whoever cites a version knows what it contains.*

## 1.1.0 — in preparazione / in preparation

### Emendamenti / Amendments

- **Recall misurato per la prima volta.** 14 sedute estratte a caso sono state lette per intero sull'immagine, contando ogni emendamento stampato. Sul campione di convalida il recall è del 67% (IC 95% 49–81) per tutti gli emendamenti e del 90% per quelli con più firmatari, che sono gli unici a produrre legami. Nella versione 1.0.0 era del 57%.
  *Recall measured for the first time on 14 randomly drawn sittings read in full: 67% on the validation sample (90% for multi-signatory amendments, which alone produce edges), up from 57% in 1.0.0.*
- **Correzioni generali all'estrattore**, tutte documentate nel codebook: la formula «L'onorevole X ha presentato il seguente emendamento», le forme «dall'onorevole», «della onorevole», «dal collega», «unitamente agli onorevoli», le proposte di chi parla, la sillabazione con segni spuri, il consolidamento che fondeva emendamenti diversi dello stesso firmatario, e diverse famiglie di falsi positivi (elenchi di oratori, atti distinti, interrogazioni, richieste di votazione).
  *General fixes to the extractor (see the codebook): new presentation formulas, hyphenation with stray marks, consolidation that merged different amendments by the same signatory, and several false-positive families.*
- **Tutti i 394 emendamenti con più firmatari controllati sull'immagine** almeno una volta (216 per la prima volta): falsi positivi 4,2%, firmatari errati 4,3%. Una seconda lettura cieca di 50 record concorda con la prima in tutti i casi decidibili (kappa 1,00).
  *All 394 multi-signatory amendments checked against the image; a blind second reading of 50 records agrees in every decidable case.*
- **Emendamenti a firma singola**: due campioni ciechi sull'immagine (60 + 50). Nel secondo, dopo le correzioni del primo, gli errori veri sono 2/48 (4,2%), più 4 record nati da una citazione nel discorso di un altro, che corrispondono comunque a un emendamento vero di quella persona. Corrette tre nuove famiglie, recuperati due elenchi pluri-firmati (sed124, sed343).
  *Singles: two blind image samples; in the second, 2/48 true errors (4.2%) plus 4 records born from a citation of a real amendment. Three more families fixed, two multi-signatory lists recovered.*
- Nuove famiglie corrette nell'estrattore: due punti dopo «dagli onorevoli:», verbo con accento spurio, «proposta di articolo… a firma degli», emendamento letto dopo un'interpellanza, blocco di emendamenti dopo un altro atto, singoli con testo proprio non più assorbiti in un elenco dello stesso primo firmatario (17 emendamenti distinti tornano separati), «fatto ‘proprio» con apice spurio.
  *More extractor families fixed; four lists of up to 42 signatories recovered.*
- **16 sedute aggiunte** (giorni di discussione del progetto che mancavano al corpus, ora 189 sedute): 126 emendamenti, 33 con più firmatari, tutti controllati sull'immagine; 2 falsi positivi e 4 elenchi incompleti trovati e corretti con sei nuove regole generali (formula al futuro «presenterò… firmato anche dagli», «presentato dall'onorevole X… reca anche le firme», «ha facoltà di svolgere… reca anche le firme», punto esclamativo spurio a fine riga, «ed astri», accento spurio). Un elenco troncato da «ed altri» nella stessa pagina dell'elenco completo è ora unito a quello.
  *16 sittings added (189 in all): 126 amendments, all 33 multi-signatory ones checked on the image; six more general rules.*
- **Casi aperti decisi tutti** sull'immagine (`pipeline/CASI_APERTI.xlsx`), con l'elenco degli incerti nel codebook; le decisioni non dipendono più dalla numerazione dei voti e restano nel foglio.
  *All open cases decided on the image; uncertain ones listed in the codebook.*
- Emendamenti 718 → 1.533; con 2+ firmatari 329 → 426; legami di co-firma 2.269 → 3.549.

### Variabili nuove / New variables

- `emendamenti_nodi.csv`: `testo` (testo stampato dell'emendamento), `tipo_emendamento` (sostituire, sopprimere, aggiungere, inserire), `id_presentatore`, `presentatore_fonte`. EN: `text_it`, `amendment_type`, `id_proposer`, `proposer_source`.
- `edgelist_emendamenti.csv`: `ruolo` (presentatore / firmatario), per la rete diretta di chi raccoglie e chi concede firme. EN: `role`.
- `emendamenti_nodi.csv`: `esito` (approvato, respinto, ritirato, decaduto, assorbito; assegnato al 17%, convalida 26/30), `articolo_in_discussione` (dall'ordine dei lavori, convalida 14/20), `materia` e `articolo_costituzione` (dalla tavola della Camera progetto → Costituzione, materia giusta 17/18), `controllo_data`. EN: `outcome`, `article_under_discussion`, `subject_title`, `constitution_article`, `date_check`.
- `edgelist_emendamenti.csv`, `edgelist_voti.csv`: `abbinamento` (criterio di riconoscimento del nome). EN: `matching`.
- `costituenti_nodi.csv`: `commissione_75`, `sottocommissione`, `comitato_redazione`, `ruolo_commissione`; `voti_in_carica`, `voti_presente`, `voti_congedo`, `voti_assente`, `quota_presenza`; `eletto_camera_1948`. EN: `committee_75`, `subcommittee`, `drafting_committee`, `committee_role`, `votes_in_office`, `votes_present`, `votes_on_leave`, `votes_absent`, `share_present`, `elected_chamber_1948`.
- `voti_nodi.csv`: `numero_legale_mancato`. EN: `quorum_failed`.
- `gruppi_periodi.csv` (EN `group_spells.csv`) e `gruppo_alla_data` negli archi di co-firma e di voto (EN `group_at_date`); `viaf_id` nei costituenti.

### File nuovi / New files

- `menzioni_discorso.csv` (EN `speech_mentions.csv`): rete diretta delle menzioni nei discorsi, chi nomina chi in Aula; 9.824 menzioni, 3.995 coppie dirette.
- `pipeline/tools/test_regole.py`: test di non-regressione delle regole di estrazione (66 passi veri, 67 controlli).
- `pipeline/tools/estrai_menzioni_discorso.py`, `pipeline/tools/coesione_voto.py`, `pipeline/tools/ritaglia.py`, `pipeline/tools/qualita_ocr.py` (qualità dell'OCR per pagina, `pipeline/extraction/qualita_pagine.csv`).
- File di verifica in `pipeline/extraction/VERIFICA_*`: recall, precisione, pluri-firmati, kappa, menzioni, singoli, esiti, articolo, altri atti.
- `altri_atti_nodi.csv`, `edgelist_altri_atti.csv` (EN `other_acts_nodes.csv`, `edgelist_other_acts.csv`): strato multiplex di 897 atti co-firmati che non sono emendamenti.
- `edgelist_*_conservativa.csv` (EN `*_conservative.csv`): reti con i soli abbinamenti esatti o corretti a mano.
- `data/graphml/`: le sei reti in GraphML; `R/00_build_networks.R`: gli oggetti `igraph`.
- `pipeline/CASI_APERTI.xlsx` e `pipeline/tools/prepara_casi_aperti.py`: i casi da decidere sulla pagina; le decisioni si applicano a ogni esportazione.
- `pipeline/sedute_non_trascritte.csv`, `pipeline/tools/scarica_pdf_mancanti.py`, `pipeline/tools/scarica_fonti_esterne.py`: sedute e dati da scaricare con la rete.
- `pipeline/fonti/`: tavola della Camera progetto → Costituzione; eletti alla Camera nel 1948.
- `paper/data_note.md`: bozza della nota sul dataset.

### Voti / Votes

- 29 votazioni (2 dalle sedute aggiunte, sed073 e sed187). **Le votazioni sono rinumerate in ordine di seduta**: gli `id_voto` della 1.0.0 non corrispondono più; si riabbinano con seduta e pagina. Aggiunto il controllo di validità con l'indice di Rice per gruppo: PCI 0,996, DC 0,985.
  *29 votes; **votes are renumbered in sitting order** (re-match 1.0.0 `id_vote` by sitting and page). Rice-index validity check (PCI 0.996, DC 0.985).*
- Totali di sed187 letti male dall'OCR (452/468) ricavati dall'ultimo numero dopo l'etichetta e da presenti meno astenuti (152/168, confermati sull'immagine). Decisioni sulla pagina: 11 voti aggiunti (uno incerto, Fuschini in sed187), due abbinamenti approssimati corretti (Bernamonti, Montagnana). Legami di voto 9.778.
  *sed187 totals repaired; 11 votes added and 2 approximate matches corrected from page decisions; 9,778 vote edges.*
- Le cinque votazioni «senza totali» sono state lette sull'immagine. Quattro (v5, v11, v14, v25 nella numerazione attuale) sono nulle per mancanza del numero legale: nuova variabile `numero_legale_mancato` (EN `quorum_failed`). La quinta (v26) aveva i totali stampati nella formula «Voti favorevoli / contrari», ora letta, con due cifre storpiate dall'OCR corrette dall'aritmetica del riquadro. Controllo: 21 ok, 2 verificati, 4 nulle, 0 senza totali.
  *The five votes «without totals» were read on the image: four are void for lack of quorum (new variable `quorum_failed`); the fifth had its totals printed as «Voti favorevoli / contrari», now read.*
- L'ordine alfabetico degli elenchi controlla ora anche gli abbinamenti approssimati: sei nomi attribuiti alla persona sbagliata sono stati corretti (Vanoni, Iotti, Pella, Marina, Massini, Montini tolti; Giolitti, Preti, Cassiani aggiunti), e sono stati recuperati Carpano Maglioli (v26) e Maria Jervolino (v8, v15; numerazione attuale). Legami: sei tolti e sei aggiunti, totale invariato (9.119).
  *Alphabetical order now also checks approximate matches: six wrong attributions fixed, three members recovered.*
- Omonimi nei voti: 7 degli 8 cognomi ambigui risolti con il nome proprio staccato dall'OCR o per esclusione degli omonimi già presenti nello stesso voto. Legami di voto 9.119 → 9.125; scarto medio dai totali ufficiali 2,61 → 2,26.
  *Namesakes in votes: 7 of 8 ambiguous surnames resolved; vote edges 9,119 → 9,125.*

## 1.0.0 — 25.10.2026

Prima versione pubblica. *First public version.* DOI 10.5281/zenodo.23646593.
