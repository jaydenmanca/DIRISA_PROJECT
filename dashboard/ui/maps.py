"""Pydeck map layers and legend metadata for the national-mood view."""

import pydeck as pdk

from dashboard import data as dd
from dashboard.ui.theme import TOKENS as T


def municipality_map(d, turnout_muni, summary, level, colour_by):
    """Build a map without deep-copying the static polygon coordinates on each rerun."""
    local = turnout_muni - level
    if colour_by == 'Priority':
        values = d['priority']['priority_score'].reindex(turnout_muni.index)
        colours = dd.colour_scale(values, (253, 231, 218), (235, 104, 52),
                                  (168, 67, 27), values.min(), values.max())
        legend = ('Priority score', ['#fde7da', '#f5a877', '#eb6834', '#a8431b'],
                  [f'{values.min():.0f}', f'{values.max():.0f}'],
                  'Published priority weights use the central forecast; this layer does not change with mood.')
    elif colour_by == 'Above / below province':
        values = local
        colours = dd.colour_scale(values, (227, 73, 72), (240, 239, 236),
                                  (42, 120, 214), -6, 6, vmid=0)
        legend = ('Turnout relative to chosen mood',
                  ['#e34948', '#f0a0a0', '#f0efec', '#86b6ef', '#2a78d6'],
                  ['−6 pts', '0', '+6 pts'],
                  'Red means below the province; blue means above. Scale stays fixed as mood moves.')
    else:
        values = turnout_muni
        colours = dd.colour_scale(values, (205, 226, 251), (134, 182, 239),
                                  (16, 66, 129), 25, 55)
        legend = ('Turnout at this mood',
                  ['#cde2fb', '#86b6ef', '#2a78d6', '#104281'],
                  ['25%', '40%', '55%'],
                  'Fixed turnout scale: darker blue means higher turnout. Colours change as mood moves.')
    colour_of = dict(zip(values.index, colours))
    features = []
    for feature in d['geojson']['features']:
        code = feature['properties']['municipality_code_2021']
        features.append({'type': 'Feature', 'geometry': feature['geometry'],
                         'properties': {'municipality_code_2021': code,
                                        'name': d['names'][code], 'fill': colour_of[code],
                                        'turnout': f'{turnout_muni[code]:.1f}%',
                                        'position': f'{local[code]:+.1f} pts',
                                        'below': int(summary.loc[code, 'districts_below']),
                                        'rank': int(d['priority'].loc[code, 'rank'])}})
    geo = {'type': 'FeatureCollection', 'features': features}
    labels = dd.map_label_points(d['geojson'])
    for point in labels:
        point['label'] = d['names'][point['code']].replace('City of ', '')
    deck = pdk.Deck(
        layers=[
            pdk.Layer('GeoJsonLayer', geo, id='municipalities', pickable=True,
                      stroked=True, filled=True, get_fill_color='properties.fill',
                      get_line_color=[252, 252, 251], line_width_min_pixels=1.5),
            pdk.Layer('TextLayer', labels, id='labels', pickable=False,
                      get_position='[lon, lat]', get_text='label', get_size=11,
                      get_color=[11, 11, 11], get_text_anchor='middle',
                      get_alignment_baseline='center', outline_width=2,
                      outline_color=[252, 252, 251]),
        ],
        initial_view_state=pdk.ViewState(latitude=-25.8, longitude=30.3, zoom=6.45,
                                         min_zoom=5, max_zoom=10, pitch=0, bearing=0),
        map_style=None,
        tooltip={'html': '<b>{name}</b><br>Turnout at this mood: {turnout}<br>'
                         'Local position: {position}<br>Districts below threshold: {below}'
                         '<br>Priority rank: #{rank}',
                 'style': {'backgroundColor': T['raised'], 'color': T['ink'],
                           'fontSize': '12px', 'padding': '10px', 'borderRadius': '8px'}},
    )
    return deck, legend
