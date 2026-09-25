"""Data loading and scenario maths for the dashboard.

Everything is read from derived/ (written by model.ipynb), so the dashboard needs no model
training and no large input files. Run the notebook first if derived/ is missing.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

DERIVED = Path(__file__).resolve().parents[1] / 'derived'

# Swing sensitivity (vd_beta) rests on only 3-5 past elections per district, so it is noisy.
# For the slider it is shrunk halfway towards 1 and capped at 0.5-1.5:
# a district then moves between half and one-and-a-half times as much as the province.
BETA_SHRINK = 0.5
BETA_RANGE = (0.5, 1.5)


@st.cache_data
def load():
    """All dashboard inputs, as one dict of DataFrames (plus the model info and map)."""
    d = {
        'info': json.loads((DERIVED / 'models' / 'turnout_model_info.json').read_text(encoding='utf-8')),
        'geojson': json.loads((DERIVED / 'mpumalanga_municipalities_2016.geojson').read_text(encoding='utf-8')),
        'vd': pd.read_csv(DERIVED / 'forecast_2026_voting_district.csv', dtype={'voting_district': str}),
        'muni': pd.read_csv(DERIVED / 'forecast_2026_municipality.csv', index_col=0),
        'features': pd.read_csv(DERIVED / 'features_municipality.csv', index_col=0),
        'registration': pd.read_csv(DERIVED / 'registration_denominators_2021_2026.csv', index_col=0),
        'gap': pd.read_csv(DERIVED / 'gap_breakdown.csv', index_col=0),
        'priority': pd.read_csv(DERIVED / 'priority_list.csv', index_col=0),
        'scenarios': pd.read_csv(DERIVED / 'forecast_2026_province_scenarios.csv'),
        'backtest': pd.read_csv(DERIVED / 'model_backtest.csv'),
        'backtest_muni': pd.read_csv(DERIVED / 'backtest_municipality_predictions.csv'),
        'backtest_local': pd.read_csv(DERIVED / 'model_backtest_local.csv'),
        'feature_tests': pd.read_csv(DERIVED / 'feature_tests.csv', index_col=0),
        'profiles': pd.read_csv(DERIVED / 'participation_profiles.csv', index_col=0),
        'election_panel': pd.read_csv(DERIVED / 'municipality_election_panel_2021_boundaries.csv'),
        'province_backtest': pd.read_csv(DERIVED / 'model_backtest_province.csv'),
        # 10,000 simulated 2026 elections (notebook cell 5.6) and their backtest
        'sim_province': pd.read_csv(DERIVED / 'simulation_2026_province.csv'),
        'sim_muni': pd.read_csv(DERIVED / 'simulation_2026_municipality.csv', index_col=0),
        'sim_vd': pd.read_csv(DERIVED / 'simulation_2026_voting_district.csv', dtype={'voting_district': str}),
        'sim_backtest': pd.read_csv(DERIVED / 'simulation_backtest.csv'),
        'sim_calibration': pd.read_csv(DERIVED / 'simulation_calibration.csv'),
    }
    d['names'] = d['muni']['municipality_name_2021'].str.split(' - ').str[1].to_dict()   # code -> short name
    # 2026 first: district counts use the ESTIMATED 2026 roll (each district's 2021 roll x its
    # municipality's growth to 2026; the IEC publishes 2026 registration per municipality only).
    # Scaling is uniform within a municipality, so municipal turnout is unchanged.
    sim_cols = ['voting_district', 'registered_2026_est', 'turnout_median', 'turnout_p10', 'turnout_p90',
                'p_below_25', 'non_voters_expected']
    vd = d['vd'].merge(d['sim_vd'][sim_cols], on='voting_district', how='left', validate='one_to_one')
    assert vd['registered_2026_est'].notna().all(), 'simulation file does not cover every voting district'
    vd['registered_voters_2021'] = vd['registered_voters']
    vd['registered_voters'] = vd['registered_2026_est']
    d['vd'] = vd
    beta = vd['vd_beta'].fillna(1.0)
    vd['beta_slider'] = (1 + BETA_SHRINK * (beta - 1)).clip(*BETA_RANGE)
    return d


def district_turnout(d, province_level):
    """2026 turnout per voting district if Mpumalanga turns out at `province_level` %.
    turnout = province level + local position + (swing sensitivity - 1) x (shift from the central forecast)."""
    central = d['info']['province_2026_pct']['central']
    vd = d['vd']
    shift = province_level - central
    return (province_level + vd['local_position_forecast'] + (vd['beta_slider'] - 1) * shift).clip(0, 100)


def municipality_turnout(d, turnout_vd):
    """Registered-voter-weighted municipal turnout from district turnout."""
    vd = d['vd'].assign(t=turnout_vd)
    g = vd.assign(v=vd['t'] * vd['registered_voters']).groupby('municipality_code_2021')
    return g['v'].sum() / g['registered_voters'].sum()


def expected_ballots(d, turnout_muni):
    """2026 roll x municipal turnout, summed over Mpumalanga."""
    reg = d['registration']['registered_2026'].reindex(turnout_muni.index)
    return float((reg * turnout_muni / 100).sum())


def priority_scores(d, weights):
    """Recompute the priority score (0-100) with new weights; same rescaling as notebook cell 5.10."""
    p = d['priority']
    comp = p[['value_low_turnout_forecast', 'value_youth_gap', 'value_low_registration', 'value_weak_audit']].copy()
    comp.columns = ['low_turnout_forecast', 'youth_gap', 'low_registration', 'weak_audit']
    scaled = (comp - comp.min()) / (comp.max() - comp.min())
    for c in ['low_turnout_forecast', 'low_registration', 'weak_audit']:      # low values = high priority
        scaled[c] = 1 - scaled[c]
    total = sum(weights.values()) or 1
    score = sum(scaled[c] * w for c, w in weights.items()) / total * 100
    return score.sort_values(ascending=False)


def plan_teams(d, n_teams, turnout_vd):
    """Send one voter-education team to each of the n at-risk districts with the most registered
    voters (at-risk = lowest fifth of predicted local position). Returns the chosen districts."""
    vd = d['vd'].assign(turnout_at_scenario=turnout_vd)
    at_risk = vd[vd['at_risk_district']].sort_values('registered_voters', ascending=False)
    return at_risk.head(n_teams)


def colour_scale(values, low_rgb, mid_rgb, high_rgb, vmin, vmax, vmid=None):
    """Map values to RGBA lists for the map (diverging if vmid is given, else low -> high)."""
    vmid = (vmin + vmax) / 2 if vmid is None else vmid
    out = []
    for v in values:
        if v <= vmid:
            t = 0 if vmid == vmin else (v - vmin) / (vmid - vmin)
            a, b = low_rgb, mid_rgb
        else:
            t = 1 if vmax == vmid else (v - vmid) / (vmax - vmid)
            a, b = mid_rgb, high_rgb
        t = float(np.clip(t, 0, 1))
        out.append([int(a[i] + (b[i] - a[i]) * t) for i in range(3)] + [210])
    return out


def actual_2021(d):
    """Observed province-wide 2021 turnout from the notebook backtest export."""
    rows = d['province_backtest'].loc[d['province_backtest']['test_year'] == 2021, 'actual']
    return float(rows.iloc[0])


def mood_summary(d, turnout_vd, threshold):
    """Per-municipality threshold counts from the saved district forecasts and scenario."""
    frame = d['vd'][['municipality_code_2021', 'registered_voters']].copy()
    frame['below'] = turnout_vd.to_numpy() < threshold
    frame['voters_below'] = frame['registered_voters'].where(frame['below'], 0)
    return frame.groupby('municipality_code_2021').agg(
        districts_below=('below', 'sum'), voters_below=('voters_below', 'sum'))


@st.cache_data
def coverage_curve(vd):
    """Cumulative reach when one team visits each largest at-risk district."""
    eligible = vd.loc[vd['at_risk_district'], 'registered_voters'].sort_values(ascending=False)
    reached = np.r_[0, eligible.cumsum().to_numpy()]
    total = float(eligible.sum())
    return pd.DataFrame({'teams': np.arange(len(reached)),
                         'share_reached': 100 * reached / total,
                         'voters_reached': reached})


@st.cache_data
def province_history(panel, features):
    """Province history from the model's municipal turnout, weighted by each year's roll.

    The PR rows supply roll weights only; the turnout values come from the canonical
    municipality feature table and retain the notebook's max(PR, Ward) definition.
    """
    pr = panel.loc[panel['ballot_type'] == 'PR']
    values = {}
    for year, group in pr.groupby('election_year'):
        turnout = features[f'turnout_{year}'].reindex(group['municipality_code_2021'])
        values[year] = np.average(turnout.to_numpy(), weights=group['registered_voters'])
    return pd.Series(values).sort_index()


@st.cache_data
def map_label_points(geojson):
    """Area-weighted label anchors from the committed municipal polygons."""
    nudges = {'MP316': (-0.12, 0.08), 'MP315': (0.08, -0.07),
              'MP311': (-0.09, -0.04), 'MP312': (0.07, 0.05)}
    points = []
    for feature in geojson['features']:
        code = feature['properties']['municipality_code_2021']
        rings = [poly[0] for poly in feature['geometry']['coordinates']]
        ring = max(rings, key=len)
        xy = np.asarray(ring, dtype=float)
        x, y = xy[:, 0], xy[:, 1]
        cross = x[:-1] * y[1:] - x[1:] * y[:-1]
        area2 = cross.sum()
        if abs(area2) < 1e-10:
            lon, lat = x.mean(), y.mean()
        else:
            lon = ((x[:-1] + x[1:]) * cross).sum() / (3 * area2)
            lat = ((y[:-1] + y[1:]) * cross).sum() / (3 * area2)
        dx, dy = nudges.get(code, (0, 0))
        points.append({'code': code, 'lon': lon + dx, 'lat': lat + dy})
    return points


def chance_at_or_below(d, level):
    """Share of the 10,000 simulated 2026 elections with Mpumalanga turnout at or below `level`."""
    return float((d['sim_province']['province_turnout'] <= level).mean())
