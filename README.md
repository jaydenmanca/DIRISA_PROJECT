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
| C | Participation profiles and a transparent priority list | Where youth, low turnout and weak municipal performance overlap |

## Status

| Stage | Content | Status |
|---|---|---|
| 1 | Environment, metadata, source checks, raw ingestion | Done |
| 2 | Mpumalanga election panel 2000-2021 (voting district x election x ballot), 2021 boundaries, reconciliation with IEC; provincial-election turnout 2004-2024 | Done |
| 3 | Census 2022 indicators, registration denominators, Auditor-General audit outcomes | Done |
| 4 | Exploratory analysis (6 figures) and feature engineering (30 leakage-checked features) | Done |
| 5 | Models: turnout forecast, gap breakdown, profiles and priority list | Next |
| 6 | Dashboard (Streamlit) | To do |

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
model.ipynb                  the full pipeline (every cell has WHAT / WHY / HOW TO READ comments)
requirements.txt             exact package versions (Python 3.13)
metadata/
  README.md                  data rules: Census usage rules, Stage 2-4 notes, limitations
  source_registry.csv        every source: origin, date, grain, limitations, status
  data_dictionary.csv        variable definitions
  geography_crosswalk.csv    municipality code/name decisions (e.g. MP314 = Emakhazeni)
  census2022_household_codebook_derived.csv   Census code -> label for every household variable
  census2022_docs/           official Stats SA Census 2022 10% sample metadata (PDF)
DATASETS/
  LGE2011/MP_2011.csv, LGE2016_MP/MP_2016.csv, LGE2021_MP/MP_2021.csv   IEC detailed results, Mpumalanga
  IEC_official_turnout/      IEC official Mpumalanga turnout reports (reconciliation)
  voter_turnout/             provincial-election turnout per municipality 2004-2024 (compiled from IEC municipal reports)
  AGSA_audit_opinions/       Auditor-General audit outcomes (National Treasury Municipal Money API)
  2026 Registered voters.xlsx, youth_registration_variables_national.csv   2026 registration (IEC)
  iec_2026_registration_press_figures.csv   sourced IEC press figures (context only)
derived/                     outputs rebuilt by the notebook (panels, features, figures/)
```

## Data sources

| Source | Used for | In this repo? |
|---|---|---|
| IEC detailed LGE results 2011, 2016, 2021 (Mpumalanga), [results.elections.org.za](https://results.elections.org.za/home/downloads/me-results) | Turnout history per voting district | Yes |
| Team baseline `LGE_All_Sources_Master_721327_Rows.csv` (IEC results 2000-2021) | 2000 and 2006 results; cross-check of 2011-2021 | **No** (464 MB) |
| IEC official Mpumalanga turnout reports 2011/2016/2021 (from the challenge zip) | Reconciliation | Yes |
| IEC provincial-election turnout per municipality 2004, 2009, 2014, 2024 | Recent turnout signal (feature) | Yes |
| IEC voter registration dashboard, [elections.org.za](https://www.elections.org.za/pw/StatsData/Voter-Registration-Statistics), as of 23 Sep 2026 | 2026 registration by municipality, age, gender | Yes |
| Stats SA Census 2022 10% sample (F18 geography, F19 households, F21 persons), [ISIbalo](https://isibaloweb.statssa.gov.za/pages/surveys/pss/censuses/2022/census2022.php) | Living conditions; eligible adult citizens | **No** (over 100 MB) |
| Auditor-General audit outcomes via National Treasury [Municipal Money](https://municipaldata.treasury.gov.za) API (`audit_opinions`, downloaded 24 Sep 2026) | Municipal performance score | Yes |
| IEC statements via ITWeb, Joburg ETC, Independent on Saturday, GroundUp (see `iec_2026_registration_press_figures.csv` for every URL) | Context: online registration, national youth turnout | Yes |

### Data not in this repository

GitHub rejects files over 100 MB. Before running the notebook, place these files locally:

| File | Where it goes | How to get it |
|---|---|---|
| `LGE_All_Sources_Master_721327_Rows.csv` | project root | Team shared drive (team-built from IEC results) |
| `DIRISA_Election_Challenge.zip` | project root | Challenge data pack |
| `Census2022sample_F18.csv`, `_F19.csv`, `_F21.csv` | `DATASETS/Census2022_raw/` | Extract from `DIRISA_Election_Challenge.zip` (`data/raw/demographics/`) |
| `Census2022_F18_F19_Combined_full.csv` | `DATASETS/` | F18 and F19 joined one-to-one on `QID` (1,338,295 households); see `metadata/README.md` |

## How to run

```powershell
python -m venv .venv                      # Python 3.13
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Open `model.ipynb` in VS Code, select the kernel **`.venv\Scripts\python.exe`** (cell 1.1 stops with a clear message if the wrong Python is selected), then **Run All**. The whole notebook takes about 3-4 minutes. Every derived table and figure is written to `derived/`.

## Findings so far (Stages 1-4)

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
- The 2019 provincial election is not yet in `DATASETS/voter_turnout/`, so the 2021 forecast features use 2014.
- One 2000 record (Mdala Nature Reserve) has spoilt votes recorded as NULL at source (set to 0). MP325's 2021 official turnout report differs slightly from the detailed results file.

## Submission

Code and video are due **8am, 28 September 2026** on the DIRISA NextCloud platform. The shareable link goes to Ms Boitshepo Sebusho (bsebusho@csir.co.za).
