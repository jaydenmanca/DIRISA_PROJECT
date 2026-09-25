"""Small reusable presentation components with consistent data formatting."""

import base64
from html import escape
from pathlib import Path

import streamlit as st

from dashboard.ui.theme import TOKENS

ASSETS = Path(__file__).resolve().parents[1] / 'assets'


def count(value):
    """Format a whole-person count with separators."""
    return f'{round(value):,}'


def compact(value):
    """Use millions only when a large headline is easier to scan that way."""
    return f'{value / 1_000_000:.2f} m' if abs(value) >= 1_000_000 else count(value)


def pct(value):
    """Format turnout and registration percentages to one decimal."""
    return f'{value:.1f}%'


def pts(value):
    """Show a signed percentage-point difference with a true minus sign."""
    sign = '+' if value >= 0 else '−'
    return f'{sign}{abs(value):.1f} pts'


def signed_count(value):
    """Show a signed ballot or roll difference without decimals."""
    return ('+' if value >= 0 else '−') + count(abs(value))


def name(code, names):
    """Use reader-friendly place names while keeping the unambiguous code."""
    return f'{names[code]} ({code})'


def header():
    """Render the neutral product header and data-era descriptor."""
    mark = base64.b64encode((ASSETS / 'mark.svg').read_bytes()).decode('ascii')
    st.markdown(
        '<div class="site-header"><div class="brand-row">'
        f'<img class="brand-mark" src="data:image/svg+xml;base64,{mark}" alt="Abstract turnout mark">'
        '<div><div class="wordmark">Turnout 2026 · Mpumalanga</div>'
        '<div class="descriptor">Forecast and planning tool · DIRISA SDC 2026</div></div></div>'
        '<div class="freshness">Voters’ roll as of 23 Sep 2026 · Results 2000–2021</div></div>',
        unsafe_allow_html=True)


def footer():
    """Cite data publishers without imitating institutional branding."""
    st.markdown(
        '<div class="site-footer">Sources: IEC election results and voter registration · '
        'Stats SA Census 2022 · Auditor-General via National Treasury Municipal Money · '
        'Municipal Demarcation Board boundaries via geoBoundaries (CC BY 3.0 IGO).<br>'
        'Team: {TEAM NAME} · Forecasts are scenarios, not election results. '
        '<a href="?tab=method">How it works</a></div>',
        unsafe_allow_html=True)


def section(eyebrow, title, dek):
    """Introduce a page or major section with a consistent editorial hierarchy."""
    st.markdown(f'<div class="eyebrow">{escape(eyebrow)}</div>'
                f'<h2 class="section-title">{escape(title)}</h2>'
                f'<p class="section-dek">{escape(dek)}</p>', unsafe_allow_html=True)


def tile(label, value, context='', hero=False):
    """Display one KPI with its basis or comparison visible underneath."""
    kind = 'kpi hero' if hero else 'kpi'
    st.markdown(f'<div class="{kind}"><div class="kpi-label">{escape(label)}</div>'
                f'<div class="kpi-value">{escape(str(value))}</div>'
                f'<div class="kpi-context">{escape(str(context))}</div></div>', unsafe_allow_html=True)


def insight(title, body, kind='insight'):
    """Use one rule colour to distinguish evidence, caution and interpretation.
    `body` is a list of short points (preferred) or one short sentence."""
    if isinstance(body, (list, tuple)):
        inner = '<ul class="pts">' + ''.join(f'<li>{escape(str(b))}</li>' for b in body) + '</ul>'
    else:
        inner = f'<p>{escape(body)}</p>'
    st.markdown(f'<div class="insight {escape(kind)}"><strong>{escape(title)}</strong>{inner}</div>',
                unsafe_allow_html=True)


def key(items, title='Key'):
    """A map-style key: one row per symbol or term, each with a few words of meaning.
    items: (symbol, term, meaning); symbol is a colour ('#2a78d6'), 'ring:#hex', 'line:#hex',
    'bar:#hex', or '' for a plain term."""
    rows = []
    for symbol, term, meaning in items:
        if symbol.startswith('ring:'):
            mark = f'<span class="k-sym ring" style="border-color:{symbol[5:]}"></span>'
        elif symbol.startswith('line:'):
            mark = f'<span class="k-sym line" style="background:{symbol[5:]}"></span>'
        elif symbol.startswith('bar:'):
            mark = f'<span class="k-sym bar" style="background:{symbol[4:]}"></span>'
        elif symbol:
            mark = f'<span class="k-sym dot" style="background:{symbol}"></span>'
        else:
            mark = '<span class="k-sym none"></span>'
        rows.append(f'<div class="k-row">{mark}<b>{escape(term)}</b><span>{escape(meaning)}</span></div>')
    st.markdown(f'<div class="key"><div class="key-title">{escape(title)}</div>'
                f'<div class="key-grid">{"".join(rows)}</div></div>', unsafe_allow_html=True)


def chips(*labels):
    """Show short categorical facts without turning each into a heavy card."""
    st.markdown(''.join(f'<span class="chip">{escape(str(v))}</span>' for v in labels if v),
                unsafe_allow_html=True)


def venue_chips(venues):
    """Explain station-name venue categories with the original matching icon family."""
    parts = []
    for venue in sorted(set(venues)):
        if not venue or venue not in {'school', 'farm', 'tent', 'traditional',
                                      'church', 'hall', 'other'}:
            continue
        icon = base64.b64encode((ASSETS / f'venue-{venue}.svg').read_bytes()).decode('ascii')
        parts.append(f'<span class="chip"><img src="data:image/svg+xml;base64,{icon}" '
                     f'alt="">{escape(venue.capitalize())}</span>')
    if parts:
        st.markdown(''.join(parts), unsafe_allow_html=True)


def legend(title, colours, ticks, note):
    """Make map colours explainable without relying on a hover tooltip."""
    ramp = ', '.join(colours)
    labels = ''.join(f'<span>{escape(str(v))}</span>' for v in ticks)
    st.markdown(f'<div class="map-legend"><div class="legend-title">{escape(title)}</div>'
                f'<div class="legend-ramp" style="background:linear-gradient(90deg,{ramp})"></div>'
                f'<div class="legend-ticks">{labels}</div>'
                f'<div class="footnote">{escape(note)}</div></div>', unsafe_allow_html=True)


def two_step_explainer(level, local_label):
    """Show the forecast decomposition as code-rendered text, never in an image."""
    st.markdown('<div class="two-step">'
                f'<div class="step-block"><strong>{pct(level)}</strong>Province-wide scenario<br>uncertain level</div>'
                '<span class="step-op">+</span>'
                f'<div class="step-block"><strong>{escape(local_label)}</strong>Local position<br>tested on past elections</div>'
                '<span class="step-op">=</span>'
                '<div class="step-block"><strong>Turnout forecast</strong>Scenario + local position</div>'
                '</div>', unsafe_allow_html=True)
