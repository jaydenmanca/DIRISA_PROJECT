# DIRISA SDC 2026: Electoral participation in Mpumalanga

Team submission for the **DIRISA Student Datathon Challenge 2026, Teams Qualification**. The theme is voter registration, participation and representation ahead of the **4 November 2026 Local Government Elections**.

## Problem statement

Turnout in Mpumalanga's local government elections fell from **56.4% in 2016 to 42.8% in 2021** (IEC results, team calculation). Ahead of 2026, only **41.0% of eligible 18-29-year-olds** in the province are registered, against **65.3% of those aged 30+**. The Auditor-General also keeps reporting weak financial management in several municipalities. This evidence is spread across IEC, Stats SA and Auditor-General sources, so it is hard to see *where* participation is at risk and *why*.

**Question:** *Which Mpumalanga municipalities and voting districts are most at risk of low turnout in 2026, how much of that risk comes from registration gaps versus turnout gaps, where does a young voters' roll overlap with historically low turnout, and how does municipal performance relate to participation?*

**For:** the IEC and civil society (targeting voter education), journalists (which areas to watch), and municipalities and parties (where registration isn't turning into votes).

| Part | Method | Answers |
|---|---|---|
| A | Turnout forecast (machine learning, backtested on 2016 and 2021 against "same as last election") | Which areas are most at risk of low turnout in 2026 |
| B | Registration gap vs turnout gap (calculated) | Is the problem registration, or voting? |
| C | Socio-economic factors (rank correlations; model feature importance) | Which living conditions, education levels and audit records go with low participation |
| D | Participation profiles and a transparent priority list | Where youth, low turnout and weak municipal performance overlap |

## Status

| Stage | Content | Status |
|---|---|---|
| 1 | Environment, metadata, source checks, raw ingestion | Done |
| 2 | Mpumalanga election panel 2000-2021 (voting district x election x ballot), 2021 boundaries, reconciliation with IEC; provincial-election turnout 2004-2024 | Done |
| 3 | Census 2022 living conditions, education and age structure, registration rates, Auditor-General audit outcomes | Done |
| 4 | Exploratory analysis (6 figures) and feature engineering (leakage-checked features) | Done |
| 5 | Models: turnout forecast (A), registration vs turnout gap (B), socio-economic factors (C), profiles and priority list (D); limitations and references | Done |
| 6 | Dashboard (Streamlit) | Next |

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
  reference/                 context-only files (IEC press figures, VAP 2000-2016, municipal codes, national age tables)
  compressed/                the 4 large inputs as zip files (each under GitHub's 100 MB limit)
metadata/                    source registry, data dictionary, geography crosswalk, Census codebook and Stats SA metadata
derived/                     outputs rebuilt by the notebook (panels, features, forecasts, priority list, figures/, models/)
docs/                        competition brief, Day 1 problem statement, planning documents, references
```

## Data sources

| Source | Used for | Where |
|---|---|---|
| IEC detailed LGE results 2011, 2016, 2021 (Mpumalanga), [results.elections.org.za](https://results.elections.org.za/home/downloads/me-results) | Turnout history per voting district | `DATASETS/iec_results/local_elections/` |
| Team baseline (IEC results 2000-2021) | 2000 and 2006 results; cross-check of 2011-2021 | zipped in `DATASETS/compressed/` |
| IEC official Mpumalanga turnout reports 2011/2016/2021 | Reconciliation | `DATASETS/iec_results/official_turnout_reports/` |
| IEC provincial-election turnout per municipality 2004, 2009, 2014, 2019, 2024 | Recent turnout signal (feature) | `DATASETS/iec_results/provincial_elections/` |
| IEC voter registration dashboard, [elections.org.za](https://www.elections.org.za/pw/StatsData/Voter-Registration-Statistics), as of 23 Sep 2026 | 2026 registration by municipality, age, gender | `DATASETS/iec_registration/` |
| Stats SA Census 2022 10% sample (F18 geography, F19 households, F21 persons), [ISIbalo](https://isibaloweb.statssa.gov.za/pages/surveys/pss/censuses/2022/census2022.php) | Living conditions, education, eligible adult citizens | zipped in `DATASETS/compressed/` |
| Auditor-General audit outcomes via National Treasury [Municipal Money](https://municipaldata.treasury.gov.za) API (`audit_opinions`, downloaded 24 Sep 2026) | Municipal performance score | `DATASETS/auditor_general/` |
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

## Findings

**Model results (Stage 5)**
- **Part A, turnout forecast:** gradient boosting beat the "same as last election" rule in the backtests (average municipal error 6.7 vs 7.8 percentage points; 1.6 points when predicting 2016). Every method predicted 2021 too high, because the 2021 collapse could not be foreseen from earlier elections. The model relies mostly on turnout history. **Mpumalanga 2026 forecast: 46.2%** (2021: 42.8%). Backtests suggest actual turnout tends to land at or below the forecast (80% range: -14.6 to +0.5 points).
- **Part B, registration vs turnout gap:** in 11 of 17 municipalities more eligible citizens are lost to *not being registered* than to *registered but not voting* (2021).
- **Part C, socio-economic factors** (17 municipalities, association not cause): municipalities with a younger adult population have lower registration (rho -0.78). Internet, computer and car ownership go with higher registration (+0.64 to +0.66). Adult hunger goes with a lower share of eligible citizens voting (-0.55).
- **Part D, priority list:** top 5 are MP312 Emalahleni, MP307 Govan Mbeki, MP313 Steve Tshwete, MP302 Msukaligwa and MP326 City of Mbombela. The ranking is stable under other weightings (rank correlation 0.80-0.95).

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
- Only two backtests are possible, and one of them is the 2021 collapse, so the forecast's error range is a rough guide.
- Ward councillor, party registration and by-election data were not downloadable from the IEC during the project.
- One 2000 record (Mdala Nature Reserve) has spoilt votes recorded as NULL at source (set to 0). MP325's 2021 official turnout report differs slightly from the detailed results file.

## Submission

Code and video are due **8am, 28 September 2026** on the DIRISA NextCloud platform. The shareable link goes to Ms Boitshepo Sebusho (bsebusho@csir.co.za).
