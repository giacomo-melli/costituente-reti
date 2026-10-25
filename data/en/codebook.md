# Networks of the Italian Constituent Assembly (1946–1948) — codebook

A dataset on the 581 members of the Italian Constituent Assembly. It contains one formal network (membership of committees and other bodies) and three interaction networks built from day-to-day activity on the floor and in committees.

**Why 581 and not 556.** The Assembly had 556 seats: that is how many deputies sat at any one time, and it is the figure usually quoted. The 581 rows of `members_nodes.csv` are instead the *people* who held one of those seats for at least a day between 1946 and 1948. The difference is turnover: deaths, resignations, forfeitures and the options exercised by candidates elected in several constituencies, all replaced as the work went on. The fields `term_start` and `term_end` make it possible to reconstruct who was in office on a given date: on 22 December 1947, the day the Constitution was approved, there were exactly 556. Anyone who would rather treat the Assembly as a body of 556 can filter on that date.

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
| `amendments_nodes.csv` | 738 amendments tabled in the Assembly, extracted from the records by OCR |
| `edgelist_amendments.csv` | Two-mode network member × amendment (who signed; 2,198 edges) |
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

**Roll-call votes (two-mode, signed).** How each member voted in the 27 roll calls. Absences and leave are not edges.

## Amendments and votes: construction and accuracy

Signatures on amendments and roll-call votes are not available in structured form: they appear only in the verbatim records of the Assembly, published as images. They were reconstructed as follows (code in `pipeline/`):

1. **OCR.** The records of the 173 sittings with amendments or roll calls (4,786 pages) were converted to text with Tesseract (Italian model), splitting the two columns of each page (`ocr_costituente.R`). The 3,275 pages that mention amendments were read again at 400 dpi (`ocr_400dpi.R`); for each page the reading that recognises more members' surnames is used.
2. **Amendments.** They are identified by presentation formulas («l'onorevole X ha presentato il seguente emendamento») and by signature blocks; the classifier excludes questions, interpellations, motions, orders of the day and requests for a roll call. Names are matched to the members in office on the date of the sitting (`estrai_emendamenti.py`).
3. **Votes.** For each roll call the lists «Rispondono sì», «Rispondono no», «Si sono astenuti» and «Sono in congedo» are extracted and compared with the totals announced by the President (`estrai_voti.py`).
4. **Check.** 73 randomly drawn mentions were checked against the PDF: 40 (seed 1947) by hand, 34 by Claude (an AI model) from the page image, oversampling amendments with several signatories (seed 1948). The systematic errors found were fixed in the code: lists of distinct amendments («gli emendamenti degli onorevoli X, Y e Z») mistaken for joint signatures, the proposer omitted in «firmato anche dagli onorevoli» formulas, questions to ministers, and OCR noise between names. Votes with discrepancies of more than three names were checked against the page image.
5. **Completeness.** 10 randomly drawn pages (seed 2026) were read in full by Claude to find amendments with several signatories that the extraction missed. There were 6, of which 2 were extracted correctly. The causes (the formula «Gli onorevoli X e Y hanno presentato…», «a firma degli», «insieme con gli onorevoli», signature blocks broken by OCR, hyphenation, OCR noise in names) were fixed across the whole corpus; after the fix 5 of the 6 are complete and the sixth has 7 of 9 signatories. An automatic search for sentences with two or more surnames that were not extracted (`cerca_mancati.py`) guided further fixes. The number of amendments with several signatories rose from 217 to 327. A second check on a further 20 pages (seed 2027, excluding the earlier ones), carried out in the same way, found 5 amendments with several signatories: all 5 had been extracted with the full list of signatories. The other 17 pages contained none; the multiple signatures they do carry belong to parliamentary questions and interpellations, which are outside the dataset by construction. Details in `pipeline/extraction/richiamo2/ESITO.md`.

**Accuracy of amendments.** Three samples were verified, each record read against the page image: 139 records in all. The first two (99 records) guided the fixes to the extractor, so their rates are optimistic by construction. The third (40 records) was drawn at random **after** those fixes, among records never looked at before, and gives the estimate to use (95% Wilson intervals; `valuta_campioni.py`):

- false positives: 3 of 40, 7.5% (2.6–19.9%);
- genuine amendments with missing or wrong signatories: 1 of 37, 2.7% (0.5–13.8%).

On the two tuning samples the same rates are 4 of 99 (4.0%) and 1 of 78 (1.3%): the gap between the two estimates measures how far tuning made the first one optimistic, which is why the second is the published figure.

False positives take three recurring forms: a sentence citing several distinct amendments in a single list («Restano così assorbiti gli emendamenti degli onorevoli X, Y e Z» — 'the amendments of Members X, Y and Z are thus absorbed'), now largely recognised and discarded; the chair of a committee speaking in that capacity and taken for a mover; and the formula by which the Presidency asks two movers of different amendments which one they keep. The errors found in the samples are corrected by hand in the data (`esporta_dataset.py`); the rates are estimates for the remaining amendments. `complete = 0` flags lists ending with «ed altri» (and others), whose further signatories are unknown.

**Accuracy of votes.** Of 21 votes with official totals, 19 differ by at most three names per side between matched names and totals (`check = ok`). For votes v16 and v21 the extraction matches the printed page, but the printed list itself differs from the announced totals (`verified: …`). For six votes the record gives no totals (`no official totals`). Two official totals misread by OCR were corrected from the page image (v7 and v27). Consistency checks on the whole dataset: no votes or signatures outside a member's term of office; if a member appears in two lists of the same vote the exact match is kept, and if both are exact (Zappelli in v16, printed twice) the vote is left missing.

### Amendment variables (`amendments_nodes.csv`)

| Variable | Description |
|---|---|
| `n_signatories` | Number of signatories (see `edgelist_amendments.csv`) |
| `complete` | 1 if the list of signatories is complete, 0 if it ends with «ed altri» |
| `article_mentioned` | 1 if the text cites an article of the draft Constitution |
| `sitting`, `date`, `pdf_page`, `url_pdf` | First mention and link to the page of the record |
| `source` | `signature block` or `presentation formula` |

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
