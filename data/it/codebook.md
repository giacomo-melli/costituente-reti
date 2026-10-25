# Le reti dell'Assemblea Costituente (1946–1948) — codebook

Dataset sui 581 membri dell'Assemblea Costituente italiana. Contiene una rete formale (appartenenza agli organi) e tre reti di interazione costruite dall'attività quotidiana in Aula e nelle commissioni.

**Perché 581 e non 556.** I seggi dell'Assemblea sono 556: tanti sono i deputati in carica in un dato momento, ed è il numero che si trova di solito citato. Le 581 righe di `costituenti_nodi.csv` sono invece le *persone* che quel seggio lo hanno occupato almeno un giorno fra il 1946 e il 1948. La differenza sono i ricambi: morti, dimissioni, decadenze e opzioni dei candidati eletti in più circoscrizioni, tutti rimpiazzati in corso d'opera. I campi `inizio_mandato` e `fine_mandato` permettono di ricostruire chi fosse in carica a una certa data: il 22 dicembre 1947, giorno dell'approvazione della Costituzione, erano esattamente 556. Chi preferisce lavorare sull'Assemblea come corpo di 556 membri può filtrare su quella data.

## Come fu eletta l'Assemblea

Conoscere la via per cui si arrivò a quei 581 nomi aiuta a leggere le variabili elettorali del dataset.

Si votò **domenica 2 giugno 1946**, lo stesso giorno del referendum fra monarchia e repubblica. Fu la prima elezione nazionale a **suffragio universale**: votarono i cittadini dai 21 anni compiuti, uomini e donne. Le donne elette furono 21.

Il sistema era **proporzionale a liste concorrenti**, in 32 circoscrizioni plurinominali, con un **collegio unico nazionale** al quale erano attribuiti i seggi residui: 81 dei 581 costituenti del dataset vi furono eletti, e per loro `circoscrizione` e `regione_elezione` valgono entrambe «COLLEGIO UNICO NAZIONALE». La Valle d'Aosta ebbe un collegio a seggio unico.

La legge elettorale prevedeva 573 deputati, ma ne furono eletti **556**: non si votò a Gorizia, Trieste, Pola, Fiume, Zara e Bolzano. I 581 del dataset sono i 556 più chi subentrò nel corso dei lavori (vedi «Perché 581 e non 556»).

L'Assemblea si riunì per la prima volta il **25 giugno 1946** e approvò la Costituzione il **22 dicembre 1947**, dopo 347 sedute, 170 delle quali dedicate al progetto costituzionale.

Due assenze nei dati sono legittime e non vanno lette come lacune: il campo `campo_laurea` è vuoto per chi non ha una laurea, e un costituente (Amedeo Filippo, in carica dal 13 al 18 giugno 1946) non ha gruppo parlamentare perché i gruppi si costituirono dopo la prima seduta.

Fonti di questo paragrafo: Camera dei deputati, [pagina sull'Assemblea Costituente](https://comunicazione.camera.it/eventi/80-costituente/assemblea-costituente); Wikipedia, [Assemblea Costituente (Italia)](https://it.wikipedia.org/wiki/Assemblea_Costituente_(Italia)).

**Fonti** (estrazione del 22.10.2026): Camera dei deputati, open data (dati.camera.it) e portale costituente.camera.it; Senato, open data (dati.senato.it); Wikidata; Wikipedia italiana.

## File

| File | Contenuto |
|---|---|
| `costituenti_nodi.csv` | Un record per costituente, con 99 attributi |
| `organi_nodi.csv` | 31 organi: commissioni, sottocommissioni, giunte, comitati |
| `edgelist.csv` | Rete two-mode costituente × organo (756 archi), con ruolo |
| `edgelist_periodi.csv` | Come sopra, un record per periodo di appartenenza (767) |
| `edgelist_proiezione_costituenti.csv` | Proiezione one-mode: costituenti che condividono organi (peso = n. organi) |
| `temi_nodi.csv` | 738 temi di discussione in Aula e nelle commissioni |
| `edgelist_temi.csv` | Rete two-mode costituente × tema (5.521 archi) |
| `edgelist_scambi.csv` | Rete one-mode di interazione: costituenti intervenuti sulla stessa pagina del resoconto (7.787 coppie) |
| `edgelist_corelatori.csv` | Relazioni e proposte firmate insieme (16 coppie) |
| `edgelist_sostituzioni.csv` | Rete diretta: chi è subentrato a chi in un organo (99 archi) |
| `emendamenti_nodi.csv` | 718 emendamenti presentati in Aula, estratti dai resoconti con l'OCR |
| `edgelist_emendamenti.csv` | Rete two-mode costituente × emendamento (chi ha firmato; 2.246 archi) |
| `voti_nodi.csv` | 27 votazioni per appello nominale, con totali ufficiali e controllo |
| `edgelist_voti.csv` | Rete two-mode costituente × voto, con il voto espresso (sì, no, astenuto) |
| `evidenze_wikipedia.csv` | Categorie e frasi di Wikipedia alla base degli indicatori su antifascismo e Resistenza |

Gli identificativi sono `d` + id Camera per i costituenti, `o` + id per gli organi, `t` + numero per i temi, `a` + numero per gli emendamenti, `v` + numero per i voti.

## Le reti

**Organi (formale).** Appartenenza a commissioni, sottocommissioni e giunte. È decisa dai gruppi parlamentari in proporzione alla loro forza: misura la posizione assegnata, non le scelte individuali.

**Temi (two-mode).** Un tema è un argomento discusso: in Aula il titolo del dibattito (per esempio un articolo del progetto di Costituzione), in commissione la voce in discussione (per esempio «La famiglia»). Il peso è il numero di pagine del resoconto con interventi del costituente su quel tema.

**Scambi (one-mode, non diretta).** Due costituenti sono legati se intervengono sulla stessa pagina dello stesso resoconto: una buona approssimazione del confronto diretto (botta e risposta, interruzioni, repliche). Il peso `n_pagine` conta le pagine condivise; `n_pagine_senza_presidenza` esclude le pagine in cui uno dei due presiede quell'organo, perché la presenza dei presidenti è spesso procedurale. Il legame non distingue accordo e disaccordo.

**Corelatori.** Relazioni di sottocommissione e relazioni su disegni di legge firmate da più costituenti. Rete piccola ma di collaborazione esplicita.

**Sostituzioni (diretta).** `subentrante` → `sostituito`, con organo e data.

**Emendamenti (two-mode).** Chi firma insieme un emendamento: un legame scelto, a differenza dell'appartenenza agli organi. Proiettata sui costituenti, misura la collaborazione nella stesura del testo.

**Voti nominali (two-mode, con segno).** Come ha votato ciascun costituente nelle 27 votazioni per appello nominale. Le assenze e i congedi non sono archi.

## Emendamenti e voti: costruzione e accuratezza

Le firme degli emendamenti e i voti nominali non esistono in forma strutturata: si trovano solo nei resoconti stenografici dell'Assemblea, pubblicati come immagini. Sono stati ricostruiti così (codice in `pipeline/`):

1. **OCR.** I resoconti delle 173 sedute con emendamenti o voti (4.786 pagine) sono stati convertiti in testo con Tesseract (modello italiano), separando le due colonne della pagina (`ocr_costituente.R`). Le 3.275 pagine che parlano di emendamenti sono state rilette a 400 dpi (`ocr_400dpi.R`); per ogni pagina si usa la lettura che riconosce più cognomi di costituenti.
2. **Emendamenti.** Sono riconosciuti dalle formule di presentazione («l'onorevole X ha presentato il seguente emendamento») e dai blocchi di firma in calce; il classificatore esclude interrogazioni, interpellanze, mozioni, ordini del giorno e richieste di appello nominale. I nomi sono abbinati all'elenco dei costituenti in carica alla data della seduta (`estrai_emendamenti.py`).
3. **Voti.** Per ogni votazione per appello nominale sono estratti gli elenchi «Rispondono sì», «Rispondono no», «Si sono astenuti» e «Sono in congedo», e confrontati con i totali annunciati dal Presidente (`estrai_voti.py`).
4. **Verifica.** 73 menzioni estratte a caso sono state controllate sul PDF: 40 (seme 1947) a mano, 34 da Claude (un modello di IA) sull'immagine della pagina, scelte sovrarappresentando gli emendamenti con più firmatari (seme 1948). Gli errori sistematici emersi sono stati corretti nel codice: elenchi di emendamenti distinti («gli emendamenti degli onorevoli X, Y e Z») scambiati per firme congiunte, presentatore omesso nelle formule «firmato anche dagli onorevoli», interrogazioni ai ministri, rumore dell'OCR tra i nomi. I voti con scarti superiori a tre nomi sono stati controllati sull'immagine della pagina.
5. **Completezza.** 10 pagine estratte a caso (seme 2026) sono state lette per intero da Claude per trovare gli emendamenti con più firmatari che l'estrazione non coglieva. Erano 6: ne venivano estratti correttamente 2. Le cause (la formula «Gli onorevoli X e Y hanno presentato…», «a firma degli», «insieme con gli onorevoli», blocchi di firma spezzati dall'OCR, sillabazione, rumore dell'OCR nei nomi) sono state corrette su tutto il corpus; dopo la correzione 5 dei 6 sono completi e il sesto ha 7 firmatari su 9. Una ricerca automatica delle frasi con almeno due cognomi non estratte (`cerca_mancati.py`) ha guidato le correzioni successive. Il numero di emendamenti con più firmatari è passato da 217 a 327. Una seconda verifica su altre 20 pagine (seme 2027, escluse le precedenti), condotta allo stesso modo, ha trovato 5 emendamenti con più firmatari: tutti e 5 erano estratti con l'elenco completo dei firmatari. Le altre 17 pagine non contenevano emendamenti con più firmatari; le firme multiple che vi compaiono appartengono a interrogazioni e interpellanze, che per costruzione restano fuori dal dataset. Dettaglio in `pipeline/extraction/richiamo2/ESITO.md`.

**Accuratezza degli emendamenti.** Gli emendamenti non esistono come dato strutturato: sono ricavati dal testo dei resoconti e contengono errori. Sono stati misurati su quattro campioni, leggendo ogni record sull'immagine della pagina: 219 record in tutto. I primi due (99 record) hanno guidato le correzioni dell'estrattore, quindi i loro tassi sono ottimistici per costruzione. Il terzo (40 record) e il quarto (80 record) sono stati estratti a caso **dopo** le rispettive correzioni, fra record mai guardati prima, e sono le stime da usare (intervalli di Wilson al 95%; `tools/valuta_campioni.py`):

| | campione 3 | campione 4 |
|---|---|---|
| falsi positivi | 3/40 = 7,5% (2,6–19,9) | **2/80 = 2,5% (0,7–8,7)** |
| firmatari mancanti o errati | 1/37 = 2,7% (0,5–13,8) | **6/78 = 7,7% (3,6–15,8)** |
| — fra gli emendamenti con 2+ firmatari | 1/22 = 4,5% (0,8–21,8) | 5/38 = 13,2% (5,8–27,3) |

I due campioni misurano due versioni successive dell'estrattore. Fra l'una e l'altra i falsi positivi sono stati ridotti di due terzi, perché la lettura integrale dei contesti di tutti i record ha permesso di riconoscere le forme ricorrenti e di scartarle: il nome retto da un sostantivo di atto linguistico («le parole, le dichiarazioni, l'opinione dell'onorevole X»), l'elenco di atti distinti retto da un plurale («gli emendamenti degli onorevoli X, Y e Z»), gli atti collettivi che non sono emendamenti (richieste di appello nominale, ordini del giorno, risoluzioni, lettere aperte), e il presidente di commissione che parla in quella veste.

Il quarto campione ha invece messo a fuoco il problema opposto, che il terzo aveva sottostimato: gli **elenchi di firmatari incompleti**. Le cause sono l'interruzione di riga dell'OCR dentro un cognome, le formule di cofirma non riconosciute («che reca anche le firme dei colleghi…»), e i cognomi che nel resoconto compaiono in forma diversa da quella dell'elenco ufficiale. Quattro dei sei casi trovati sono stati corretti dopo la misura, che resta quindi una stima **conservativa**: il tasso della versione pubblicata è più basso di quello dichiarato. I due residui sono errori di riconoscimento dei nomi da parte dell'OCR («Toncilo» per Tonello, «Gabriele» per Gabrieli).

**Omonimi.** Quando il resoconto stampa il solo cognome e due costituenti lo condividono (Gullo Fausto e Gullo Rocco, Mastino Pietro e Mastino Gesumino, Pajetta Gian Carlo e Pajetta Giuliano…), l'abbinamento si risolve in tre passaggi: il partito prevalente fra i cofirmatari già identificati; le firme che i candidati hanno apposto altrove insieme agli altri firmatari del gruppo; e infine la presenza in quella stessa seduta — un omonimo che in quella seduta non compare mai non può aver presentato l'emendamento. Il terzo criterio è stato verificato su 248 casi di controllo, costruiti prendendo i nomi per i quali il resoconto stampa anche il nome proprio e nascondendolo: la regola ha scelto la persona giusta 248 volte su 248. Restano 19 nomi ambigui, quasi tutti Gullo, Mastino, Mariani e Cortese, dove entrambi i candidati sono attivi nella seduta: quelle firme sono scartate, non attribuite a caso. La colonna `abbinamento` di `menzioni_nomi.csv` registra per ogni nome quale criterio è stato usato.

Gli errori trovati nei campioni sono corretti a mano nel dataset (`esporta_dataset.py`); i tassi valgono come stima per gli altri emendamenti. `completo = 0` segnala gli elenchi chiusi da «ed altri», in cui i firmatari successivi non sono noti.

**Elenchi interrotti dall'OCR.** Un segnale interno individua i record in cui la colonna ha letto più nomi di quanti ne siano stati abbinati: sono gli elenchi che la sillabazione o una riga sporca interrompe a metà («… La Rocca, Togliatti, Mora-/‘nino»). Gli undici casi del corpus sono stati letti sull'immagine della pagina. Due difetti generali ne sono emersi e sono stati corretti nell'estrattore: la sillabazione con due o tre trattini a fine riga, e il presentatore indicato solo dal nome in testa al turno di parola («LACONI. Presento all'Assemblea il seguente emendamento firmato anche dai colleghi…»). Le restanti differenze sono correzioni puntuali registrate in `esporta_dataset.py`, fra cui un emendamento che aveva assorbito un firmatario di quello stampato sopra. In tutto i legami di co-firma passano da 2.246 a 2.269.

**Accuratezza dei voti.** Su 22 voti con totali ufficiali, 20 hanno uno scarto di al massimo tre nomi per lato tra nomi abbinati e totali (`controllo = ok`); per cinque voti il resoconto non riporta i totali (`senza totali`). Nei voti v16 e v21 l'estrazione è fedele alla pagina, ma è l'elenco stampato a non coincidere con i totali annunciati (`verificato: …`). Due totali ufficiali letti male dall'OCR sono stati corretti sull'immagine (v7 e v27).

Gli elenchi dell'appello nominale sono stampati in ordine alfabetico, e questo è un vincolo esterno sfruttabile: un cognome storpiato dall'OCR («CARIEPA», «LACOTII», «VANOM») può essere cercato solo fra i cognomi compresi fra il precedente e il successivo già abbinati. Dove la fascia contiene al massimo otto nomi e la somiglianza supera la soglia, il nome è recuperato (`abbinamento = fascia alfabetica`): 16 casi. Sono esclusi i nomi propri staccati («Maria», «Luigi») e le parole di verbale catturate dall'elenco («Dichiaro», «Votazione», «Segretari»). Le righe che ripetono un costituente già presente nello stesso voto — duplicati di stampa o di OCR, come «Cingolani Mario» seguito da «Cingolani» — sono marcate `duplicato` e non generano un secondo arco: 11 casi. Il giudice di entrambe le operazioni è esterno, perché sono i totali annunciati dal Presidente a dire se il recupero è corretto: lo scarto medio fra nomi abbinati e totali ufficiali scende da 3,05 a 2,64 nomi per votazione, con 8 votazioni più vicine al totale e nessuna allontanata (l'unico scarto in crescita è v16, dove la rimozione di un duplicato rende visibile un elenco stampato davvero incompleto).

Controlli di coerenza su tutto il dataset: nessun voto fuori dal mandato, nessuna firma fuori dal mandato; se un costituente compare in due elenchi dello stesso voto si tiene l'abbinamento esatto, e se lo sono entrambi il suo voto resta mancante.

### Variabili degli emendamenti (`emendamenti_nodi.csv`)

| Variabile | Descrizione |
|---|---|
| `firmatari_id`, `n_firmatari` | Firmatari (id separati da `\|`) e loro numero |
| `completo` | 1 se l'elenco dei firmatari è completo, 0 se termina con «ed altri» |
| `articolo_menzionato` | 1 se il testo cita un articolo del progetto di Costituzione |
| `prima_seduta`, `data`, `pagina`, `url_pdf` | Prima menzione e link alla pagina del resoconto |
| `fonte` | `firma` (blocco di firma) o `presentazione` (formula di presentazione) |

### Variabili dei voti (`voti_nodi.csv`)

| Variabile | Descrizione |
|---|---|
| `seduta`, `data`, `pagina`, `url_pdf` | Seduta e link alla pagina della chiama |
| `label_en`, `on_constitution` | Oggetto del voto (in inglese) e se riguarda la Costituzione |
| `si_ufficiali`, `no_ufficiali`, `astenuti_ufficiali` | Totali annunciati dal Presidente |
| `si_abbinati`, `no_abbinati`, `astenuti_abbinati`, `congedo_abbinati` | Nomi abbinati ai costituenti |
| `scarto_si`, `scarto_no`, `controllo` | Differenza tra abbinati e ufficiali, ed esito del controllo |
| `excerpt_it` | Testo che precede la votazione, per identificarne l'oggetto |

## Variabili dei costituenti (`costituenti_nodi.csv`)

### Anagrafica, elezione, gruppo

| Variabile | Descrizione |
|---|---|
| `id_dep`, `cognome`, `nome` | |
| `donna` | 1 = donna (21) |
| `data_nascita`, `anno_nascita`, `eta_1946` | Età in anni compiuti al 25.6.1946 |
| `comune_nascita`, `prov_nascita`, `regione_nascita` | Regioni attuali |
| `macro_nascita` | Nord-Ovest, Nord-Est, Centro, Sud, Isole, Estero |
| `regione_nascita_statuto` | Statuto `speciale` o `ordinario` (classificazione attuale) |
| `nato_estero` | Nato fuori dall'Italia attuale (Fiume inclusa) |
| `lista_partito` | Lista di elezione |
| `gruppo_iniziale`, `gruppo_finale`, `n_gruppi`, `cambio_gruppo` | Gruppi parlamentari |
| `circoscrizione`, `collegio_unico_naz` | Circoscrizione (indicata col capoluogo) o Collegio unico nazionale |
| `regione_elezione`, `macro_elezione`, `stessa_regione` | Udine-Belluno assegnata al Friuli-Venezia Giulia |
| `inizio_mandato`, `fine_mandato`, `motivo_cessazione` | |
| `subentrato` | Mandato iniziato dopo la prima seduta (25.6.1946). Vale 1 per 104 costituenti, ma non sono 104 sostituzioni: comprende i subentri veri, le proclamazioni tardive per operazioni elettorali non ancora chiuse (24 già nel luglio 1946) e le surroghe dopo l'opzione dei pluri-eletti |

### Istruzione e professione

| Variabile | Descrizione |
|---|---|
| `titolo_studio`, `laurea`, `campo_laurea` | Dalla scheda Camera |
| `professione_testo`, `descrizione_camera` | Testo originale |
| `professione_cat` | Codifica automatica per parole chiave della prima professione indicata |

### Carriera precedente

| Variabile | Descrizione |
|---|---|
| `deputato_regno`, `n_leg_regno` | Deputato del Regno prima del 1946 |
| `consulta_nazionale` | Membro della Consulta nazionale (1945–46) |
| `governo_prima`, `governo_durante` | Incarico di governo iniziato prima o durante la Costituente |
| `aventiniano` | Deputato aventiniano (1924) |

### Antifascismo e Resistenza (Wikidata e Wikipedia)

| Variabile | Descrizione |
|---|---|
| `resistenza_fonte_strutturata` | Categoria Wikipedia (Partigiani italiani, Brigate…, Resistenza…) o occupazione Wikidata «partigiano» |
| `resistenza_testo` | Una frase descrive un ruolo personale nella Resistenza (partecipò, comandò, organizzò, nome di battaglia…) |
| `resistenza` | 1 se una delle due |
| `cln`, `resistenza_o_cln` | Ruolo in un Comitato di Liberazione Nazionale |
| `antifascista` | Categoria «Antifascisti italiani» o menzione |
| `confino`, `tribunale_speciale`, `carcere`, `esilio` | Esperienza personale descritta nella voce |
| `persecuzione_fascista` | Almeno una tra confino, Tribunale speciale, carcere, esilio |
| `guerra_spagna` | Partecipazione alla guerra civile spagnola |
| `qid`, `wp_title`, `voce_wikipedia` | Collegamenti a Wikidata e Wikipedia |

Codifiche automatiche: le sezioni Opere, Note e Bibliografia sono escluse, ma restano errori possibili. `evidenze_wikipedia.csv` riporta fino a due frasi per indicatore. Sei costituenti non hanno una voce.

### Carriera successiva (dopo il 31.1.1948)

| Variabile | Descrizione |
|---|---|
| `carriera_parlamento` | Deputato o senatore della Repubblica |
| `carriera_apice` | Presidente della Repubblica, del Consiglio, della Camera o del Senato |
| `carriera_corte` | Giudice della Corte costituzionale |
| `carriera_livello` | Livello più alto: `apice` > `corte costituzionale` > `parlamento` > `nessuna` |
| `futuro_pdr`, `futuro_pdc`, `futuro_pres_camera`, `futuro_pres_senato`, `futuro_giudice_cost` | Singole cariche |
| `futuro_ministro`, `futuro_sottosegretario`, `n_incarichi_gov_dopo`, `governo_dopo`, `ministro_mai` | Governo (dati Camera) |
| `deputato_rep`, `n_leg_camera_rep`, `futuro_senatore`, `n_leg_senato_rep`, `senatore_a_vita`, `parlamentare_dopo_1948` | Parlamento (Camera, Senato, Wikidata) |
| `futuro_eurodeputato`, `futuro_sindaco` | Wikidata |

### Posizione nella rete degli organi

| Variabile | Descrizione |
|---|---|
| `n_organi`, `n_organi_costituz` | Grado two-mode; solo organi costituzionali (Commissione dei 75, sottocommissioni, Comitato di redazione) |
| `grado_proiez`, `forza_proiez`, `betweenness`, `closeness`, `eigenvector` | Sulla proiezione one-mode (eigenvector pesata, 0 per gli isolati) |
| `bip_betweenness` | Betweenness sulla rete bipartita |
| `cost_grado_proiez`, `cost_eigenvector`, `cost_betweenness` | Solo organi costituzionali |
| `presidenze_organi`, `incarichi_ufficio` | Presidenze; cariche (presidente, vice, segretario, questore) |

### Attività e interazioni

| Variabile | Descrizione |
|---|---|
| `att_pagine_tot`, `att_pagine_assemblea`, `att_pagine_commissioni` | Pagine dei resoconti con suoi interventi |
| `att_pagine_costituzione` | Pagine sul progetto di Costituzione |
| `att_temi`, `att_sedute` | Temi e sedute in cui è intervenuto |
| `att_interrogazioni`, `att_relazioni` | Interrogazioni presentate; relazioni e proposte |
| `scambi_grado`, `scambi_forza` | Grado e forza nella rete degli scambi |

## Limiti

- **Emendamenti e voti.** Sono ricostruiti con l'OCR e contengono errori residui: vedi «Emendamenti e voti: costruzione e accuratezza». Gli emendamenti coprono le sedute dell'Aula, non i lavori delle commissioni.
- **Interrogazioni.** Le fonti registrano solo il primo firmatario, quindi non consentono una rete di cofirma.
- **Presidenti.** Chi presiede l'Aula o un organo (per esempio Terracini, Ruini, Tupini) compare in molte pagine per ragioni procedurali: usare `n_pagine_senza_presidenza` o controllare per `presidenze_organi`.
- **Membri del governo.** I membri del governo in carica (De Gasperi, Scelba, Segni…) non sedevano nelle commissioni: la loro centralità nella rete degli organi è bassa per costruzione. Controllare per `governo_durante`.
- **Integrazioni a mano.** Le presidenze di Camera e Senato sono integrate a mano dove Wikidata è incompleto; i giudici costituzionali sono verificati sull'elenco di Wikipedia.
