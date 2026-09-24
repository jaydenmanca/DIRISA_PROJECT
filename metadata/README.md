# DIRISA 2026 data metadata and join contract

This folder governs the files used by `model.ipynb` and the root-level baseline file `LGE_All_Sources_Master_721327_Rows.csv`.

## Current source inventory

The current `DATASETS` folder contains:

1. `2026 Registered voters.xlsx` - a report-style workbook containing multiple logical tables on one worksheet.
2. `Census2022_F18_F19_Combined.csv` - household-level coded Census records with a household weight.

The root baseline is:

3. `LGE_All_Sources_Master_721327_Rows.csv` - a team-derived, long-format integration of IEC/election-results data. It contains 721,327 data rows and is not the final modelling table.

## Governing rules

- Treat raw files as immutable. Any cleaned or aggregated table must have a new name and a recorded transformation.
- The canonical modelling grain is one row per `municipality_code x election_year`, subject to successful geography and denominator validation.
- Party/ballot/source rows in the baseline must be aggregated before modelling. Repeated `registered_voters` and turnout values are not independent observations.
- The primary analytical scope is Mpumalanga. All-province baseline records may be used for context or a deliberately specified robustness design, but must not silently mix with the main result.
- `reported_turnout_pct`, `ballot_turnout_pct`, `pr_turnout_pct`, `reported_ballot_votes_cast`, `ballot_votes_cast`, and other same-election outcome components are target variables or target components. They are prohibited from a same-election forward-looking feature matrix.
- Every model feature needs a prediction cutoff date and a source/reference period.
- Census variables are coded categories until the official codebook is attached. Numeric codes must not be treated as ordered measurements without justification.
- Census aggregation must use `HH_WGT` and must publish the aggregation denominator and effective coverage.
- Municipality joins must use a reviewed canonical code crosswalk, never fuzzy name matching alone.

## Required next steps

1. Attach the official source URLs, download dates, codebooks and boundary versions to `source_registry.csv`.
2. Split the Excel report into tidy tables: `voter_province_2026`, `voter_age_gender_2026`, and `voter_municipality_2026`.
3. Extract the distinct Mpumalanga `municipality_code`/`municipality_source` pairs from the root baseline and resolve them against `geography_crosswalk.csv`.
4. Obtain and attach the Census 2022 variable codebook, including the universe and valid values for every `H*` and `DERH_*` field.
5. Aggregate Census records to municipality level with `HH_WGT`; keep the raw household table separate and never expose `QID` in dashboard outputs.
6. Add automated join tests: exact code match rate, unmatched records, one-to-many matches, duplicate canonical keys and totals before/after joining.

## Status meanings

- `approved-for-audit-not-modeling`: usable for inspection and reconciliation, not yet a modelling input.
- `quarantine-until-profiled`: present but missing enough provenance/definitions that it must not enter the model.
- `provisional`: a candidate crosswalk row requiring review.
- `pending` or `unresolved`: do not join.

## Relationship to `model.ipynb`

The notebook should load these metadata files before loading data. The first notebook cells should:

1. read `source_registry.csv`, `data_dictionary.csv` and `geography_crosswalk.csv`;
2. assert that all input files have a registry entry;
3. assert that all model columns have a dictionary entry;
4. fail if any join row is `pending` or `unresolved` for the selected modelling scope;
5. record the final input filenames, file sizes/checksums and metadata version in the run manifest.

## Census 2022 usage rules (added 2026-09-24)

Source: Stats SA Census 2022 Ten Percent Sample (report 03-01-47). The official metadata PDFs are in `metadata/census2022_docs/`. The code-to-label mapping for every household variable is in `metadata/census2022_household_codebook_derived.csv`. It was derived by joining the coded file to the labelled `housing_dataset.csv` on QID (1,048,575 households, identical weights) and checked against the Stats SA household metadata.

Files:
- `DATASETS/Census2022_raw/Census2022sample_F18.csv`: geography (Province, District, Municipality, Geo_type), one row per household (QID).
- `DATASETS/Census2022_raw/Census2022sample_F19.csv`: household variables + `HH_WGT`.
- `DATASETS/Census2022_raw/Census2022sample_F21.csv`: persons (age, sex, citizenship, education, ...) + `PERS_WGT`; link to F18 on QID for municipality.
- `DATASETS/Census2022_F18_F19_Combined_full.csv`: F18 + F19 joined one-to-one on QID (1,338,295 households, all 9 provinces).
- `housing_dataset.csv` (root): labelled version of F19, but truncated at 1,048,575 rows and 104,023 rows stored as one quoted string. Use only as a codebook reference, never as data.

Rules:
1. **Households = conventional dwellings only** (`H01_QUARTERS` in 1, 2). Weighted total 17.82M matches the published 17.8M. Codes 3-5 are excluded from household indicators.
2. **Always weight** with `HH_WGT` (households) or `PERS_WGT` (persons). Weights are inverse inclusion probabilities calibrated to Census counts per local municipality by age, sex and population group, so municipality-level aggregates are the intended use.
3. **Unspecified is missing, not "no"**. Codes 9 / 99 (and 8 / 88 = not applicable) are excluded from numerators and denominators. About 16.5% of households are Unspecified across tenure, RDP, household goods, internet and hunger together (the same households, 99.98% overlap). The share ranges 6.4%-35.1% by municipality and is higher in metros and the Western Cape. Every indicator must publish `specified_share` next to it.
4. **Persons (F21) cover household residents only**: homeless, transient and institutional residents (questionnaire types 2-4) were out of scope. An adult (18+) count from F21 is therefore a household-population VAP and slightly understates the total adult population. Citizenship code 101 = South Africa (999 = Unspecified). Checked 2026-09-24: weighted persons 61.37M vs published 62.0M (the gap is the out-of-scope homeless, transient and institutional population); adults 18+ = 41.99M; adult SA citizens 18+ = 40.05M (citizenship unspecified for 0.31% of adults). Every person links to a municipality via QID.
5. Census municipality codes are the 2022 (= 2021 LGE) boundaries, e.g. MP326 City of Mbombela; see `census2022_docs/06. Census 2022 Code lists.pdf`.
6. Data caveat: DataFirst notes that Stats SA did not release some questionnaire sections in its version because of reporting and coverage bias (including housing, household goods/services and food security). The fields in this extract carry the high Unspecified rates described in rule 3. State this limitation whenever those indicators are used.

## Stage 2 election panel (added 2026-09-24)

Outputs in `derived/` (rebuilt by notebook Stage 2):
- `election_vd_panel.parquet`: one row per election_year x voting_district x ballot_type (PR, WARD, DC40, DMA_DC60), 2000-2021, all provinces. Columns include registered_voters, votes_cast (= valid + spoilt), turnout_pct, the source municipality and the 2021 municipality with the mapping method.
- `vd_to_2021_municipality_map.csv`: each voting district per election mapped to a 2021 municipality (`vd_code_match`, `municipality_majority` or `unmapped`).
- `municipality_election_panel_2021_boundaries.csv`: one row per 2021 municipality x election x ballot (213 municipalities x 5 elections).
- `reconciliation_*.csv`: checks against the IEC's published figures.

Rules and findings:
- Turnout here = votes cast / registered voters for the ballot. The IEC's official turnout = max(PR, Ward) votes cast / (registered + MEC7 votes). MEC7 counts are not in the raw files, so national turnout comes out 0.10-0.18 points above published figures. Mpumalanga matches the official reports to <0.005 points once MEC7 is added, except MP325 in 2021 (official report: +1,019 registered, +6 votes; the report was printed later than the results file).
- One 2000 row (MPDMA31 Mdala Nature Reserve, voting district 54580226, Ward ballot) has spoilt votes recorded as NULL at source; it is set to 0.
- 378 voting district x ballot rows have more votes than registered voters (voters on another station's roll voting with an MEC7 form). They are kept.
- Boundary mapping: 98.8% (2000) to 99.6% (2016) of registered voters map by exact voting district code; the rest by municipality majority; none unmapped. 2000 district management areas and some 2000 local municipalities split across several 2021 municipalities.

## Stage 3 Census indicators and registration denominators (added 2026-09-24)

Outputs in derived/ (rebuilt by notebook Stage 3):
- census2022_municipality_indicators.csv: one row per municipality (213). Weighted household shares (%) for internet, cellphone, computer, car, piped water, electricity, flush toilet, weekly refuse, informal dwelling, RDP house, adult hunger and female-headed households. Each indicator has an *_answered_pct column. The file also has urban/traditional/farms shares (Geo_type 1/2/3) and mean household size.
- registration_denominators_2021_2026.csv: adult SA citizens (18+, 18-29, 30+) aged to 1 Nov 2021 and 23 Sep 2026 using birth year and month. It also has the registered voters in 2021 (PR, Stage 2) and 2026 (IEC dashboard, by age), with registration rates, the youth-vs-older gap, youth share of the roll and roll growth.

Findings and caveats:
- Nationally, 65.7% of eligible citizens were registered in 2021 and 65.0% in 2026. In 2026 the rate is 46.5% for ages 18-29 and 71.7% for ages 30+.
- Deaths after Feb 2022 are not removed. The 2026 eligible count (44.9M) is therefore too high, mostly among older adults, so 2026 rates are lower bounds and the youth gap is understated.
- 5 municipalities have 2026 rates above 100%: LIM361, NC064, NC067 (201%), NC074 and NC453. They are kept and flagged. Likely causes are small samples, people registered away from where they live, and migration.
- Answer rates for household goods, internet, RDP and hunger range from 61% to 94% by municipality.

## Stage 4 features (added 2026-09-24)

Team decisions: youth = 18-29; history = all elections 2000-2021; turnout = max(PR, Ward) votes cast / registered voters per voting district (IEC rule without MEC7).

Outputs in derived/ (rebuilt by notebook Stage 4):
- figures/fig1..fig5 *.png: charts for the slides.
- features_vd.parquet: one row per voting district x target election (2006, 2011, 2016, 2021 = history with known turnout; 2026 = forecast rows built on the 2021 districts). 26 features, all known before the election. Census 2022 context is a later snapshot for 2006-2021 targets (stated limitation).
- feature_dictionary.csv: source, "known before the election?" and missing share for every feature.
- features_municipality.csv: 2021-boundary municipality table with turnout 2000-2021, registration rates 2021/2026, youth gap, youth share of roll, participation 2021 (= registration rate x turnout) and Census context. Used for Parts B and C.

Findings:
- National turnout (IEC rule): 48.2% (2000), 48.2% (2006), 57.8% (2011), 58.1% (2016), 46.0% (2021).
- Youth (18-29) registration is below 30+ registration in 211 of 213 municipalities.
- Census conditions are only weakly associated with 2021 municipal turnout (Spearman |rho| <= 0.28). Turnout history is expected to carry most of the predictive signal.
- A voting district's own history exists for 78% of 2006 targets, rising to 97% of 2021 targets. The remainder are new or renumbered districts, which fall back on municipality history.
