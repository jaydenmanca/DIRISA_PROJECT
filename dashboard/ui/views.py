"""Six focused dashboard views; all calculation remains in dashboard.data."""

import base64
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from dashboard import data as dd
from dashboard.ui import charts
from dashboard.ui import interactive
from dashboard.ui.components import (chips, compact, count, insight, legend, name, pct,
                           key, pts, section, signed_count, tile, two_step_explainer, venue_chips)
from dashboard.ui.theme import TOKENS as T

ASSETS = Path(__file__).resolve().parents[1] / 'assets'


def _switch_tab(label):
    """Move between the lazy tabs while preserving the shared mood slider."""
    st.session_state.active_tab = label
    st.query_params['tab'] = {'Story': 'story', 'Map & mood': 'map',
                              'Municipality': 'muni', 'IEC planner': 'planner',
                              'Can you trust it?': 'trust', 'How it works': 'method'}[label]


def _set_municipality(code):
    """Open a place selected on the map/table in the dedicated drill-down."""
    st.session_state.municipality_code = code
    st.query_params['muni'] = code
    _switch_tab('Municipality')


def story(d):
    """Tell the surge, scenario, local-position, and action story in one scan."""
    h, info = d['info']['headline'], d['info']
    actual = dd.actual_2021(d)
    at_risk = d['vd'].loc[d['vd']['at_risk_district']]
    interactive.surge_hero(d)
    st.write('')
    sim = info['simulation']['main']
    for col, args in zip(st.columns(4, gap='medium'), [
        ('Registered to vote', compact(h['registered_2026']), 'IEC roll · 23 Sep 2026'),
        ('Expected to vote', count(h['ballots_2026']),
         f"{pct(info['mpumalanga_turnout_2026_forecast_pct'])} of registered · likely "
         f"{sim['ballots_80pct'][0] / 1e3:,.0f}k–{sim['ballots_80pct'][1] / 1e3:,.0f}k"),
        ('Expected to stay home', compact(h['registered_2026'] - h['ballots_2026']),
         'registered, but not expected to vote'),
        ('Chance of a new record low', f"{100 * sim['p_below_record_low']:.0f}%",
         f"turnout under {pct(actual)} · cautious estimate "
         f"{100 * info['simulation']['cautious']['p_below_record_low']:.0f}%"),
    ]):
        with col:
            tile(*args, hero=True)
    st.write('')
    cards = [
        ('The mood is the big unknown',
         ['How many vote across the province: hard to predict', 'So we test many moods (Map & mood tab)'], 'caution'),
        ('Where turnout is lowest: predictable',
         [f"{count(len(at_risk))} voting districts most at risk", 'Checked against the 2011, 2016 and 2021 elections'],
         'insight'),
        ('New registrations are not the problem',
         ['Fast-growing rolls looked like they vote less', 'That was a statistical illusion',
          'The risk is the mood, not the new voters'], 'trap'),
    ]
    for col, (title, body, kind) in zip(st.columns(3, gap='medium'), cards):
        with col:
            insight(title, body, kind)
    key([('', 'Turnout', 'share of registered voters who vote'),
         ('', 'Voting district', 'the area served by one voting station'),
         ('', 'At risk', 'the fifth of districts with the lowest expected turnout'),
         ('', 'Chance', 'share of 10,000 simulated election days'),
         ('', 'Record low', f'{pct(actual)}, the 2021 turnout'),
         ('', 'Likely range', '8 in 10 simulations land inside it')], title='Words used here')
    st.button('Try the national mood →', type='primary', on_click=_switch_tab, args=('Map & mood',))


def map_and_mood(d):
    """The principal interactive view: the browser-side explorer (ui/interactive.py) drives the
    scenario; this table follows the level and threshold it writes back to session state."""
    level, threshold = interactive.mood_explorer(d)
    turnout_vd = dd.district_turnout(d, level)
    turnout_muni = dd.municipality_turnout(d, turnout_vd)
    summary = dd.mood_summary(d, turnout_vd, threshold)
    st.write('')
    section('MUNICIPAL VIEW', 'Municipalities at this mood', 'Updates when you move the slider above.')
    key([('', 'Turnout', 'expected at the mood you chose'),
         ('', 'Above / below', 'points compared with Mpumalanga'),
         ('', 'Districts below the line', 'voting districts under the red line'),
         ('', 'Priority rank', '1 = act here first')])
    table = pd.DataFrame({
        'Code': turnout_muni.index,
        'Municipality': [d['names'][c] for c in turnout_muni.index],
        'Turnout (%)': turnout_muni.to_numpy(),
        'Above / below (pts)': (turnout_muni - level).to_numpy(),
        'Districts below the line': summary.loc[turnout_muni.index, 'districts_below'].to_numpy(),
        'Voters in them': summary.loc[turnout_muni.index, 'voters_below'].to_numpy(),
        'Priority rank': d['priority'].loc[turnout_muni.index, 'rank'].to_numpy(),
    }).sort_values('Turnout (%)')
    st.dataframe(table, hide_index=True, height=360, width='stretch',
                 column_config={
                     'Turnout (%)': st.column_config.ProgressColumn('Turnout (%)', min_value=0,
                                                                     max_value=100, format='%.1f%%'),
                     'Above / below (pts)': st.column_config.NumberColumn('Above / below (pts)', format='%+.1f'),
                     'Voters in them': st.column_config.NumberColumn('Voters in them', format='%d'),
                 })
    open_code = st.selectbox('Open a municipality', table['Code'].tolist(),
                             format_func=lambda c: name(c, d['names']), key='map_open_code')
    st.button('Open municipality →', on_click=_set_municipality, args=(open_code,))


def municipality(d):
    """Give a planner the local forecast, gap composition and downloadable district list."""
    codes = list(d['muni'].sort_values('local_position_forecast').index)
    code = st.selectbox('Choose a municipality', codes, key='municipality_code',
                        format_func=lambda c: f"{name(c, d['names'])} · #{int(d['priority'].loc[c, 'rank'])} priority")
    mu, feat, gap, pr = (d['muni'].loc[code], d['features'].loc[code],
                         d['gap'].loc[code], d['priority'].loc[code])
    section('PLACE PROFILE', name(code, d['names']),
            'The 2026 outlook, where voters are lost, and the districts to watch.')
    chips(pr['profile'].split(': ', 1)[-1], f"{gap['main_gap']} gap",
          f"Priority #{int(pr['rank'])} of {len(d['muni'])}")
    for col, args in zip(st.columns(4, gap='medium'), [
        ('Expected turnout 2026', pct(mu['turnout_2026_forecast']), 'share of registered voters'),
        ('Compared with Mpumalanga', pts(mu['local_position_forecast']),
         'below the province' if mu['local_position_forecast'] < 0 else 'above the province'),
        ('Priority rank', f"#{int(pr['rank'])} of {len(d['muni'])}", '1 = act here first'),
        ('Young people registered', pct(feat['youth_registration_rate_2026_pct']),
         f"ages 18–29 · vs {pct(feat['older_registration_rate_2026_pct'])} of 30+"),
    ]):
        with col:
            tile(*args)
    sm = d['sim_muni'].loc[code]
    st.markdown('<div class="eyebrow" style="margin-top:14px">4 NOVEMBER 2026 · FROM 10,000 SIMULATED ELECTIONS</div>',
                unsafe_allow_html=True)
    for col, args in zip(st.columns(4, gap='medium'), [
        ('Chance turnout drops vs 2021', f"{100 * sm['p_below_own_2021']:.0f}%",
         f"2021 turnout was {pct(sm['turnout_2021'])}"),
        ('Likely turnout', f"{sm['turnout_p10']:.0f}–{sm['turnout_p90']:.0f}%", '8 in 10 simulations'),
        ('Expected to stay home', count(sm['non_voters_median']),
         f"of {count(sm['registered_2026'])} registered"),
        ('Chance of lowest turnout in Mpumalanga', f"{100 * sm['rank_lowest_share']:.0f}%", 'out of 17 municipalities'),
    ]):
        with col:
            tile(*args)
    left, right = st.columns(2, gap='large')
    with left:
        st.markdown('### Turnout through time')
        st.altair_chart(charts.history_chart(code, feat, mu, dd.province_history(d['election_panel'], d['features'])),
                       width='stretch', theme=None)
        key([(T['blue'], 'Blue line', 'this municipality'), ('#898781', 'Grey line', 'Mpumalanga'),
             ('ring:' + T['blue'], 'Hollow dot', '2026 forecast'), ('line:' + T['blue'], 'Bar', 'likely range')])
    with right:
        st.markdown('### Where participation was lost')
        st.altair_chart(charts.gap_chart(gap), width='stretch', theme=None)
        key([('bar:' + T['blue'], f"{gap['voted_per_100']:.0f} voted", 'of every 100 adults (2021)'),
             ('bar:' + T['orange'], f"{gap['registered_not_voted_per_100']:.0f} stayed home", 'registered, did not vote'),
             ('bar:#d9d8d2', f"{gap['not_registered_per_100']:.0f} not registered", 'could not vote'),
             ('', 'Main gap', gap['main_gap'].lower())])
    st.write('')
    section('LOCAL CONTEXT', 'What else do we know?', 'Background facts, not causes.')
    chips(f"Audit score {feat['audit_score_avg_last3']:.1f} / 4",
          f"Registration {pct(feat['registration_rate_2026_pct'])}",
          f"Roll growth {pct(feat['roll_growth_2021_2026_pct'])}",
          f"Youth share of roll {pct(feat['youth_share_of_roll_2026_pct'])}",
          f"Internet access {pct(feat['c22_internet_any_pct'])}",
          f"Adult hunger {pct(feat['c22_adult_hunger_pct'])}",
          f"Urban households {pct(feat['c22_urban_pct'])}")
    districts = d['vd'].loc[(d['vd']['municipality_code_2021'] == code) &
                            d['vd']['at_risk_district']].sort_values('local_position_forecast')
    total_voters = districts['registered_voters'].sum()
    position = mu['local_position_forecast']
    relation = f"{abs(position):.1f} points {'below' if position < 0 else 'above'} the province"
    st.write('')
    insight('This place in three points',
            [f"Expected turnout {relation}",
             f"{len(districts)} at-risk voting districts",
             f"{count(total_voters)} voters live in them ({mu['voters_in_at_risk_districts_pct']:.0f}% of its voters)"])
    st.markdown('### At-risk voting districts')
    key([('', 'At risk', 'in Mpumalanga’s lowest-turnout fifth'),
         ('', 'Registered 2026', 'estimated from the 2021 roll'),
         ('', 'Chance below 25%', 'from 10,000 simulated elections'),
         ('', 'Venue', 'read from the voting-station name')])
    venue_chips(districts['venue_type'].dropna())
    cols = ['voting_district', 'venue_type', 'registered_voters', 'vd_turnout_lag1',
            'turnout_forecast', 'p_below_25', 'non_voters_expected']
    if districts.empty:
        st.image(str(ASSETS / 'empty-state.svg'), width=240)
        st.info('No at-risk voting districts here.')
    else:
        st.dataframe(districts[cols].rename(columns={
            'voting_district': 'Voting district', 'venue_type': 'Venue',
            'registered_voters': 'Registered 2026 (est.)', 'vd_turnout_lag1': 'Turnout 2021 (%)',
            'turnout_forecast': '2026 forecast (%)', 'p_below_25': 'Chance below 25%',
            'non_voters_expected': 'Expected to stay home',
        }).assign(**{'Chance below 25%': lambda f: 100 * f['Chance below 25%']}),
            hide_index=True, width='stretch', height=min(420, 52 + 35 * len(districts)),
            column_config={'2026 forecast (%)': st.column_config.ProgressColumn(
                '2026 forecast (%)', min_value=0, max_value=100, format='%.1f%%'),
                           'Chance below 25%': st.column_config.ProgressColumn(
                'Chance below 25%', min_value=0, max_value=100, format='%.0f%%'),
                           'Registered 2026 (est.)': st.column_config.NumberColumn(format='%.0f'),
                           'Expected to stay home': st.column_config.NumberColumn(format='%.0f'),
                           'Turnout 2021 (%)': st.column_config.NumberColumn(format='%.1f%%')})
        st.download_button(f'Download at-risk districts (CSV, {len(districts)} rows)',
                           data=districts[cols].to_csv(index=False),
                           file_name=f'at_risk_districts_{code}_2026.csv', mime='text/csv')


def _reset_weights(default):
    """Restore the published team weights before the weight widgets render."""
    for name, value in default.items():
        st.session_state[f'weight_{name}'] = float(value)


def planner(d):
    """Translate at-risk districts into a transparent one-team-per-district allocation."""
    section('STEP 3 · ACT', 'You have voter-education teams. Where should they go?',
            'One team per at-risk district, biggest districts first.')
    at_risk = d['vd'].loc[d['vd']['at_risk_district']]
    n_teams = st.slider('Number of teams', min_value=5, max_value=len(at_risk),
                        value=min(50, len(at_risk)), step=5, key='team_count')
    turnout_vd = dd.district_turnout(d, st.session_state.province_level)
    plan = dd.plan_teams(d, n_teams, turnout_vd)
    all_voters = at_risk['registered_voters'].sum()
    reached = plan['registered_voters'].sum()
    avg_turnout = (plan['turnout_at_scenario'] * plan['registered_voters']).sum() / reached
    for col, args in zip(st.columns(4, gap='medium'), [
        ('Voters reached', count(reached), 'registered in the chosen districts'),
        ('Share of at-risk roll', f'{100 * reached / all_voters:.0f}%', f'of {count(all_voters)} voters'),
        ('Municipalities covered', count(plan['municipality_code_2021'].nunique()),
         f"of {len(d['muni'])} municipalities"),
        ('Average predicted turnout', pct(avg_turnout), 'in selected districts · current mood'),
    ]):
        with col:
            tile(*args)
    left, right = st.columns([1.2, .8], gap='large')
    with left:
        st.markdown('### Coverage as teams grow')
        st.altair_chart(charts.coverage_chart(dd.coverage_curve(d['vd']), n_teams),
                       width='stretch', theme=None)
    with right:
        st.markdown('### Allocation by municipality')
        by_muni = plan.groupby('municipality_code_2021').agg(
            teams=('voting_district', 'size'), voters=('registered_voters', 'sum')).reset_index()
        by_muni['municipality'] = by_muni['municipality_code_2021'].map(d['names'])
        st.altair_chart(charts.allocation_chart(by_muni), width='stretch', theme=None)
    plan_cols = ['voting_district', 'municipality_name_2021', 'venue_type',
                 'registered_voters', 'turnout_at_scenario']
    st.dataframe(plan[plan_cols].rename(columns={
        'voting_district': 'Voting district', 'municipality_name_2021': 'Municipality',
        'venue_type': 'Venue', 'registered_voters': 'Registered 2026 (est.)',
        'turnout_at_scenario': 'Turnout at mood (%)',
    }), hide_index=True, height=350, width='stretch',
        column_config={'Turnout at mood (%)': st.column_config.NumberColumn(format='%.1f%%')})
    st.download_button(f'Download team plan (CSV, {len(plan)} rows)',
                       plan[plan_cols].to_csv(index=False),
                       file_name='voter_education_team_plan_2026.csv', mime='text/csv')
    st.write('')
    section('TEAM JUDGMENT', 'Re-weight the priority list', 'Your choice of what matters most. Not a model result.')
    defaults = d['info']['priority_weights']
    weight_labels = {
        'low_turnout_forecast': 'Low turnout forecast', 'youth_gap': 'Youth registration gap',
        'low_registration': 'Low registration', 'weak_audit': 'Weak audit record',
    }
    weights = {}
    for col, (key, label) in zip(st.columns(4, gap='small'), weight_labels.items()):
        with col:
            weights[key] = st.slider(label, 0.0, 1.0, float(defaults[key]), 0.05,
                                     key=f'weight_{key}')
    total = sum(weights.values())
    st.caption('Normalised shares: ' + ' · '.join(
        f'{label} {100 * weights[key] / total:.0f}%'
        for key, label in weight_labels.items()) if total else
        'All weights are zero; choose at least one to make the score meaningful.')
    st.button('Reset to team weights', on_click=_reset_weights, args=(defaults,))
    if total == 0:
        st.warning('Choose at least one non-zero weight to display a ranking.')
        return
    score = dd.priority_scores(d, weights)
    ranking = pd.DataFrame({
        'Rank now': range(1, len(score) + 1),
        'Municipality': [name(c, d['names']) for c in score.index],
        'Priority score': score.to_numpy(),
        'Default rank': d['priority'].loc[score.index, 'rank'].astype(int).to_numpy(),
    })
    ranking['Change'] = ranking.apply(lambda r: ('↑' + str(int(r['Default rank'] - r['Rank now']))
                                          if r['Default rank'] > r['Rank now'] else
                                          '↓' + str(int(r['Rank now'] - r['Default rank']))
                                          if r['Default rank'] < r['Rank now'] else '—'), axis=1)
    st.dataframe(ranking, hide_index=True, height=390, width='stretch',
                 column_config={'Priority score': st.column_config.ProgressColumn(
                     min_value=0, max_value=100, format='%.1f')})


def trust(d):
    """Replay chronological holdout years and expose the model's genuine failure cases."""
    section('STEP 4 · CHECK', 'Replay past elections. Each model only saw earlier ones.',
            'Pick a past election: see what we would have predicted, and what happened.')
    years = sorted(d['backtest']['test_year'].unique().tolist())
    year = st.segmented_control('Election predicted', years,
                                default=years[-1], key='backtest_year', required=True)
    frame = d['backtest_muni'].loc[d['backtest_muni']['test_year'] == year].copy()
    frame['municipality'] = frame['municipality_code_2021'].map(
        lambda c: name(c, d['names']))
    left, right = st.columns([1.25, .75], gap='large')
    with left:
        st.altair_chart(charts.backtest_scatter(frame), width='stretch', theme=None)
        key([('line:#898781', 'Diagonal', 'perfect prediction'), ('', 'Above it', 'predicted too high'),
             ('', 'Below it', 'predicted too low'), (T['blue'], 'Blue', 'our model')])
    with right:
        st.markdown('### The scorecard')
        scores = d['backtest'].loc[d['backtest']['test_year'] == year,
                                    ['approach', 'muni_MAE_pp', 'muni_bias_pp',
                                     'muni_rank_rho', 'lowest5_found']].rename(columns={
            'approach': 'Approach', 'muni_MAE_pp': 'Average miss (pts)',
            'muni_bias_pp': 'Bias (pts)', 'muni_rank_rho': 'Ranking quality',
            'lowest5_found': 'Lowest 5 found',
        })
        st.dataframe(scores, hide_index=True, width='stretch', height=205,
                     column_config={'Average miss (pts)': st.column_config.NumberColumn(format='%.1f'),
                                    'Bias (pts)': st.column_config.NumberColumn(format='%+.1f'),
                                    'Ranking quality': st.column_config.NumberColumn(format='%.2f'),
                                    'Lowest 5 found': st.column_config.NumberColumn(format='%.0f')})
        key([('', 'Average miss', 'points off per municipality (lower is better)'),
             ('', 'Bias', '+ too high, − too low'), ('', 'Ranking quality', '1 = perfect order')])
        if year == years[-1]:
            two_step = d['backtest'].loc[(d['backtest']['test_year'] == year) &
                                         (d['backtest']['approach'] == 'Two-step forecast')].iloc[0]
            baseline = d['province_backtest'].loc[
                (d['province_backtest']['test_year'] == year) &
                (d['province_backtest']['method'] == 'Same as last election')].iloc[0]
            ratio = d['province_backtest'].loc[
                (d['province_backtest']['test_year'] == year) &
                (d['province_backtest']['method'] == 'Provincial-election ratio')].iloc[0]
            insight(f'The honest {year} result',
                    [f"Province-wide miss: {abs(baseline['error_pp']):.1f} → {abs(ratio['error_pp']):.1f} points",
                     f"Found {int(two_step['lowest5_found'])} of the 5 lowest municipalities"], 'caution')
    st.write('')
    section('TWO STEPS, DIFFERENT CERTAINTY', 'Where does the forecast come from?',
            'Two parts: one uncertain, one well tested.')
    two_step_explainer(d['info']['province_2026_pct']['central'], 'district difference')
    st.caption(f'Chosen using these {len(years)} past elections: a guide, not a guarantee.')
    st.write('')
    section('WERE OUR 2026 PROBABILITIES HONEST?', 'The simulation, tested on past elections',
            'We simulated 2016 and 2021 the same way, using only earlier elections.')
    key([('', '80% range', 'should catch the real result about 8 times in 10'),
         ('', 'AUC', 'how well risky districts were ranked (1 = perfect)')])
    sb = d['sim_backtest']
    rows = []
    for _, r in sb.iterrows():
        rows.append({'Election predicted': int(r['test_year']),
                     'Mpumalanga inside its 80% range': 'Yes' if r['province_inside_80pct'] else 'No',
                     'Municipalities inside their 80% range': f"{100 * r['municipalities_inside_80pct']:.0f}%",
                     'Voting districts inside their 80% range': f"{100 * r['districts_inside_80pct']:.0f}%",
                     'Ranking quality, low-turnout districts (AUC, 1 = perfect)': f"{r['ranking_auc_low_turnout']:.2f}",
                     'Districts below 25%: actual vs simulated 80% range':
                         f"{int(r['districts_below_25_actual'])} (range {r['districts_below_25_80pct_range']})"})
    st.dataframe(pd.DataFrame(rows), hide_index=True, width='stretch')
    cal = d['sim_calibration'].copy()
    cal['Election'] = cal['test_year'].astype(int).astype(str)
    diagonal = pd.DataFrame({'x': [0, 0.6], 'y': [0, 0.6]})
    left, right = st.columns([1, 1], gap='large')
    with left:
        st.altair_chart(
            (alt.Chart(diagonal).mark_line(color=T['reference'], strokeWidth=1).encode(x='x:Q', y='y:Q')
             + alt.Chart(cal).mark_circle(opacity=.9).encode(
                 x=alt.X('mean_predicted:Q', title='Predicted chance of turnout below 25%', axis=alt.Axis(format='%'),
                         scale=alt.Scale(domain=[0, .6])),
                 y=alt.Y('share_happened:Q', title='Share that really fell below 25%', axis=alt.Axis(format='%'),
                         scale=alt.Scale(domain=[0, .6])),
                 size=alt.Size('districts:Q', title='Districts', scale=alt.Scale(range=[40, 600])),
                 color=alt.Color('Election:N', scale=alt.Scale(range=[T['orange'], T['blue']])),
                 tooltip=['Election', alt.Tooltip('mean_predicted:Q', format='.1%', title='Predicted'),
                          alt.Tooltip('share_happened:Q', format='.1%', title='Happened'), 'districts:Q']))
            .properties(height=300), width='stretch', theme=None)
    with right:
        insight('What this shows',
                ['Real results landed inside our ranges', 'Risky districts ranked very well (AUC 0.96)',
                 'Raw chances were too cautious, so we corrected them', 'The correction passed a cross-check'], 'insight')
        key([('line:#898781', 'Grey line', 'perfect calibration'), ('', 'Dot size', 'number of districts')])
    with st.expander('What we tested: local models and new feature groups'):
        local = d['backtest_local'].groupby('model')[['vd_MAE_pp', 'muni_MAE_pp']].mean().rename(columns={
            'vd_MAE_pp': 'District average miss (pts)',
            'muni_MAE_pp': 'Municipality average miss (pts)',
        })
        st.dataframe(local.round(2), width='stretch')
        groups = d['feature_tests'][['vd_MAE_pp', 'muni_MAE_pp']].rename(columns={
            'vd_MAE_pp': 'District average miss (pts)',
            'muni_MAE_pp': 'Municipality average miss (pts)',
        })
        st.dataframe(groups.round(2), width='stretch')
        st.caption('Kept only if it lowered the error. Gains were small.')


def method(d):
    """A plain-language account of sources, method, uncertainty and responsible use."""
    years = sorted(d['backtest']['test_year'].unique().tolist())
    ratio = d['province_backtest'].loc[
        d['province_backtest']['method'] == 'Provincial-election ratio']
    early = ratio.loc[ratio['test_year'] != years[-1]]
    early_misses = ', '.join(
        f"{int(row.test_year)} ({abs(row.error_pp):.1f} points)"
        for row in early.itertuples())
    section('BEHIND THE NUMBERS', 'How it works', 'The short version.')
    left, right = st.columns(2, gap='large')
    with left:
        insight('The question', ['Where in Mpumalanga will turnout be lowest on 4 November 2026?',
                                 'Is the loss before registration, or after?',
                                 'For: the IEC, civil society, journalists'], 'insight')
        insight('The data', ['IEC election results, 2000–2021', 'IEC voters’ roll, 23 Sep 2026',
                             'Census 2022, Auditor-General, provincial elections',
                             'Map: Municipal Demarcation Board (geoBoundaries)'], 'insight')
        insight('What the model looks at', ['Past turnout of each voting district', 'How competitive past elections were',
                                            'District size, venue, swing, roll growth'], 'insight')
    with right:
        insight('How the forecast works', ['1. Province-wide mood (uncertain)', '2. Each district above or below it (tested)',
                                           '3. Election day simulated 10,000 times → chances'], 'insight')
        insight('Limits', [f'Only {len(years)} past elections to test on',
                           f'Province-wide level missed in {early_misses}',
                           '2026 district rolls are estimates',
                           'Census only goes down to municipalities',
                           'Patterns are not causes'], 'caution')
        insight('Using the downloads', ['Starting lists, not final orders', 'Check with local knowledge first'], 'trap')
    two_step_explainer(d['info']['province_2026_pct']['central'], 'district difference')
    st.caption('Sources: [IEC results](https://results.elections.org.za/home/downloads/me-results) · '
               '[IEC registration](https://www.elections.org.za/pw/StatsData/Voter-Registration-Statistics) (23 Sep 2026) · '
               '[Census 2022](https://isibaloweb.statssa.gov.za/pages/surveys/pss/censuses/2022/census2022.php) · '
               '[Municipal Money](https://municipaldata.treasury.gov.za) (24 Sep 2026) · '
               '[geoBoundaries](https://www.geoboundaries.org) (CC BY 3.0 IGO)')
    st.info('QR code: added once the dashboard has a public link.')
