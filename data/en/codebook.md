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
| `amendments_nodes.csv` | 1,397 amendments tabled in the Assembly, extracted from the records by OCR |
| `edgelist_amendments.csv` | Two-mode network member × amendment (who signed, with the role of proposer or signatory; 3,180 edges) |
| `votes_nodes.csv` | 27 roll-call votes, with official totals and check |
| `edgelist_votes.csv` | Two-mode network member × vote, with the vote cast (yes, no, abstain) |
| `evidence_wikipedia.csv` | Wikipedia categories and sentences behind the antifascism and Resistance indicators |

Identifiers: `d` + Chamber id for members, `o` + id for bodies, `t` + number for topics.

## The networks

**Bodies (formal).** Membership of committees, subcommittees, and boards. Seats were allocated to parliamentary groups in proportion to their size, so this network records assigned positions, not individual choices.

**Topics (two-mode).** A topic is a matter under debate: on the floor, the title of the debate (for example an article of the draft Constitution); in committee, the item discussed (for example "La famiglia"). The weight is the number of record pages with the member's contributions on that topic.

**Exchanges (one-mode, undirected).** Two members are tied if they both speak on the same page of the same record. This is a close proxy for direct confrontation: replies, interruptions, rejoinders. `n_pages` counts shared pages; `n_pages_no_chair` drops pages where either member chairs that body, since chairs appear for procedural reasons. A tie does not distinguish agreement from disagreement.

**Co-rapporteurs.** Subcommittee reports and reports on bills signed by more than one member. A small network, but of explicit collaboration.

**Substitutions (directed).** `incoming` → `replaced`, with body and date.

**Amendments (two-mode).** Who signed an amendment together: a chosen tie, unlike committee membership. Projected onto members, it measures collaboration in drafting the text.

**Amendments (two-mode, directed).** `edgelist_amendments.csv` has a `role` column: `proposer` for whoever tabled the amendment, `signatory` for those who co-signed it. Projecting only the signatory → proposer edges gives a directed network: who gathers signatures and who gives them. The proposer was compared with the list transcribed from the image for the 131 multi-signatory amendments of the systematic check: it matches in 130 of 131 cases (99.2%, CI 95.8–99.9); the only error («presentato dall'onorevole Gasparotto e da me», where the speaker was placed first) was fixed in the extractor. Of 1,397 amendments, 187 have the proposer given by a formula, 199 by the first name in the list, 1,010 are single-signatory and 1 is not identifiable.

**Roll-call votes (two-mode, signed).** How each member voted in the 27 roll calls. Absences and leave are not edges.

## Amendments and votes: construction and accuracy

Signatures on amendments and roll-call votes are not available in structured form: they appear only in the verbatim records of the Assembly, published as images. They were reconstructed as follows (code in `pipeline/`):

1. **OCR.** The records of the 173 sittings with amendments or roll calls (4,786 pages) were converted to text with Tesseract (Italian model), splitting the two columns of each page (`ocr_costituente.R`). The 3,275 pages that mention amendments were read again at 400 dpi (`ocr_400dpi.R`); for each page the reading that recognises more members' surnames is used.
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

**Regression test and second round of fixes.** `tools/test_regole.py` runs the extractor on 46 real passages from the records, each with its expected outcome (the signatory lists it must produce, or none), and checks in about a second that a change to one rule does not break another; the cases are in `tools/test_regole_casi.json`, and those marked «controllato sull'immagine» were compared with the scan. Building the test exposed general defects, which were fixed in the extractor and checked record by record against the page image: (1) hyphenation with a stray mark between the dash and the line break («MARAZ-'» / «- ZA», «Cle-.» / «rici») split the signature block or list, and the amendment was lost entirely: missing as a result were, among others, an additional article with 16 signatures (sed126) and two Christian Democrat amendments with 28 and 16 signatures (sed119, sed122); (2) consolidation absorbed a single-signatory amendment into any longer list containing that name, even when it was a separate act («Segue l'emendamento dell'onorevole Bubbio», thirteenth signatory of another one): a single name is now absorbed only if it is the first signatory, because the record refers to an amendment by its first signer's name; (3) the plural governing a list («gli emendamenti degli onorevoli…») reached across a sentence ending right before the mention («…pervenute. Gli onorevoli») and across a nearer singular («…valgono anche per l'emendamento degli onorevoli…»); (4) the proposer was missed in the forms «l'onorevole X ha ora presentato…», «l'onorevole X, la quale, insieme con gli onorevoli…» and «presentato dagli onorevoli X, Y e da me»; (5) a request for a roll-call vote in the *following* sentence deleted the amendment tabled in the sentence before. Also added: «presentati rispettivamente dagli onorevoli» (separate acts), «interruzione» and «cortesia» (speech acts), surnames run together without a comma («Targetti Amadei e Bordon») and the conjunction with a stray full stop («Rodnò Mario e. Puoti»). Finally, two manual corrections recorded in `esporta_dataset.py` were not being applied because their key included the first name («Rossi Paolo»): they now apply, and a missing signatory (Bianchi Bianca, sed261) is restored. Amendments rise from 718 to 787, those with 2+ signatories from 329 to 337, co-signature edges from 2,269 to 2,425.

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

Almost all errors belonged to general families, fixed in the extractor: lists of separate acts («hanno proposto ciascuno un identico emendamento», «hanno presentato due emendamenti», «gli emendamenti, più sostanziali, degli onorevoli X e Y» with a stray OCR mark in between), lists of speakers («dall'onorevole X, dall'onorevole Y e da altri a favore dell'emendamento…»), signature blocks of interrogations («per sapere», «se non ravvisi») and vote requests garbled by OCR («chiesto la .votazione: a serutinio segreto»), the proposer in «ha facoltà di parlare l'onorevole X, per svolgere il seguente emendamento, firmato anche dagli onorevoli…», and two OCR errors inside a list («Tremelloni e-Carboni», «De' : Palma»). Blocks 5 and 6 revealed three more families: the signatures of interrogations announced at the end of a sitting (each opens with «Il sottoscritto chiede d'interrogare»), the roll-call request that «porta le firme anche degli onorevoli…», and the proposer being taken from the first «L'onorevole X ha presentato» in the window rather than the last, which attributed a list to the proposer of the previous amendment. Two lists continuing into the next column or page were corrected by hand. With this check, every one of the 386 amendments with several signatories in the dataset has been checked against the image at least once. Two uncertain cases remain: «Mariani» (Enrico or Francesco, both Socialists), left out, and «Massa» matched approximately to Massola in a Liberal and Qualunquist list. File: `pipeline/extraction/VERIFICA_2plus_blocchi*_verificato.csv`.

**Accuracy of votes.** Of 22 votes with official totals, 20 differ by at most three names per side between matched names and totals (`check = ok`); for five votes the record gives no totals (`no official totals`). For votes v16 and v21 the extraction matches the printed page, but the printed list itself differs from the announced totals (`verified: …`). Two official totals misread by OCR were corrected from the page image (v7 and v27).

Roll-call lists are printed in alphabetical order, which is an external constraint worth exploiting: a surname garbled by OCR («CARIEPA», «LACOTII», «VANOM») can only be searched among the surnames falling between the previous and the next name already matched. Where that band holds at most eight names and similarity clears the threshold, the name is recovered (`matching = alphabetical band`): 16 cases. Stranded first names («Maria», «Luigi») and procedural words caught from the list («Dichiaro», «Votazione», «Segretari») are excluded. Rows repeating a member already present in the same vote — printing or OCR duplicates, such as «Cingolani Mario» followed by «Cingolani» — are flagged `duplicate` and generate no second edge: 11 cases. Both operations are judged externally, since it is the totals announced by the President that say whether a recovery is right: the mean gap between matched names and official totals falls from 3.05 to 2.64 names per vote, with 8 votes moving closer to their total and none moving away (the one widening gap is v16, where removing a duplicate exposes a printed list that is genuinely incomplete).

Consistency checks on the whole dataset: no votes or signatures outside a member's term of office; if a member appears in two lists of the same vote the exact match is kept, and if both are exact the vote is left missing.

### Amendment variables (`amendments_nodes.csv`)

| Variable | Description |
|---|---|
| `n_signatories` | Number of signatories (see `edgelist_amendments.csv`) |
| `complete` | 1 if the list of signatories is complete, 0 if it ends with «ed altri» |
| `article_mentioned` | 1 if the text cites an article of the draft Constitution |
| `sitting`, `date`, `pdf_page`, `url_pdf` | First mention and link to the page of the record |
| `source` | `signature block` or `presentation formula` |
| `id_proposer` | Who tabled the amendment: the name given by a formula («L'onorevole X ha presentato… firmato anche dagli onorevoli», «insieme con», «da me e dagli onorevoli», the name heading the speaking turn) or, failing that, the first printed signatory, who by the record's convention is the proposer. Empty if the first printed name is not matched (unresolved homonym, illegible name): the second signatory is not promoted in its place |
| `proposer_source` | `formula`, `first in list`, `single signatory` or `not identified` |
| `amendment_type` | `replace`, `delete`, `add`, `insert` or `undetermined`: the first operation in the opening formula of the text («Sostituirlo col seguente», «Al secondo comma sopprimere…»); if the text does not print it, from the adjective in the presentation («emendamento soppressivo», «articolo aggiuntivo»). Agreement with a blind reading of the image: 29/40 = 72.5% (57.2–83.9). The most frequent error is a full text printed without a verb («la seguente dizione: «…»»), which the extractor leaves `undetermined` and a reader classifies as a replacement: a first-pass coding, to be used with care |
| `text_it` | Text of the amendment as printed in quotation marks after the presentation formula (or before the signature block), in Italian, with OCR misreadings; `/` separates paragraphs; empty if the page does not print it (139 cases, mostly citations in speeches). On sample 5: 22 texts correct, 6 partial (only a piece, or including the following sentence), 2 wrong, 5 absent, 5 not verifiable from the crop |

### Vote variables (`votes_nodes.csv`)

| Variable | Description |
|---|---|
| `sitting`, `date`, `pdf_page`, `url_pdf` | Sitting and link to the page of the roll call |
| `label_en`, `on_constitution` | Subject of the vote and whether it concerns the Constitution |
| `yes_official`, `no_official` | Totals announced by the President |
| `yes_matched`, `no_matched`, `abstain_matched`, `leave_matched` | Names matched to members |
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
