const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, BorderStyle, ShadingType,
  PageBreak, Footer, Header, SectionType, VerticalAlign, LevelFormat,
  TabStopType, TabStopPosition
} = require('docx');
const fs = require('fs');

const OUT = 'DIRISA_2026_Implementation_Plan_v2.docx';
const navy = '16324F', teal = '0F766E', sky = 'E8F1F5', pale = 'F5F8FA', gold = 'B7791F', red = '9B2C2C', gray = '52606D', light = 'D9E2EC';

const borders = { top:{style:BorderStyle.SINGLE,size:4,color:light}, bottom:{style:BorderStyle.SINGLE,size:4,color:light}, left:{style:BorderStyle.SINGLE,size:4,color:light}, right:{style:BorderStyle.SINGLE,size:4,color:light}, insideHorizontal:{style:BorderStyle.SINGLE,size:4,color:light}, insideVertical:{style:BorderStyle.SINGLE,size:4,color:light} };
function cell(text, opts={}) { return new TableCell({ width: opts.width ? {size:opts.width,type:WidthType.DXA}:undefined, shading: opts.shading ? {fill:opts.shading,type:ShadingType.CLEAR}:undefined, margins:{top:100,bottom:100,left:130,right:130}, verticalAlign:VerticalAlign.CENTER, children:[new Paragraph({spacing:{after:0}, children:[new TextRun({text:String(text),bold:!!opts.bold,color:opts.color||'1F2933',size:opts.size||19,font:'Aptos'})]})]}); }
function table(headers, rows, widths) {
  const all = [new TableRow({tableHeader:true, children:headers.map((h,i)=>cell(h,{bold:true,color:'FFFFFF',shading:navy,width:widths&&widths[i]}))})];
  for (const row of rows) all.push(new TableRow({children:row.map((v,i)=>cell(v,{width:widths&&widths[i]}))}));
  return new Table({width:{size:9360,type:WidthType.DXA}, borders, rows:all, columnWidths:widths});
}
function p(text='', opts={}) { const runs=[]; if (Array.isArray(text)) text.forEach(x=>runs.push(typeof x==='string'?new TextRun({text:x,font:'Aptos',size:opts.size||20,color:opts.color||'1F2933'}):new TextRun({...x,font:'Aptos',size:x.size||opts.size||20}))); else runs.push(new TextRun({text, font:'Aptos', size:opts.size||20, color:opts.color||'1F2933', bold:opts.bold||false, italics:opts.italics||false})); return new Paragraph({style:opts.style, alignment:opts.align, spacing:{before:opts.before||0,after:opts.after===undefined?120:opts.after,line:opts.line||276}, keepNext:opts.keepNext, children:runs}); }
function bullet(text, level=0) { return new Paragraph({style:'List Bullet', numbering:{reference:'bullets',level}, spacing:{after:70,line:260}, children:[new TextRun({text,font:'Aptos',size:19,color:'1F2933'})]}); }
function number(text) { return new Paragraph({style:'List Number', numbering:{reference:'numbers',level:0}, spacing:{after:70,line:260}, children:[new TextRun({text,font:'Aptos',size:19,color:'1F2933'})]}); }
function h(text, level=1) { return new Paragraph({text, heading:level===1?HeadingLevel.HEADING_1:level===2?HeadingLevel.HEADING_2:HeadingLevel.HEADING_3, keepNext:true, spacing:{before:level===1?260:180,after:90},}); }
function callout(label, text, color=teal) { return new Table({width:{size:9360,type:WidthType.DXA},borders:{top:{style:BorderStyle.SINGLE,size:8,color},bottom:{style:BorderStyle.SINGLE,size:8,color},left:{style:BorderStyle.SINGLE,size:24,color},right:{style:BorderStyle.SINGLE,size:8,color}},rows:[new TableRow({children:[new TableCell({shading:{fill:pale,type:ShadingType.CLEAR},margins:{top:160,bottom:160,left:220,right:180},children:[new Paragraph({spacing:{after:60},children:[new TextRun({text:label.toUpperCase(),bold:true,color,size:17,font:'Aptos'})]}),new Paragraph({spacing:{after:0},children:[new TextRun({text,font:'Aptos',size:19,color:'1F2933'})]})]})]})]}); }

const doc = new Document({
  creator:'DIRISA 2026 Datathon Team', title:'DIRISA 2026 Data Science Implementation Plan', subject:'SDC qualifier and Day 1 refined problem', language:'en-ZA',
  styles:{default:{document:{run:{font:'Aptos',size:20,color:'1F2933'},paragraph:{spacing:{after:120,line:276}}}}, paragraphStyles:[
    {id:'TitleCustom',name:'Title Custom',basedOn:'Normal',run:{font:'Aptos Display',size:38,bold:true,color:navy},paragraph:{spacing:{after:160,line:320}}},
    {id:'SubtitleCustom',name:'Subtitle Custom',basedOn:'Normal',run:{font:'Aptos',size:22,color:gray},paragraph:{spacing:{after:260,line:300}}},
    {id:'List Bullet',name:'List Bullet',basedOn:'Normal',paragraph:{indent:{left:420,hanging:220},spacing:{after:70,line:260}}},
    {id:'List Number',name:'List Number',basedOn:'Normal',paragraph:{indent:{left:420,hanging:220},spacing:{after:70,line:260}}},
  ]}, numbering:{config:[{reference:'bullets',levels:[{level:0,format:LevelFormat.BULLET,text:'•',alignment:AlignmentType.LEFT,style:{paragraph:{indent:{left:420,hanging:220}},run:{font:'Arial'}}}]},{reference:'numbers',levels:[{level:0,format:LevelFormat.DECIMAL,text:'%1.',alignment:AlignmentType.LEFT,style:{paragraph:{indent:{left:420,hanging:220}}} }]}]},
  sections:[{properties:{page:{margin:{top:900,right:900,bottom:850,left:900}}}, headers:{default:new Header({children:[new Paragraph({alignment:AlignmentType.RIGHT,children:[new TextRun({text:'DIRISA 2026 | Implementation Plan',font:'Aptos',size:15,color:gray})]})]})}, footers:{default:new Footer({children:[new Paragraph({alignment:AlignmentType.CENTER,children:[new TextRun({text:'Working plan - validate against the latest qualifier rules and data dictionary',font:'Aptos',size:14,color:gray})]})]})}, children:[]}]});
const C = doc.documentWrapper.document.body.root;
C.length = 0;

C.push(new Paragraph({}));
C.push(new Paragraph({style:'TitleCustom',children:[new TextRun({text:'DIRISA 2026 Data Science Implementation Plan'})]}));
C.push(new Paragraph({style:'SubtitleCustom',children:[new TextRun({text:'Mpumalanga voter-participation analysis | SDC qualifier context + Day 1 refined problem'})]}));
C.push(new Paragraph({spacing:{after:220},children:[new TextRun({text:'Version 1.0  •  23 September 2026  •  Whole-notebook delivery plan',font:'Aptos',size:17,color:gray})]}));
C.push(callout('Decision in one sentence','Build an auditable municipality-election analytical pipeline first; only then add predictive modelling and an interactive dashboard. The primary deliverable is a defensible answer about registration gaps, turnout gaps and participation profiles - not a high-scoring model by itself.'));
C.push(h('Executive summary',1));
C.push(p('The team’s refined problem is to understand unequal electoral participation in South Africa, with an initial focus on Mpumalanga municipalities, by integrating electoral results, voter registration, demographic, geographic, socioeconomic and digital-registration-related data. The intended outputs are: (1) a clean analytical dataset, (2) evidence on registration versus turnout gaps, (3) municipality participation profiles, (4) a carefully validated predictive or forecasting component, and (5) a decision-oriented dashboard for 2026 election preparation.'));
C.push(p('The implementation should be organised as one reproducible notebook with clear stage boundaries, but the notebook must behave like a pipeline: raw inputs are immutable, transformations are deterministic, intermediate tables have declared grains, and every conclusion is traceable to a quality check, chart or model evaluation.'));
C.push(h('Non-negotiable pushback before modelling',1));
C.push(table(['Issue observed','Why it matters','Required correction'],[
['Baseline CSV is long-format party/ballot data','721,327 rows do not mean 721,327 independent municipality observations. Repeated registration and turnout values can inflate apparent sample size and distort uncertainty.','Aggregate to explicit grains such as municipality-election-ballot and municipality-election before profiling or modelling. Preserve the raw long table only for vote-share analysis.'],
['Scope is not yet aligned','Day 1 states Mpumalanga, while the baseline header says “ALL NINE PROVINCES”. Mixing scopes can produce misleading comparisons and accidental train/test contamination.','Lock the analytical scope in a configuration cell: Mpumalanga for the main answer, all provinces only for robustness/context.'],
['Target is not yet operationalised','“Participation”, “registration” and “digital registration” are different outcomes. A single turnout target cannot answer all three.','Define separate estimands: registration rate/gap, turnout rate/gap, youth registration gap, youth turnout gap, and optional high-gap classification.'],
['Turnout and registration may leak into features','Reported turnout, registered voters and derived turnout are either the target or components of the target. Using them as predictors makes performance meaningless.','Create a feature eligibility table by prediction date. Exclude target components and post-event fields from any forward-looking model.'],
['2026 ground truth may not exist at build time','A 2026 forecast cannot be evaluated against the actual 2026 outcome until the outcome is observed.','Use rolling historical backtesting: train on earlier elections, validate on the next election, and label 2026 results as prospective rather than “validated”.'],
['Supervised learning may be overpromised','There are only a small number of election years and municipalities relative to the row count. Complex models can memorise geography or time.','Use simple baselines first, regularisation, grouped/time-aware splits, uncertainty intervals and a clear “model not useful” exit criterion.'],
['Clustering can create arbitrary stories','Clusters are sensitive to scaling, missingness, feature choice and k. They are descriptive segments, not discovered causal types.','Run stability checks, report sensitivity to k and seeds, and name clusters from measured profiles rather than from model labels.']],[2600,3600,3160]));
C.push(h('1. Objectives, scope and success criteria',1));
C.push(h('1.1 Analytical questions',2));
['Where are registration gaps, turnout gaps and combined participation gaps concentrated?','Are youth gaps different from overall gaps, and do they vary by municipality type, settlement pattern or socioeconomic context?','Does digital registration availability or uptake align with registration levels after accounting for population structure and access-related covariates?','Can historical information produce useful, calibrated municipality-level forecasts or prioritisation scores for the next election?','Which municipality profiles are operationally distinct enough to support targeted interpretation or resource allocation?'].forEach(b=>C.push(bullet(b)));
C.push(h('1.2 Scope rules',2));
C.push(table(['Dimension','Default decision','Guardrail'],[
['Geography','Primary: Mpumalanga municipalities. Secondary: all provinces for descriptive benchmark only.','Every chart and model table carries province and geography scope.'],
['Time','Historical local-government election cycles available in the data.','Do not interpolate a trend as if elections were annual observations.'],
['Unit of analysis','Municipality-election, with ballot-type fields retained where needed.','No model is fit on party rows or station rows unless the question is explicitly station-level.'],
['Audience','Data-science judges and stakeholders planning participation interventions.','Every “insight” states population, period, denominator and uncertainty/limitation.'],
['Success','Credible evidence and useful prioritisation, not maximum leaderboard complexity.','A simpler model wins if it is better calibrated, more transparent and no worse in temporal backtests.']],[2200,3600,3560]));
C.push(h('2. Data inventory and provenance',1));
C.push(p('Create a source registry at the top of the notebook. The qualifier materials point to IEC electoral statistics/results resources and the SDC data portal; the team’s merged file should be treated as a derived product whose lineage must be reconstructed, not as a self-authenticating source.'));
C.push(table(['Source class','Minimum metadata to capture','Validation questions'],[
['IEC election results','URL/file, download date, election year, geography, ballot type, original row count, checksum','Are turnout, registered voters and votes defined consistently across years? Are municipal boundaries comparable?'],
['Voter registration / age','URL/file, reference date, age bands, geography, numerator and denominator','Does “youth” have a fixed age definition? Is the denominator registered voters or eligible population?'],
['Demographic / socioeconomic','Provider, census/survey year, geography, units, boundary version','Are years aligned to elections, or are we silently attributing later data to earlier elections?'],
['Geographic / spatial','Boundary source and version, CRS, municipality code mapping','Do codes and names map one-to-one? Are boundary changes documented?'],
['Digital registration','Definition, channel, date window, coverage and missingness','Does the measure capture access, usage, completed registration or merely availability?'],
['Derived baseline CSV','Transformation version, source files, repair rules, row grain','Can every derived value be traced back to raw fields? What was repaired versus observed?']],[2200,3500,3660]));
C.push(callout('Stop-the-line data rule','If a field cannot be explained in one sentence - what it measures, its denominator, date and source - it cannot enter the model. Keep it in a quarantine/unknown column until resolved.',gold));
C.push(h('3. Data model and grain design',1));
C.push(p('The current baseline contains identifiers and measures such as election year, municipality, ward, voting district, ballot type, party, registered voters, votes cast, spoilt votes, reported turnout and derived vote totals. Its immediate use is audit and aggregation; it is not the final modelling table.'));
C.push(table(['Table','One row means','Core fields','Use'],[
['raw_results_long','One source record / party / ballot / voting unit','source IDs, geography, year, ballot, party, raw measures, repair flags','Audit trail and party-share analysis'],
['election_unit','One voting unit x election x ballot type','registered voters, votes cast, spoilt votes, valid votes, quality flags','Reconcile and aggregate'],
['municipality_election','One municipality x election','registered voters, votes cast, turnout, spoilt rate, ballot coverage','Primary descriptive and supervised-learning table'],
['municipality_features','One municipality x prediction year','historical lags, demographics, socioeconomic and geographic covariates','Model matrix; only pre-outcome features'],
['municipality_profile','One municipality x profile version','cluster label, profile metrics, stability diagnostics','Dashboard segmentation and interpretation'],
['model_predictions','One municipality x held-out election','prediction, interval, actual, residual, calibration fields','Evaluation and dashboard evidence']],[1800,2500,3000,2060]));
C.push(h('4. End-to-end notebook architecture',1));
C.push(number('Environment and configuration: package versions, random seed, paths, scope, target, youth definition, boundary version and feature cutoff date.')); 
C.push(number('Source registry and ingestion: load files without overwriting raw values; record shape, dtypes, encodings, checksums and source metadata.'));
C.push(number('Schema and data-quality audit: uniqueness, duplicate keys, missingness, ranges, categorical drift, reconciliation and repair flags.'));
C.push(number('Standardisation: normalise names/codes, parse numbers, standardise years and ballot labels, map geography, and preserve before/after fields.'));
C.push(number('Aggregation: build the declared intermediate tables and reconcile totals before deriving rates.'));
C.push(number('Exploratory analysis: denominators first, then distributions, trends, maps and subgroup comparisons.'));
C.push(number('Feature engineering: lags, changes, rolling summaries, context features and missingness indicators using only information available by the cutoff.'));
C.push(number('Baselines and modelling: naive historical baseline, regularised regression, tree-based benchmark, optional clustering; no model enters the dashboard without backtesting.'));
C.push(number('Evaluation and uncertainty: rolling-origin validation, calibration, subgroup errors, sensitivity, residual maps and error analysis.'));
C.push(number('Decision layer: prioritisation logic, profile interpretation, caveats, dashboard-ready tables and export.'));
C.push(number('Reproducibility and handoff: final assertions, artefact manifest, limitations, run log and a clean output package.'));
C.push(h('5. Detailed lifecycle plan',1));
C.push(h('5.1 Ingest, standardise and validate',2));
['Read raw files once and never mutate them in place.','Create a canonical geography mapping table with source name, canonical code, province, effective boundary version and match status.','Use strict numeric parsing; retain parse-error and repair flags rather than silently coercing.','Check primary-key candidates at every grain. For example, party rows should be unique by source record ID; municipality-election rows should be unique by municipality code and election year, with ballot type explicitly handled.','Recompute votes cast, valid votes and turnout from components where possible. Compare to reported values and publish mismatch rates by source, year, province and ballot.','Profile missingness by year and geography. Missing not at random is a modelling risk, not merely a cleaning nuisance.'] .forEach(b=>C.push(bullet(b)));
C.push(h('5.2 Exploratory and diagnostic analysis',2));
C.push(p('The EDA should answer the problem before it decorates the dashboard. Start with denominator-aware tables and plots: registered voters, eligible or population denominator where available, votes cast, turnout, spoilt rate, youth registration/turnout, and changes between elections. Show both absolute gaps and percentage-point gaps.'));
C.push(table(['Diagnostic','What to show','Failure signal'],[
['Coverage','Municipalities present by year; matched/unmatched geography; source coverage','A trend is driven by changing coverage rather than behaviour.'],
['Consistency','Reported versus recomputed turnout; totals by hierarchy','Large unreconciled differences or duplicated totals.'],
['Temporal comparability','Boundary changes, election cadence, definition changes','Cross-year comparisons have no stable denominator.'],
['Distribution','Municipality size, turnout and gap distributions','Outliers are data errors or dominate the narrative.'],
['Subgroups','Youth, urban/rural proxy, socioeconomic bands, province','Small denominators make rankings unstable.'],
['Spatial','Maps with boundaries and missingness overlays','Visual clusters are mistaken for causal geography.']],[1900,4200,3260]));
C.push(h('5.3 Feature engineering',2));
['Historical turnout level and change (lagged by election), with minimum-history flags.','Historical registration level and change, separated from turnout.','Youth share / age structure and youth-specific historical gaps, where denominators are valid.','Socioeconomic and access context, standardised within the appropriate reference year.','Geographic context such as municipality size, density or remoteness proxies, only if definitions are documented.','Data-quality features: coverage, missingness, mismatch rate and boundary confidence. These may explain prediction reliability, but must not be confused with behavioural causes.'].forEach(b=>C.push(bullet(b)));
C.push(callout('Leakage test','For every feature, write: “Would this value be known before the election outcome being predicted?” If the answer is no, exclude it from the forward-looking model. This specifically applies to reported turnout, votes cast, post-election repairs and any derived measure containing the target.',red));
C.push(h('5.4 Modelling strategy',2));
C.push(table(['Layer','Method','Purpose / decision rule'],[
['Baseline 0','Historical mean / last-election turnout; province or municipality hierarchy','Sets the bar. If ML cannot beat this in rolling backtests, do not ship ML.'],
['Baseline 1','Regularised linear/elastic-net model','Transparent directionality and stable coefficients; useful with few time points.'],
['Benchmark','Random forest/gradient boosting with constrained depth','Nonlinear benchmark only after leakage and split checks. Compare against baseline, not training score.'],
['Forecast uncertainty','Conformal or bootstrap interval where defensible; otherwise empirical error bands','Communicate what is uncertain; do not present point forecasts as facts.'],
['Profiles','Standardised descriptive features + hierarchical/k-means clustering; sensitivity over k/seeds','Segment municipalities for interpretation, not to claim causal types.'],
['Optional prioritisation','Transparent score combining gap magnitude, population affected, confidence and feasibility','Keep separate from “risk” or causal language; document weights and test sensitivity.']],[1700,3000,4660]));
C.push(h('5.5 Validation and evaluation',2));
['Use rolling-origin or leave-one-election-cycle-out validation. A random row split is invalid because it mixes the same municipality-election information across train and test.','Group by municipality where needed, and keep election years chronological. If using all provinces for training and Mpumalanga for evaluation, state the domain-shift question explicitly.','Report MAE/RMSE only alongside calibration, error by municipality size, worst-case errors, rank stability and subgroup performance.','For classification, report precision/recall, PR-AUC, calibration and a confusion matrix at a predeclared threshold.','For clusters, report silhouette only as a diagnostic; also report bootstrap stability, feature summaries and whether profiles persist across election years.','Perform a “decision usefulness” review: would the result change where attention or resources go, and is that change stable under reasonable assumptions?'].forEach(b=>C.push(bullet(b)));
C.push(h('6. Dashboard and communication plan',1));
C.push(p('The dashboard should be the final view over certified tables, not a second analytical environment. It should make the problem legible without implying that association is causation.'));
C.push(table(['View','Minimum content','Interpretation guardrail'],[
['Overview','Scope, headline turnout/registration metrics, coverage and data freshness','Show denominators and avoid rankings without uncertainty.'],
['Map','Municipality gap metric with selectable year and gap type','Use consistent scales; offer missingness and boundary notes.'],
['Profiles','Cluster/profile cards with size, median metrics and stability','Profiles describe observed patterns; they do not diagnose causes.'],
['Forecast / prioritisation','Prediction, interval, baseline comparison, top drivers if valid','Label prospective forecasts and model limitations prominently.'],
['Drill-down','Municipality history, source coverage, quality flags and subgroup metrics','Allow users to inspect evidence behind a score.']],[1800,4200,3360]));
C.push(h('7. Reproducibility, governance and quality gates',1));
['Pin package versions and random seeds; record run date and input checksums.','Keep a data dictionary with units, denominators, date semantics, source and transformation.','Add assertions: expected columns, no duplicate keys at target grain, valid ranges, nonnegative counts, turnout bounds, reconciliation tolerance and geography match rate.','Save intermediate outputs as parquet/CSV with a manifest, not only rendered charts.','Separate exploratory cells from certified outputs; every dashboard table must be generated from a named function or final cell.','Document privacy and ethics: use aggregate data, avoid individual-level inference, and do not label municipalities or youth as deficient without context and uncertainty.'].forEach(b=>C.push(bullet(b)));
C.push(h('8. Proposed execution sequence',1));
C.push(table(['Phase','Deliverable','Exit criterion'],[
['0. Lock question','One-page analytical specification and target dictionary','Team agrees on geography, unit, target(s), youth definition and forecast horizon.'],
['1. Audit baseline','Source registry, schema report, grain report, mismatch/missingness report','No unresolved duplicate-key or denominator issue is hidden.'],
['2. Build canonical tables','Validated municipality-election and feature tables','Aggregations reconcile; geography match and coverage are quantified.'],
['3. Descriptive evidence','EDA figures and gap taxonomy','Claims are supported by denominator-aware tables and stable comparisons.'],
['4. Backtest models','Baseline + model comparison, calibration and error analysis','A model beats a credible baseline or is rejected.'],
['5. Profile and prioritise','Stable profiles and transparent decision score','Cluster/score sensitivity is documented; no causal claims.'],
['6. Dashboard and narrative','Dashboard-ready exports and 3-5 evidence-backed messages','A reviewer can trace every headline to source, query and chart.'],
['7. Final QA','Clean notebook run, artefact manifest and limitations','Fresh run completes from raw/approved inputs with no manual hidden steps.']],[1600,3900,3860]));
C.push(h('9. Final acceptance checklist',1));
['The notebook runs top-to-bottom from a clean environment.','The current 721,327-row baseline is explicitly treated as a long-format source table and not as the modelling sample size.','All target grains are unique and documented.','Mpumalanga scope is separated from all-province context.','Registration, turnout and digital-registration outcomes are not collapsed into one ambiguous metric.','No target components or post-outcome variables enter a forward-looking model.','Validation is chronological and grouped at the relevant geographic level.','Baselines, uncertainty, subgroup error and failure cases are reported.','Cluster stability and score sensitivity are shown.','The dashboard distinguishes observed facts, model outputs, associations and recommendations.','The final narrative states what the data cannot establish, especially causality and 2026 ground-truth validation.'].forEach(b=>C.push(bullet(b)));
C.push(h('Appendix A - initial notebook cell map',1));
C.push(table(['Cell block','Name','Output'],[
['01','Imports and configuration','Config object, versions, seed'],['02','Source registry','Source table + checksums'],['03','Raw ingestion','Raw dataframes, row counts'],['04','Schema/grain audit','Audit report + assertions'],['05','Geography harmonisation','Crosswalk + match report'],['06','Aggregation','Election-unit and municipality-election tables'],['07','Target construction','Target dictionary + outcome tables'],['08','EDA','Figures and summary tables'],['09','Feature pipeline','Feature matrix with cutoff checks'],['10','Baselines','Naive forecasts and benchmark metrics'],['11','Models','Fitted models + predictions'],['12','Validation','Rolling backtests, calibration, errors'],['13','Clustering/profiles','Profiles + stability report'],['14','Dashboard exports','Certified tables and chart data'],['15','Final QA','Manifest, limitations and run summary']],[1300,3000,5060]));
C.push(h('Appendix B - working assumptions to confirm',1));
['The main geography is Mpumalanga municipalities, with wider South Africa used only as context or a deliberately specified training/robustness design.','The primary outcomes are municipality-level registration and turnout gaps, not party preference or individual voter prediction.','The baseline CSV is a derived IEC/election-results integration and its repair flags are retained as evidence.','Digital registration data will be evaluated for temporal and geographic coverage before being treated as a causal or predictive variable.','The team will prefer an interpretable, calibrated model or a descriptive score over a complex model that cannot be validated with the available election history.'].forEach(b=>C.push(bullet(b)));

Packer.toBuffer(doc).then(buf=>fs.writeFileSync(OUT,buf));
