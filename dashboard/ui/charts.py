"""Reusable Altair charts for the six editorial views."""

import altair as alt
import pandas as pd

from dashboard.ui.theme import TOKENS as T

APPROACHES = ['Two-step forecast', 'One-step model (first version)', 'Same as last election']
APPROACH_COLOURS = [T['blue'], T['orange'], T['reference']]


def headline_chart(h):
    """Compare the observed roll/ballots with the 2026 roll and ballot scenario."""
    rows = [
        ('Registered voters', '2021 actual', h['registered_2021']),
        ('Registered voters', '2026 roll', h['registered_2026']),
        ('Ballots cast', '2021 actual', h['ballots_2021']),
        ('Ballots cast', '2026 scenario', h['ballots_2026']),
    ]
    frame = pd.DataFrame(rows, columns=['measure', 'series', 'value'])
    frame['millions'] = frame['value'] / 1_000_000
    frame['year'] = frame['series'].str[:4]
    base = alt.Chart(frame).encode(
        x=alt.X('measure:N', title=None, sort=['Registered voters', 'Ballots cast'], axis=alt.Axis(labelAngle=0)),
        xOffset=alt.XOffset('year:N', sort=['2021', '2026']),
    )
    bars = base.mark_bar(cornerRadiusEnd=3, size=45).encode(
        y=alt.Y('millions:Q', title='Millions of people / ballots', scale=alt.Scale(domain=[0, 2.5])),
        color=alt.Color('year:N', scale=alt.Scale(domain=['2021', '2026'],
                                                 range=[T['reference'], T['blue']]), title='Year'),
        tooltip=[alt.Tooltip('measure:N', title='Measure'), alt.Tooltip('series:N', title='Basis'),
                 alt.Tooltip('value:Q', format=',.0f', title='Count')],
    )
    error = pd.DataFrame([{'measure': 'Ballots cast', 'year': '2026',
                           'low': h['ballots_2026_low'] / 1_000_000,
                           'high': h['ballots_2026_high'] / 1_000_000}])
    rule = alt.Chart(error).mark_rule(color=T['ink'], strokeWidth=2).encode(
        x=alt.X('measure:N', sort=['Registered voters', 'Ballots cast']),
        xOffset=alt.XOffset('year:N', sort=['2021', '2026']), y='low:Q', y2='high:Q',
    )
    return (bars + rule).properties(height=270)


def history_chart(code, features, forecast, province_series):
    """Show local election history with an explicitly separate forecast point."""
    years = [2000, 2006, 2011, 2016, 2021]
    frame = pd.DataFrame({
        'year': years * 2,
        'turnout': [features[f'turnout_{year}'] for year in years] +
                   [province_series.loc[year] for year in years],
        'series': ['Municipality'] * len(years) + ['Mpumalanga'] * len(years),
    })
    lines = alt.Chart(frame).mark_line(point=alt.OverlayMarkDef(size=55), strokeWidth=2).encode(
        x=alt.X('year:Q', title='Local election year', scale=alt.Scale(domain=[2000, 2027]),
                axis=alt.Axis(values=years + [2026], format='d')),
        y=alt.Y('turnout:Q', title='Turnout (%)', scale=alt.Scale(domain=[20, 70])),
        color=alt.Color('series:N', scale=alt.Scale(domain=['Municipality', 'Mpumalanga'],
                                                   range=[T['blue'], T['reference']]), title=None),
        tooltip=[alt.Tooltip('series:N', title='Series'), alt.Tooltip('year:Q', format='.0f', title='Year'),
                 alt.Tooltip('turnout:Q', format='.1f', title='Turnout (%)')],
    )
    fc = pd.DataFrame([{'year': 2026, 'turnout': forecast['turnout_2026_forecast'],
                        'low': forecast['range_low'], 'high': forecast['range_high']}])
    interval = alt.Chart(fc).mark_rule(color=T['blue'], strokeWidth=2).encode(
        x='year:Q', y='low:Q', y2='high:Q',
        tooltip=[alt.Tooltip('low:Q', format='.1f', title='Scenario low (%)'),
                 alt.Tooltip('high:Q', format='.1f', title='Scenario high (%)')],
    )
    point = alt.Chart(fc).mark_point(filled=False, size=155, strokeWidth=3, color=T['blue']).encode(
        x='year:Q', y='turnout:Q',
        tooltip=[alt.Tooltip('turnout:Q', format='.1f', title='2026 forecast (%)')],
    )
    label = alt.Chart(fc).mark_text(align='left', dx=8, dy=-8, color=T['ink2'], fontSize=11).encode(
        x='year:Q', y='turnout:Q', text=alt.value('forecast'))
    return (lines + interval + point + label).properties(height=285)


def gap_chart(gap):
    """Partition 100 eligible citizens into the three observed 2021 outcomes."""
    frame = pd.DataFrame([
        {'basis': '2021 observed', 'segment': 'Voted', 'value': gap['voted_per_100'], 'order': 1},
        {'basis': '2021 observed', 'segment': 'Registered, did not vote',
         'value': gap['registered_not_voted_per_100'], 'order': 2},
        {'basis': '2021 observed', 'segment': 'Not registered',
         'value': gap['not_registered_per_100'], 'order': 3},
    ])
    chart = alt.Chart(frame).mark_bar(size=49).encode(
        x=alt.X('value:Q', stack='zero', scale=alt.Scale(domain=[0, 100]),
                title='Of every 100 eligible citizens'),
        y=alt.Y('basis:N', title=None), order='order:Q',
        color=alt.Color('segment:N', scale=alt.Scale(
            domain=['Voted', 'Registered, did not vote', 'Not registered'],
            range=[T['blue'], T['orange'], '#d4d2ca']), title=None),
        tooltip=[alt.Tooltip('segment:N', title='Group'),
                 alt.Tooltip('value:Q', format='.1f', title='People per 100')],
    )
    labels = alt.Chart(frame).mark_text(color=T['ink'], fontSize=11).encode(
        x=alt.X('value:Q', stack='center'), y='basis:N', order='order:Q',
        text=alt.Text('value:Q', format='.0f'))
    return (chart + labels).properties(height=135)


def coverage_chart(curve, teams):
    """Show the cumulative share of at-risk-roll voters reached by team count."""
    selected = curve.loc[curve['teams'] == teams]
    base = alt.Chart(curve).mark_line(color=T['blue'], strokeWidth=2.5).encode(
        x=alt.X('teams:Q', title='Teams (one per district)'),
        y=alt.Y('share_reached:Q', title='At-risk voters reached (%)', scale=alt.Scale(domain=[0, 100])),
        tooltip=[alt.Tooltip('teams:Q', format=',.0f', title='Teams'),
                 alt.Tooltip('voters_reached:Q', format=',.0f', title='Voters reached'),
                 alt.Tooltip('share_reached:Q', format='.1f', title='Share (%)')],
    )
    rule = alt.Chart(selected).mark_rule(color=T['orange'], strokeDash=[4, 4]).encode(x='teams:Q')
    dot = alt.Chart(selected).mark_point(filled=True, color=T['orange'], size=115).encode(
        x='teams:Q', y='share_reached:Q')
    return (base + rule + dot).properties(height=260)


def allocation_chart(by_muni):
    """Rank municipalities by the number of proposed voter-education teams."""
    bars = alt.Chart(by_muni).mark_bar(cornerRadiusEnd=3, color=T['blue']).encode(
        y=alt.Y('municipality:N', sort='-x', title=None, axis=alt.Axis(labelLimit=165)),
        x=alt.X('teams:Q', title='Teams'),
        tooltip=[alt.Tooltip('municipality:N', title='Municipality'),
                 alt.Tooltip('teams:Q', title='Teams'),
                 alt.Tooltip('voters:Q', format=',.0f', title='Voters reached')])
    text = alt.Chart(by_muni).mark_text(align='left', dx=5, fontSize=11, color=T['ink2']).encode(
        y=alt.Y('municipality:N', sort='-x'), x='teams:Q', text='teams:Q')
    return (bars + text).properties(height=max(190, 28 * len(by_muni)))


def backtest_scatter(frame):
    """Compare predicted and actual municipal turnout with a fixed equal-scale diagonal."""
    domain = [20, 75]
    diagonal = pd.DataFrame({'actual': domain, 'predicted': domain})
    line = alt.Chart(diagonal).mark_line(color=T['grid'], strokeDash=[5, 5], strokeWidth=2).encode(
        x=alt.X('actual:Q', title='Actual turnout (%)', scale=alt.Scale(domain=domain)),
        y=alt.Y('predicted:Q', title='Predicted turnout (%)', scale=alt.Scale(domain=domain)))
    dots = alt.Chart(frame).mark_circle(size=78, opacity=.78, stroke=T['surface'], strokeWidth=1).encode(
        x=alt.X('actual:Q', scale=alt.Scale(domain=domain)),
        y=alt.Y('predicted:Q', scale=alt.Scale(domain=domain)),
        color=alt.Color('approach:N', scale=alt.Scale(domain=APPROACHES, range=APPROACH_COLOURS), title=None),
        tooltip=[alt.Tooltip('municipality:N', title='Municipality'),
                 alt.Tooltip('approach:N', title='Model'),
                 alt.Tooltip('actual:Q', format='.1f', title='Actual (%)'),
                 alt.Tooltip('predicted:Q', format='.1f', title='Predicted (%)')])
    return (line + dots).properties(height=390)
