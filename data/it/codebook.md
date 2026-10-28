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
| `emendamenti_nodi.csv` | 1.408 emendamenti presentati in Aula, estratti dai resoconti con l'OCR, con il testo e il tipo |
| `edgelist_emendamenti.csv` | Rete two-mode costituente × emendamento (chi ha firmato, con il ruolo di presentatore o firmatario; 3.275 archi) |
| `menzioni_discorso.csv` | Rete diretta delle menzioni nei discorsi: chi, parlando in Aula, nomina chi (9.194 menzioni) |
| `voti_nodi.csv` | 27 votazioni per appello nominale, con totali ufficiali e controllo |
| `edgelist_voti.csv` | Rete two-mode costituente × voto, con il voto espresso (sì, no, astenuto) |
| `edgelist_emendamenti_conservativa.csv`, `edgelist_voti_conservativa.csv` | Versione conservativa delle due reti: solo gli archi con abbinamento esatto del nome o elenco corretto a mano sull'immagine (3.216 archi di co-firma su 3.275; 9.007 di voto su 9.125) |
| `graphml/*.graphml` | Le sei reti già costruite in GraphML (co-firma bipartita e proiettata, rete diretta firmatario → presentatore, voti con segno, menzioni, altri atti), per Gephi, igraph, networkx; `R/00_build_networks.R` costruisce gli stessi oggetti `igraph` dai CSV |
| `altri_atti_nodi.csv` | 842 atti co-firmati che non sono emendamenti: interrogazioni, interpellanze, ordini del giorno, mozioni, richieste di votazione |
| `edgelist_altri_atti.csv` | Rete two-mode costituente × atto (2.111 archi) |
| `evidenze_wikipedia.csv` | Categorie e frasi di Wikipedia alla base degli indicatori su antifascismo e Resistenza |

Gli identificativi sono `d` + id Camera per i costituenti, `o` + id per gli organi, `t` + numero per i temi, `a` + numero per gli emendamenti, `v` + numero per i voti.

## Le reti

**Organi (formale).** Appartenenza a commissioni, sottocommissioni e giunte. È decisa dai gruppi parlamentari in proporzione alla loro forza: misura la posizione assegnata, non le scelte individuali.

**Temi (two-mode).** Un tema è un argomento discusso: in Aula il titolo del dibattito (per esempio un articolo del progetto di Costituzione), in commissione la voce in discussione (per esempio «La famiglia»). Il peso è il numero di pagine del resoconto con interventi del costituente su quel tema.

**Scambi (one-mode, non diretta).** Due costituenti sono legati se intervengono sulla stessa pagina dello stesso resoconto: una buona approssimazione del confronto diretto (botta e risposta, interruzioni, repliche). Il peso `n_pagine` conta le pagine condivise; `n_pagine_senza_presidenza` esclude le pagine in cui uno dei due presiede quell'organo, perché la presenza dei presidenti è spesso procedurale. Il legame non distingue accordo e disaccordo.

**Corelatori.** Relazioni di sottocommissione e relazioni su disegni di legge firmate da più costituenti. Rete piccola ma di collaborazione esplicita.

**Sostituzioni (diretta).** `subentrante` → `sostituito`, con organo e data.

**Emendamenti (two-mode).** Chi firma insieme un emendamento: un legame scelto, a differenza dell'appartenenza agli organi. Proiettata sui costituenti, misura la collaborazione nella stesura del testo.

**Emendamenti (two-mode, con direzione).** `edgelist_emendamenti.csv` ha la colonna `ruolo`: `presentatore` per chi presenta l'emendamento, `firmatario` per chi lo sottoscrive. Proiettando solo gli archi firmatario → presentatore si ottiene una rete diretta, chi raccoglie firme e chi le concede. Il presentatore è stato confrontato con l'elenco trascritto sull'immagine per i 131 emendamenti pluri-firmati della verifica sistematica: coincide in 130 casi su 131 (99,2%, IC 95,8–99,9); l'unico errore («presentato dall'onorevole Gasparotto e da me», dove chi parla veniva messo per primo) è stato corretto nell'estrattore. Su 1.408 emendamenti: 185 hanno il presentatore indicato da una formula, 209 dal primo nome dell'elenco e 1.014 sono a firma singola.

**Menzioni nei discorsi (diretta).** Chi, parlando in Aula, nomina un altro costituente: «l'onorevole X», «dell'/dall'/all'onorevole X», «il collega X», «on. X». A differenza della co-firma è un legame asimmetrico e non concordato, e misura chi è preso come riferimento nel dibattito. Chi parla è il nome in testa al turno di parola, anche quando l'intestazione è stampata in linea («…(Approvazioni). PRESIDENTE. Pongo in votazione…»); i turni del Presidente dell'Assemblea sono esclusi, perché quasi tutti procedurali («Ha facoltà di parlare l'onorevole X»), come le autocitazioni. `tipo_menzione` distingue le menzioni che riguardano un emendamento, gli atti di parola («le dichiarazioni dell'onorevole X», le stesse frasi che l'estrattore degli emendamenti scarta), le didascalie del resoconto («(Interruzione dell'onorevole X)», che registrano un'interazione ma non sono parole dell'oratore) e le altre. Codice: `tools/estrai_menzioni_discorso.py`, che usa le stesse regole di lettura e di abbinamento dei nomi dell'estrattore degli emendamenti.

**Voti nominali (two-mode, con segno).** Come ha votato ciascun costituente nelle 27 votazioni per appello nominale. Le assenze e i congedi non sono archi.

## Emendamenti e voti: costruzione e accuratezza

Le firme degli emendamenti e i voti nominali non esistono in forma strutturata: si trovano solo nei resoconti stenografici dell'Assemblea, pubblicati come immagini. Sono stati ricostruiti così (codice in `pipeline/`):

1. **OCR.** I resoconti delle 173 sedute con emendamenti o voti (4.786 pagine) sono stati convertiti in testo con Tesseract (modello italiano), separando le due colonne della pagina (`ocr_costituente.R`). Le 3.275 pagine che parlano di emendamenti sono state rilette a 400 dpi (`ocr_400dpi.R`); per ogni pagina si usa la lettura che riconosce più cognomi di costituenti.
2. **Emendamenti.** Sono riconosciuti dalle formule di presentazione («l'onorevole X ha presentato il seguente emendamento») e dai blocchi di firma in calce; il classificatore esclude interrogazioni, interpellanze, mozioni, ordini del giorno e richieste di appello nominale. I nomi sono abbinati all'elenco dei costituenti in carica alla data della seduta (`estrai_emendamenti.py`).
3. **Voti.** Per ogni votazione per appello nominale sono estratti gli elenchi «Rispondono sì», «Rispondono no», «Si sono astenuti» e «Sono in congedo», e confrontati con i totali annunciati dal Presidente (`estrai_voti.py`).
4. **Verifica.** 73 menzioni estratte a caso sono state controllate sul PDF: 40 (seme 1947) a mano, 34 sull'immagine della pagina, scelte sovrarappresentando gli emendamenti con più firmatari (seme 1948). Gli errori sistematici emersi sono stati corretti nel codice: elenchi di emendamenti distinti («gli emendamenti degli onorevoli X, Y e Z») scambiati per firme congiunte, presentatore omesso nelle formule «firmato anche dagli onorevoli», interrogazioni ai ministri, rumore dell'OCR tra i nomi. I voti con scarti superiori a tre nomi sono stati controllati sull'immagine della pagina.
5. **Completezza.** 10 pagine estratte a caso (seme 2026) sono state lette per intero per trovare gli emendamenti con più firmatari che l'estrazione non coglieva. Erano 6: ne venivano estratti correttamente 2. Le cause (la formula «Gli onorevoli X e Y hanno presentato…», «a firma degli», «insieme con gli onorevoli», blocchi di firma spezzati dall'OCR, sillabazione, rumore dell'OCR nei nomi) sono state corrette su tutto il corpus; dopo la correzione 5 dei 6 sono completi e il sesto ha 7 firmatari su 9. Una ricerca automatica delle frasi con almeno due cognomi non estratte (`cerca_mancati.py`) ha guidato le correzioni successive. Il numero di emendamenti con più firmatari è passato da 217 a 327. Una seconda verifica su altre 20 pagine (seme 2027, escluse le precedenti), condotta allo stesso modo, ha trovato 5 emendamenti con più firmatari: tutti e 5 erano estratti con l'elenco completo dei firmatari. Le altre 17 pagine non contenevano emendamenti con più firmatari; le firme multiple che vi compaiono appartengono a interrogazioni e interpellanze, che per costruzione restano fuori dal dataset. Dettaglio in `pipeline/extraction/richiamo2/ESITO.md`.

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

**Test di non-regressione e seconda tornata di correzioni.** `tools/test_regole.py` lancia l'estrattore su 57 passi veri dei resoconti, ciascuno con l'esito atteso (gli elenchi di firmatari che deve produrre, o nessuno), e controlla in un secondo che una modifica alle regole non ne rompa un'altra; i casi sono in `tools/test_regole_casi.json`, e quelli segnati «controllato sull'immagine» sono stati confrontati con la scansione. Costruendo il test sono emersi difetti generali, corretti nell'estrattore e verificati sull'immagine della pagina record per record: (1) la sillabazione con un segno spurio fra il trattino e l'a capo («MARAZ-'» / «- ZA», «Cle-.» / «rici») spezzava il blocco di firma o l'elenco, e l'emendamento andava perso per intero: così mancavano, fra gli altri, un articolo aggiuntivo con 16 firme (sed126) e due emendamenti democristiani con 28 e 16 firme (sed119, sed122); (2) il consolidamento assorbiva un emendamento a firma singola in qualunque elenco più lungo che contenesse quel nome, anche quando era un atto distinto («Segue l'emendamento dell'onorevole Bubbio», tredicesimo firmatario di un altro): ora un nome solo è assorbito soltanto se è il primo firmatario, perché il resoconto chiama un emendamento col nome del primo; (3) il plurale che regge un elenco («gli emendamenti degli onorevoli…») scavalcava una fine di frase subito prima della menzione («…pervenute. Gli onorevoli») e un singolare più vicino («…valgono anche per l'emendamento degli onorevoli…»); (4) il presentatore mancava nelle formule «l'onorevole X ha ora presentato…», «l'onorevole X, la quale, insieme con gli onorevoli…» e «presentato dagli onorevoli X, Y e da me»; (5) una richiesta di appello nominale nella frase *successiva* cancellava l'emendamento presentato nella frase prima. Sono state aggiunte le forme «presentati rispettivamente dagli onorevoli» (atti distinti), «interruzione» e «cortesia» (atti di parola), i cognomi senza virgola in mezzo («Targetti Amadei e Bordon») e la congiunzione con il punto spurio («Rodnò Mario e. Puoti»). Infine due correzioni manuali registrate in `esporta_dataset.py` non venivano applicate perché la chiave riportava anche il nome proprio («Rossi Paolo»): ora valgono, e una firmataria mancante (Bianchi Bianca, sed261) è rientrata. Gli emendamenti passano da 718 a 787, quelli con 2+ firmatari da 329 a 337, i legami di co-firma da 2.269 a 2.425.

**Completezza (recall): quanti emendamenti stampati sono nel dataset.** Tutte le misure precedenti riguardano la precisione: dicono se ciò che è stato estratto è giusto, non quanto manca. Per misurare il recall sono state estratte a caso intere sedute fra le 165 del corpus che discutono il progetto di Costituzione, e tutte le loro pagine sono state lette sull'immagine da un lettore che non vedeva il dataset, annotando ogni emendamento stampato con un proponente nominato (presentato, letto, votato, ritirato o citato in un discorso) e il grado di certezza. Il confronto con il dataset considera preso un emendamento se nella stessa seduta e nella stessa pagina (±1) c'è una menzione dei suoi firmatari collegata a un emendamento non già usato per un'altra riga. La misura principale usa le righe ad alta certezza; quelle a media e bassa certezza sono soprattutto proposte fatte a voce nella discussione generale, che il lettore stesso non era sicuro fossero emendamenti.

| | sedute | emendamenti (alta certezza) | versione pubblicata il 26.10 | dopo le correzioni |
|---|---|---|---|---|
| campione 1, seme 2028 (sviluppo) | sed060, sed115, sed220, sed224, sed231 | 30 | 10/30 = 33,3% (19,2–51,2) | 28/30 = 93,3% (78,7–98,2) |
| campione 2, seme 2030 (sviluppo) | sed170, sed251, sed254, sed292 | 19 | 10/19 = 52,6% (31,7–72,7) | 17/19 = 89,5% (68,6–97,1) |
| **campione 3, seme 2031 (convalida)** | sed118, sed149, sed215, sed252, sed282 | 30 | 17/30 = 56,7% (39,2–72,6) | **20/30 = 66,7% (48,8–80,8)** |

Intervalli di Wilson al 95%. I campioni 1 e 2 hanno guidato le correzioni, quindi i loro valori dopo le correzioni sono ottimistici per costruzione. Il campione 3 è stato estratto e letto dopo che le regole erano state fissate, ed è **la stima da usare: il recall degli emendamenti è di circa due terzi** (67%, intervallo 49–81%). Due correzioni minori introdotte dopo la sua lettura lo portano a 22/30, ma quel valore non è più una stima indipendente. Il recall degli emendamenti con **più firmatari**, gli unici che producono legami di co-firma, è molto più alto: 9/10 nel campione di convalida (90%, intervallo 60–98) e 21/22 sui tre campioni insieme. Le perdite riguardano quindi soprattutto gli emendamenti a firma singola, cioè i conteggi per persona più che la rete.

Le cause trovate erano generali e sono state corrette nell'estrattore: (1) la formula con cui il Presidente legge un emendamento a firma singola, «L'onorevole X ha presentato il seguente emendamento», non era riconosciuta come presentazione (serviva solo ad aggiungere il presentatore ai «firmato anche dagli onorevoli»), e con le sue varianti («ha proposto di sopprimere», «ha presentato a questo articolo», «l'onorevole X, a sua volta, ha proposto che») era la prima causa di perdita; (2) mancavano le forme «dall'onorevole X», «Dall'onorevole», «della onorevole», «dal collega onorevole», «unitamente agli onorevoli» e gli elenchi che ripetono «dell'onorevole» per ogni nome; (3) il consolidamento univa in un solo emendamento tutti quelli dello stesso firmatario in sedute vicine (Nitti, Colitto, Caronia, Conti, Perassi ne presentano molti), ora tenuti distinti dal testo; (4) le proposte di chi parla («CRISPO. … Propongo che l'articolo 4 sia redatto nel modo seguente: «…»», «Ho presentato questo emendamento») sono attribuite al nome in testa al turno di parola; (5) rumore dell'OCR («Dallonorevole», «onorevo!e», «onòérevole», «preseritato», un apice fra la formula e il nome) e fine di frase con virgolette spurie. Ciò che resta escluso di proposito sono le «proposte» citate nella discussione generale senza essere chiamate emendamento («la proposta dell'onorevole Rubilli»), perché in quella forma la parola indica più spesso una tesi che un atto.

Le nuove regole sono state controllate anche sulla precisione, con un **quinto campione di 40 record** estratti a caso fra tutti e letti sull'immagine: falsi positivi 2/40 = 5,0% (1,4–16,5), contando come errori i due casi non giudicabili dal ritaglio; firmatari mancanti o errati 3/38 = 7,9% (2,7–20,8), in linea con il campione 4. Le tre famiglie di errore emerse (il presentatore nelle formule «Abbiamo presentato… firmato anche dagli» e «firmato anche da me», e il proponente confuso con chi svolge l'emendamento) sono state corrette dopo la misura. Una prima tornata, controllata su 40 record nuovi, aveva trovato due altre famiglie di falsi positivi introdotte dalla forma «dall'onorevole» («fatto proprio dall'onorevole X», «l'inconveniente accennato dall'onorevole X»), escluse prima della misura finale. Gli emendamenti passano da 787 a 1.406, quelli con 2+ firmatari da 337 a 395, i legami di co-firma da 2.425 a 3.227. File: `pipeline/extraction/VERIFICA_recall_campione*.tsv` (letture), `VERIFICA_recall_campione*_esito.csv` (confronto), `VERIFICA_precisione_campione5_verificato.csv`.

**Verifica sistematica degli emendamenti con più firmatari.** Tutti i legami di co-firma vengono dagli emendamenti con almeno due firmatari. Dopo le correzioni, 216 dei 395 non erano mai stati guardati sull'immagine; sono stati messi in ordine casuale (seme 2033) e controllati a blocchi di 40, per cui ogni blocco è anche un campione casuale. Per ogni record si confronta l'elenco attribuito con quello stampato, controllando in particolare che l'elenco non continui oltre la colonna e che nessun nome venga dall'emendamento stampato sopra o sotto; i casi in cui il ritaglio non bastava sono stati riletti sulle colonne intere. Risultati per blocco (falsi positivi; firmatari mancanti o errati fra gli emendamenti veri):

| blocco | falsi positivi | firmatari errati |
|---|---|---|
| 1 | 2/40 | 1/38 |
| 2 | 2/40 | 1/38 |
| 3 | 2/40 | 3/38 |
| 4 | 1/40 | 2/39 |
| 5 | 2/40 | 2/38 |
| 6 | 0/16 | 0/16 |
| **tutti (216)** | **9/216 = 4,2% (2,2–7,7)** | **9/207 = 4,3% (2,3–8,1)** |

Gli errori erano quasi tutti di famiglie generali, corrette nell'estrattore: elenchi di atti distinti («hanno proposto ciascuno un identico emendamento», «hanno presentato due emendamenti», «gli emendamenti, più sostanziali, degli onorevoli X e Y» con un segno spurio dell'OCR in mezzo), elenchi di oratori («dall'onorevole X, dall'onorevole Y e da altri a favore dell'emendamento…»), blocchi di firma di interrogazioni («per sapere», «se non ravvisi») e richieste di votazione scritte male dall'OCR («chiesto la .votazione: a serutinio segreto»), il presentatore nella formula «ha facoltà di parlare l'onorevole X, per svolgere il seguente emendamento, firmato anche dagli onorevoli…», e due errori dell'OCR dentro l'elenco («Tremelloni e-Carboni», «De' : Palma»). Nei blocchi 5 e 6 sono emerse altre tre famiglie: le firme delle interrogazioni annunciate a fine seduta (ognuna si apre con «Il sottoscritto chiede d'interrogare»), la richiesta di appello nominale che «porta le firme anche degli onorevoli…», e il presentatore cercato nella prima formula «L'onorevole X ha presentato» della finestra invece che nell'ultima, che attribuiva un elenco al presentatore dell'emendamento precedente. Due elenchi che proseguono nella colonna o nella pagina successiva sono stati corretti a mano. Con questa verifica tutti i 394 emendamenti con più firmatari del dataset sono stati controllati almeno una volta sull'immagine. Restano due casi incerti: «Mariani» (Enrico o Francesco, entrambi socialisti), lasciato fuori, e «Massa» in un elenco liberale e qualunquista della seduta 322, attribuito a Mazza (Uomo Qualunque) invece che a Massola (PCI) in base a partito e co-firme, e marcato come incerto. File: `pipeline/extraction/VERIFICA_2plus_blocchi*_verificato.csv`.

**Falsi positivi fra gli emendamenti a firma singola.** Le formule aggiunte stanotte hanno più che raddoppiato i singoli, che non producono legami ma entrano nei conteggi per persona. Un campione dedicato di 60 singoli estratti a caso (seme 2037), letti sull'immagine, ha dato 5 falsi positivi più 1 incerto: 6/60 = 10,0% (IC 4,7–20,1), sopra la soglia del 5% fissata per intervenire. Le famiglie erano due, corrette nell'estrattore: un nome retto da un participio o sostantivo di giudizio («l'inconveniente segnalato dall'onorevole X», «le ragioni esposte dall'onorevole X», «le preoccupazioni dell'onorevole X», «definita come emendamento dall'onorevole X»), e chi svolge o riprende l'emendamento di un altro («l'emendamento dell'onorevole Nobile, svolto dall'onorevole Stampacchia», «ripreso dall'onorevole Pignatari»), distinto da «l'emendamento già svolto dall'onorevole X», dove X è il proponente. Su tutto il corpus le correzioni tolgono 10 record, tutti controllati sul contesto. In 6 dei 60 l'emendamento aveva altri firmatari che il record singolo non riporta (elenchi chiusi da «ed altri», o un firmatario nominato altrove): è il limite già noto per gli emendamenti citati invece che letti. File: `pipeline/extraction/VERIFICA_singoli_campione6_verificato.csv`.

**Secondo campione di singoli, dopo le correzioni.** Un nuovo campione di 50 singoli (seme 2038, esclusi i 60 precedenti), letti alla cieca sulle colonne intere della pagina, distingue due casi che il primo campione teneva insieme. In 4 record il nome compare in una citazione nel discorso di un altro («Per quanto riguarda l'emendamento dell'onorevole Piemonte», il relatore; «c'è già un emendamento presentato dall'onorevole De Vita», Macrelli): l'emendamento esiste ed è di quella persona, ma il record nasce dalla citazione e non dalla lettura, perché l'annuncio del Presidente non è stato estratto o cade a più di tre sedute di distanza. Questi record si tengono: sono l'unica traccia di un emendamento vero, e quando l'annuncio è estratto nelle sedute vicine la citazione vi è già assorbita. Gli errori veri sono 2 su 48 giudicabili (4,2%, IC 1,2–14,0): «la questione posta dall'onorevole Cevolotto», che non è un emendamento, e «l'emendamento dell'onorevole Nitti, integrato dall'onorevole Ruini», attribuito a Ruini. Contando anche le citazioni, i record che non corrispondono a un emendamento letto in quel punto sono 5/48 (10,4%, IC 4,5–22,2). Un singolo era in realtà un articolo aggiuntivo con sei firme («Segue l'articolo 7-quinquies, proposto dagli onorevoli Paris, Gullo Rocco, La ‘ Malfa…»), perso per la formula e per l'apice spurio dentro il nome. Le tre famiglie sono corrette nell'estrattore («integrato dall'», «posta / posto dall'» salvo che segua la proposta, articolo aggiuntivo «proposto dagli», apice seguito da spazio dentro un nome); la correzione del nome recupera anche l'elenco «Monterisi, Caccuri, Perrone ' Capano, Gabrieli» (sed124, controllato sull'immagine). File: `pipeline/extraction/VERIFICA_singoli_campione7_verificato.csv`.

**Strato multiplex: gli altri atti co-firmati.** Le regole che tengono fuori dagli emendamenti le interrogazioni, le interpellanze, gli ordini del giorno, le mozioni e le richieste di votazione per appello nominale o a scrutinio segreto riconoscono anche questi atti: invece di scartarli, l'estrattore li registra in `altri_atti_nodi.csv` con il tipo (`interrogazione` 784, `richiesta di votazione` 28, `ordine del giorno` 16, `interpellanza` 12, `mozione` 2; 257 con due o più firmatari). La co-firma di un'interrogazione o di una richiesta di voto segue logiche diverse da quella di un emendamento, e i due strati insieme danno una rete multiplex. Su 20 atti con più firmatari letti alla cieca sull'immagine (seme 2046), il tipo è giusto in 17 casi e l'elenco dei firmatari in 19; i tre errori di tipo erano emendamenti: uno (sed265, Benvenuti e Clerici, preceduto dalla lettura di un'interpellanza) è stato corretto nell'estrattore e recuperato fra gli emendamenti, uno è una citazione di un emendamento già nel dataset, uno (sed329 p1) è un blocco di emendamenti aggiuntivi all'inizio della seduta. File: `pipeline/extraction/VERIFICA_altri_atti_verificato.csv`.

**Citazioni assorbite: il caso del testo stampato.** Un emendamento a firma singola che nelle sedute vicine ha lo stesso primo firmatario di un emendamento con più firme era trattato come una citazione di quest'ultimo e assorbito. Ora l'assorbimento non avviene se il singolo stampa un testo proprio e l'elenco no (salvo che il pezzo di testo dell'elenco sia contenuto nel singolo): 17 emendamenti distinti di proponenti prolifici, prima fusi (per esempio tre emendamenti di Badini Confalonieri su articoli diversi in sed102), tornano separati.

**Recall a livello di persona.** 108 costituenti non hanno nessun legame di co-firma, e 64 non compaiono né negli emendamenti né nelle menzioni nei discorsi. Per escludere che siano invisibili per un errore della pipeline, `pipeline/tools/recall_persone.py` cerca nel corpus il loro cognome subito dopo la parola «emendamento» in una formula di firma o di presentazione: i passi trovati (`pipeline/extraction/recall_persone.csv`) sono quasi tutti richieste di votazione o citazioni, ma tre erano emendamenti persi, e hanno rivelato tre famiglie generali corrette nell'estrattore: i due punti dopo «dagli onorevoli:» (sed118, 11 firme), il verbo con l'accento spurio dell'OCR («hanno prèsentato», sed123, 13 firme) e «una proposta di articolo 8-bis, a firma degli onorevoli…» scambiata per un elenco di proposte distinte (sed301, 12 firme). Le stesse correzioni hanno recuperato l'articolo aggiuntivo con 42 firme sul giuramento del Presidente della Repubblica (sed268 p25, controllato sull'immagine). La correlazione di rango fra il numero di emendamenti firmati e le pagine di attività in Aula sul progetto di Costituzione dell'indice della Camera (`att_pagine_costituzione`) è 0,66: chi interviene molto firma molto, come ci si aspetta se i nomi non vanno persi.

**Due versioni delle reti.** Ogni arco di `edgelist_emendamenti.csv` e `edgelist_voti.csv` porta la colonna `abbinamento`, il criterio con cui il nome è stato riconosciuto: `esatto`, `esatto+partito`, `prefisso`, `ambiguo+cofirme` e `ambiguo+seduta` (omonimi risolti), `approssimato`, `fascia alfabetica`, `omonimo risolto`, `correzione manuale` (elenco letto sull'immagine), `decisione manuale` (dal foglio dei casi aperti). I file `*_conservativa.csv` tengono solo `esatto`, `esatto+partito` e `correzione manuale`. Mostrare che un risultato tiene su entrambe le versioni è il modo più diretto di rispondere all'obiezione che i dati vengono dall'OCR; `pipeline/extraction/incertezza_rete.csv` fa lo stesso in modo continuo (vedi sotto).

**Incertezza delle statistiche di rete.** `pipeline/tools/incertezza_rete.py` propaga alle statistiche della rete di co-firma gli errori misurati sull'immagine: in 1.000 repliche toglie ogni emendamento con più firmatari con probabilità 0,042 (falsi positivi) e ogni firma con probabilità 0,043 (firmatari sbagliati). Risultati (`pipeline/extraction/incertezza_rete.csv`; osservato, versione conservativa, intervallo al 95% delle repliche):

| Statistica | Osservato | Conservativa | IC 95% |
|---|---|---|---|
| Densità della proiezione | 0,042 | 0,041 | 0,035–0,040 |
| Grado medio | 24,6 | 23,7 | 20,2–23,1 |
| Centralizzazione di grado | 0,191 | 0,189 | 0,145–0,193 |
| Quota di legami fra membri dello stesso gruppo | 0,654 | 0,656 | 0,640–0,711 |
| Omofilia (quota osservata / attesa per caso) | 3,24 | 3,25 | 3,17–3,52 |
| Reciprocità firmatario → presentatore | 0,102 | 0,098 | 0,084–0,103 |

Le misure di struttura (omofilia, reciprocità) cambiano poco; quelle di volume (densità, grado) scendono di circa un decimo se si tolgono gli errori, perché gli errori aggiungono legami. Il calcolo non simula il recall: le sedute trascritte contengono circa due terzi degli emendamenti stampati, e i legami mancanti abbassano densità e grado in modo che queste repliche non misurano.

**Copertura.** Il corpus contiene le 173 sedute in cui l'indice dei lavori registra emendamenti o voti, su 373 sedute dell'Assemblea. Il confronto con la tavola dei lavori preparatori della Camera (date della discussione di ogni articolo del progetto) mostra che 16 sedute tenute in giorni di discussione del progetto — tutte l'altra seduta di un giorno di cui una seduta è trascritta (le sedute antimeridiane e pomeridiane hanno numeri distinti) — non sono nel corpus: i loro emendamenti mancano tutti, e il recall misurato dentro le sedute trascritte (67%) non ne tiene conto. L'elenco delle 200 sedute non trascritte, con questa marcatura e l'indirizzo del PDF, è in `pipeline/sedute_non_trascritte.csv`; `pipeline/ocr_costituente.R` e `ocr_400dpi.R` includono ora le 16 sedute (le scaricano e le leggono al prossimo lancio). Gli elenchi chiusi da «ed altri» (`completo = 0`) sono 32, di cui 24 con almeno due firmatari: i legami con i firmatari non nominati mancano.

**Validazione esterna.** Non esiste, in forma utilizzabile, un indice a stampa che elenchi gli emendamenti per nome; la tavola dei lavori preparatori della Camera indica articoli e date, non i proponenti. Due giudici esterni sono comunque usati: la correlazione con le pagine di attività dell'indice della Camera (sopra) e la tavola, che conferma la materia e la data di discussione dell'articolo emendato.

**Casi aperti e decisioni a mano.** I casi che l'estrazione non sa decidere — cognomi condivisi da più costituenti senza nome proprio né cofirmatari che aiutino (Gullo, Mastino, Mariani, Merlin, Cortese), nomi illeggibili, elenchi chiusi da «ed altri», nomi di voto non abbinati, abbinamenti approssimati — sono raccolti da `pipeline/tools/prepara_casi_aperti.py` in `pipeline/CASI_APERTI.xlsx`, con il collegamento alla pagina e le scelte possibili. Le decisioni scritte nel foglio, prese guardando la pagina, sono applicate da `esporta_dataset.py` a ogni esportazione e restano nel repository: ogni scelta a mano è quindi documentata e reversibile.

**Qualità dell'OCR per pagina.** `pipeline/tools/qualita_ocr.py` assegna a ogni pagina la quota di parole (4+ lettere) che ricorrono almeno 20 volte nel corpus — una parola storpiata dall'OCR è quasi sempre rara — e la quota di caratteri spuri; il risultato è in `pipeline/extraction/qualita_pagine.csv` (3.275 pagine; mediana 0,89, 5° percentile 0,79). Il punteggio non predice gli errori di estrazione: sui 492 record controllati sull'immagine, quelli sbagliati cadono su pagine di qualità quasi identica a quelli giusti (0,905 contro 0,908; test di permutazione p = 0,22). Gli errori dipendono dalle formule e dal contesto, non dalla leggibilità della pagina; il file serve a chi vuole escludere le pagine peggiori in un'analisi di robustezza.

**Accordo fra due letture indipendenti.** Le verifiche sull'immagine dicono quanto sono accurati i dati solo se il giudizio di chi legge è a sua volta riproducibile. 50 record della verifica sistematica (blocchi 3 e 4, estratti a caso, seme 2036) sono stati riletti da un secondo lettore, sulle stesse immagini e con le stesse istruzioni, senza accesso ai verdetti del primo. Escludendo i casi in cui uno dei due non poteva decidere (2 per la domanda «è un emendamento?», 4 per i firmatari), l'accordo è completo: 48/48 sull'esistenza dell'emendamento (kappa di Cohen 1,00; accordo 100%, IC 92,6–100) e 46/46 sulla correttezza dei firmatari (kappa 1,00; IC 92,3–100), compresi i 3 falsi positivi e i 4 elenchi sbagliati che entrambi hanno riconosciuto. Poiché i due lettori seguono le stesse istruzioni scritte, il risultato misura la riproducibilità del giudizio, non l'assenza di errori che entrambi potrebbero commettere allo stesso modo. File: `pipeline/extraction/VERIFICA_kappa_coppie.csv`.

**Accuratezza dei voti.** Su 23 voti con totali ufficiali, 21 hanno uno scarto di al massimo tre nomi per lato tra nomi abbinati e totali (`controllo = ok`). Nei voti v16 e v21 l'estrazione è fedele alla pagina, ma è l'elenco stampato a non coincidere con i totali annunciati (`verificato: …`). Quattro votazioni (v4, v10, v13, v23) sono nulle: il Presidente annuncia che il numero legale non è stato raggiunto e non comunica i totali (`numero_legale_mancato = 1`, `controllo = votazione nulla: …`); i voti espressi sono stampati e restano nel dataset, perché registrano comunque la posizione di chi ha risposto alla chiama, ma l'Assemblea non ha deliberato. Tutte e quattro le dichiarazioni sono state verificate sull'immagine. I totali ufficiali letti male dall'OCR («1» scambiato per «4») sono corretti con l'aritmetica del riquadro: se sì + no non dà i votanti, si sostituisce un «4» con «1» e la correzione si accetta solo se è l'unica che fa tornare la somma (v24: «434» e «471» letti per 134 e 171, verificato sull'immagine; v27). Il totale di v7 è corretto a mano sull'immagine, perché anche i votanti sono letti male e la somma non può fare da giudice. I totali sono stampati in due formule, «Hanno risposto sì / no» e «Voti favorevoli / contrari»: l'estrazione le legge entrambe.

Gli elenchi dell'appello nominale sono stampati in ordine alfabetico, e questo è un vincolo esterno sfruttabile: un cognome storpiato dall'OCR («CARIEPA», «LACOTII», «VANOM») può essere cercato solo fra i cognomi compresi fra il precedente e il successivo già abbinati. Dove la fascia contiene al massimo otto nomi e la somiglianza supera la soglia, il nome è recuperato (`abbinamento = fascia alfabetica`): 20 casi. Lo stesso vincolo fa da controllo sugli abbinamenti approssimati: se il cognome scelto per somiglianza rompe l'ordine dell'elenco, l'abbinamento è annullato e il nome ripassa per la fascia. Sei abbinamenti sono stati corretti così, tutti confermati sul testo della pagina: «Vanni» fra Farina e Farini è la coda di «Farina Gio-vanni», non Vanoni; «Gio-htti» è Giolitti, non Iotti; «Prell» fra Pressinotti e Preziosi è Preti, non Pella; «Mana» fra due Rossi è «Rossi Maria Maddalena», non Marina; «Massiani» fra Caso e Castelli è Cassiani, non Massini; «Berné&monti» è Bernamonti, non Montini. Nella fascia si riconosce anche la coda di un cognome spezzato dalla sillabazione (un solo cognome della fascia che finisce così) e il cognome doppio diviso in due pezzi («Garpano — Maglioli», Carpano Maglioli). Un cognome stampato da solo e condiviso da più costituenti («Rossi», «Orlando», «Leone») si risolve in due modi: con il nome proprio che l'OCR ha staccato nella riga successiva («Morelli — Nato», Morelli Renato), oppure per esclusione, perché una persona vota una volta sola e gli omonimi già abbinati nello stesso voto non possono essere lui («Rossi» fra Rossi Giuseppe e Rossi Paolo è Rossi Maria Maddalena): `abbinamento = omonimo risolto`, 7 casi su 8; resta ambiguo un «Barontini» (Anelito o Ilio). «De Unterrichter Maria» (Maria Jervolino) è riconosciuta anche quando l'OCR stacca il «De» con un punto o storpia il cognome («Unterrichier»). Sono esclusi i nomi propri staccati («Maria», «Luigi») e le parole di verbale catturate dall'elenco («Dichiaro», «Votazione», «Segretari»). Le righe che ripetono un costituente già presente nello stesso voto — duplicati di stampa o di OCR, come «Cingolani Mario» seguito da «Cingolani» — sono marcate `duplicato` e non generano un secondo arco: 11 casi. Il giudice di entrambe le operazioni è esterno, perché sono i totali annunciati dal Presidente a dire se il recupero è corretto: lo scarto medio fra nomi abbinati e totali ufficiali scende da 3,05 a 2,64 nomi per votazione (2,52 dopo il controllo dell'ordine alfabetico e 2,26 dopo la risoluzione degli omonimi, sui 23 voti con totali), con 8 votazioni più vicine al totale e nessuna allontanata (l'unico scarto in crescita è v16, dove la rimozione di un duplicato rende visibile un elenco stampato davvero incompleto).

**Validità di costrutto: coesione dei gruppi.** Se l'abbinamento dei nomi nei voti fosse rumoroso, i gruppi notoriamente disciplinati risulterebbero poco compatti. L'indice di Rice per gruppo e votazione (|sì − no| / (sì + no), astenuti esclusi, gruppi con almeno 5 voti espressi; `tools/coesione_voto.py`, dettaglio in `pipeline/extraction/coesione_voto.csv`) dà in media sulle 27 votazioni 0,996 per il gruppo comunista (0,1 voti dissenzienti per votazione), 0,983 per il democristiano, 0,93 per il socialista, 0,83 per il socialista dei lavoratori, 0,91 per il repubblicano, e 0,46 per il gruppo misto, che per natura non vota compatto. Il gruppo è quello finale: la scissione socialista del gennaio 1947 precede quasi tutte le votazioni.

Controlli di coerenza su tutto il dataset: nessun voto fuori dal mandato, nessuna firma fuori dal mandato; se un costituente compare in due elenchi dello stesso voto si tiene l'abbinamento esatto, e se lo sono entrambi il suo voto resta mancante.

### Variabili degli emendamenti (`emendamenti_nodi.csv`)

| Variabile | Descrizione |
|---|---|
| `firmatari_id`, `n_firmatari` | Firmatari (id separati da `\|`) e loro numero |
| `completo` | 1 se l'elenco dei firmatari è completo, 0 se termina con «ed altri» |
| `articolo_menzionato` | Ultimo numero d'articolo citato nelle righe intorno alla menzione («all'articolo 31»), come stampato. È spesso un articolo citato di passaggio (nel testo dell'emendamento o nel discorso): sul campione di sviluppo coincide con l'articolo emendato in 7 casi su 13. Preferire `articolo_in_discussione` |
| `articolo_in_discussione` | Articolo del testo in esame (numerazione del progetto di Costituzione o del disegno di legge discusso in quella seduta) a cui l'emendamento si riferisce, ricavato dall'ordine dei lavori stampato dal Presidente («Passiamo all'articolo 31», «Si dia lettura dell'articolo 86»): l'ultimo annunciato prima della menzione; se sulla pagina ne sono annunciati più d'uno, quello che coincide con `articolo_menzionato`. Assegnato a 916 emendamenti su 1.408. Su un campione di convalida letto alla cieca sull'immagine (seme 2045) è giusto in 14 casi su 20: 70% (48,1–85,5); gli errori sono di un articolo (l'emendamento letto prima dell'annuncio del successivo) o articoli aggiuntivi («8-bis» registrato come 8). `pipeline/extraction/controllo_articolo.csv` riporta per ogni emendamento anche gli articoli annunciati sulla pagina e l'esito del confronto con `articolo_menzionato` |
| `materia` | Parte e titolo del progetto di Costituzione a cui appartiene l'articolo emendato («Parte I - Titolo III» = rapporti economici; «Parte II - Titolo V» = Regioni, Province, Comuni…), dalla tavola della Camera (`pipeline/fonti/tavola_progetto_costituzione.tsv`: articolo del progetto → articolo della Costituzione, con le date della discussione in Assemblea). Assegnata a 995 emendamenti; vuota per le sedute su altre leggi o senza articolo determinabile. Su 18 emendamenti del campione di convalida letti sull'immagine è giusta in 17 |
| `articolo_costituzione` | Articolo (o articoli, separati da «;») della Costituzione approvata che corrisponde all'articolo emendato del progetto, dalla stessa tavola. La numerazione dell'articolo emendato è affidabile al 67–70% (vedi sopra); la materia molto di più, perché gli errori sono quasi sempre di un articolo vicino dello stesso titolo |
| `controllo_data` | Confronto con le date della tavola: `data coerente` (la seduta cade in un giorno in cui quell'articolo fu discusso: 871), `unico articolo discusso quel giorno` (l'articolo è dedotto dalla data: 124), `giorno senza articoli del progetto` (la seduta discute un'altra legge: 112), `data discordante` (44: da guardare), `non determinato` |
| `prima_seduta`, `data`, `pagina`, `url_pdf` | Prima menzione e link alla pagina del resoconto |
| `fonte` | `firma` (blocco di firma) o `presentazione` (formula di presentazione) |
| `id_presentatore` | Chi presenta l'emendamento: il nome indicato da una formula («L'onorevole X ha presentato… firmato anche dagli onorevoli», «insieme con», «da me e dagli onorevoli», il nome in testa al turno di parola) o, in mancanza, il primo firmatario stampato, che per convenzione del resoconto è il presentatore. Vuoto se il primo nome stampato non è abbinato (omonimo irrisolto, nome illeggibile): in quel caso il secondo firmatario non viene promosso al suo posto |
| `presentatore_fonte` | `formula`, `primo dell'elenco`, `firma singola` o `non identificato` |
| `tipo_emendamento` | `sostituire`, `sopprimere`, `aggiungere`, `inserire` o `non determinato`: la prima operazione nella formula d'apertura del testo («Sostituirlo col seguente», «Al secondo comma sopprimere…»); se il testo non la stampa, dall'aggettivo della presentazione («emendamento soppressivo», «articolo aggiuntivo»). Accordo con la lettura cieca dell'immagine: 29/40 = 72,5% (57,2–83,9). L'errore più frequente è un testo integrale stampato senza verbo («la seguente dizione: «…»»), che l'estrattore lascia `non determinato` e chi legge classifica come sostituzione: è una codifica di primo livello, da usare con prudenza |
| `esito` | `approvato`, `respinto`, `ritirato`, `decaduto (assente)`, `assorbito` o `non determinato`. Si cerca, dalla pagina dell'emendamento in avanti nella stessa seduta (e nelle due successive solo se accanto ricorre un pezzo del testo), la messa ai voti che nomina il primo firmatario seguita dalla didascalia «(È approvato)» / «(Non è approvato)», il ritiro detto dal firmatario in risposta alla domanda del Presidente («Onorevole X, lo mantiene?» — «Lo ritiro»), la decadenza per assenza, l'assorbimento. Le regole sono strette di proposito: un esito è assegnato a 236 emendamenti su 1.408 (17%), gli altri restano `non determinato` (votati in un testo concordato, decisi per alzata di mano senza nominarli, o con formule ambigue). Su un campione di convalida di 30 esiti assegnati, letti alla cieca sull'immagine (seme 2042), 26 sono giusti: 86,7% (70,3–94,7); due errori sono emendamenti votati di fatto nel testo della Commissione. Due campioni precedenti (40 + 30) sono serviti a scrivere le regole. File: `pipeline/extraction/VERIFICA_esiti_convalida_verificato.csv` |
| `testo` | Testo dell'emendamento come stampato fra virgolette dopo la formula di presentazione (o prima del blocco di firma), con i refusi dell'OCR; `/` separa i capoversi; vuoto se la pagina non lo stampa (139 casi, per lo più citazioni nei discorsi). Sul campione 5: 22 testi giusti, 6 parziali (un pezzo solo, o la frase seguente inclusa), 2 sbagliati, 5 assenti, 5 non verificabili dal ritaglio |

### Variabili delle menzioni nei discorsi (`menzioni_discorso.csv`)

| Variabile | Descrizione |
|---|---|
| `seduta`, `data`, `pagina`, `url_pdf` | Dove sta la menzione |
| `id_parlante`, `parlante_stampato`, `ruolo_parlante` | Chi parla: id, intestazione del turno come stampata, eventuale ruolo («Presidente della Commissione», «Relatore», «Ministro…») |
| `id_menzionato`, `forma_stampata` | Chi è nominato e come lo stampa il resoconto. Vuoto se il cognome è di più costituenti e nessuno dei due parla in quella seduta (258 casi) o se il nome non corrisponde a un costituente (134: deputati del passato, ministri non costituenti, refusi) |
| `abbinamento` | Come è stato abbinato il nome (`esatto`, `approssimato`, `prefisso`, `+seduta` per gli omonimi risolti con chi parla nella seduta, `ambiguo`, `non trovato`) |
| `tipo_menzione` | `su un emendamento`, `atto di parola`, `didascalia`, `altro` |
| `contesto` | Il testo attorno, con la menzione fra `[[ ]]` |

**Accuratezza.** Due campioni di 40 menzioni estratte a caso, letti sull'immagine con le colonne intere della pagina e la colonna precedente. Il primo ha messo in luce le intestazioni di turno stampate in linea, che facevano attribuire all'oratore precedente le parole del Presidente, e le didascalie fra parentesi: corrette entrambe. Sul secondo, dopo le correzioni: menzioni vere 40/40; persona menzionata giusta 40/40 (100%, IC 91,2–100); chi parla giusto in 31 casi su 31 in cui l'inizio del turno è visibile (100%, IC 89,0–100), mai sbagliato; tipo della menzione giusto 33/40 (82,5%, IC 68,0–91,3), perché `su un emendamento` dipende dalla parola «emendamento» o «proposta» nelle vicinanze e non coglie le frasi che parlano del contenuto di un emendamento senza nominarlo. File: `pipeline/extraction/VERIFICA_menzioni_discorso_verificato.csv`.

### Variabili dei voti (`voti_nodi.csv`)

| Variabile | Descrizione |
|---|---|
| `seduta`, `data`, `pagina`, `url_pdf` | Seduta e link alla pagina della chiama |
| `label_en`, `on_constitution` | Oggetto del voto (in inglese) e se riguarda la Costituzione |
| `si_ufficiali`, `no_ufficiali`, `astenuti_ufficiali` | Totali annunciati dal Presidente |
| `si_abbinati`, `no_abbinati`, `astenuti_abbinati`, `congedo_abbinati` | Nomi abbinati ai costituenti |
| `scarto_si`, `scarto_no`, `controllo` | Differenza tra abbinati e ufficiali, ed esito del controllo |
| `numero_legale_mancato` | 1 se il Presidente annuncia che il numero legale non è stato raggiunto (votazione nulla, totali non comunicati) |
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

### Commissione per la Costituzione e presenza agli appelli

| Variabile | Descrizione |
|---|---|
| `commissione_75` | 1 se ha fatto parte della Commissione per la Costituzione in qualunque momento (97 persone, per le sostituzioni) |
| `sottocommissione` | `I`, `II`, `III` (più d'una separate da «;») |
| `comitato_redazione` | Comitato di redazione, detto «dei 18» (20 persone nel tempo) |
| `ruolo_commissione` | Carica più alta nella Commissione o nei suoi organi: `presidente`, `vicepresidente`, `segretario`, `componente` |
| `voti_in_carica` | Votazioni per appello nominale tenute mentre era in carica (su 27) |
| `voti_presente`, `voti_congedo`, `voti_assente` | Ha risposto sì, no o si è astenuto; era in congedo; non risulta in nessun elenco. Le votazioni nulle per mancanza del numero legale contano, perché la chiama c'è stata |
| `quota_presenza` | `voti_presente / voti_in_carica`. Un nome stampato ma non abbinato fa risultare assente chi ha votato: l'errore è quello misurato sui totali ufficiali (in media 2,3 nomi su circa 350 per votazione). Terracini, Presidente dell'Assemblea dal febbraio 1947, non compare mai negli elenchi |
| `eletto_camera_1948` | 1 se eletto alla Camera il 18 aprile 1948 (I legislatura; esclusi i subentrati): 260. Fonte: elenco degli eletti per circoscrizione su Wikipedia, `pipeline/fonti/eletti_camera_1948_wikipedia.txt`; tutti i 260 risultano deputati della Repubblica nei dati della Camera (`deputato_rep`). Il Senato del 1948 non è coperto: `futuro_senatore` dice se una persona è stata senatrice, non quando |

Fonte: `edgelist.csv` (organi o621–o625) e `edgelist_voti.csv`; calcolate da `pipeline/tools/arricchisci_costituenti.py`.

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
