# Networks of the Italian Constituent Assembly (1946–1948) — codebook

A dataset on the 581 members of the Italian Constituent Assembly. It contains one formal network (membership of committees and other bodies) and three interaction networks built from day-to-day activity on the floor and in committees.

**Why 581 and not 556.** The Assembly had 556 seats: that is how many deputies sat at any one time, and it is the figure usually quoted. The 581 rows of `members_nodes.csv` are instead the *people* who held one of those seats for at least a day between 1946 and 1948. The difference is turnover: deaths, resignations, forfeitures and the options exercised by candidates elected in several constituencies, all replaced as the work went on. The fields `term_start` and `term_end` make it possible to reconstruct who was in office on a given date: on 22 December 1947, the day the Constitution was approved, there were exactly 556. Anyone who would rather treat the Assembly as a body of 556 can filter on that date.

## How the Assembly was elected

Knowing how those 581 names came about helps in reading the dataset's electoral variables.

Voting took place on **Sunday 2 June 1946**, the same day as the referendum between monarchy and republic. It was the first national election under **universal suffrage**: all citizens aged 21 and over voted, women and men alike. Twenty-one women were elected.

The system was **proportional representation with competing lists**, in 32 multi-member constituencies, plus a **national pool** to which the remaining seats were allocated: 81 of the dataset's 581 members were elected there, and for them `constituency` and `election_region` both read «COLLEGIO UNICO NAZIONALE» and «NATIONAL POOL». Aosta Valley had a single-seat constituency.

The electoral law provided for 573 deputies, but **556** were elected: no polling took place in Gorizia, Trieste, Pola, Fiume, Zara and Bolzano. The dataset's 581 are those 556 plus the members who replaced others during the Assembly's work (see «Why 581 and not 556»).

The Assembly first met on **25 June 1946** and approved the Constitution on **22 December 1947**, after 347 sittings, 170 of them devoted to the constitutional text.

Two absences in the data are legitimate and should not be read as gaps: `degree_field` is empty for members without a degree, and one member (Amedeo Filippo, in office from 13 to 18 June 1946) has no parliamentary group because the groups were formed after the first sitting.

Sources for this section: Chamber of Deputies, [page on the Constituent Assembly](https://comunicazione.camera.it/eventi/80-costituente/assemblea-costituente); Wikipedia, [Assemblea Costituente (Italia)](https://it.wikipedia.org/wiki/Assemblea_Costituente_(Italia)).

**Sources** (retrieved 22 October 2026): Italian Chamber of Deputies open data (dati.camera.it) and the costituente.camera.it portal; Italian Senate open data (dati.senato.it); Wikidata; Italian Wikipedia.

Source texts (debate topics, document titles, occupations as recorded, Wikipedia evidence) are kept in Italian. Party lists and parliamentary groups keep their original Italian names.

## Files

| File | Content |
|---|---|
| `members_nodes.csv` | One record per member, with 99 attributes |
| `bodies_nodes.csv` | 31 bodies: committees, subcommittees, boards |
| `edgelist_bodies.csv` | Two-mode network, member × body (756 ties), with role |
| `edgelist_bodies_spells.csv` | As above, one record per spell of membership (767) |
| `edgelist_projection_members.csv` | One-mode projection: members sharing bodies (weight = number of shared bodies) |
| `topics_nodes.csv` | 738 topics debated on the floor and in committees |
| `edgelist_topics.csv` | Two-mode network, member × topic (5,521 ties) |
| `edgelist_exchanges.csv` | One-mode interaction network: members speaking on the same page of the record (7,787 pairs) |
| `edgelist_corapporteurs.csv` | Reports and proposals signed jointly (16 pairs) |
| `edgelist_substitutions.csv` | Directed network: who replaced whom on a body (99 ties) |
| `amendments_nodes.csv` | 1,532 amendments tabled in the Assembly, extracted from the records by OCR |
| `edgelist_amendments.csv` | Two-mode network member × amendment (who signed, with the role of proposer or signatory; 3,547 edges) |
| `speech_mentions.csv` | Directed network of mentions in speeches: who, speaking in the Assembly, names whom (9,824 mentions) |
| `votes_nodes.csv` | 29 roll-call votes, with official totals and check |
| `edgelist_votes.csv` | Two-mode network member × vote, with the vote cast (yes, no, abstain) |
| `edgelist_amendments_conservative.csv`, `edgelist_votes_conservative.csv` | Conservative version of the two networks: only edges with an exact name match or a list corrected by hand from the image (3,216 co-signature edges of 3,275; 9,007 vote edges of 9,125) |
| `graphml/*.graphml` | The six networks already built in GraphML (two-mode and projected co-signature, directed signatory → proposer network, signed votes, mentions, other acts), for Gephi, igraph, networkx; `R/00_build_networks.R` builds the same `igraph` objects from the CSVs |
| `group_spells.csv` | Membership of parliamentary groups with start and end dates (685 spells, 580 members), from the Chamber's open data (dati.camera.it); `group_at_date` in the co-signature and vote edge lists is computed from it |
| `other_acts_nodes.csv` | 897 co-signed acts that are not amendments: questions, interpellations, orders of the day, motions, vote requests |
| `edgelist_other_acts.csv` | Two-mode network member × act (2,111 edges) |
| `evidence_wikipedia.csv` | Wikipedia categories and sentences behind the antifascism and Resistance indicators |

Identifiers: `d` + Chamber id for members, `o` + id for bodies, `t` + number for topics.

## The networks

**Bodies (formal).** Membership of committees, subcommittees, and boards. Seats were allocated to parliamentary groups in proportion to their size, so this network records assigned positions, not individual choices.

**Topics (two-mode).** A topic is a matter under debate: on the floor, the title of the debate (for example an article of the draft Constitution); in committee, the item discussed (for example "La famiglia"). The weight is the number of record pages with the member's contributions on that topic.

**Exchanges (one-mode, undirected).** Two members are tied if they both speak on the same page of the same record. This is a close proxy for direct confrontation: replies, interruptions, rejoinders. `n_pages` counts shared pages; `n_pages_no_chair` drops pages where either member chairs that body, since chairs appear for procedural reasons. A tie does not distinguish agreement from disagreement.

**Co-rapporteurs.** Subcommittee reports and reports on bills signed by more than one member. A small network, but of explicit collaboration.

**Substitutions (directed).** `incoming` → `replaced`, with body and date.

**Amendments (two-mode).** Who signed an amendment together: a chosen tie, unlike committee membership. Projected onto members, it measures collaboration in drafting the text.

**Amendments (two-mode, directed).** `edgelist_amendments.csv` has a `role` column: `proposer` for whoever tabled the amendment, `signatory` for those who co-signed it. Projecting only the signatory → proposer edges gives a directed network: who gathers signatures and who gives them. The proposer was compared with the list transcribed from the image for the 131 multi-signatory amendments of the systematic check: it matches in 130 of 131 cases (99.2%, CI 95.8–99.9); the only error («presentato dall'onorevole Gasparotto e da me», where the speaker was placed first) was fixed in the extractor. Of 1,532 amendments, 199 have the proposer given by a formula, 227 by the first name in the list and 1,014 are single-signatory.

**Mentions in speeches (directed).** Who, speaking in the Assembly, names another member: «l'onorevole X», «dell'/dall'/all'onorevole X», «il collega X», «on. X». Unlike co-signature it is an asymmetric, unagreed tie, and measures who is taken as a reference in the debate. The speaker is the name heading the speaking turn, also when the heading is printed inline («…(Approvazioni). PRESIDENTE. Pongo in votazione…»); turns of the President of the Assembly are excluded, because almost all are procedural («Ha facoltà di parlare l'onorevole X»), as are self-mentions. `mention_type` distinguishes mentions concerning an amendment, speech acts («le dichiarazioni dell'onorevole X», the same phrases the amendment extractor discards), stage directions in the record («(Interruzione dell'onorevole X)», which record an interaction but are not the speaker's words) and others. Code: `tools/estrai_menzioni_discorso.py`, which uses the same reading and name-matching rules as the amendment extractor.

**Roll-call votes (two-mode, signed).** How each member voted in the 29 roll calls. Absences and leave are not edges.

## Amendments and votes: construction and accuracy

Signatures on amendments and roll-call votes are not available in structured form: they appear only in the verbatim records of the Assembly, published as images. They were reconstructed as follows (code in `pipeline/`):

1. **OCR.** The records of the 189 sittings with amendments or roll calls (5,160 pages) were converted to text with Tesseract (Italian model), splitting the two columns of each page (`ocr_costituente.R`). The 3,275 pages that mention amendments were read again at 400 dpi (`ocr_400dpi.R`); for each page the reading that recognises more members' surnames is used.
2. **Amendments.** They are identified by presentation formulas («l'onorevole X ha presentato il seguente emendamento») and by signature blocks; the classifier excludes questions, interpellations, motions, orders of the day and requests for a roll call. Names are matched to the members in office on the date of the sitting (`estrai_emendamenti.py`).
3. **Votes.** For each roll call the lists «Rispondono sì», «Rispondono no», «Si sono astenuti» and «Sono in congedo» are extracted and compared with the totals announced by the President (`estrai_voti.py`).
4. **Check.** 73 randomly drawn mentions were checked against the PDF: 40 (seed 1947) by hand, 34 from the page image, oversampling amendments with several signatories (seed 1948). The systematic errors found were fixed in the code: lists of distinct amendments («gli emendamenti degli onorevoli X, Y e Z») mistaken for joint signatures, the proposer omitted in «firmato anche dagli onorevoli» formulas, questions to ministers, and OCR noise between names. Votes with discrepancies of more than three names were checked against the page image.
5. **Completeness.** 10 randomly drawn pages (seed 2026) were read in full to find amendments with several signatories that the extraction missed. There were 6, of which 2 were extracted correctly. The causes (the formula «Gli onorevoli X e Y hanno presentato…», «a firma degli», «insieme con gli onorevoli», signature blocks broken by OCR, hyphenation, OCR noise in names) were fixed across the whole corpus; after the fix 5 of the 6 are complete and the sixth has 7 of 9 signatories. An automatic search for sentences with two or more surnames that were not extracted (`cerca_mancati.py`) guided further fixes. The number of amendments with several signatories rose from 217 to 327. A second check on a further 20 pages (seed 2027, excluding the earlier ones), carried out in the same way, found 5 amendments with several signatories: all 5 had been extracted with the full list of signatories. The other 17 pages contained none; the multiple signatures they do carry belong to parliamentary questions and interpellations, which are outside the dataset by construction. Details in `pipeline/extraction/richiamo2/ESITO.md`.

**Accuracy of amendments.** Amendments do not exist as structured data: they are derived from the text of the records and contain errors. They were measured on four samples, each record read against the page image: 219 records in all. The first two (99 records) guided the fixes to the extractor, so their rates are optimistic by construction. The third (40 records) and the fourth (80 records) were drawn at random **after** the respective fixes, among records never looked at before, and are the estimates to use (Wilson 95% intervals; `tools/valuta_campioni.py`):

| | sample 3 | sample 4 |
|---|---|---|
| false positives | 3/40 = 7.5% (2.6–19.9) | **2/80 = 2.5% (0.7–8.7)** |
| missing or wrong signatories | 1/37 = 2.7% (0.5–13.8) | **6/78 = 7.7% (3.6–15.8)** |
| — among amendments with 2+ signatories | 1/22 = 4.5% (0.8–21.8) | 5/38 = 13.2% (5.8–27.3) |

The two samples measure successive versions of the extractor. Between them false positives fell by two thirds, because reading the context of every single record made the recurring forms visible and discardable: a name governed by a speech-act noun («le parole, le dichiarazioni, l'opinione dell'onorevole X» — the words, statements, opinion of Member X), a list of distinct acts governed by a plural («gli emendamenti degli onorevoli X, Y e Z»), collective acts that are not amendments (requests for a roll-call vote, orders of the day, resolutions, open letters), and the chair of a committee speaking in that capacity.

The fourth sample brought the opposite problem into focus, which the third had underestimated: **incomplete lists of signatories**. The causes are OCR line breaks inside a surname, co-signature formulas that went unrecognised («che reca anche le firme dei colleghi…» — which also bears the signatures of colleagues…), and surnames printed in the records in a different form from the official roll. Four of the six cases found were fixed after the measurement, which therefore remains a **conservative** estimate: the published version's rate is lower than the figure stated. The two remaining are OCR misreadings of names («Toncilo» for Tonello, «Gabriele» for Gabrieli).

**Namesakes.** Where the record prints only a surname and two members share it (Gullo Fausto and Gullo Rocco, Mastino Pietro and Mastino Gesumino, Pajetta Gian Carlo and Pajetta Giuliano…), the match is resolved in three steps: the party prevailing among the co-signatories already identified; the signatures the candidates have put elsewhere alongside the other members of the group; and finally presence in that same sitting — a namesake who never appears in that sitting cannot have tabled the amendment. The third rule was tested on 248 held-out cases, built by taking the names for which the record also prints the first name and hiding it: the rule picked the right person 248 times out of 248. Nineteen names remain ambiguous, nearly all Gullo, Mastino, Mariani and Cortese, where both candidates are active in the sitting: those signatures are dropped rather than assigned at random. The `abbinamento` column of `menzioni_nomi.csv` records which rule was used for each name.

The errors found in the samples are corrected by hand in the data (`esporta_dataset.py`); the rates are estimates for the remaining amendments. `complete = 0` flags lists ending with «ed altri» (and others), whose further signatories are unknown.

**Lists cut short by OCR.** An internal signal identifies records where the column read more names than were matched: these are lists broken in the middle by hyphenation or by a dirty line («… La Rocca, Togliatti, Mora-/‘nino»). All eleven cases in the corpus were read from the page image. Two general defects emerged and were fixed in the extractor: end-of-line hyphenation printed with two or three dashes, and a proposer identified only by the name heading the speaking turn («LACONI. Presento all'Assemblea il seguente emendamento firmato anche dai colleghi…»). The remaining differences are individual corrections recorded in `esporta_dataset.py`, among them one amendment that had absorbed a signatory from the one printed above it. In all, co-signature edges rise from 2,246 to 2,269.

**Regression test and second round of fixes.** `tools/test_regole.py` runs the extractor on 67 real passages from the records, each with its expected outcome (the signatory lists it must produce, or none), and checks in about a second that a change to one rule does not break another; the cases are in `tools/test_regole_casi.json`, and those marked «controllato sull'immagine» were compared with the scan. Building the test exposed general defects, which were fixed in the extractor and checked record by record against the page image: (1) hyphenation with a stray mark between the dash and the line break («MARAZ-'» / «- ZA», «Cle-.» / «rici») split the signature block or list, and the amendment was lost entirely: missing as a result were, among others, an additional article with 16 signatures (sed126) and two Christian Democrat amendments with 28 and 16 signatures (sed119, sed122); (2) consolidation absorbed a single-signatory amendment into any longer list containing that name, even when it was a separate act («Segue l'emendamento dell'onorevole Bubbio», thirteenth signatory of another one): a single name is now absorbed only if it is the first signatory, because the record refers to an amendment by its first signer's name; (3) the plural governing a list («gli emendamenti degli onorevoli…») reached across a sentence ending right before the mention («…pervenute. Gli onorevoli») and across a nearer singular («…valgono anche per l'emendamento degli onorevoli…»); (4) the proposer was missed in the forms «l'onorevole X ha ora presentato…», «l'onorevole X, la quale, insieme con gli onorevoli…» and «presentato dagli onorevoli X, Y e da me»; (5) a request for a roll-call vote in the *following* sentence deleted the amendment tabled in the sentence before. Also added: «presentati rispettivamente dagli onorevoli» (separate acts), «interruzione» and «cortesia» (speech acts), surnames run together without a comma («Targetti Amadei e Bordon») and the conjunction with a stray full stop («Rodnò Mario e. Puoti»). Finally, two manual corrections recorded in `esporta_dataset.py` were not being applied because their key included the first name («Rossi Paolo»): they now apply, and a missing signatory (Bianchi Bianca, sed261) is restored. Amendments rise from 718 to 787, those with 2+ signatories from 329 to 337, co-signature edges from 2,269 to 2,425.

**Completeness (recall): how many printed amendments are in the dataset.** All earlier measures concern precision: they say whether what was extracted is right, not how much is missing. To measure recall, whole sittings were drawn at random from the 165 in the corpus that discuss the draft Constitution, and every page was read from the image by a reader who did not see the dataset, noting every printed amendment with a named proposer (tabled, read out, voted, withdrawn or cited in a speech) and a degree of certainty. An amendment counts as captured if, in the same sitting and on the same page (±1), there is a mention of its signatories linked to an amendment not already used for another row. The main measure uses high-certainty rows; medium- and low-certainty rows are mostly proposals made orally in the general debate, which the reader was not sure were amendments.

| | sittings | amendments (high certainty) | version published 26.10 | after the fixes |
|---|---|---|---|---|
| sample 1, seed 2028 (development) | sed060, sed115, sed220, sed224, sed231 | 30 | 10/30 = 33.3% (19.2–51.2) | 28/30 = 93.3% (78.7–98.2) |
| sample 2, seed 2030 (development) | sed170, sed251, sed254, sed292 | 19 | 10/19 = 52.6% (31.7–72.7) | 17/19 = 89.5% (68.6–97.1) |
| **sample 3, seed 2031 (validation)** | sed118, sed149, sed215, sed252, sed282 | 30 | 17/30 = 56.7% (39.2–72.6) | **20/30 = 66.7% (48.8–80.8)** |

95% Wilson intervals. Samples 1 and 2 guided the fixes, so their post-fix values are optimistic by construction. Sample 3 was drawn and read after the rules had been frozen, and is **the estimate to use: amendment recall is about two thirds** (67%, interval 49–81%). Two minor fixes introduced after reading it raise it to 22/30, but that value is no longer an independent estimate. Recall for amendments with **several signatories**, the only ones that produce co-signature edges, is much higher: 9/10 in the validation sample (90%, interval 60–98) and 21/22 across the three samples. Losses therefore concern mainly single-signatory amendments, that is per-person counts rather than the network.

The causes found were general and were fixed in the extractor: (1) the formula with which the President reads a single-signatory amendment, «L'onorevole X ha presentato il seguente emendamento», was not recognised as a presentation (it was only used to add the proposer to «firmato anche dagli onorevoli» lists), and with its variants («ha proposto di sopprimere», «ha presentato a questo articolo», «l'onorevole X, a sua volta, ha proposto che») it was the main cause of loss; (2) the forms «dall'onorevole X», «Dall'onorevole», «della onorevole», «dal collega onorevole», «unitamente agli onorevoli», and lists repeating «dell'onorevole» before each name, were missing; (3) consolidation merged into one amendment all those by the same signatory in nearby sittings (Nitti, Colitto, Caronia, Conti, Perassi table many), which are now kept apart by their text; (4) a speaker's own proposals («CRISPO. … Propongo che l'articolo 4 sia redatto nel modo seguente: «…»», «Ho presentato questo emendamento») are attributed to the name heading the speaking turn; (5) OCR noise («Dallonorevole», «onorevo!e», «onòérevole», «preseritato», a stray quote between the formula and the name) and sentence endings with stray quotation marks. Deliberately still excluded are «proposals» cited in the general debate without being called amendments («la proposta dell'onorevole Rubilli»), because in that form the word more often denotes a position than an act.

The new rules were also checked for precision, on a **fifth sample of 40 records** drawn at random from all and read from the image: false positives 2/40 = 5.0% (1.4–16.5), counting as errors the two cases the crop did not allow to judge; missing or wrong signatories 3/38 = 7.9% (2.7–20.8), in line with sample 4. The three error families found (the proposer in «Abbiamo presentato… firmato anche dagli» and «firmato anche da me», and the proposer confused with whoever speaks to the amendment) were fixed after the measurement. An earlier round, checked on 40 new records, had found two other false-positive families introduced by the «dall'onorevole» form («fatto proprio dall'onorevole X», «l'inconveniente accennato dall'onorevole X»), excluded before the final measurement. Amendments rise from 787 to 1,406, those with 2+ signatories from 337 to 395, co-signature edges from 2,425 to 3,227. Files: `pipeline/extraction/VERIFICA_recall_campione*.tsv` (readings), `VERIFICA_recall_campione*_esito.csv` (comparison), `VERIFICA_precisione_campione5_verificato.csv`.

**Systematic check of amendments with several signatories.** All co-signature edges come from amendments with at least two signatories. After the fixes, 216 of the 395 had never been checked against the image; they were put in random order (seed 2033) and checked in blocks of 40, so each block is also a random sample. For each record the attributed list is compared with the printed one, checking in particular that the list does not continue beyond the column and that no name comes from the amendment printed above or below; cases the crop could not settle were re-read on full columns. Results by block (false positives; missing or wrong signatories among true amendments):

| block | false positives | wrong signatories |
|---|---|---|
| 1 | 2/40 | 1/38 |
| 2 | 2/40 | 1/38 |
| 3 | 2/40 | 3/38 |
| 4 | 1/40 | 2/39 |
| 5 | 2/40 | 2/38 |
| 6 | 0/16 | 0/16 |
| **all (216)** | **9/216 = 4.2% (2.2–7.7)** | **9/207 = 4.3% (2.3–8.1)** |

Almost all errors belonged to general families, fixed in the extractor: lists of separate acts («hanno proposto ciascuno un identico emendamento», «hanno presentato due emendamenti», «gli emendamenti, più sostanziali, degli onorevoli X e Y» with a stray OCR mark in between), lists of speakers («dall'onorevole X, dall'onorevole Y e da altri a favore dell'emendamento…»), signature blocks of interrogations («per sapere», «se non ravvisi») and vote requests garbled by OCR («chiesto la .votazione: a serutinio segreto»), the proposer in «ha facoltà di parlare l'onorevole X, per svolgere il seguente emendamento, firmato anche dagli onorevoli…», and two OCR errors inside a list («Tremelloni e-Carboni», «De' : Palma»). Blocks 5 and 6 revealed three more families: the signatures of interrogations announced at the end of a sitting (each opens with «Il sottoscritto chiede d'interrogare»), the roll-call request that «porta le firme anche degli onorevoli…», and the proposer being taken from the first «L'onorevole X ha presentato» in the window rather than the last, which attributed a list to the proposer of the previous amendment. Two lists continuing into the next column or page were corrected by hand. With this check, every one of the 394 amendments with several signatories in the dataset has been checked against the image at least once. Two uncertain cases remain: «Mariani» (Enrico or Francesco, both Socialists), left out, and «Massa» in a Liberal and Qualunquist list at sitting 322, attributed to Mazza (Uomo Qualunque) rather than Massola (PCI) on the basis of party and co-signatures, and marked as uncertain. File: `pipeline/extraction/VERIFICA_2plus_blocchi*_verificato.csv`.

**False positives among single-signatory amendments.** The formulas added in this round more than doubled the single-signatory records, which produce no edges but enter per-person counts. A dedicated sample of 60 randomly drawn singles (seed 2037), read from the image, gave 5 false positives plus 1 uncertain: 6/60 = 10.0% (CI 4.7–20.1), above the 5% threshold set for intervening. There were two families, fixed in the extractor: a name governed by a participle or noun of judgement («l'inconveniente segnalato dall'onorevole X», «le ragioni esposte dall'onorevole X», «le preoccupazioni dell'onorevole X», «definita come emendamento dall'onorevole X»), and someone who speaks to or takes up another member's amendment («l'emendamento dell'onorevole Nobile, svolto dall'onorevole Stampacchia», «ripreso dall'onorevole Pignatari»), as distinct from «l'emendamento già svolto dall'onorevole X», where X is the proposer. Across the corpus the fixes remove 10 records, all checked on their context. In 6 of the 60 the amendment had other signatories not in the single record (lists closed by «ed altri», or a signatory named elsewhere): the known limit for amendments that are cited rather than read. File: `pipeline/extraction/VERIFICA_singoli_campione6_verificato.csv`.

**Second sample of singles, after the fixes.** A new sample of 50 singles (seed 2038, excluding the previous 60), read blind on full page columns, separates two cases the first sample lumped together. In 4 records the name appears in a citation within someone else's speech («Per quanto riguarda l'emendamento dell'onorevole Piemonte», the rapporteur; «c'è già un emendamento presentato dall'onorevole De Vita», Macrelli): the amendment exists and belongs to that member, but the record comes from the citation rather than the reading, because the President's announcement was not extracted or lies more than three sittings away. These records are kept: they are the only trace of a real amendment, and when the announcement is extracted in nearby sittings the citation is already absorbed into it. True errors are 2 of 48 decidable (4.2%, CI 1.2–14.0): «la questione posta dall'onorevole Cevolotto», which is not an amendment, and «l'emendamento dell'onorevole Nitti, integrato dall'onorevole Ruini», attributed to Ruini. Counting citations too, records that do not match an amendment read at that point are 5/48 (10.4%, CI 4.5–22.2). One single was in fact an additional article with six signatories («Segue l'articolo 7-quinquies, proposto dagli onorevoli Paris, Gullo Rocco, La ‘ Malfa…»), lost because of the formula and a stray apostrophe inside the name. The three families are fixed in the extractor («integrato dall'», «posta / posto dall'» unless the proposal follows, additional article «proposto dagli», a quote mark followed by a space inside a name); the name fix also recovers the list «Monterisi, Caccuri, Perrone ' Capano, Gabrieli» (sed124, checked on the image). File: `pipeline/extraction/VERIFICA_singoli_campione7_verificato.csv`.

**Multiplex layer: other co-signed acts.** The rules that keep questions, interpellations, orders of the day, motions and requests for roll-call or secret votes out of the amendments also recognise these acts: instead of discarding them, the extractor records them in `other_acts_nodes.csv` with their type (`question` 784, `vote request` 28, `order of the day` 16, `interpellation` 12, `motion` 2; 257 with two or more signatories). Co-signing a question or a vote request follows a different logic from co-signing an amendment, and the two layers together form a multiplex network. On 20 acts with several signatories read blind on the image (seed 2046), the type is right in 17 cases and the signatory list in 19; the three type errors were amendments: one (sed265, Benvenuti and Clerici, preceded by the reading of an interpellation) was fixed in the extractor and recovered among the amendments, one is a citation of an amendment already in the dataset, one (sed329 p1) is a block of additional amendments at the start of the sitting. File: `pipeline/extraction/VERIFICA_altri_atti_verificato.csv`.

**Absorbed citations: the printed text.** A single-signatory amendment whose signatory is the first signatory of a multi-signatory amendment in nearby sittings was treated as a citation of the latter and absorbed. Now it is not absorbed if the single prints its own text and the list does not (unless the list's piece of text is contained in the single's): 17 distinct amendments by prolific proposers, previously merged (for instance three amendments by Badini Confalonieri on different articles in sed102), are separate again.

**Recall at the level of persons.** 108 members have no co-signature edge, and 64 appear neither in amendments nor in speech mentions. To rule out that they are invisible because of a pipeline error, `pipeline/tools/recall_persone.py` searches the corpus for their surname just after the word «emendamento» in a signature or presentation formula: the passages found (`pipeline/extraction/recall_persone.csv`) are almost all vote requests or citations, but three were missed amendments, and they revealed three general families fixed in the extractor: a colon after «dagli onorevoli:» (sed118, 11 signatories), the verb with a stray OCR accent («hanno prèsentato», sed123, 13 signatories) and «una proposta di articolo 8-bis, a firma degli onorevoli…» mistaken for a list of separate proposals (sed301, 12 signatories). The same fixes recovered the additional article with 42 signatories on the oath of the President of the Republic (sed268 p25, checked on the image). The rank correlation between the number of amendments signed and the pages of activity in the Assembly on the draft Constitution in the Chamber's index (`act_pages_constitution`) is 0.66: those who speak a lot sign a lot, as expected if names are not being lost.

**Two versions of the networks.** Every edge in `edgelist_amendments.csv` and `edgelist_votes.csv` carries a `matching` column, the criterion by which the name was recognised: `exact`, `exact+party`, `prefix`, `namesake+cosignatures` and `namesake+sitting` (resolved namesakes), `approximate`, `alphabetical band`, `namesake resolved`, `manual correction` (list read on the image), `manual decision` (from the open-cases sheet). The `*_conservative.csv` files keep only `exact`, `exact+party` and `manual correction`. Showing that a result holds on both versions is the most direct answer to the objection that the data come from OCR; `pipeline/extraction/incertezza_rete.csv` does the same in a continuous way (see below).

**Uncertainty of network statistics.** `pipeline/tools/incertezza_rete.py` propagates the errors measured on the image to the statistics of the co-signature network: in 1,000 replicates it removes each multi-signatory amendment with probability 0.042 (false positives) and each signature with probability 0.043 (wrong signatories). Results (`pipeline/extraction/incertezza_rete.csv`; observed, conservative version, 95% interval of the replicates):

| Statistic | Observed | Conservative | 95% CI |
|---|---|---|---|
| Density of the projection | 0.044 | 0.043 | 0.037–0.042 |
| Mean degree | 25.8 | 24.9 | 21.2–24.1 |
| Degree centralization | 0.189 | 0.187 | 0.141–0.191 |
| Share of ties within the same group | 0.640 | 0.641 | 0.626–0.691 |
| Homophily (observed / chance share) | 3.17 | 3.18 | 3.10–3.43 |
| Reciprocity signatory → proposer | 0.104 | 0.098 | 0.084–0.104 |

Structural measures (homophily, reciprocity) change little; volume measures (density, degree) fall by about a tenth when errors are removed, because errors add ties. The calculation does not simulate recall: the transcribed sittings contain about two thirds of the printed amendments, and the missing ties lower density and degree in a way these replicates do not measure.

**Coverage.** The corpus contains 189 of the Assembly's 373 sittings: the 173 in which the index of proceedings records amendments or votes, and 16 sittings held on days when the draft Constitution was discussed that comparison with the Chamber's table of preparatory works (dates on which each article was discussed) had shown to be missing — each the other sitting of a day of which one sitting was already transcribed (morning and afternoon sittings are numbered separately). These 16 sittings were downloaded, OCR'd and extracted with the same rules in version 1.1.0 (see «Added sittings» below): no sitting discussing the draft is left out of the corpus. The list of the 184 untranscribed sittings, with the PDF address, is in `pipeline/sedute_non_trascritte.csv`; `pipeline/tools/scarica_pdf_mancanti.py --tutte` downloads them. The recall measured within transcribed sittings (67%) remains the estimate for single-signatory amendments. Lists closed by «ed altri» (`complete = 0`) number 34, 24 of them with at least two signatories: ties with the unnamed signatories are missing.

**Added sittings and open cases (28 October 2026).** The 16 added sittings bring 126 amendments (33 with several signatories) and 2 roll-call votes (v2, sed073; v18, sed187), and votes have been renumbered in sitting order: users of version 1.0.0 must re-match `id_vote` by sitting and page. As for the rest of the dataset, all new multi-signatory amendments were checked on full-column images, by readers comparing the attributed list with the printed one. Of 31 records not yet seen: 2 false positives (6.5%, CI 1.8–20.7) — a speaker citing two distinct amendments together («il criterio proposto dagli onorevoli Dozza e Cosattini», sed073) and a «proposta» that is an order of the day («L'Assemblea Costituente invita la Commissione di coordinamento…», sed279) — and 2 citations in a speech of a real amendment, kept as in the other cases; among the 29 true amendments, 4 lists missing one signatory (13.8%, CI 5.5–30.6). The errors belonged to general families, fixed in the extractor and added to the regression test (67 cases): the proposer in the future-tense formula «presenterò il seguente emendamento, firmato anche dagli onorevoli…» when the speaking turn is not preceded by a blank line (sed169, Vigorelli); «È stato presentato dall'onorevole X, che lo ha già svolto, il seguente emendamento, che reca anche le firme degli onorevoli…» (sed298, Crispo); «l'onorevole X ha facoltà di svolgere il seguente emendamento che reca anche le firme…», where X is a signatory (sed196, Rubilli); a stray exclamation mark at the end of a line that cut the list («Giua! / e Balduzzi», sed117); «ed astri» for «ed altri»; the verb with a stray accent («firmato anchè»). The same fixes recover a Bulloni-Mortati amendment of March 1947 (sed082), previously recorded as two singles. A list truncated by «ed altri» on the same page as the full list with the same first signatory is now recognised as the same act («Taviani, Ermini ed altri», sed124), while two distinct amendments by the same signatories on different pages stay separate if their texts differ (Giannini-Maffioli, sed117). Two lists cut by OCR were completed by hand after reading the image (sed189: Arcaini, proposer, with Scoca, Cappi ed altri; sed196: article 67-bis with 10 signatures, «Mastino Ge-/sumino» split). File: `pipeline/extraction/VERIFICA_sedute_aggiunte_verificato.csv`.

All cases in `pipeline/CASI_APERTI.xlsx` were decided on the page image by readers who did not see the proposed match, and the decisions, with a note on what is printed, are applied at every export (keys no longer depend on vote numbering, and decided rows stay in the sheet even when the case is no longer generated). Still uncertain, and marked as such in the note: «Mariani» (five mentions: Enrico or Francesco, both Socialists) and «Matteotti» (Giancarlo or Gianmatteo), left unattributed; Cortese Guido (inferred from the period in office, not from the printed name); Mazza Crescenzo for «Massa» (sed322, from party and co-signatures); Fuschini Giuseppe for a smudged name in the «no» list of sed187 («Fu-/schini», between Froggio and Gabrieli). In the votes, decisions add 11 votes and correct two approximate matches (Bernamonti Dante in sed270, not Bertone; Montagnana Mario in sed296, not Montalbano). The totals of the sed187 vote, misread by OCR (452/468), are taken from the last number after the label and from present minus abstaining: 152 yes, 168 no, confirmed on the image.

**External validation.** No printed index listing amendments by name exists in usable form; the Chamber's table of preparatory works gives articles and dates, not proposers. Two external judges are used all the same: the correlation with the activity pages of the Chamber's index (above) and the table, which confirms the subject and the discussion date of the amended article.

**Group at date.** `group_first` and `group_last` are not enough when a member switches group while signing or voting, as in the Socialist split of January 1947. The memberships published by the Chamber (`pipeline/fonti/camera_adesioni_gruppi.csv`, downloaded with `pipeline/tools/scarica_fonti_esterne.py`) give each member's groups with dates; for 580 of 581 members the first and last groups match `group_first` and `group_last`, and the number of groups matches `n_groups`. The `group_at_date` column of `edgelist_amendments.csv` and `edgelist_votes.csv` gives the group valid on the day of the sitting: compared with the final group it differs for 78 of 3,547 signatures and 181 of 9,797 votes. Before the first membership (groups were formed in the weeks after the first sitting) the first group applies.

**Open cases and manual decisions.** Cases the extraction cannot settle — surnames shared by several members with no first name or co-signatories to help (Gullo, Mastino, Mariani, Merlin, Cortese), illegible names, lists closed by «ed altri», unmatched names in votes, approximate matches — are collected by `pipeline/tools/prepara_casi_aperti.py` into `pipeline/CASI_APERTI.xlsx`, with a link to the page and the possible choices. Decisions written in the sheet, taken by looking at the page, are applied by `esporta_dataset.py` at every export and stay in the repository, so every manual choice is documented and reversible.

**OCR quality by page.** `pipeline/tools/qualita_ocr.py` gives each page the share of words (4+ letters) occurring at least 20 times in the corpus — a word garbled by OCR is almost always rare — and the share of stray characters; the result is in `pipeline/extraction/qualita_pagine.csv` (3,275 pages; median 0.89, 5th percentile 0.79). The score does not predict extraction errors: across the 492 records checked on the image, wrong ones fall on pages of almost identical quality to correct ones (0.905 vs 0.908; permutation test p = 0.22). Errors depend on formulas and context, not on how legible the page is; the file is there for anyone wanting to drop the worst pages in a robustness check.

**Agreement between two independent readings.** Image checks say how accurate the data are only if the reader's judgement is itself reproducible. 50 records from the systematic check (blocks 3 and 4, drawn at random, seed 2036) were re-read by a second reader, on the same images and with the same instructions, without access to the first reader's verdicts. Excluding cases where either could not decide (2 for «is it an amendment?», 4 for the signatories), agreement is complete: 48/48 on whether the amendment exists (Cohen's kappa 1.00; agreement 100%, CI 92.6–100) and 46/46 on whether the signatories are correct (kappa 1.00; CI 92.3–100), including the 3 false positives and 4 wrong lists that both recognised. Since both readers follow the same written instructions, the result measures the reproducibility of the judgement, not the absence of errors both might make in the same way. File: `pipeline/extraction/VERIFICA_kappa_coppie.csv`.

**Accuracy of votes.** Of 25 votes with official totals, 23 differ by at most three names per side between matched names and totals (`check = ok`). For votes v17 and v23 the extraction matches the printed page, but the printed list itself differs from the announced totals (`verified: …`). Four votes (v5, v11, v14, v25) are void: the President announces that the quorum was not reached and gives no totals (`quorum_failed = 1`, `check = void: …`). The votes cast are printed and kept in the dataset, since they still record the position of those who answered the roll call, but the Assembly did not decide. All four announcements were checked on the page image. Official totals misread by OCR («1» read as «4») are corrected with the arithmetic of the result box: if yes + no does not equal the number of voters, a «4» is replaced with «1», and the correction is accepted only if it is the only one that makes the sum hold (v26: «434» and «471» read for 134 and 171, checked on the image; v29). The total of v8 is corrected by hand from the image, because the number of voters is also misread and the sum cannot act as judge. Totals are printed in two formulas, «Hanno risposto sì / no» and «Voti favorevoli / contrari»; the extraction reads both.

**Reading the lists name by name (28 October 2026).** For every vote whose matched names did not equal the totals exactly, and for the four void votes (no totals), the printed lists were transcribed from the image and compared by script with the extracted ones: 30 lists in 18 votes. 25 names were missing, plus three abstentions counted as no, almost all from one general family: a surname split at the end of a line with a stray mark after the hyphen («Gar-- bonari», «Se- - reni», «Ce. - volotto», «Fede-- ‘rici», «Mari-» followed by the page-header junk line and «naro» on the next page), which left a lower-case fragment that was then discarded. Other families: an initial read in lower case («lussu»), OCR junk before the name («rrF coprreoeoe LI Caccuri»), «De. Maria», a surname taken as the first name of the previous member («Longhena Mariani Enrico»: Longhena's first name is Mario), the heading «Si sono astenulì» not recognised (three abstentions counted as no in sed129), and two defects in duplicates: a name marked as a repetition stayed deleted even when its first occurrence was later corrected to another person (Pella, Montini, Bertone), and a name printed in two lists of the same vote was counted in the first instead of being left missing as the rule says (Zappelli in v17; Cosattini in v27, printed among both yes and no and counted in both totals). One name missing from the OCR text (Vicentini, sed177) is added by hand, and an erratum in the record is applied (sed312 p20: «il deputato Conti deve figurare come astenuto» in the sed296 vote). Abstention totals, never read before, come from the «Astenuti» line of the results box, with present − (yes + no) correcting dirty digits. After the fixes, 18 of the 25 votes with totals match exactly on both sides; all remaining differences are in the record itself: the printed list, read name by name, already has that number of names (v8, v15, v19, v29 by one name; v17 and v23 by several; v27 because of Cosattini). Vote edges: 9,778 → 9,797.

**Outcomes of roll-call votes.** The caption «(L'Assemblea approva / non approva)» after a roll-call result was not linked to the amendment voted on. The outcome now goes to the amendment named in the announcement («Indico la votazione per appello nominale sull'emendamento presentato dall'onorevole Cairo») or, if the announcement names none, to the last one named before it, excluding the roll-call request; if the announcement lists signatories the amendment does not have, the link is refused. Nine more outcomes, from eight votes (Cosattini, two records, Corbino-Marchesi, Cairo, Scoccimarro-Veroni, Laconi, Bozzi, La Rocca, Lami Starnuti), all consistent with the totals. The same check found a 15-signature amendment lost because OCR had put a quotation mark between «dagli» and «onorevoli» («senza oneri per lo Stato», sed105, Corbino, Marchesi, Preti and others), now recovered; an amendment with the same list and the same text read again four sittings later (sed126 and sed130) is now one act, as is a citation by a signatory repeating the same text (Calosso in the Cairo amendment, sed129).

Roll-call lists are printed in alphabetical order, which is an external constraint worth exploiting: a surname garbled by OCR («CARIEPA», «LACOTII», «VANOM») can only be searched among the surnames falling between the previous and the next name already matched. Where that band holds at most eight names and similarity clears the threshold, the name is recovered (`matching = alphabetical band`): 20 cases. The same constraint checks approximate matches: if the surname chosen by similarity breaks the order of the list, the match is cancelled and the name goes through the band instead. Six matches were corrected this way, all confirmed on the page text: «Vanni» between Farina and Farini is the tail of «Farina Gio-vanni», not Vanoni; «Gio-htti» is Giolitti, not Iotti; «Prell» between Pressinotti and Preziosi is Preti, not Pella; «Mana» between two Rossis is «Rossi Maria Maddalena», not Marina; «Massiani» between Caso and Castelli is Cassiani, not Massini; «Berné&monti» is Bernamonti, not Montini. Within the band the tail of a surname split by hyphenation is also recognised (a single surname in the band ending that way), as is a double surname split in two pieces («Garpano — Maglioli», Carpano Maglioli). A surname printed alone and shared by several members («Rossi», «Orlando», «Leone») is resolved in two ways: by the first name that OCR split onto the next line («Morelli — Nato», Morelli Renato), or by exclusion, since a member votes only once and namesakes already matched in the same vote cannot be the one («Rossi» between Rossi Giuseppe and Rossi Paolo is Rossi Maria Maddalena): `matching = namesake resolved`, 7 of 8 cases; one «Barontini» (Anelito or Ilio) stays ambiguous. «De Unterrichter Maria» (Maria Jervolino) is recognised even when OCR detaches the «De» with a full stop or garbles the surname («Unterrichier»). Stranded first names («Maria», «Luigi») and procedural words caught from the list («Dichiaro», «Votazione», «Segretari») are excluded. Rows repeating a member already present in the same vote — printing or OCR duplicates, such as «Cingolani Mario» followed by «Cingolani» — are flagged `duplicate` and generate no second edge: 11 cases. Both operations are judged externally, since it is the totals announced by the President that say whether a recovery is right: the mean gap between matched names and official totals falls from 3.05 to 2.64 names per vote (2.52 after the alphabetical-order check and 2.26 after resolving namesakes, over the 23 votes with totals), with 8 votes moving closer to their total and none moving away (the one widening gap is v17, where removing a duplicate exposes a printed list that is genuinely incomplete).

**Construct validity: group cohesion.** If name matching in the votes were noisy, notoriously disciplined groups would appear loose. The Rice index by group and vote (|yes − no| / (yes + no), abstentions excluded, groups with at least 5 votes cast; `tools/coesione_voto.py`, details in `pipeline/extraction/coesione_voto.csv`) averages over the 29 votes 0.996 for the Communist group (0.1 dissenting votes per vote), 0.985 for the Christian Democrats, 0.94 for the Socialists, 0.85 for the Socialist Workers, 0.88 for the Republicans, and 0.46 for the Mixed group, which by nature does not vote together. The group is the final one: the Socialist split of January 1947 precedes almost all the votes.

Consistency checks on the whole dataset: no votes or signatures outside a member's term of office; if a member appears in two lists of the same vote the exact match is kept, and if both are exact the vote is left missing.

### Amendment variables (`amendments_nodes.csv`)

| Variable | Description |
|---|---|
| `n_signatories` | Number of signatories (see `edgelist_amendments.csv`) |
| `complete` | 1 if the list of signatories is complete, 0 if it ends with «ed altri» |
| `article_mentioned` | Last article number cited in the lines around the mention («all'articolo 31»), as printed. It is often an article cited in passing (in the amendment's text or in the speech): on the development sample it matches the amended article in 7 of 13 cases. Prefer `article_under_discussion` |
| `article_under_discussion` | Article of the text under examination (numbering of the draft Constitution, or of the bill debated in that sitting) the amendment refers to, taken from the order of business printed by the President («Passiamo all'articolo 31», «Si dia lettura dell'articolo 86»): the last one announced before the mention; if several are announced on the page, the one matching `article_mentioned`. Assigned to 1,022 of 1,532 amendments. On a validation sample read blind on the image (seed 2045) it is right in 14 of 20 cases: 70% (48.1–85.5); errors are off by one article (the amendment read before the next one is announced) or additional articles («8-bis» recorded as 8). `pipeline/extraction/controllo_articolo.csv` also gives, for each amendment, the articles announced on the page and the outcome of the comparison with `article_mentioned` |
| `subject_title` | Part and title of the draft Constitution the amended article belongs to («Part I - Title III» = economic relations; «Part II - Title V» = Regions, Provinces, Municipalities…), from the Chamber's table (`pipeline/fonti/tavola_progetto_costituzione.tsv`: draft article → article of the Constitution, with the dates of plenary discussion). Assigned to 1,022 amendments; empty for sittings on other bills or where the article cannot be determined. On 18 amendments of the validation sample read on the image it is right in 17 |
| `constitution_article` | Article (or articles, separated by «;») of the approved Constitution corresponding to the amended draft article, from the same table. The amended article's number is reliable in 67–70% of cases (see above); the subject much more, since errors are almost always a neighbouring article of the same title |
| `date_check` | Comparison with the table's dates: `date consistent` (the sitting falls on a day when that article was discussed: 868), `only article discussed that day` (the article is inferred from the date: 154), `day without draft articles` (the sitting discusses another bill: 110), `date inconsistent` (127: to be looked at), `undetermined` |
| `sitting`, `date`, `pdf_page`, `url_pdf` | First mention and link to the page of the record |
| `source` | `signature block` or `presentation formula` |
| `id_proposer` | Who tabled the amendment: the name given by a formula («L'onorevole X ha presentato… firmato anche dagli onorevoli», «insieme con», «da me e dagli onorevoli», the name heading the speaking turn) or, failing that, the first printed signatory, who by the record's convention is the proposer. Empty if the first printed name is not matched (unresolved homonym, illegible name): the second signatory is not promoted in its place |
| `proposer_source` | `formula`, `first in list`, `single signatory` or `not identified` |
| `amendment_type` | `replace`, `delete`, `add`, `insert` or `undetermined`: the first operation in the opening formula of the text («Sostituirlo col seguente», «Al secondo comma sopprimere…»); if the text does not print it, from the adjective in the presentation («emendamento soppressivo», «articolo aggiuntivo»). Agreement with a blind reading of the image: 29/40 = 72.5% (57.2–83.9). The most frequent error is a full text printed without a verb («la seguente dizione: «…»»), which the extractor leaves `undetermined` and a reader classifies as a replacement: a first-pass coding, to be used with care |
| `outcome` | `approved`, `rejected`, `withdrawn`, `lapsed (proposer absent)`, `absorbed` or `undetermined`. From the amendment's page onwards in the same sitting (and in the next two only if a piece of its text recurs nearby), the extractor looks for the vote naming the first signatory followed by the caption «(È approvato)» / «(Non è approvato)», the withdrawal stated by the signatory in reply to the President («Onorevole X, lo mantiene?» — «Lo ritiro»), lapse for absence, and absorption. The rules are deliberately strict: an outcome is assigned to 262 of 1,532 amendments (17.1%); the rest stay `undetermined` (voted within an agreed text, decided by show of hands without naming them, or with ambiguous wording). On a validation sample of 30 assigned outcomes read blind on the image (seed 2042), 26 are right: 86.7% (70.3–94.7); two errors are amendments voted in effect within the Committee's text. Two earlier samples (40 + 30) were used to write the rules. File: `pipeline/extraction/VERIFICA_esiti_convalida_verificato.csv` |
| `text_it` | Text of the amendment as printed in quotation marks after the presentation formula (or before the signature block), in Italian, with OCR misreadings; `/` separates paragraphs; empty if the page does not print it (146 cases, mostly citations in speeches). On sample 5: 22 texts correct, 6 partial (only a piece, or including the following sentence), 2 wrong, 5 absent, 5 not verifiable from the crop |

### Variables of mentions in speeches (`speech_mentions.csv`)

| Variable | Description |
|---|---|
| `sitting`, `date`, `pdf_page`, `url_pdf` | Where the mention is |
| `id_speaker`, `speaker_printed`, `speaker_role` | Who speaks: id, turn heading as printed, any role («Presidente della Commissione», «Relatore», «Ministro…») |
| `id_mentioned`, `printed_form` | Who is named and how the record prints it. Empty if the surname belongs to several members and neither speaks in that sitting (258 cases) or if the name is not a member (134: earlier deputies, non-member ministers, misprints) |
| `matching` | How the name was matched (`exact`, `approximate`, `prefix`, `+sitting` for homonyms resolved by who speaks in the sitting, `ambiguous`, `not found`) |
| `mention_type` | `on an amendment`, `speech act`, `stage direction`, `other` |
| `context_it` | The surrounding text, with the mention between `[[ ]]` |

**Accuracy.** Two samples of 40 randomly drawn mentions, read from the image with the full columns of the page and the preceding column. The first exposed turn headings printed inline, which caused the President's words to be attributed to the previous speaker, and stage directions in parentheses: both were fixed. On the second, after the fixes: true mentions 40/40; mentioned person correct 40/40 (100%, CI 91.2–100); speaker correct in 31 of the 31 cases where the start of the turn is visible (100%, CI 89.0–100), never wrong; mention type correct 33/40 (82.5%, CI 68.0–91.3), because `on an amendment` depends on the word «emendamento» or «proposta» nearby and misses sentences that discuss an amendment's content without naming it. File: `pipeline/extraction/VERIFICA_menzioni_discorso_verificato.csv`.

### Vote variables (`votes_nodes.csv`)

| Variable | Description |
|---|---|
| `sitting`, `date`, `pdf_page`, `url_pdf` | Sitting and link to the page of the roll call |
| `label_en`, `on_constitution` | Subject of the vote and whether it concerns the Constitution |
| `yes_official`, `no_official` | Totals announced by the President |
| `yes_matched`, `no_matched`, `abstain_matched`, `leave_matched` | Names matched to members |
| `quorum_failed` | 1 if the President announces that the quorum was not reached (void vote, totals not announced) |
| `check` | Result of the comparison between matched names and official totals |
| `excerpt_it` | Text preceding the vote (Italian), to identify its subject |

## Member variables (`members_nodes.csv`)

### Personal data, election, group

| Variable | Description |
|---|---|
| `id_member`, `surname`, `first_name` | |
| `woman` | 1 = woman (21) |
| `birth_date`, `birth_year`, `age_1946` | Age in completed years on 25 June 1946 |
| `birth_town`, `birth_province`, `birth_region` | Present-day regions |
| `birth_macroarea` | North-West, North-East, Centre, South, Islands, Abroad |
| `birth_region_status` | Region with `special` or `ordinary` statute (present-day classification) |
| `born_abroad` | Born outside present-day Italy (including Fiume/Rijeka) |
| `party_list` | Electoral list |
| `group_first`, `group_last`, `n_groups`, `group_switch` | Parliamentary groups |
| `constituency`, `national_list` | Constituency (named after its main city) or national list |
| `election_region`, `election_macroarea`, `same_region` | Udine-Belluno assigned to Friuli-Venezia Giulia |
| `term_start`, `term_end`, `term_end_reason` | |
| `replacement` | Term began after the first sitting (25 June 1946). It is 1 for 104 members, but these are not 104 replacements: it covers genuine replacements, late proclamations where electoral operations were still open (24 as early as July 1946), and the seats filled after multi-constituency candidates exercised their option |

### Education and occupation

| Variable | Description |
|---|---|
| `education`, `degree`, `degree_field` | From the Chamber record |
| `occupation_text`, `chamber_description` | Original text (Italian) |
| `occupation` | Keyword-based coding of the first occupation listed |

### Earlier career

| Variable | Description |
|---|---|
| `kingdom_deputy`, `n_terms_kingdom` | Member of the Chamber of the Kingdom before 1946 |
| `national_council` | Member of the Consulta nazionale (1945–46) |
| `gov_before`, `gov_during` | Government post begun before or during the Assembly |
| `aventine` | Aventine secession deputy (1924) |

### Antifascism and Resistance (Wikidata and Wikipedia)

| Variable | Description |
|---|---|
| `resistance_structured` | Wikipedia category (Italian partisans, Brigades…, Resistance…) or Wikidata occupation "partisan" |
| `resistance_text` | A sentence describes a personal role in the Resistance (took part, commanded, organised, nom de guerre…) |
| `resistance` | 1 if either |
| `cln`, `resistance_or_cln` | Role in a National Liberation Committee (CLN) |
| `antifascist` | Category "Italian antifascists" or mention |
| `confino`, `special_tribunal`, `prison`, `exile` | Personal experience described in the entry (internal exile, Special Tribunal for the Defence of the State, imprisonment, exile) |
| `fascist_persecution` | At least one of confino, special tribunal, prison, exile |
| `spanish_civil_war` | Took part in the Spanish Civil War |
| `wikidata_qid`, `itwiki_title`, `itwiki_entry` | Links to Wikidata and Wikipedia |

Automatic coding: sections such as Works, Notes, and Bibliography are excluded, but errors remain possible. `evidence_wikipedia.csv` gives up to two sentences per indicator. Six members have no Wikipedia entry.

### Later career (after 31 January 1948)

| Variable | Description |
|---|---|
| `career_parliament` | Deputy or senator of the Republic |
| `career_top` | President of the Republic, Prime Minister, Speaker of the Chamber, or President of the Senate |
| `career_court` | Judge of the Constitutional Court |
| `career_level` | Highest level: `top office` > `constitutional court` > `parliament` > `none` |
| `later_head_of_state`, `later_prime_minister`, `later_chamber_speaker`, `later_senate_president`, `later_constitutional_judge` | Single offices |
| `later_minister`, `later_undersecretary`, `n_gov_posts_after`, `gov_after`, `ever_minister` | Government (Chamber data) |
| `republic_deputy`, `n_terms_chamber_rep`, `later_senator`, `n_terms_senate`, `life_senator`, `mp_after_1948` | Parliament (Chamber, Senate, Wikidata) |
| `later_mep`, `later_mayor` | Wikidata |

### Position in the network of bodies

| Variable | Description |
|---|---|
| `n_bodies`, `n_bodies_constitutional` | Two-mode degree; constitutional bodies only (Committee of 75, subcommittees, Drafting Committee) |
| `degree_proj`, `strength_proj`, `betweenness`, `closeness`, `eigenvector` | On the one-mode projection (weighted eigenvector, 0 for isolates) |
| `bip_betweenness` | Betweenness on the bipartite network |
| `const_degree_proj`, `const_eigenvector`, `const_betweenness` | Constitutional bodies only |
| `n_chairs`, `n_offices` | Chairs held; offices held (chair, vice-chair, secretary, quaestor) |

### Constitution Committee and roll-call attendance

| Variable | Description |
|---|---|
| `committee_75` | 1 if ever a member of the Committee for the Constitution (97 people, because of replacements) |
| `subcommittee` | `I`, `II`, `III` (several separated by «;») |
| `drafting_committee` | Drafting Committee, known as «of the 18» (20 people over time) |
| `committee_role` | Highest office in the Committee or its bodies: `chair`, `vice-chair`, `secretary`, `member` |
| `votes_in_office` | Roll-call votes held while in office (of 27) |
| `votes_present`, `votes_on_leave`, `votes_absent` | Answered yes, no or abstained; on leave; in no list. Votes void for lack of quorum count, since the roll call took place |
| `share_present` | `votes_present / votes_in_office`. A printed but unmatched name makes a voter look absent: the error is the one measured on official totals (2.3 names out of about 350 per vote on average). Terracini, President of the Assembly from February 1947, never appears in the lists |
| `viaf_id` | VIAF (Virtual International Authority File) identifier from Wikidata (property P214), linking the dataset to library catalogues; several identifiers separated by «;». Available for 330 members |
| `elected_chamber_1948` | 1 if elected to the Chamber on 18 April 1948 (Legislature I; later replacements excluded): 260. Source: list of those elected by constituency on Wikipedia, `pipeline/fonti/eletti_camera_1948_wikipedia.txt`; all 260 are deputies of the Republic in the Chamber's data (`republic_deputy`). The 1948 Senate is not covered: `later_senator` says whether a person was ever a senator, not when |

Source: `edgelist_bodies.csv` (bodies o621–o625) and `edgelist_votes.csv`; computed by `pipeline/tools/arricchisci_costituenti.py`.

### Activity and interaction

| Variable | Description |
|---|---|
| `act_pages_total`, `act_pages_assembly`, `act_pages_committees` | Record pages with the member's contributions |
| `act_pages_constitution` | Pages on the draft Constitution |
| `act_topics`, `act_sittings` | Topics and sittings with contributions |
| `act_questions`, `act_reports` | Parliamentary questions tabled; reports and proposals |
| `exch_degree`, `exch_strength` | Degree and strength in the exchange network |

## Limitations

- **Amendments and votes.** They are reconstructed by OCR and contain residual errors: see «Amendments and votes: construction and accuracy». Amendments cover the plenary sittings, not committee work.
- **Parliamentary questions.** The sources record only the first signatory, so there is no co-sponsorship network.
- **Chairs.** Those chairing the floor or a body (for example Terracini, Ruini, Tupini) appear on many pages for procedural reasons: use `n_pages_no_chair` or control for `n_chairs`.
- **Government members.** Ministers in office (De Gasperi, Scelba, Segni…) did not sit on committees, so their centrality in the network of bodies is low by construction. Control for `gov_during`.
- **Manual additions.** The presidencies of the Chamber and Senate are added by hand where Wikidata is incomplete; constitutional judges are checked against the Wikipedia list.
