"""Smoke tests for the dashboard's locked figures and demo interactions.

Run from the repository root: python -m unittest discover -s dashboard -p test_app.py
"""

import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

from dashboard import data as dd
from dashboard.ui import maps, views


class DashboardTests(unittest.TestCase):
    """Catch missing files, changed figures and widget exceptions before recording."""

    def test_locked_model_figures(self):
        """The dashboard must not silently drift from the committed model outputs."""
        self.assertEqual(dd.__name__, 'dashboard.data')
        self.assertIs(views.dd, dd)
        self.assertIs(maps.dd, dd)
        d = dd.load()
        self.assertEqual(d['info']['headline'], {
            'registered_2021': 1902220, 'ballots_2021': 814739,
            'registered_2026': 2169700, 'ballots_2026': 860069,
            'ballots_2026_low': 738091, 'ballots_2026_high': 963322,
        })
        at_risk = d['vd'].loc[d['vd']['at_risk_district']]
        # district voter counts are on the ESTIMATED 2026 roll (2021 district roll x municipal growth)
        self.assertEqual((len(at_risk), round(at_risk['registered_voters'].sum())), (357, 527417))
        self.assertEqual(round(d['vd']['registered_voters'].sum()), 2169700)
        self.assertEqual(int(at_risk['registered_voters_2021'].sum()), 463491)
        self.assertAlmostEqual(dd.actual_2021(d), 42.8, delta=.1)
        for mood, expected in [(34, (68, 48531)), (39.5, (30, 13308)),
                               (44, (2, 537))]:
            turnout = dd.district_turnout(d, mood)
            below = turnout < 25
            result = (int(below.sum()), round(d['vd'].loc[below, 'registered_voters'].sum()))
            self.assertEqual(result, expected)
        turnout = dd.district_turnout(d, 39.5)
        for teams, result in [(50, (159306, 9)), (100, (270891, 10))]:
            plan = dd.plan_teams(d, teams, turnout)
            self.assertEqual((round(plan['registered_voters'].sum()),
                              int(plan['municipality_code_2021'].nunique())), result)
        self.assertEqual(d['priority'].sort_values('rank').head(5).index.tolist(),
                         ['MP307', 'MP302', 'MP312', 'MP316', 'MP315'])
        low_vd, high_vd = dd.district_turnout(d, 34), dd.district_turnout(d, 44)
        low_muni = dd.municipality_turnout(d, low_vd)
        high_muni = dd.municipality_turnout(d, high_vd)
        low_map, _ = maps.municipality_map(d, low_muni, dd.mood_summary(d, low_vd, 25),
                                           34, 'Turnout at this mood')
        high_map, _ = maps.municipality_map(d, high_muni, dd.mood_summary(d, high_vd, 25),
                                            44, 'Turnout at this mood')
        low_colours = [f['properties']['fill'] for f in low_map.layers[0].data['features']]
        high_colours = [f['properties']['fill'] for f in high_map.layers[0].data['features']]
        self.assertNotEqual(low_colours, high_colours,
                            'The mood map must visibly recolour when its slider moves')

    def test_explorer_payload_matches_model(self):
        """The browser explorer recomputes turnout from its payload; that maths must give the
        same locked numbers as dashboard/data.py (mirrors districtTurnout in mood_explorer.js)."""
        from dashboard.ui import interactive
        d = dd.load()
        p = interactive._mood_payload(d, 'test')
        for mood, expected in [(34, (68, 48531)), (39.5, (30, 13308)), (44, (2, 537))]:
            n = voters = 0
            for code, m, local, beta, reg, venue, t21, p_low, p10, p90 in p['vds']:
                t = min(100, max(0, mood + local + (beta - 1) * (mood - p['central'])))
                if t < 25:
                    n += 1
                    voters += reg
            self.assertEqual((n, round(voters)), expected)
        self.assertEqual(len(p['vds']), 1785)
        self.assertEqual(len(p['geo']), 17)

    def test_simulation_outputs(self):
        """The 2026 simulation headline must stay tied to the notebook run."""
        d = dd.load()
        sim = d['info']['simulation']
        self.assertEqual(sim['n_simulations'], 10000)
        self.assertEqual(len(d['sim_province']), 10000)
        self.assertAlmostEqual(sim['main']['p_below_record_low'], 0.7248, places=3)
        self.assertTrue(sim['calibration_step_used'])
        self.assertAlmostEqual(dd.chance_at_or_below(d, 100), 1.0)
        self.assertTrue(((d['vd']['p_below_25'] >= 0) & (d['vd']['p_below_25'] <= 1)).all())

    def test_demo_path(self):
        """Every requested view and high-value control must rerun cleanly."""
        at = AppTest.from_file(str(Path(__file__).resolve().parent / 'app.py'),
                               default_timeout=120).run()
        self.assertFalse(at.exception)
        # AppTest does not expose a tab-click event for tracked/lazy st.tabs, so
        # select each tab and control through Session State before its rerun.
        # The mood slider lives in the browser-side explorer (ui/interactive.py); it writes the
        # level and threshold back to Session State, which is what the table below follows.
        for mood in [34.0, 44.0, 39.5]:
            at.session_state['active_tab'] = 'Map & mood'
            at.session_state['province_level'] = mood
            at.run()
            self.assertFalse(at.exception)
        at.session_state['active_tab'] = 'Map & mood'
        at.session_state['threshold'] = 30
        at.run()
        self.assertFalse(at.exception)

        for code in ['MP312', 'MP311', 'MP325']:
            at.session_state['active_tab'] = 'Municipality'
            at.session_state['municipality_code'] = code
            at.run()
            self.assertFalse(at.exception)
            self.assertEqual(at.selectbox(key='municipality_code').value, code)

        at.session_state['active_tab'] = 'IEC planner'
        at.session_state['team_count'] = 100
        at.run()
        self.assertFalse(at.exception)
        self.assertEqual(at.slider(key='team_count').value, 100)
        at.session_state['active_tab'] = 'IEC planner'
        at.session_state['weight_weak_audit'] = 0.0
        at.run()
        self.assertFalse(at.exception)

        for year in [2011, 2016, 2021]:
            at.session_state['active_tab'] = 'Can you trust it?'
            at.session_state['backtest_year'] = year
            at.run()
            self.assertFalse(at.exception)
        at.session_state['active_tab'] = 'How it works'
        at.run()
        self.assertFalse(at.exception)


if __name__ == '__main__':
    unittest.main()
