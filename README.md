# DIRISA SDC 2026: Electoral participation in Mpumalanga

Team submission for the **DIRISA Student Datathon Challenge 2026, Teams Qualification**. The theme is voter registration, participation and representation ahead of the **4 November 2026 Local Government Elections**.

## Problem statement

Turnout in Mpumalanga's local government elections fell from **56.4% in 2016 to 42.8% in 2021** (IEC results, team calculation). Ahead of 2026, only **41.0% of eligible 18-29-year-olds** in the province are registered, against **65.3% of those aged 30+**. The Auditor-General also keeps reporting weak financial management in several municipalities. This evidence is spread across IEC, Stats SA and Auditor-General sources, so it is hard to see *where* participation is at risk and *why*.

**Question:** *Which Mpumalanga municipalities and voting districts are most at risk of low turnout in 2026, how much of that risk comes from registration gaps versus turnout gaps, where does a young voters' roll overlap with historically low turnout, and how does municipal performance relate to participation?*

**For:** the IEC and civil society (targeting voter education), journalists (which areas to watch), and municipalities and parties (where registration isn't turning into votes).

| Part | Method | Answers |
|---|---|---|
| A | Two-step turnout forecast: province-wide level (from provincial-election turnout) + each voting district's local position (machine learning), backtested on 2011, 2016 and 2021 | Which areas are most at risk of low turnout in 2026 |
| B | Registration gap vs turnout gap (calculated) | Is the problem registration, or voting? |
| C | Socio-economic factors (rank correlations; model feature importance) | Which living conditions, education levels and audit records go with low participation |
| D | Participation profiles and a transparent priority list | Where youth, low turnout and weak municipal performance overlap |

## Status

| Stage | Content | Status |
|---|---|---|
| 1 | Environment, metadata, source checks, raw ingestion | Done |
| 2 | Mpumalanga election panel 2000-2021 (voting district x election x ballot), 2021 boundaries, reconciliation with IEC; provincial-election turnout 2004-2024 | Done |
| 3 | Census 2022 living conditions, education and age structure, registration rates, Auditor-General audit outcomes | Done |
| 4 | Exploratory analysis (6 figures) and feature engineering (leakage-checked features: relative position, party competition, swing sensitivity, station venue, registration surge) | Done |
| 5 | Models: two-step turnout forecast (A), registration vs turnout gap (B), socio-economic factors (C), profiles and priority list (D); limitations and references | Done |
| 6 | Dashboard (Streamlit): story, national-mood map, municipality drill-down, IEC team planner, backtest replay and methods | Built; visual screenshot review still needed |

## Team decisions

| Decision | Choice |
|---|---|
| Scope | **Mpumalanga**, 17 local municipalities, 2021 boundaries |
| Youth | ages **18-29** (matches the IEC roll's age bands) |
| History | all local elections **2000-2021** (2000 used only as history) |
| Turnout | **IEC rule**: max(PR, Ward) votes cast / registered voters, per voting district |
| Model level | voting district, aggregated to municipality for reporting |
| Digital registration / national youth figures | used as **context only**, since they are published only nationally or by province |

## Repository layout

```
model.ipynb                  the full pipeline, Stages 1-5 (every cell has WHAT / WHY / HOW TO READ comments)
dashboard/                   Streamlit app (six lazy views, shared visual system, data.py = loading and scenario maths); reads derived/ only
requirements.txt             pinned package versions (Python 3.11-3.13)
DATASETS/
  iec_results/
    local_elections/         IEC detailed results, Mpumalanga: MP_LGE_2011.csv, MP_LGE_2016.csv, MP_LGE_2021.csv
    official_turnout_reports/  IEC official Mpumalanga turnout reports 2011/2016/2021 (reconciliation)
    provincial_elections/    provincial-election turnout per municipality 2004-2024 (+ 2019 IEC report)
    LGE_All_Sources_Master_721327_Rows.csv   team baseline 2000-2021 (unpacked from compressed/)
  iec_registration/          2026 registered voters workbook; 2026 dashboard extract by municipality, age, gender
  census2022/                Census 2022 combined household file + raw/ F18, F21 (unpacked from compressed/)
  auditor_general/           Auditor-General audit outcomes (National Treasury Municipal Money API)
  reference/                 context-only files (IEC press figures, VAP 2000-2016, municipal codes, national age tables) and municipal boundaries for the map
  compressed/                the 4 large inputs as zip files (each under GitHub's 100 MB limit)
metadata/                    source registry, data dictionary, geography crosswalk, Census codebook and Stats SA metadata
derived/                     outputs rebuilt by the notebook (panels, features, forecasts, priority list, map boundaries, figures/, models/)
docs/                        competition brief, Day 1 problem statement, planning documents, references
```

## Data sources

| Source | Used for | Where |
|---|---|---|
| IEC detailed LGE results 2011, 2016, 2021 (Mpumalanga), [results.elections.org.za](https://results.elections.org.za/home/downloads/me-results) | Turnout history per voting district | `DATASETS/iec_results/local_elections/` |
| Team baseline (IEC results 2000-2021) | 2000 and 2006 results; cross-check of 2011-2021 | zipped in `DATASETS/compressed/` |
| IEC official Mpumalanga turnout reports 2011/2016/2021 | Reconciliation | `DATASETS/iec_results/official_turnout_reports/` |
| IEC provincial-election turnout per municipality 2004, 2009, 2014, 2019, 2024 | Recent turnout signal (feature) | `DATASETS/iec_results/provincial_elections/` |
| IEC provincial-election results per voting district 2004-2024, [results.elections.org.za](https://results.elections.org.za/home/downloads/npe-results) (downloaded 25 Sep 2026) | District turnout at provincial elections (tested feature) | `DATASETS/iec_results/provincial_elections/district_results/` |
| IEC voter registration dashboard, [elections.org.za](https://www.elections.org.za/pw/StatsData/Voter-Registration-Statistics), as of 23 Sep 2026 | 2026 registration by municipality, age, gender | `DATASETS/iec_registration/` |
| Stats SA Census 2022 10% sample (F18 geography, F19 households, F21 persons), [ISIbalo](https://isibaloweb.statssa.gov.za/pages/surveys/pss/censuses/2022/census2022.php) | Living conditions, education, eligible adult citizens | zipped in `DATASETS/compressed/` |
| Auditor-General audit outcomes via National Treasury [Municipal Money](https://municipaldata.treasury.gov.za) API (`audit_opinions`, downloaded 24 Sep 2026) | Municipal performance score | `DATASETS/auditor_general/` |
| Municipal Demarcation Board boundaries via [geoBoundaries](https://www.geoboundaries.org) (ZAF ADM3, simplified, CC BY 3.0 IGO) | Map of the 17 municipalities (Figure 13) | `DATASETS/reference/geoBoundaries-ZAF-ADM3_simplified.geojson` |
| IEC statements via ITWeb, Joburg ETC, Independent on Saturday, GroundUp (every URL in the file) | Context: online registration, national youth turnout | `DATASETS/reference/iec_2026_registration_press_figures.csv` |

## How to run (any computer)

```bash
git clone https://github.com/jaydenmanca/DIRISA_PROJECT.git
cd DIRISA_PROJECT
python -m venv .venv                                  # Python 3.11-3.13
# Windows:        .venv\Scripts\python.exe -m pip install -r requirements.txt
# macOS / Linux:  .venv/bin/python -m pip install -r requirements.txt
```

Open `model.ipynb` in VS Code (or Jupyter), select the `.venv` kernel, then **Restart** and **Run All**.

- **No manual data download is needed.** Cell 1.3 unpacks the four large inputs from `DATASETS/compressed/` on the first run (about 1-2 minutes, once).
- **Disk space:** allow about **3 GB free** (clone about 0.2 GB, Python environment about 0.6 GB, unpacked data about 1.3 GB, plus outputs). Cell 1.3 checks the free space and stops with a clear message if there isn't enough.
- Cell 1.1 checks that the required packages are installed and tells you exactly what to install if not.
- The whole notebook takes about 5-6 minutes. Cell 1.6 loads a 487 MB file (about 1.5 minutes): let it finish.
- Every derived table, figure and the trained model are written to `derived/`.

**Dashboard** (after the notebook has run once, so `derived/` exists). A fresh clone can skip the notebook once every dashboard input, including `derived/backtest_municipality_predictions.csv`, is committed:

```bash
.venv\Scripts\python.exe -m streamlit run dashboard/app.py      # Windows
.venv/bin/python -m streamlit run dashboard/app.py              # macOS / Linux
```

It opens at http://localhost:8501 (or the next free port). The six views are **Story**, **Map & mood**, **Municipality**, **IEC planner**, **Can you trust it?**, and **How it works**. The mood slider redraws turnout scenarios and the map; municipality and planner lists can be downloaded as CSV. `dashboard/requirements.txt` is the minimal list for hosting on Streamlit Community Cloud. Verify the final layout in a browser at desktop and phone widths before recording the demo.

Check the dashboard's fixed figures and controls with:

```bash
.venv\Scripts\python.exe -m unittest discover -s dashboard -p test_app.py   # Windows
.venv/bin/python -m unittest discover -s dashboard -p test_app.py      # macOS / Linux
```

## Findings

**Model results (Stage 5)**
- **Part A, turnout forecast (two steps).** Turnout = province-wide level + local position.
  - *Why two steps:* the first version predicted turnout directly and missed 2021 by 11.7 points, because turnout fell across the whole province (56.4% to 42.8%). No local data can foresee that; *where* turnout is lowest changes much less.
  - *Local position* (each voting district above or below the province): an ensemble of gradient boosting and regression to the mean, using district turnout history and party competition. Across three backtests (2011, 2016, 2021) it is off by **1.4-2.5 points per municipality** and ranks the 1,800 voting districts at rho 0.69 (simple rule: 0.55). Adding Census 2022, audit and provincial-election context did **not** improve it (5.49 vs 5.35 points per district).
  - *Creative features*, each tested on its own and kept only if it improved the backtest: **swing sensitivity** (how strongly a district's turnout has followed the province's, and that times the expected province-wide swing), **station venue** (tent, farm, traditional authority, church, school or hall, read from 1,785 voting-station names) and **registration surge** (municipal roll growth against the province). All three passed, but the gain is small: district error 5.29 to 5.27 points, municipal error 1.86 to 1.82, and it holds in every backtest year.
  - *District-level provincial-election turnout* (IEC results for 2004, 2009, 2014, 2019 and 2024, every voting district; 84-99% of districts match): the freshest turnout signal (2024) was also tested. It gave the largest district-level gain of any feature (district error 5.29 → 5.19, ranking 0.69 → 0.71) but made municipal totals slightly worse (1.86 → 1.92), so under the rule fixed before testing it was **not kept**. The data and the test stay in the notebook (cell 2.9).
  - *Province-wide level:* 2024 provincial-election turnout x the usual ratio of local to provincial turnout. It beat "same as last election" (average error 6.6 vs 7.8 points) but is the uncertain part: it missed 2011 and 2016 by 9-10 points.
  - *Overall:* average municipal error 6.8 points (first version 7.2, "same as last election" 7.7); in 2021, 2.3 points instead of 11.7.
  - **Mpumalanga 2026 forecast: 39.6%** (range 33.8-44.2%; 2021: 42.8%). 2024 provincial turnout fell to 57.1%, and local turnout has always been 59-78% of the preceding provincial turnout.
  - **357 at-risk voting districts** (lowest fifth of predicted local position), holding about 527,000 voters on the estimated 2026 roll (463,000 on the 2021 roll); most are in Emalahleni, City of Mbombela, Govan Mbeki and Bushbuckridge.
  - **10,000 simulated 2026 elections** (cell 5.6). Each draws the province-wide mood (spread of past local/provincial ratios) and the model's real past misses (one shared per municipality, one per district by size). Results: median turnout **39.9%** (80% range 33.4-46.1%); a **72% chance of a new record-low turnout** below 2021's 42.8% (65% under a more cautious, wider assumption); about **1.3 million registered voters expected to stay home**; 41 voting districts more likely than not to fall below 25%.
  - **The simulation is itself backtested** on 2016 and 2021 using only earlier elections: Mpumalanga's actual turnout fell inside the 80% range both times; municipalities 88% and 100% inside their 80% ranges; districts 81% and 92%; low-turnout districts ranked with AUC 0.96. District chances were too flat, so a calibration step (isotonic regression) rescales them; it is used only because it improved results when learned on one election and tested on the other.
  - **The registration surge:** the roll grew by 267,000 (1.90 million to 2.17 million), but the forecast implies only about 45,000 more ballots than 2021 (range: 77,000 fewer to 149,000 more).
  - **Does a registration surge dilute turnout?** At first sight yes: the fastest-growing fifth of voting districts fell 4.9 points relative to the province (2011-2021). But those were small districts that had started 9.5 points *above* the province, and they fell back towards it (regression to the mean). After adjusting for that, 10 points more roll growth went with **+0.4 points** of relative turnout (95% range +0.2 to +0.6): no sign that new registrations dilute turnout. The 2026 problem is the province-wide mood, not the new registrants.
- **Part B, registration vs turnout gap:** in 11 of 17 municipalities more eligible citizens are lost to *not being registered* than to *registered but not voting* (2021).
- **Part C, socio-economic factors** (17 municipalities, association not cause): municipalities with a younger adult population have lower registration (rho -0.78). Internet, computer and car ownership go with higher registration (+0.64 to +0.66). Adult hunger goes with a lower share of eligible citizens voting (-0.55). These factors describe *where* participation is low but add nothing to the forecast once turnout history is known.
- **Part D, priority list:** top 5 are MP307 Govan Mbeki, MP302 Msukaligwa, MP312 Emalahleni, MP316 Dr JS Moroka and MP315 Thembisile Hani. The ranking is stable under other weightings (rank correlation 0.83-0.96).

**Figures for the slides** (`derived/figures/`): Figure 16 is the 10,000 simulated 2026 elections, Figure 14 the headline (roll vs ballots), Figure 13 the map (where turnout is at risk, and the priority ranking), Figure 15 the at-risk voting districts per municipality, Figure 7 the backtest, Figure 12 the registration-surge test.

**Data findings (Stages 1-4)**

- **Data quality:** the original IEC files and the team baseline agree exactly for 2011-2021. The official IEC Mpumalanga turnout reports are reproduced exactly for 18/18 municipalities (2011), 17/17 (2016) and 16/17 (2021).
- **Turnout:** 44.3% (2000), 46.6% (2006), 55.9% (2011), 56.4% (2016), **42.8% (2021)**.
- **Youth registration (2026):** 41.0% of 18-29-year-old citizens vs 65.3% of those aged 30+. Youth trail in **all 17** municipalities, with gaps from 15 points (MP304) to 37 points (MP306).
- **Municipal performance:** audit outcomes vary widely. Steve Tshwete had the most clean audits; Thaba Chweu had disclaimers every year 2011-2017.
- **Context:** across the 17 municipalities, 2021 turnout was higher where more households live in RDP housing (Spearman +0.63) or have piped water in the yard (+0.50). This is association, not cause.

## Limitations (also written into the notebook)

- The 2026 eligible-citizen counts come from Census 2022 aged forward. Deaths after 2022 are not removed, so 2026 registration rates are lower bounds and the youth gap is understated.
- About 16.5% of Census households left the household-goods, internet and hunger questions unanswered (6-35% by municipality). Rates use answering households only, with the answer rate shown.
- Online-registration and age-level turnout figures exist only nationally or provincially, so they are used as context, not as model inputs. There is no municipal youth registration history before 2026.
- Census 2022 is a later snapshot when used as context for the 2006-2021 elections.
- The Census 10% sample identifies municipalities only, so socio-economic factors vary across 17 places; employment and income were withheld by Stats SA.
- Only three backtests (2011, 2016, 2021) and four past local/provincial turnout ratios exist. The local picture is well tested; the province-wide level is not, so it is shown as a range of scenarios.
- The 2004 provincial turnout per municipality excludes Bushbuckridge (then in Limpopo) while the 2006 local turnout includes it; like-for-like, the 2006 ratio moves from 0.589 to 0.592 and the 2026 forecast by 0.04 points.
- The 2026 simulation assumes the province-wide mood varies like the four past local/provincial ratios and that the model's 2011-2021 misses are typical of 2026; a cautious wider variant is reported beside every headline probability.
- The IEC publishes 2026 registration per municipality only, so district-level 2026 voter counts are estimates (2021 district roll x municipal growth).
- Station venue is read from voting-station names with keyword rules; names are missing for 2000 and 2006, so venue is learned from the 2016 and 2021 backtests only. Swing sensitivity needs at least three past elections per district.
- Party competition comes from the previous local election's PR ballot; 2024 national results by voting district were not available, so the 2024 shift in party support is not in the local model.
- Ward councillor, party registration and by-election data were not downloadable from the IEC during the project.
- One 2000 record (Mdala Nature Reserve) has spoilt votes recorded as NULL at source (set to 0). MP325's 2021 official turnout report differs slightly from the detailed results file.

## Submission

Code and video are due **8am, 28 September 2026** on the DIRISA NextCloud platform. The shareable link goes to Ms Boitshepo Sebusho (bsebusho@csir.co.za).
