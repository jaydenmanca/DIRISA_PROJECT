"""Civic-editorial colour tokens, Streamlit CSS, and the Altair 6 chart theme."""

import altair as alt
import streamlit as st

TOKENS = {
    'surface': '#fcfcfb', 'raised': '#ffffff', 'plane': '#f5f4f0',
    'ink': '#0b0b0b', 'ink2': '#52514e', 'muted': '#898781',
    'grid': '#e1e0d9', 'blue': '#2a78d6', 'blue_light': '#86b6ef',
    'orange': '#eb6834', 'red': '#e34948', 'mid': '#f0efec',
    'reference': '#898781',
}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:wght@600&family=Inter:wght@400;500;600;700&display=swap');
:root { color-scheme: light; }
html, body, [class*="css"], [data-testid="stApp"] { font-family: Inter, Arial, sans-serif; }
[data-testid="stApp"] { background: #fcfcfb; color: #0b0b0b; }
[data-testid="stMainBlockContainer"] { max-width: 1280px; padding: 18px 32px 64px; }
h1, h2, h3, .editorial-title, .wordmark { font-family: Fraunces, Georgia, serif !important; font-weight: 600 !important; letter-spacing: -.025em; }
h1 { font-size: 36px !important; line-height: 1.2 !important; }
h2 { font-size: 24px !important; line-height: 1.3 !important; }
p, li { line-height: 1.6; }
[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"], footer { display: none !important; }
[data-testid="stTabs"] [role="tablist"] { gap: 28px; border-bottom: 1px solid #e1e0d9; overflow-x: auto; flex-wrap: nowrap; scrollbar-width: none; }
[data-testid="stTabs"] [role="tablist"]::-webkit-scrollbar { display: none; }
[data-testid="stTabs"] [role="tab"] { white-space: nowrap; border-radius: 0; color: #52514e; font-size: 14px; font-weight: 600; padding: 14px 2px; }
[data-testid="stTabs"] [role="tab"][aria-selected="true"] { color: #0b0b0b; border-bottom: 2px solid #2a78d6; }
[data-testid="stTabs"] [role="tabpanel"] { padding-top: 28px; }
[data-testid="stSlider"] [role="slider"] { box-shadow: 0 0 0 4px #fcfcfb; }
[data-testid="stSlider"] [data-baseweb="slider"] { padding-top: 10px; }
[data-testid="stButton"] button, [data-testid="stDownloadButton"] button { border-radius: 8px; font-weight: 600; }
[data-testid="stButton"] button:focus-visible, [data-testid="stDownloadButton"] button:focus-visible,
[role="tab"]:focus-visible, [role="slider"]:focus-visible { outline: 2px solid #2a78d6 !important; outline-offset: 2px; }
.site-header { display:flex; align-items:center; justify-content:space-between; gap:20px; border-bottom:1px solid #e1e0d9; padding:4px 0 16px; margin-bottom:3px; }
.brand-row { display:flex; align-items:center; gap:12px; min-width:0; }
.brand-mark { width:34px; height:34px; flex:none; }
.wordmark { font-size:19px; line-height:1.1; color:#0b0b0b; }
.descriptor { font-size:12px; color:#52514e; margin-top:2px; }
.freshness { font-size:12px; color:#52514e; text-align:right; white-space:nowrap; }
.eyebrow { font-size:11px; font-weight:700; letter-spacing:.12em; text-transform:uppercase; color:#52514e; margin:0 0 9px; }
.section-title { margin:0 0 7px; font-size:27px; line-height:1.2; }
.section-dek { margin:0 0 24px; color:#52514e; max-width:72ch; font-size:15px; }
.hero-band { background:#f5f4f0; border-radius:10px; padding:34px 34px 26px; min-height:240px; display:flex; flex-direction:column; justify-content:center; }
.hero-band h1 { max-width:17ch; margin:0 0 13px; font-size:clamp(32px,3vw,48px) !important; }
.hero-band p { max-width:60ch; color:#52514e; margin:0; font-size:16px; }
.hero-art { display:block; width:100%; height:auto; border-radius:10px; }
.site-footer a { color:#52514e; text-decoration:underline; text-underline-offset:2px; }
.kpi { border-top:2px solid #e1e0d9; padding:13px 0 14px; min-height:116px; }
.kpi.hero { border-top-color:#2a78d6; min-height:126px; }
.kpi-label { font-size:12px; color:#52514e; letter-spacing:.01em; }
.kpi-value { font-family:Fraunces,Georgia,serif; font-size:34px; line-height:1.16; margin:5px 0; color:#0b0b0b; }
.kpi.hero .kpi-value { font-size:38px; }
.kpi-context { font-size:12px; color:#52514e; line-height:1.35; }
.insight { border-left:3px solid #2a78d6; background:#f5f4f0; padding:16px 18px; border-radius:0 8px 8px 0; min-height:118px; }
.insight.caution { border-left-color:#898781; }
.insight.trap { border-left-color:#eb6834; }
.insight strong { display:block; font-size:15px; margin-bottom:6px; }
.insight p { margin:0; color:#52514e; font-size:13px; line-height:1.48; }
.insight ul.pts { margin:0; padding-left:16px; color:#52514e; font-size:13px; line-height:1.5; }
.insight ul.pts li { margin:2px 0; }
.key { border:1px solid #e1e0d9; border-radius:10px; background:#fff; padding:10px 14px 8px; margin:8px 0 14px; }
.key-title { font-size:11px; font-weight:700; letter-spacing:.12em; text-transform:uppercase; color:#898781; margin-bottom:6px; }
.key-grid { display:grid; grid-template-columns:repeat(auto-fill, minmax(250px, 1fr)); gap:4px 22px; }
.k-row { display:flex; align-items:baseline; gap:8px; font-size:12.5px; color:#52514e; line-height:1.4; }
.k-row b { color:#0b0b0b; font-weight:600; white-space:nowrap; }
.k-sym { flex:none; display:inline-block; width:10px; height:10px; transform:translateY(1px); }
.k-sym.dot { border-radius:50%; } .k-sym.ring { border-radius:50%; border:2px solid; box-sizing:border-box; }
.k-sym.line { height:2px; width:14px; transform:translateY(-3px); } .k-sym.bar { width:14px; height:8px; border-radius:2px; }
.k-sym.none { width:0; }
.chip { display:inline-block; background:#f5f4f0; color:#52514e; border-radius:999px; padding:5px 11px; font-size:12px; margin:2px 6px 2px 0; }
.chip img { width:14px; height:14px; vertical-align:-2px; margin-right:5px; }
.mood-number { font-family:Fraunces,Georgia,serif; font-size:48px; line-height:1; letter-spacing:-.04em; color:#0b0b0b; margin:12px 0 16px; }
.scenario-note, .footnote { font-size:12px; line-height:1.5; color:#52514e; }
.map-legend { background:#fff; border:1px solid #e1e0d9; border-radius:8px; padding:10px 13px; margin-top:10px; }
.legend-title { font-size:12px; font-weight:600; margin-bottom:6px; }
.legend-ramp { height:9px; border-radius:999px; }
.legend-ticks { display:flex; justify-content:space-between; color:#52514e; font-size:11px; margin-top:5px; }
.two-step { display:flex; flex-wrap:wrap; align-items:center; gap:10px; padding:20px; background:#f5f4f0; border-radius:10px; }
.step-block { background:#fff; border:1px solid #e1e0d9; border-radius:8px; padding:11px 14px; flex:1; min-width:145px; font-size:13px; }
.step-block strong { display:block; font-size:16px; margin-bottom:3px; }
.step-op { color:#898781; font-size:23px; }
.site-footer { border-top:1px solid #e1e0d9; margin-top:46px; padding-top:17px; color:#52514e; font-size:11px; line-height:1.6; }
.prose { max-width:72ch; }
.prose h3 { margin-top:28px; }
@media (max-width:700px) {
 [data-testid="stMainBlockContainer"] { padding:10px 16px 40px; }
 .site-header { align-items:flex-start; padding-bottom:12px; }
 .wordmark { font-size:16px; }
 .descriptor { font-size:10px; }
 .freshness { display:none; }
 .hero-band { min-height:180px; padding:24px 20px; }
 .hero-band h1 { font-size:32px !important; }
 .kpi { min-height:0; }
 .kpi-value, .kpi.hero .kpi-value { font-size:30px; }
 .mood-number { font-size:40px; }
 .section-title { font-size:24px; }
}
@media (prefers-reduced-motion:reduce) { *, *::before, *::after { transition-duration:0.01ms !important; animation-duration:0.01ms !important; } }
</style>
"""


def apply_theme():
    """Install the small CSS layer and a consistent Vega-Lite theme."""
    st.markdown(CSS, unsafe_allow_html=True)
    if 'civic_editorial' not in alt.theme.names():
        @alt.theme.register('civic_editorial', enable=True)
        def civic_editorial():
            return {
                'config': {
                    'background': TOKENS['surface'], 'view': {'stroke': None},
                    'font': 'Inter, Arial, sans-serif',
                    'axis': {'labelFont': 'Inter, Arial, sans-serif', 'titleFont': 'Inter, Arial, sans-serif',
                             'labelColor': TOKENS['ink2'], 'titleColor': TOKENS['ink2'],
                             'labelFontSize': 11, 'titleFontSize': 12, 'gridColor': TOKENS['grid'],
                             'gridOpacity': 1, 'domain': False, 'ticks': False},
                    'axisX': {'grid': False}, 'axisY': {'grid': True},
                    'legend': {'labelColor': TOKENS['ink2'], 'titleColor': TOKENS['ink2'],
                               'labelFontSize': 11, 'titleFontSize': 12},
                    'title': {'font': 'Fraunces, Georgia, serif', 'fontSize': 17,
                              'fontWeight': 600, 'color': TOKENS['ink']},
                }
            }
    else:
        alt.theme.enable('civic_editorial')
