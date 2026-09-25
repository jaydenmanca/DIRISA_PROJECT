"""DIRISA SDC 2026 civic-editorial dashboard.

Run from the repository root with: python -m streamlit run dashboard/app.py
This app reads committed derived/ outputs; it never trains or rewrites the model.
"""

from pathlib import Path
import sys

import streamlit as st

# Streamlit executes this file as a script; make the repo package importable even
# when launched from a different working directory. Never import plain "data":
# another package can already own that name in a long-lived Python process.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard import data as dd
from dashboard.ui import views
from dashboard.ui.components import footer, header
from dashboard.ui.theme import apply_theme

ASSETS = Path(__file__).resolve().parent / 'assets'
LABELS = ['Story', 'Map & mood', 'Municipality', 'IEC planner',
          'Can you trust it?', 'How it works']
SLUGS = {'story': LABELS[0], 'map': LABELS[1], 'muni': LABELS[2],
         'planner': LABELS[3], 'trust': LABELS[4], 'method': LABELS[5]}

st.set_page_config(page_title='Turnout 2026 · Mpumalanga', page_icon=str(ASSETS / 'favicon.png'),
                   layout='wide', initial_sidebar_state='collapsed')
apply_theme()

try:
    d = dd.load()
except (FileNotFoundError, KeyError, ValueError) as exc:
    st.image(str(ASSETS / 'empty-state.svg'), width=300)
    st.title('The results are not here yet')
    st.write('This dashboard reads the tables saved in `derived/`. From the repository root, '
             'run `model.ipynb` with **Restart → Run All**, then refresh this page.')
    st.caption(f'Missing or incomplete input: {exc}')
    st.stop()

central = float(d['info']['province_2026_pct']['central'])
codes = set(d['muni'].index)


def initial_mood():
    """Accept a shareable mood URL only when it is on the slider's valid grid."""
    try:
        value = float(st.query_params.get('mood', ''))
        if 30 <= value <= 50 and value * 2 == round(value * 2):
            return value
    except (TypeError, ValueError):
        pass
    return round(central * 2) / 2


def on_tab_change():
    """Keep the tab deep link in sync without touching the shared mood widget."""
    slug = next(k for k, v in SLUGS.items() if v == st.session_state.active_tab)
    st.query_params['tab'] = slug


if 'province_level' not in st.session_state:
    st.session_state.province_level = initial_mood()
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = SLUGS.get(st.query_params.get('tab', ''), LABELS[0])
if 'municipality_code' not in st.session_state:
    requested = st.query_params.get('muni', '')
    st.session_state.municipality_code = requested if requested in codes else d['muni']['local_position_forecast'].idxmin()

header()
tabs = st.tabs(LABELS, key='active_tab', on_change=on_tab_change)
renderers = [views.story, views.map_and_mood, views.municipality,
             views.planner, views.trust, views.method]

for tab, render in zip(tabs, renderers):
    if tab.open:
        with tab:
            render(d)

footer()
