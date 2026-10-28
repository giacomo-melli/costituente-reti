# The networks of the Italian Constituent Assembly, 1946–1948: amendments, votes and speech mentions reconstructed from the printed record

*Giacomo Melli, Department of Sociology, University of Oxford*

*Draft data note for version 1.1.0 of the dataset (DOI 10.5281/zenodo.23646592). Figures refer to that version; the codebook (`data/en/codebook.md`) is the reference for every variable.*

## Abstract

The Italian Constituent Assembly (25 June 1946 – 31 January 1948) wrote the Constitution of the Republic in a chamber of 556 seats held, over its life, by 581 people. This dataset describes them as a set of networks: membership of the Assembly's bodies, co-signature of amendments (1,408 amendments, 394 with two or more signatories, 3,275 member–amendment ties), a directed network from signatories to proposers, mentions of members in other members' speeches (9,194 mentions), 27 roll-call votes (9,125 member–vote ties), and 842 other co-signed acts (questions, interpellations, orders of the day, vote requests). Amendments, mentions and votes are reconstructed from the printed proceedings by optical character recognition and rule-based extraction. Each component is validated against an independent judge: the page image for amendments, the totals announced by the President for votes, the alphabetical order of printed roll calls for names, and the Chamber of Deputies' table of preparatory works for the article and subject of each amendment.

## Background and motivation

Co-sponsorship and roll-call data are standard material for the study of legislatures, but for constituent assemblies, and for the Italian one in particular, they have not been available in machine-readable form. The Assembly's proceedings are published as scanned PDF files without a text layer. The dataset turns them into networks while keeping every step reproducible and every record traceable to the printed page.

## Methods

**Sources.** Members, bodies and activity indexes come from the historical portal of the Chamber of Deputies; biographical indicators from Wikidata and Wikipedia; amendments, mentions and votes from the stenographic records (*resoconti*) of the plenary sittings, as PDF scans published by the Chamber.

**Text.** The 173 sittings in which the index of proceedings records amendments or votes (4,786 pages) were transcribed with Tesseract (Italian model), splitting the two printed columns; the 3,275 pages that mention amendments were read a second time at 400 dpi, and the reading recognising more members' surnames is kept.

**Amendments.** A rule-based extractor recognises the formulas with which amendments are presented («L'onorevole X ha presentato il seguente emendamento», «Gli onorevoli X, Y e Z hanno presentato…», «Segue l'emendamento degli onorevoli…») and the signature blocks printed under the text of an amendment. It excludes, by explicit rules, mentions that are not amendments: names governed by verbs or nouns of speech («le dichiarazioni dell'onorevole X»), lists of distinct acts («gli emendamenti degli onorevoli X e Y»), questions, motions, orders of the day and vote requests. Each mention is resolved to a member through the list of members in office on that date; shared surnames are resolved by co-signatories and by who else is present in the same sitting. Repeated readings of the same amendment are merged when signatories and printed text are compatible. Every family of errors found during validation was fixed in the extractor and added to a regression test of 63 real passages (`pipeline/tools/test_regole.py`).

**Votes.** Roll-call lists are parsed from the printed record, names are matched to members, and the alphabetical order of the list is used both to recover names garbled by OCR and to reject approximate matches that break the order. The totals announced by the President are the external judge.

**Speech mentions.** References such as «come ha detto l'onorevole X» are kept as a directed network from the speaker (the name heading the turn) to the member mentioned.

**Further variables.** Proposer and signatories are distinguished; the printed text and type of each amendment (replace, delete, add, insert), its outcome where the record states it unambiguously, the article under discussion, its subject (part and title of the draft) and the corresponding article of the Constitution; for members, membership of the Committee for the Constitution and its subcommittees, attendance at roll calls and re-election to the Chamber in 1948.

## Data records

All files are in `data/it` (Italian variable names) and `data/en` (English), as CSV in UTF-8, with the same content. GraphML versions of the six networks are in `data/graphml`, and `R/00_build_networks.R` builds the corresponding `igraph` objects. Every amendment record carries the address of the PDF page it comes from.

## Technical validation

| Component | Check | Result |
|---|---|---|
| Amendments, recall | 14 random sittings read in full on the image; validation sample | 20/30 = 67% (49–81); multi-signatory 9/10 |
| Amendments, precision | 40 random records on the image | false positives 2/40; wrong signatories 3/38 |
| Multi-signatory amendments | every one checked on the image at least once | false positives 4.2%, wrong signatories 4.3% (216 checked for the first time) |
| Single-signatory amendments | two blind samples (60 + 50) | true errors 2/48 = 4.2% in the second, after fixes |
| Reproducibility of the image reading | 50 records re-read blind | Cohen's kappa 1.00 on both questions |
| Proposer | against 131 lists transcribed from the image | 130/131 |
| Amendment type | blind reading | 29/40 = 72.5% |
| Outcome | blind validation sample, assigned outcomes only | 26/30 = 86.7% (70.3–94.7); assigned to 17% of amendments |
| Subject (part and title of the draft) | blind validation sample | 17/18 |
| Article under discussion | blind validation sample | 14/20 = 70% |
| Votes | matched names against official totals | 21 of 23 votes within three names per side; two printed lists differ from the announced totals; four votes void for lack of quorum |
| Vote matching | group cohesion (Rice index) | PCI 0.996, DC 0.983 |
| Speech mentions | blind reading | member mentioned 40/40; speaker 31/31 where visible |
| Other co-signed acts | blind reading | type 17/20, signatories 19/20 |
| Persons | members with no ties searched in the corpus | three missed amendments found, their error families fixed |

The effect of the measured errors on network statistics is reported in the codebook: homophily and reciprocity change little; density and degree fall by about a tenth when errors are removed. A conservative version of each network keeps only exact matches and hand-corrected lists.

## Usage notes and limitations

The dataset contains about two thirds of the amendments printed in the transcribed sittings, and 16 sittings held on days when the draft Constitution was discussed are not yet transcribed (listed in `pipeline/sedute_non_trascritte.csv`). Network volume measures are therefore lower bounds; structural measures are more robust. Thirty-two amendment lists are closed by «ed altri» and lack the unnamed signatories. Group affiliation at the date of each signature and vote comes from the Chamber's open data on group membership. Open cases that the extraction cannot settle (shared surnames without other evidence, illegible names) are listed in `pipeline/CASI_APERTI.xlsx`; decisions taken on the page image are applied at every export and remain in the repository.

## Code availability

The full pipeline (OCR, extraction, verification files, export) is in `pipeline/`, under the MIT licence; the data are released under CC BY-SA 4.0. The record of every verification sample is in `pipeline/extraction/VERIFICA_*`.
