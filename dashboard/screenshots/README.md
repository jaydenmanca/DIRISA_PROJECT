# Screenshot QA still to record

The automated data and Streamlit widget tests pass, but these are not substitutes
for visual review. The in-app browser was unavailable during implementation, so
no screenshot is claimed here.

Open the app in a browser and capture each of the six tabs at 1920×1080,
1366×768, and 390×844. Save final PNGs in this folder after checking:

- No text or chart-label collisions, clipping, or horizontal page overflow.
- The mobile map remains at least 320 px tall and can be panned/zoomed.
- The default map recolours from 34% to 44% mood; the low-turnout count changes
  from 68 to 2 at the 25% threshold.
- The red/blue relative map has a neutral midpoint and readable legend.
- Tables scroll within their own containers; download buttons remain visible.
- All six tabs have consistent spacing and working controls at each width.

Use the light theme. The app deliberately does not offer a separate dark theme.
