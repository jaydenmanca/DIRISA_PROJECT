# Design brief: Mpumalanga 2026 turnout dashboard

> **Update (25 Sep):** the Story hero (`ui/js/surge_hero.*`) and the Map & mood explorer (`ui/js/mood_explorer.*`) are now custom browser components built on the 10,000-simulation 2026 forecast. Keep their behaviour and numbers; polish around them. District voter counts now use the estimated 2026 roll.

**For:** the coding agent redesigning `dashboard/` (Streamlit).
**Goal:** turn a working but plain scaffold into a dashboard that competition judges remember: calm, precise, editorial and obviously designed by people who care. It must not look like a default Streamlit app or like something generated in one pass.
**Deadline context:** the team records a 15-minute video demo on Sunday 27 September 2026 and submits at 08:00 on Monday 28 September. The dashboard must be finished, stable and demo-ready by Sunday morning. Prefer finished and consistent over ambitious and half-done.

Read this whole brief before writing code. Then read `dashboard/app.py`, `dashboard/data.py`, `README.md` and skim `model.ipynb` Stage 5 so you understand what each number means.

---

## 0. Ground rules (non-negotiable)

1. **Do not change any numbers.** The model, the notebook (`model.ipynb`) and everything in `derived/` are finished and must not be edited. The dashboard only *reads* `derived/`. If you need a value that is not in `derived/`, compute it in `dashboard/data.py` from what is there, and say so in a code comment.
2. **Keep the logic in `dashboard/data.py`.** Presentation code goes in `app.py` (or in new UI modules under `dashboard/`, see §3). Do not change the maths in `district_turnout`, `municipality_turnout`, `expected_ballots`, `priority_scores` or `plan_teams`. You may add helpers.
3. **Keep the widget key `province_level`.** It holds the national-mood slider value and is shared across tabs.
4. **No hardcoded data values in the UI.** One exists today: the Story tab's "vs 2021" delta uses a literal `42.8`. Replace it with the 2021 actual from `derived/model_backtest_province.csv` (row `test_year == 2021`, column `actual`, any method) or from `features_municipality.csv` + registration weights. Every number on screen must come from the data.
5. **Dependencies:** use what is pinned: `streamlit==1.64.0`, `pandas`, `numpy`, `altair==6.3.0`, `pydeck==0.9.3`. Do not add packages unless there is no other way. If you add one, pin it in **both** `requirements.txt` and `dashboard/requirements.txt` and explain why in your summary. Before using any Streamlit API, check that it exists in 1.64 (`python -c "import streamlit as st; help(st.segmented_control)"` and so on). Do not rely on memory of the API.
6. **Political neutrality.** This is an election dashboard for the IEC, civil society and journalists.
   - No party names, logos or party colours as design elements. Avoid ANC green/black/gold, DA blue as a brand colour, and EFF red as a brand colour. The data palette (blue/red diverging) is fine because it encodes above/below the province, but never pair it with party wording.
   - No IEC, Stats SA, CSIR, DIRISA or government logos or crests. Do not imitate any official organisation's branding. Sources are cited in text only.
   - Neutral, non-blaming language: "at risk", "priority", "below the province". Never "failing", "worst", "apathetic" or "bad voters".
7. **Honesty in the interface.** Where the model is uncertain, the UI shows it (ranges, the scenario nature of the province level, the swing-sensitivity damping). Never present the 2026 forecast as a fact.
8. **Commits:** do not add any `Co-Authored-By` lines or AI attribution to commit messages. If you commit, the author is the repository owner's configured identity. If none is configured, stop and ask rather than invent one.
9. **The existing behaviour must keep working** (see the acceptance tests in §17).

---

## 1. What the dashboard is for (read this to design with intent)

**Question the project answers:** *Which Mpumalanga municipalities and voting districts are most at risk of low turnout in the 4 November 2026 local elections, how much of that is a registration gap versus a turnout gap, and where does a young voters' roll overlap with historically low turnout?*

**The story in four beats. The dashboard should tell it in this order:**
1. **The surge:** Mpumalanga's voters' roll grew by about 267,000 since 2021 (1.90 m to 2.17 m), but on current patterns that becomes only about 45,000 more ballots (range from 77,000 fewer to 149,000 more). The 2026 turnout forecast is **39.6%** (range 33.8% to 44.2%; 2021 was 42.8%, the lowest on record).
2. **The model's key idea:** we cannot predict the province-wide mood (2021 fell 13.6 points across the whole province), but we can predict **where** turnout will be lowest. The forecast has two steps: a province-wide level (a scenario) plus each voting district's local position (tested on three past elections, about 1.4 to 2.5 points off per municipality).
3. **Where it hurts:** 357 at-risk voting districts hold about 463,000 registered voters, concentrated in Emalahleni, Govan Mbeki, City of Mbombela and Bushbuckridge. The priority list's top 5 are Govan Mbeki, Msukaligwa, Emalahleni, Dr JS Moroka and Thembisile Hani.
4. **What to do about it:** a planner that turns the forecast into a deployment of voter-education teams, and a replay of past elections that shows why the model can be trusted.

**The one moment judges must remember:** dragging the national-mood slider and watching the map and counts change. At 34% province-wide turnout, 68 voting districts fall below 25% turnout; at 44%, only 2. Everything in the design should make that moment feel responsive, clear and a little bit dramatic.

**Users:**
- Judges (data-science literate, time-poor, watching a video and possibly opening the live link on a phone via a QR code).
- IEC and civil-society planners (want lists and downloads).
- Journalists (want the headline and the map).

**Tone:** a serious public-interest data product. Think the data desks of the Financial Times, The Economist, the Pudding or Our World in Data. Editorial, confident, restrained; not a SaaS admin panel and not a crypto dashboard.

---

## 2. Visual direction

### 2.1 Concept
**"Civic editorial."** A clean white-paper surface, strong typography, one accent colour, maps and charts that carry the colour. Most of the screen is quiet; colour appears only where it means something: data, the one primary action, the risk signal.

Mood words: *calm, precise, trustworthy, South African, human, editorial, spacious.*
Avoid: *neon, gradient-heavy, glassy, gamer, corporate-stock, cute.*

### 2.2 The "doesn't look vibecoded" checklist (things to avoid)
- Default Streamlit look: the red primary colour, default title sizes, the "Made with Streamlit" feel, the deploy button and hamburger menu visible in the demo.
- Emoji used as icons (🗳️📊🔥). Use a consistent icon set (see §11) or none.
- Purple/blue gradient hero banners, glassmorphism, neumorphism, glow effects, animated gradients.
- Rainbow or jet colour maps. Every scale here is single-hue sequential or two-hue diverging with a gray middle.
- A card around everything, heavy drop shadows, borders on every block, inconsistent corner radii.
- Centred body text; walls of bold text; more than two font families; more than three weights.
- Generic stock imagery (ballot boxes with ticks, hands holding flags, people queueing). If there is imagery, it is custom and abstract (§11).
- Lorem ipsum, placeholder labels, "Chart 1", unlabelled axes, raw column names (`vd_MAE_pp`) shown to users.
- Numbers with inconsistent formatting (see §4.4).
- Tooltips that dump every field.

### 2.3 Design tokens

Define these once, in `.streamlit/config.toml` `[theme]` where Streamlit supports it and in one small CSS block (and a Python `TOKENS` dict for charts) for the rest. **The chart and map colours must match the notebook figures** in `derived/figures/`, because the same visuals appear in the slides. Keep the data palette exactly:

| Token | Light | Dark | Use |
|---|---|---|---|
| `surface` | `#fcfcfb` | `#1a1a19` | page / chart background |
| `surface-raised` | `#ffffff` | `#232321` | cards, the map panel |
| `page-plane` | `#f5f4f0` | `#0f0f0e` | subtle section bands |
| `ink` | `#0b0b0b` | `#ffffff` | primary text |
| `ink-2` | `#52514e` | `#c3c2b7` | secondary text, axis labels |
| `muted` | `#898781` | `#8f8d86` | captions, reference marks |
| `grid` | `#e1e0d9` | `#34332f` | hairlines, gridlines, dividers |
| `series-1` (blue) | `#2a78d6` | `#3987e5` | primary data colour; "above province"; 2026 |
| `series-2` (orange) | `#eb6834` | `#f07a4a` | priority / attention scales; reference lines |
| `negative` (red) | `#e34948` | `#e66767` | "below province" pole of the diverging scale |
| `diverging-mid` | `#f0efec` | `#383835` | neutral midpoint (never a hue) |
| `reference` (gray) | `#898781` | `#8f8d86` | 2021 actual, baselines |

- **Diverging (local position, turnout vs mood):** `#e34948` → `#f0a0a0` → `#f0efec` → `#86b6ef` → `#2a78d6`. Symmetric around 0 (or around the chosen mood level).
- **Sequential orange (priority):** `#fde7da` → `#f5a877` → `#eb6834` → `#a8431b`.
- **Sequential blue (magnitudes such as voters):** `#cde2fb` → `#86b6ef` → `#2a78d6` → `#104281`.
- **Primary action / brand accent:** use `series-1` blue for the one primary interactive element per screen (the mood slider thumb and track fill, selected tabs, primary buttons). Do not introduce another brand colour.
- **Status colours** (only if you need success/warning messages): good `#0ca30c`, warning `#fab219`, critical `#d03b3b`. Always with an icon and a label, never colour alone.

**Radius:** 10px for cards and panels, 8px for inputs and buttons, 999px for pills and chips. Pick these and use them everywhere.
**Elevation:** at most one soft shadow level (`0 1px 2px rgba(0,0,0,.04), 0 4px 16px rgba(0,0,0,.04)`) for raised panels. Most separation comes from whitespace and hairlines.
**Spacing scale:** 4, 8, 12, 16, 24, 32, 48, 64 px. Section gaps 48 to 64 px; within a card 16 to 24 px.
**Grid:** content max-width about 1280 px, centred, with 32 px side gutters on desktop and 16 px on mobile. Use `layout='wide'` but constrain the content width with CSS so lines of text never run the full width of a 1920 px screen (max ~70 characters per line for prose).

### 2.4 Typography
- **Two families at most.** Recommended:
  - **Headings:** a characterful but serious sans or serif. Good choices: *Fraunces* (editorial serif, use at 600) or *Source Serif 4*.
  - **Everything else:** *Inter* (or *IBM Plex Sans*). Numbers in tables use tabular figures (`font-variant-numeric: tabular-nums`). Hero numbers use proportional figures.
- Load them through Streamlit's theme font configuration if 1.64 supports custom font faces (check `streamlit config show` for `theme.fontFaces` / `theme.font` / `theme.headingFont`). Otherwise use one `<style>@import</style>` block. Provide the system fallback stack. If fonts fail to load (offline recording), the layout must still look right with fallbacks.
- **Type scale** (desktop; scale down about 15% on mobile):
  - Hero number: 56/60, 600, proportional figures
  - Page title (H1): 36/44, heading family 600
  - Section title (H2): 24/32, heading family 600
  - Card title (H3): 17/24, sans 600
  - Body: 16/26, sans 400
  - Secondary / caption: 13/20, sans 400, `ink-2` or `muted`
  - Table: 14/20, tabular figures
  - Axis labels: 12, `ink-2`; tick labels 11, `muted`
- Sentence case everywhere (not Title Case). South African / British spelling: *colour, organisation, programme, centre*.

---

## 3. Information architecture and layout

### 3.1 Structure
Keep the five areas; you may switch from `st.tabs` to multipage navigation (`st.navigation` + `st.Page`) if 1.64 supports it well, because pages give deep links and cleaner code. If you do, keep the shared mood value in `st.session_state['province_level']` and make it survive page changes.

1. **Story** (landing)
2. **Map & mood** (the centrepiece)
3. **Municipality** (drill-down)
4. **IEC planner**
5. **Can you trust it?** (backtest replay)
6. **New: How it works** (method, limitations, sources; see §10)

Suggested code organisation (optional but encouraged):
```
dashboard/
  app.py              # page config, theme/CSS injection, navigation, header/footer
  data.py             # unchanged logic + new helpers
  ui/
    theme.py          # TOKENS dict, CSS string, Altair theme registration
    components.py     # kpi_tile(), section_header(), legend(), chip(), callout(), empty_state()
    charts.py         # every Altair chart as a function
    maps.py           # pydeck map builder + HTML legend
  pages/ or views/    # one module per area
  assets/             # logo, icons, images (see §11)
.streamlit/config.toml
```
Register one **Altair theme** (`alt.theme.register(...)` / `alt.themes.register` depending on the Altair 6 API; check it) so every chart gets the fonts, colours, gridlines and axis styles from the tokens automatically.

### 3.2 Global chrome
- **Header bar (every page):** a small custom logo mark (§11) + product name "**Turnout 2026 · Mpumalanga**" + a quiet descriptor "Forecast and planning tool · DIRISA SDC 2026". On the right, a **data-freshness badge**: "Voters' roll as of 23 Sep 2026 · Results 2000-2021". Keep it one line, about 56 px tall, with a hairline bottom border. No logos of real organisations.
- **Navigation:** horizontal, under the header, text tabs with a 2 px blue underline for the active tab (not pill buttons, not emoji). On mobile it scrolls horizontally.
- **Hide Streamlit chrome for recording:** set `client.toolbarMode = "viewer"` (or the 1.64 equivalent) and hide the deploy button, the running-man status and "Made with Streamlit" footer via config/CSS, so the video looks like a product.
- **Footer (every page):** sources in one or two lines (IEC results and registration; Stats SA Census 2022; Auditor-General via National Treasury Municipal Money; Municipal Demarcation Board boundaries via geoBoundaries, CC BY 3.0 IGO), the team name placeholder `{TEAM NAME}`, and a link "How it works". Small, `muted`.
- **Deep links:** support `?mood=34&muni=MP312&tab=map`-style query parameters (`st.query_params`) so a QR code on the final slide can open a specific view. Parse defensively (ignore invalid values). Update the URL when the user changes the mood or municipality, if that does not cause flicker.

### 3.3 Responsive targets
- **1920×1080** (video recording; the most important). Everything in a view fits without scrolling where possible: especially the Map & mood page. Slider, KPIs and map must be visible together.
- **1366×768** (judges' laptops).
- **390×844** (a phone opening the QR code). Columns stack; the map stays usable (at least 320 px tall); tables scroll horizontally inside their container; no horizontal page scroll.

---

## 4. Shared components (build once, reuse everywhere)

### 4.1 KPI tile
Replace raw `st.metric` styling with a consistent tile: label (13 px, `ink-2`, sentence case) → value (28 to 40 px, 600) → context line (13 px): delta with a tiny up/down glyph and colour **only when direction has meaning** (e.g. ballots vs 2021), else neutral `muted` text (e.g. "of 1,785 districts"). Optional 24 px sparkline or micro-bar where it adds meaning. Tiles in a row share equal height. On the Story page, use the larger hero variant.
- Colour logic: more ballots = neutral/positive blue, lower turnout = the text says "−3.2 pts vs 2021" in `ink-2` with a down glyph; do **not** paint drops in alarm red everywhere. Red is reserved for the data scale.

### 4.2 Section header
Eyebrow (12 px uppercase letter-spaced `muted`, e.g. "STEP 2 · WHERE") + H2 + one-sentence dek in `ink-2`. Used at the top of every page and major section.

### 4.3 Callout / insight card
For the key findings: a 3 px left rule in `series-1`, title, one or two sentences, an optional small "Why this matters" line. Variants: `insight` (blue rule), `caution` (gray rule + info icon: for limitations), `trap` (orange rule; for the regression-to-the-mean finding).

### 4.4 Number formatting (write one `fmt` helper module and use it everywhere)
- Counts: thousands separators with commas: `463,491`. Big counts in text: `2.17 m`, `267,000` (round to the nearest thousand in prose; keep exact in tables).
- Percentages: one decimal for turnout (`39.6%`), none for shares in prose (`24%`).
- Percentage-point changes: signed, one decimal, the word "pts": `−3.2 pts`, `+1.4 pts`. Use a true minus sign (−) not a hyphen.
- Ranges: `33.8–44.2%` with an en dash.
- Never show more than one decimal in the UI. Never show raw floats like `39.47219`.
- Municipality labels: `Emalahleni (MP312)` in prose and selectors; code-first `MP312 Emalahleni` only in dense tables.

### 4.5 Legends
Pydeck has no legend: build an HTML legend component (continuous gradient bar with 3 to 5 labelled ticks, a title, and a note such as "Red = below the province, blue = above"). Same component styling for Altair legends (configure via theme).

### 4.6 Chips and badges
Small pills for categorical facts: venue type ("Tent", "Farm", "School"…), main gap ("Registration gap" / "Turnout gap"), profile name, "At-risk". Neutral fill `page-plane`, text `ink-2`, 999 px radius, 12 px text, optional 14 px icon.

### 4.7 Tables
Use `st.dataframe` with `column_config` for every table: human labels, formats (`%.1f%%`, thousands), `ProgressColumn` for turnout and shares (0 to 100, blue), `NumberColumn` with signed format for local position, text columns for names, venue shown with its icon or label. Hide the index. Fixed sensible column widths. Default sort meaningful (most at risk first). Row height comfortable. Max visible height about 420 px with internal scroll.

### 4.8 Buttons and downloads
One primary style (blue fill, white text, 8 px radius) for the main action on a page; secondary style (outline) for downloads and resets. Download labels say what you get: "Download at-risk districts (CSV, 43 rows)". File names include the municipality code and the date: `at_risk_districts_MP312_2026-09-27.csv`.

### 4.9 Loading, empty and error states
- **Missing `derived/` files:** a friendly full-page state with an illustration (§11) explaining "Run model.ipynb first (Restart → Run All). The dashboard reads the results it saves in derived/." Do not show a Python traceback.
- **Empty table:** e.g. Victor Khanye has only 1 at-risk district; a municipality with none shows "No at-risk districts here. All of this municipality's voting districts are above the lowest fifth." with a small illustration.
- **Loading:** the data is cached and fast; avoid spinners. If one is unavoidable, use a skeleton block in `page-plane`, not the default running icon.

### 4.10 Tooltips
Short, formatted, 2 to 4 lines: title in 600, then label: value pairs. Same style for pydeck (HTML tooltip with inline style) and Altair (configure via theme).

---

## 5. Page 1: Story (landing)

**Purpose:** in 10 seconds a judge understands the problem, the headline and the model's idea, and wants to touch the slider.

Layout (top to bottom):
1. **Hero band.** Eyebrow "4 NOVEMBER 2026 LOCAL ELECTIONS · MPUMALANGA". H1: **"A record voters' roll. Will it turn into votes?"** Dek (one sentence): "Mpumalanga's roll grew by 267,000 since 2021. On current patterns that adds only about 45,000 ballots." Optional abstract hero artwork on the right (§11), subdued, never behind text.
2. **Four hero KPI tiles:** Voters on the roll 2026 (2.17 m, +267,480 since 2021) · Expected ballots 2026 (0.86 m, +45,330, range shown in the context line) · Turnout forecast 2026 (39.6%, range 33.8–44.2%, 2021: 42.8%) · At-risk voting districts (357, 463,491 registered voters). All from data.
3. **The headline chart:** a clean grouped bar chart. Registered voters vs ballots, 2021 (reference gray) vs 2026 (blue), with the forecast range drawn as a thin error bar on the 2026 ballots bar, and two direct annotations: "+267k voters" and "+45k ballots (range −77k to +149k)". Match `derived/figures/fig14_headline.png` in meaning, but make it native, crisp and responsive.
4. **Three insight cards** in a row:
   - "We can't predict the mood. We can predict where." (two-step idea; 2021 miss 11.7 → 2.3 points).
   - "357 districts, 463,000 voters." (where the risk concentrates; name the top 3 municipalities).
   - "The surge trap." (fast-growing rolls *look* like they dilute turnout; it is regression to the mean; after adjusting, growth goes with slightly higher turnout).
5. **Primary call to action:** a button "Try the national mood →" that goes to Map & mood.
6. Footer.

---

## 6. Page 2: Map & mood (the centrepiece; spend the most care here)

**Purpose:** the judge drags one slider and sees where low turnout lands.

### 6.1 Layout at 1920×1080 (no scrolling for the core)
Two columns: **left control rail** (~360 px) and **map** (the rest). Under both, a full-width municipality table (scrolling is fine for it).

**Left control rail, top to bottom:**
1. Section header: eyebrow "STEP 1 · CHOOSE THE MOOD", title "You choose the national mood. The model shows where it hurts."
2. **The mood slider** (the hero control):
   - Range 30–50%, step 0.5, key `province_level`, default = central forecast (from `turnout_model_info.json`, `province_2026_pct.central`, rounded to 0.5).
   - Make it big: a thick track, a large thumb, and the current value shown as a large number above it ("39.5%").
   - **Reference ticks under the track**, labelled: "Low scenario 33.8%", "Central 39.5%", "2021 actual 42.8%", "High scenario 44.2%". If a native slider cannot show these, render an SVG/HTML scale directly under it that lines up exactly with the track (compute positions from the min/max), plus three quick-set buttons: **Low · Central · High** (and "2021 level").
   - A **live sentence** under the slider that changes with the value: "At 34.0%, 68 voting districts fall below 25% turnout, with 48,531 registered voters." Write the rules for this sentence in code; it must read naturally at every value.
3. **Threshold control:** "Count a district as low turnout below: 25%" (10–40). Secondary styling (smaller than the mood slider).
4. **Three live KPI tiles** stacked or in a 3-up row: districts below the threshold · registered voters in them · expected ballots (with delta vs 2021).
5. **Map colour switch:** a segmented control (not a radio list): "Turnout at this mood" · "Above / below province" · "Priority".

**Map (right):**
- Pydeck `GeoJsonLayer` of the 17 municipalities (`derived/mpumalanga_municipalities_2016.geojson`).
- Fill from the diverging or sequential scales in §2.3, depending on the switch. For "Turnout at this mood", centre the diverging scale on the slider value and keep the colour limits **fixed** as the slider moves (e.g. ±6 points around the mood), so colour changes mean something. Document the choice in the legend.
- 1.5 px white (surface) boundaries; hover highlight (thicker outline in `ink`, no colour change); tooltip per §4.10: name, turnout at this mood, local position, districts below threshold, priority rank.
- **Labels:** a `TextLayer` with short municipality names at label points (use the centroids already computed in the notebook's logic, or compute in `data.py`). 11–12 px, `ink` with a 2 px surface-coloured halo for legibility. Avoid collisions: nudge Dr JS Moroka / Thembisile Hani and Victor Khanye / Emalahleni.
- **Basemap:** either none (clean, like the notebook figure; recommended for reliability) or a very light Carto basemap without a token. If a basemap is used, it must be desaturated and must not compete with the data. The view must fit Mpumalanga's bounds at 1920×1080 and on mobile. Disable map rotation/pitch.
- **Legend** (§4.5) overlaid in a corner of the map panel, not below the fold.
- **Motion:** when the slider moves, colours should update without the whole page jumping. Keep layout heights fixed so nothing reflows. If pydeck supports `transitions` on `get_fill_color` in this version, use a short (~300 ms) colour transition; otherwise skip animation rather than hack it.

**Under the map:** full-width table "Municipalities at this mood": municipality · turnout at this mood (progress bar) · above/below province (signed pts) · districts below threshold · registered voters in them · priority rank. Default sort by turnout ascending. Clicking a row (if `st.dataframe` selection is available in 1.64) opens that municipality in the Municipality page, or offers an "Open" link.

**Explain the damping:** a small caption or info popover near the map: "Districts that have swung harder than the province in past elections move further here. Their sensitivity is based on 3–5 past elections, so it is damped halfway towards the province and capped at 0.5–1.5×."

---

## 7. Page 3: Municipality

**Purpose:** everything about one municipality on one screen, for a planner or a journalist.

1. **Selector:** searchable select, options sorted by risk (lowest local position first) and showing the name, code and a small risk hint: "Emalahleni (MP312) · #3 priority". Also settable from the URL (`?muni=MP312`) and from the map.
2. **Header card:** municipality name (H1 size), code, district municipality if you can derive it (optional), profile chip (from `participation_profiles.csv` / `priority_list.csv` `profile`), main-gap chip ("Registration gap" or "Turnout gap").
3. **Four KPI tiles:** 2026 turnout forecast (+ range) · local position (signed, "vs Mpumalanga") · priority rank (# of 17, score) · youth registration gap (pts, with 18–29 vs 30+ rates).
4. **Two charts side by side:**
   - **Turnout history and forecast:** line 2000–2021 (blue), Mpumalanga's line in `reference` gray for comparison (compute the province series from `features_municipality.csv` weighted by registered voters, or from backtest files; document it), the 2026 forecast as a hollow blue point with the range as a vertical bar, a subtle "forecast" label, and the 2021 low highlighted. Y from 20% to 70%, fixed.
   - **Where participation was lost in 2021:** a single 100% stacked horizontal bar (Voted · Registered but didn't vote · Not registered) out of 100 eligible citizens, with the segments labelled directly inside when wide enough (outside otherwise), plus the 2026 projection as a second thin bar for comparison if the data supports it (`voted_per_100_2026_projection`).
5. **Context row:** chips or a compact fact list: audit score (last 3 years, of 4) · registration rate 2026 · roll growth since 2021 · youth share of roll · 2 or 3 Census facts (internet access, adult hunger, urban share) with the note "context, not cause".
6. **At-risk voting districts:** table per §4.7 with: district code · venue (icon + label) · registered voters · 2021 turnout · predicted local position · predicted 2026 turnout. Download button (§4.8). Empty state (§4.9).
7. A short, generated-from-data paragraph: "Emalahleni is predicted 2.0 points below the province. 43 of its voting districts are among the province's lowest fifth, holding 84,310 voters (45% of its roll)." Build it from data; test it on all 17 municipalities.

---

## 8. Page 4: IEC planner

**Purpose:** turn the forecast into a decision.

### 8.1 Team allocation
- Section header: eyebrow "STEP 3 · ACT", title "You have voter-education teams. Where should they go?"
- **Teams slider** (5–357, step 5; default 50) with a live sentence: "50 teams reach 139,000 registered voters, 30% of everyone in at-risk districts."
- **KPI tiles:** voters reached · share of all at-risk voters · municipalities covered · average predicted turnout in the chosen districts.
- **Coverage curve (new, strong visual):** an Altair line showing "share of at-risk voters reached" (y) against "number of teams" (x, 0–357), with the current slider value marked by a vertical rule and a dot. It shows diminishing returns at a glance. Compute it in `data.py` from `plan_teams` (cumulative sum of `registered_voters` over the at-risk districts sorted by size).
- **Allocation by municipality:** horizontal bars (teams per municipality) sorted descending, blue, direct labels.
- **The team plan table** + download.
- Note the planning rule in plain words: "One team per district, largest at-risk districts first. At-risk = the lowest fifth of districts by predicted local position."

### 8.2 Priority weights
- Section header: "Re-weight the priority list".
- Four weight sliders in a 2×2 or 4-up grid with clear labels and a one-line explanation each; a live note showing the weights as shares of 100% (they are normalised); a **Reset to team weights** button (35 / 25 / 20 / 20).
- **Ranking table** with rank now, the default rank, and a movement column (▲2 / ▼1 / –) in `ink-2`; top 5 highlighted by a subtle row tint or a bold rank.
- Optional: a small slope chart (default rank → current rank) for the top 10. Only if it stays readable.

---

## 9. Page 5: Can you trust it?

**Purpose:** answer "why believe this?" visually and briefly.

1. Section header: eyebrow "STEP 4 · CHECK", title "Replay past elections. Each model only saw earlier ones."
2. **Year control:** segmented 2011 · 2016 · 2021 (default 2021).
3. **Scatter:** actual (x) vs predicted (y) turnout per municipality, one colour per approach, using the categorical order blue (Two-step forecast), orange (One-step model, first version), gray (Same as last election). The diagonal line is labelled "perfect prediction". Direct-label the approaches (legend always present too). Tooltips with the municipality and both values. Equal axes, fixed domain per year.
4. **Scorecard:** a compact table with human column names: "Average miss per municipality (pts)", "Bias (pts)", "Ranking quality (0–1)", "Lowest 5 found (of 5)". Highlight the best value per column.
5. **The two-step explainer (important for judges):** a small diagram built in code (Altair or inline SVG), not a generated image, showing turnout = province-wide level (uncertain, a scenario) + local position (tested), with the 2021 numbers: one-step miss 11.7 points vs two-step 2.3.
6. **"What we tested"** expander: local-position models and feature tests, with readable labels and a sentence explaining the rule ("a feature group was kept only if it lowered the district error without raising the municipal error").

## 10. Page 6: How it works (new)

A calm long-read page with a narrow text column (~70 characters):
1. **The question and who it is for.**
2. **The data** (the sources, with dates and links as text; boundary licence CC BY 3.0 IGO).
3. **The two-step model** (plain language + the explainer diagram reused).
4. **What the features are** (turnout history, party competition, swing sensitivity, station venue, registration surge), one line each.
5. **Limitations** (from the README; keep them honest and visible): the province-wide level is the uncertain part; only three backtests; Census is municipality-level only; station names only from 2011; swing sensitivity damped for the slider; association is not cause; 2026 eligible counts are lower bounds.
6. **How to use the downloads.**

---

## 11. Custom imagery and icons (use your image-generation and drawing abilities)

The goal is a small, coherent set of custom assets that make the product feel designed. **Numbers, labels and maps are never baked into images.** They are always rendered by code.

### 11.1 Asset list (store in `dashboard/assets/`)

| Asset | Format / size | Where | Brief |
|---|---|---|---|
| **Logo mark** | SVG, 32×32 and 64×64 (also `favicon.png` 64×64) | header, favicon (`page_icon`) | A simple geometric mark: an abstract ballot-slot / map-contour fusion, one or two shapes, `series-1` blue on transparent, works at 16 px. Hand-write the SVG. No flags, no ticks, no party symbols. |
| **Wordmark** | text, not an image | header | "Turnout 2026 · Mpumalanga" set in the heading font. |
| **Hero artwork** | generated PNG/WebP, 1600×900 (2×), under 300 KB | Story page, right side | Abstract, calm, editorial illustration: layered topographic contour lines suggesting Mpumalanga's escarpment and lowveld, with a subtle grid of small dots evoking voting districts, some dots slightly brighter. Palette strictly from the tokens (surface off-white, blues, one orange accent, grays). Flat vector style, generous negative space, no text, no people, no flags, no ballot boxes, no party colours. Must still look right when cropped on mobile (keep the focal area in the centre-right). |
| **Venue icons** | SVG, 16×16 and 20×20, 1.5 px stroke, round caps | tables, chips | tent, farm (barn/fence), traditional authority (a meeting-tree or hut roofline), church, school, hall (building with columns), other (dot). One consistent line style, `ink-2`. Hand-draw as SVG paths, or use one consistent open-licence icon set (e.g. Lucide or Tabler, MIT) and credit it in the footer. Do not mix icon families. |
| **Section icons** | SVG, 20×20 | page headers, nav (optional) | Story (open book / spark line), Map (map pin), Municipality (building), Planner (route / people), Trust (check-in-circle), How it works (info). Same set as the venue icons. |
| **Empty-state illustration** | generated PNG/WebP 480×320, or SVG | missing data, empty tables | A minimal line illustration in the token palette, e.g. an empty clipboard over contour lines. No text in the image. |
| **Social preview (Open Graph) image** | generated PNG 1200×630 | used when the live link is shared | Background: the hero artwork style. The title text **"A record voters' roll. Will it turn into votes?"** and "Mpumalanga 2026 turnout forecast" must be typeset by you in code/SVG (the headline font) over the generated background, not generated as image text. |
| **QR-code panel** | SVG/PNG generated by code at runtime or build time | the How it works page + for the final slide | A QR code for the live URL (use a pure-Python generator only if one is already available; otherwise leave a clearly marked placeholder and a note on how to generate it once the URL exists). Framed with the logo mark and the URL in text. |

### 11.2 Rules for generated images
- Style keywords for every generated image: *flat vector, editorial, minimal, off-white background #fcfcfb, restrained blue palette (#2a78d6, #86b6ef, #cde2fb), single orange accent (#eb6834), fine linework, generous negative space, no text, no logos, no people, no flags.*
- Generate two or three variations and pick the calmest. Check it at 390 px width. Compress (WebP where possible). Give every image meaningful `alt` text.
- If image generation is unavailable in your environment, fall back to hand-written SVG (topographic contour lines can be generated procedurally with a few layered paths) rather than skipping the asset.
- Record every asset's origin (generated by the team / icon set + licence) in `dashboard/assets/README.md`.

---

## 12. Charts: specifications for every chart (Altair)

Apply to all charts through the registered Altair theme:
- Background `surface`; no chart border; gridlines horizontal only, 1 px `grid`; no vertical grid; axis domain lines off except the baseline; ticks off.
- Axis titles 12 px `ink-2`, labels 11 px `muted`; titles in sentence case; units in the title ("Turnout (%)").
- Marks: bars with 2 px surface gaps between adjacent bars and 3–4 px rounded data ends (`cornerRadiusEnd`) anchored at the baseline; lines 2 px; points ≥ 8 px with a 2 px surface stroke where they overlap lines.
- Direct labels selectively (the endpoint, the extreme, the one that matters), never a value on every mark.
- A legend whenever there are 2 or more series; ≤ 4 series also direct-labelled.
- Tooltips on every mark, formatted (§4.4).
- Heights fixed per chart so the page does not jump when data changes.
- Charts: headline grouped bars (Story), coverage curve and allocation bars (Planner), history + forecast (Municipality), participation stacked bar (Municipality), backtest scatter (Trust), two-step explainer (Trust / How it works). Specifications for each are in the page sections above.

---

## 13. Dark mode
Support both light and dark via Streamlit's theme mechanism if 1.64 supports a user-selectable theme; otherwise ship light as default and make sure nothing breaks if the viewer's Streamlit is set to dark. Dark mode uses the dark column of §2.3; the diverging midpoint becomes `#383835`; map boundaries become the dark surface; verify text contrast (≥ 4.5:1 for body text, ≥ 3:1 for large numbers and chart marks against their background).

## 14. Accessibility
- Colour is never the only carrier of meaning: the map has a legend, tooltips and a table; the backtest scatter has a legend and direct labels; deltas have glyphs and words.
- Body text ≥ 4.5:1 contrast; interactive elements ≥ 3:1.
- Every control has a visible text label (not placeholder-only). Sliders show their current value in text.
- Keyboard: tab order follows the visual order; focus rings visible (2 px blue outline).
- Images have alt text; decorative images are marked decorative.
- Motion: no auto-playing animation; respect `prefers-reduced-motion`.

## 15. Copy (microcopy guide)
- Plain English, short sentences, active voice, no jargon in the UI. Say "points" not "pp"; "local position" once explained; "voting district" (not "VD") in the UI.
- Explain every metric the first time it appears (a small ⓘ popover or caption).
- Always show the basis of a number: "2021 roll", "as of 23 Sep 2026", "forecast", "scenario".
- Suggested key strings (keep or improve, but keep the meaning):
  - Mood slider label: "Mpumalanga turnout in 2026"
  - Mood helper: "The province-wide level is the uncertain part of the forecast. Try the scenarios."
  - At-risk definition: "At-risk districts are the fifth of Mpumalanga's voting districts with the lowest predicted turnout relative to the province."
  - Trust page dek: "Each model was trained only on elections before the one it predicts, then compared with what really happened."

## 16. Performance and robustness
- `@st.cache_data` for all loading (already there); precompute anything static (label points, legend gradients, the coverage curve) once.
- The mood slider must feel instant (< 200 ms re-run on a laptop). Profile if needed; avoid `copy.deepcopy` of the GeoJSON on every run if it becomes slow (build fill colours as a separate list and inject).
- No network dependency at runtime other than optional fonts and optional basemap tiles; the app must still work (with fallbacks) offline during recording.
- No warnings in the terminal (the `use_container_width` deprecation is already fixed; keep it that way).

## 17. Acceptance tests (must pass before you finish)

1. **Automated widget test**, run from the project root:
```python
from streamlit.testing.v1 import AppTest
at = AppTest.from_file('dashboard/app.py', default_timeout=120).run()
assert not at.exception
at.slider(key='province_level').set_value(34.0).run(); assert not at.exception
at.slider(key='province_level').set_value(44.0).run(); assert not at.exception
```
If you move to multipage navigation, adapt the test to open each page and exercise its controls (mood slider, threshold, colour switch, municipality selector for MP312, MP311 and MP325, teams slider, a weight slider, the reset button, each backtest year) and assert no exceptions. Add the test as `dashboard/test_app.py`.

2. **Numbers match the notebook** (with the default settings):
   - Roll 2026: **2,169,700** (2.17 m); roll 2021: **1,902,220**; ballots 2021: **814,739**; expected ballots 2026: **860,069** (headline from `turnout_model_info.json`).
   - Turnout forecast 2026: **39.6%**, range **33.8–44.2%**; 2021 actual **42.8%**.
   - At-risk districts: **357**, holding **527,417** voters on the estimated 2026 roll (463,491 on the 2021 roll).
   - Simulation: **72%** chance of a record-low turnout (cautious 65%); 10,000 simulations; calibration step used.
   - Mood 34%: **68** districts below 25% (**48,531** voters, est. 2026 roll); central (39.5%): **30** (**13,308**); mood 44%: **2** (**537**).
   - Planner: 50 teams reach **159,306** voters (9 municipalities).
   - Planner: 100 teams reach **270,891** voters (10 municipalities).
   - Priority top 5: Govan Mbeki, Msukaligwa, Emalahleni, Dr JS Moroka, Thembisile Hani.
3. **Visual QA:** take screenshots at 1920×1080, 1366×768 and 390×844 of every page, in light (and dark if supported), and check them for label collisions, clipped text, overflow, horizontal scroll, colour-scale correctness (red = below), alignment and consistent spacing. Fix what you find, re-screenshot, and include the final screenshots in `dashboard/screenshots/` (PNG, compressed) for the team's slides.
4. **Demo run-through:** the video path works without a single glitch: Story → "Try the national mood" → drag to 34% → drag to 44% → back to central → switch to Priority colouring → open Emalahleni → download its districts → Planner with 100 teams → Trust, 2021 → How it works.
5. **Fresh clone:** `pip install -r dashboard/requirements.txt` in a new environment + `streamlit run dashboard/app.py` works without running the notebook (because `derived/` is committed).

## 18. Process (how to work)

1. **Plan first.** Write a short plan in your first message: the files you will create, the order, and any Streamlit 1.64 capability you verified or found missing (with the fallback you will use).
2. **Build the foundation:** tokens, config.toml, CSS, Altair theme, `fmt` helpers, shared components, header/footer, navigation. Screenshot.
3. **Map & mood** (the centrepiece) to finished quality. Screenshot at all three sizes.
4. **Story**, then **Municipality**, then **Planner**, then **Trust**, then **How it works**. Screenshot each.
5. **Assets** (§11) as soon as the layout is stable.
6. **Full QA** (§17), fix, re-test.
7. **Summary:** what you built, screenshots, anything you could not do and why, any new dependency, and the exact commands to run the app.

Keep the code readable for students who will explain it in a video: short functions, clear names, a docstring on every module and component, comments that say *why*, not *what*.

**Quality bar:** when a judge opens the link on a phone or sees the video, the dashboard should feel like it was designed by a small professional data-journalism team, with every number formatted and explained, every colour meaningful, and every screen answering one question.
