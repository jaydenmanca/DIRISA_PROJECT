"""The two signature interactive pieces, built as Streamlit v2 components (HTML/CSS/JS in ui/js/).

- surge_hero:    the Story headline told with dots (1 dot = 1,000 voters), animated in three steps.
- mood_explorer: the national-mood slider, live counts, municipal map and a field of 1,785 voting
                 districts that slide and turn red as turnout falls.

Both run in the browser, so they animate smoothly instead of reloading the page. The maths in
mood_explorer.js mirrors dashboard/data.py; the mood slider writes its value back to
st.session_state['province_level'] so the table below and the planner follow it.
"""

from pathlib import Path

import numpy as np

import streamlit as st

from dashboard import data as dd

JS_DIR = Path(__file__).resolve().parent / 'js'


def _read(name):
    return (JS_DIR / name).read_text(encoding='utf-8')


_MOUNTS = {}


def _component(name, stem):
    """Register a component with the current Streamlit runtime if it is not there yet.

    Registration is per runtime, not per Python process: a module imported before the
    runtime started (tests, a server restart) must register again, but re-registering on
    every rerun would log warnings, so check the registry first."""
    from streamlit.runtime import Runtime
    if Runtime.exists() and Runtime.instance().bidi_component_registry.get(name) is None:
        _MOUNTS.pop(name, None)
    if name not in _MOUNTS:
        _MOUNTS[name] = st.components.v2.component(name, html=_read(f'{stem}.html'),
                                                   css=_read(f'{stem}.css'), js=_read(f'{stem}.js'))
    return _MOUNTS[name]


@st.cache_data
def _histogram(turnouts, width=0.5):
    """Simulated province turnouts binned for the hero: one dot per 10 simulations."""
    edges = np.arange(np.floor(turnouts.min()), np.ceil(turnouts.max()) + width, width)
    counts, edges = np.histogram(turnouts, bins=edges)
    return [{'x': float(x), 'n': int(round(c / 10))} for x, c in zip(edges[:-1], counts)]


def surge_hero(d):
    """Render the 2026 hero (Story tab): roll -> forecast -> 10,000 simulated elections."""
    h, info, sim = d['info']['headline'], d['info'], d['info']['simulation']
    _component('dirisa_surge_hero', 'surge_hero')(key='surge_hero', data={
        'reg2021': h['registered_2021'], 'reg2026': h['registered_2026'],
        'ballots2026': h['ballots_2026'],
        'ballotsLow': sim['main']['ballots_80pct'][0], 'ballotsHigh': sim['main']['ballots_80pct'][1],
        'turnout2026': info['mpumalanga_turnout_2026_forecast_pct'],
        'pRecord': sim['main']['p_below_record_low'], 'pRecordCautious': sim['cautious']['p_below_record_low'],
        'recordLow': sim['record_low_pct'],
        'bins': _histogram(d['sim_province']['province_turnout'].to_numpy()), 'binWidth': 0.5,
    })


@st.cache_data
def _mood_payload(_d, cache_key):
    """Static part of the explorer's data: districts, municipalities, map shapes, label points."""
    d = _d
    muni = d['muni'].sort_values('local_position_forecast')
    order = {code: i for i, code in enumerate(muni.index)}
    reg26 = d['registration']['registered_2026']
    vd = d['vd']
    rows = [[r.voting_district, order[r.municipality_code_2021], round(float(r.local_position_forecast), 3),
             round(float(r.beta_slider), 4), round(float(r.registered_voters), 2),
             (None if str(r.venue_type) == 'nan' else str(r.venue_type).capitalize()),
             (None if str(r.vd_turnout_lag1) == 'nan' else round(float(r.vd_turnout_lag1), 1)),
             round(float(r.p_below_25), 3), round(float(r.turnout_p10), 1), round(float(r.turnout_p90), 1)]
            for r in vd.itertuples()]
    sim_p10, sim_p90 = d['info']['simulation']['main']['turnout_80pct']
    geo = [{'code': f['properties']['municipality_code_2021'],
            'rings': [[[round(x, 4), round(y, 4)] for x, y in poly[0]] for poly in f['geometry']['coordinates']]}
           for f in d['geojson']['features']]
    return {
        'munis': [{'code': c, 'name': d['names'][c], 'reg2026': int(reg26[c]),
                   'pBelow2021': float(d['sim_muni'].loc[c, 'p_below_own_2021']),
                   'pRecord': float(d['sim_muni'].loc[c, 'p_below_record_low'])} for c in muni.index],
        'vds': rows, 'geo': geo,
        'labels': [{'code': p['code'], 'lon': p['lon'], 'lat': p['lat']} for p in dd.map_label_points(d['geojson'])],
        'central': float(d['info']['province_2026_pct']['central']),
        'low': float(d['info']['province_2026_pct']['low']), 'high': float(d['info']['province_2026_pct']['high']),
        'actual2021': float(dd.actual_2021(d)), 'ballots2021': int(d['info']['headline']['ballots_2021']),
        'reg2026Total': int(reg26.sum()),
        # 1,001 quantiles of the 10,000 simulated province turnouts: the browser reads the chance
        # of any slider level from them
        'quantiles': [round(float(q), 3) for q in np.percentile(d['sim_province']['province_turnout'], np.linspace(0, 100, 1001))],
        'marks': [['Low (1 in 10)', sim_p10], ['Forecast', float(d['info']['province_2026_pct']['central'])],
                  ['2021 record low', float(dd.actual_2021(d))], ['High (9 in 10)', sim_p90]],
    }


def _sync_from_component():
    """Copy the explorer's state into the shared session keys (runs before the rerun)."""
    state = st.session_state.get('mood_explorer') or {}
    if state.get('level') is not None:
        st.session_state.province_level = float(state['level'])
        st.query_params['mood'] = str(st.session_state.province_level)
    if state.get('threshold') is not None:
        st.session_state.threshold = int(state['threshold'])


def _open_from_component():
    """A municipality was clicked on the map or in the dot field: open its drill-down."""
    state = st.session_state.get('mood_explorer') or {}
    code = state.get('open')
    if code:
        st.session_state.municipality_code = code
        st.session_state.active_tab = 'Municipality'
        st.query_params['muni'] = code
        st.query_params['tab'] = 'muni'


def mood_explorer(d):
    """Render the explorer; returns (level, threshold) currently shown."""
    level = float(st.session_state.province_level)
    threshold = int(st.session_state.get('threshold', 25))
    payload = dict(_mood_payload(d, 'v2'), level=level, threshold=threshold)
    _component('dirisa_mood_explorer', 'mood_explorer')(key='mood_explorer', data=payload, default={'level': level, 'threshold': threshold},
          on_level_change=_sync_from_component, on_threshold_change=_sync_from_component,
          on_open_change=_open_from_component)
    return level, threshold
