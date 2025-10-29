import numpy as np
import streamlit as st
from plotly import graph_objects as go


# ========================================================
# 1) PAGE + THEME (slide-ready, blues-only)
# ========================================================
st.set_page_config(page_title="Urban Performance", layout="wide")

# ---- Color system -------------------------------------------------------
PALETTE = {
    "bg": "#08121C",           # app background
    "text": "#EAF4FF",         # primary text
    "muted": "rgba(234,244,255,0.72)",  # secondary text
    "primary": "#39A8FF",       # main blue for emphasis
    "primary_2": "#73C0FF",     # mid blue (lines, active tracks)
    "primary_3": "#B9DDFF",     # light blue (fills)
    "line_soft": "rgba(115,192,255,0.25)",
    "grid": "rgba(255,255,255,0.10)",
}

# Distinct shades of the same hue family for categories
CATEGORY_ORDER = ["Economic", "Environmental", "Social"]
CATEGORY_COLORS = {
    "Economic": PALETTE["primary"],     # strong blue
    "Environmental": "#4FB7FF",        # medium blue
    "Social": "#9AD2FF",              # light blue
}

# ---- CSS (fix header band, unify sliders, compact spacing) --------------
CSS = f"""
<style>
  /* Eliminate any white band/topbar and match the background */
  html, body {{ background: {PALETTE['bg']}; }}
  header[data-testid="stHeader"] {{ background: {PALETTE['bg']}; box-shadow: none; visibility: hidden; height: 0; }}
  .stApp {{ background: {PALETTE['bg']}; color: {PALETTE['text']}; font-family: 'Inter','Montserrat',system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif; }}

  /* Wider canvas for PPT look */
  .block-container {{ max-width: 1540px; padding: .6rem 1.2rem .4rem; }}

  h1,h2,h3,h4 {{ letter-spacing: .02em; font-weight: 600; }}
  .app-title {{ font-size: 2.0rem; letter-spacing: .20em; text-transform: uppercase; margin: 0 0 .3rem 0; color: {PALETTE['text']}; }}

  .section-label {{ text-transform: uppercase; letter-spacing: .22em; color: {PALETTE['primary_3']}; font-size: .68rem; margin: .2rem 0 .3rem; }}

  /* Search input */
  div[data-testid="stTextInput"] input {{ background: rgba(8,18,28,.6); border: 1px solid {PALETTE['line_soft']}; color: {PALETTE['text']}; font-size: .92rem; padding: .38rem .6rem; border-radius: 6px; text-transform: uppercase; letter-spacing: .08em; }}
  div[data-testid="stTextInput"] input::placeholder {{ color: {PALETTE['muted']}; }}

  /* Mini metric bars */
  .mini-metric {{ display: grid; grid-template-columns: 1fr auto; gap: .18rem .5rem; align-items: center; margin-bottom: .2rem; }}
  .mini-label {{ font-size: .68rem; letter-spacing: .16em; text-transform: uppercase; color: {PALETTE['muted']}; }}
  .mini-track {{ grid-column: 1 / -1; width: 100%; height: 6px; border-radius: 999px; background: rgba(115,192,255,.15); position: relative; overflow: hidden; }}
  .mini-fill {{ position: absolute; inset: 0 auto 0 0; height: 100%; border-radius: 999px; }}
  .mini-value {{ font-size: .68rem; letter-spacing: .10em; color: {PALETTE['muted']}; }}

  /* Slider system (compact + blue; overrides any default red accents) */
  div[data-testid="stSlider"] {{ margin: .2rem 0 .4rem; }}
  /* rail */
  div[data-testid="stSlider"] [data-baseweb="slider"] > div[style*="height"] {{ height: 2px !important; background: rgba(115,192,255,.28); }}
  /* active track */
  div[data-testid="stSlider"] [data-baseweb="slider"] > div[style*="height"]:not(:first-of-type) {{ background: {PALETTE['primary_2']}!important; }}
  /* thumb */
  div[data-testid="stSlider"] [role="slider"] {{ width: 12px; height:12px; border-radius: 999px; background: {PALETTE['primary_2']}; border:1px solid #07101A; box-shadow:none; }}
  /* numeric label color (Streamlit renders labels) */
  div[data-testid="stSlider"] label {{ color: {PALETTE['primary_3']} !important; font-weight: 600; }}
# ADD these rules inside your CSS string (after your current slider block)

  /* Remove BaseWeb's red value bubble & use our own pill (below) */
  div[data-testid="stSlider"] [data-baseweb="slider"] div[aria-hidden="true"] {{ display: none !important;}}

  /* Force any leftover slider accent/focus states to our blue */
  div[data-testid="stSlider"] [data-baseweb="slider"] *:focus {{
    outline: none !important;
  }}
  div[data-testid="stSlider"] [data-baseweb="slider"] * {{
    caret-color: {PALETTE['primary_2']} !important;
    color: {PALETTE['primary_3']} !important;
  }}

  /* Our tiny value pill that replaces the red number */
  .value-pill {{
    display:inline-block; min-width: 28px; padding: 2px 6px; 
    border-radius: 6px; text-align:center; font-size:.70rem; 
    color: {PALETTE['bg']}; background: {PALETTE['primary_2']};
    border: 1px solid rgba(115,192,255,.45);
    margin-left:.5rem;
  }}

  .column-heading {{ font-size:.72rem; letter-spacing:.18em; text-transform:uppercase; color:{PALETTE['muted']}; margin:.1rem 0 .1rem; }}
  .caption-text {{ color:{PALETTE['muted']}; font-size:.70rem; letter-spacing:.10em; text-transform:uppercase; }}
  hr {{ border-color: rgba(115,192,255,.15); margin:.5rem 0 .3rem; }}

  /* Chevron button for expanding sub-sliders (refined look) */
  .slider-toggle .stButton > button {{
    width: 22px; height: 22px; border-radius: 6px; padding: 0; line-height: 1; font-size: 14px;
    background: rgba(57,168,255,0.10) !important;
    color: {PALETTE['primary_2']} !important;
    border: 1px solid rgba(115,192,255,.45) !important; 
    box-shadow: none !important;
  }}
  .slider-toggle .stButton > button:hover {{ 
    background: rgba(57,168,255,0.18) !important; 
  }}
  .slider-toggle .stButton > button:active {{
    transform: translateY(1px); 
  }}

</style>
"""

st.markdown(CSS, unsafe_allow_html=True)

# ========================================================
# 2) DATA (same semantics)
# ========================================================
YEARS = list(range(2025, 2036))

CITY_DATA = {
    "Skyhaven": {
        "video_url": "https://www.youtube.com/watch?v=lJIrF4YjHfQ",
        "kpis": [
            {"name": "Inclusive GDP Growth", "category": "Economic", "value": 5.2},
            {"name": "Innovation Output", "category": "Economic", "value": 6.1},
            {"name": "Green Employment", "category": "Economic", "value": 4.8},
            {"name": "Digital Services", "category": "Economic", "value": 5.6},
            {"name": "Circular Procurement", "category": "Environmental", "value": 3.9},
            {"name": "Renewable Share", "category": "Environmental", "value": 4.5},
            {"name": "Transit Emissions", "category": "Environmental", "value": 3.4},
            {"name": "Urban Canopy", "category": "Environmental", "value": 4.1},
            {"name": "Healthy Mobility", "category": "Social", "value": 5.7},
            {"name": "Accessible Housing", "category": "Social", "value": 4.6},
            {"name": "Community Safety", "category": "Social", "value": 5.1},
            {"name": "Active Commons", "category": "Social", "value": 4.2},
        ],
        "time_series": {
            "economy": [98, 100, 103, 105, 108, 111, 114, 118, 121, 124, 128],
            "environment": [152, 149, 145, 142, 138, 134, 131, 126, 122, 119, 116],
            "health": [84, 86, 88, 90, 92, 94, 97, 99, 101, 103, 106],
        },
    },
    "Harborlight": {
        "video_url": "https://www.youtube.com/watch?v=ysz5S6PUM-U",
        "kpis": [
            {"name": "Inclusive GDP Growth", "category": "Economic", "value": 4.3},
            {"name": "Innovation Output", "category": "Economic", "value": 4.9},
            {"name": "Green Employment", "category": "Economic", "value": 3.7},
            {"name": "Digital Services", "category": "Economic", "value": 4.4},
            {"name": "Circular Procurement", "category": "Environmental", "value": 3.1},
            {"name": "Renewable Share", "category": "Environmental", "value": 4.0},
            {"name": "Transit Emissions", "category": "Environmental", "value": 2.9},
            {"name": "Urban Canopy", "category": "Environmental", "value": 3.5},
            {"name": "Healthy Mobility", "category": "Social", "value": 4.6},
            {"name": "Accessible Housing", "category": "Social", "value": 3.8},
            {"name": "Community Safety", "category": "Social", "value": 4.2},
            {"name": "Active Commons", "category": "Social", "value": 3.9},
        ],
        "time_series": {
            "economy": [93, 95, 96, 99, 101, 103, 106, 109, 112, 114, 118],
            "environment": [164, 161, 158, 154, 151, 147, 144, 140, 136, 133, 130],
            "health": [79, 80, 82, 83, 85, 87, 89, 91, 93, 95, 98],
        },
    },
}

# Interventions (weights define spillover into categories)
INTERVENTIONS = [
    {"id": "upzoning",   "label": "Upzoning",                        "impact_weights": {"Economic": .45, "Environmental": .15, "Social": .40}, "sub_sliders": [{"label":"Housing Units Added (per yr)","min":0,"max":1800,"value":400},{"label":"Inclusionary %","min":0,"max":60,"value":12}]},
    {"id": "retrofits",  "label": "Building Retrofits & Standards", "impact_weights": {"Economic": .25, "Environmental": .55, "Social": .20}, "sub_sliders": [{"label":"Net-Zero Retrofits (per yr)","min":0,"max":200,"value":40},{"label":"Local Workforce Share (%)","min":0,"max":100,"value":20}]},
    {"id": "grid",       "label": "Clean Energy & Grid Modernization","impact_weights": {"Economic": .35, "Environmental": .45, "Social": .20}, "sub_sliders": [{"label":"Renewables Added (MW)","min":0,"max":600,"value":120},{"label":"Storage Capacity (MWh)","min":0,"max":800,"value":150}]},
    {"id": "mixed_use",  "label": "Mixed Use Zoning",               "impact_weights": {"Economic": .50, "Environmental": .25, "Social": .25}, "sub_sliders": [{"label":"Transit Parcels (%)","min":0,"max":60,"value":15},{"label":"Community Amenities (#)","min":0,"max":50,"value":10}]},
    {"id": "freight",    "label": "Urban Freight Transition",       "impact_weights": {"Economic": .35, "Environmental": .45, "Social": .20}, "sub_sliders": [{"label":"EV Fleets Converted (%)","min":0,"max":100,"value":20},{"label":"Consolidation Hubs (#)","min":0,"max":40,"value":8}]},
    {"id": "mobility",   "label": "Active Mobility Networks",       "impact_weights": {"Economic": .25, "Environmental": .40, "Social": .35}, "sub_sliders": [{"label":"Protected Lanes (km)","min":0,"max":120,"value":20},{"label":"Mode Share Target (%)","min":0,"max":60,"value":12}]},
    {"id": "circular",   "label": "Circular Waste & Materials",     "impact_weights": {"Economic": .10, "Environmental": .60, "Social": .30}, "sub_sliders": [{"label":"Organic Diversion (%)","min":0,"max":90,"value":20},{"label":"Recycling Coverage (%)","min":0,"max":100,"value":35}]},
    {"id": "transit",    "label": "Public Transit Expansion",       "impact_weights": {"Economic": .20, "Environmental": .35, "Social": .45}, "sub_sliders": [{"label":"New Routes (#)","min":0,"max":25,"value":5},{"label":"Service Frequency (%)","min":0,"max":80,"value":15}]},
]

INTERVENTION_LOOKUP = {i["id"]: i for i in INTERVENTIONS}

# ========================================================
# 3) HELPERS (focused)
# ========================================================

def find_city(match: str) -> str:
    """Find city by exact or prefix match; default to first."""
    if not match:
        return list(CITY_DATA.keys())[0]
    for c in CITY_DATA:
        if c.lower().startswith(match.strip().lower()):
            return c
    return list(CITY_DATA.keys())[0]


def compute_category_scores_from_state() -> dict[str, float]:
    """Aggregate intervention intensities (main + sub averages) into
    category scores using intervention impact weights. Output capped at 100."""
    scores = {c: 0.0 for c in CATEGORY_ORDER}
    for it in INTERVENTIONS:
        main = float(st.session_state.get(f"main_{it['id']}", 0))
        subs, defs = [], it["sub_sliders"]
        for s in defs:
            subs.append(float(st.session_state.get(f"{it['id']}_{s['label']}", 0)))
        if subs:
            norm = [(v / s["max"] * 100) if s["max"] else 0 for v, s in zip(subs, defs)]
            intensity = (main + float(np.mean(norm))) / 2
        else:
            intensity = main
        for cat, w in it["impact_weights"].items():
            scores[cat] += intensity * w
    return {k: min(v, 100.0) for k, v in scores.items()}


def improved_kpis(city_key: str, cat_scores: dict[str, float]) -> list[float]:
    """Scale each KPI by its category lift. Max value is clipped at 10."""
    vals = []
    for k in CITY_DATA[city_key]["kpis"]:
        base = k["value"]
        lift = 1 + (cat_scores[k["category"]] / 100) * 0.35
        vals.append(round(min(base * lift, 10.0), 2))
    return vals

# ---------- Charts (blues-only) -----------------------------------------

def radar(current: list[float], improved: list[float], labels: list[str], cats: list[str]) -> go.Figure:
    """Radar chart with faint category envelopes; two blue tones for Current/2035."""
    maxv = 10
    n = len(labels)
    angles = np.linspace(0, 360, n, endpoint=False)
    thetas = angles.tolist() + [angles[0]]

    base = go.Scatterpolar(
        r=current + [current[0]], theta=thetas,
        name="Current", mode="lines",
        line=dict(color=PALETTE["primary_2"], width=2),
        fill="toself", fillcolor="rgba(115,192,255,0.20)",
    )
    imp = go.Scatterpolar(
        r=improved + [improved[0]], theta=thetas,
        name="2035", mode="lines",
        line=dict(color=PALETTE["primary"], width=3),
        fill="toself", fillcolor="rgba(57,168,255,0.28)",
    )

    envs = []  # light envelopes per category
    for cat in CATEGORY_ORDER:
        idx = [i for i, c in enumerate(cats) if c == cat]
        if not idx: continue
        cat_theta = [angles[i] for i in idx] + [angles[idx[0]]]
        envs.append(go.Scatterpolar(
            r=[maxv]*len(cat_theta), theta=cat_theta, mode="lines",
            line=dict(color="rgba(115,192,255,0.16)", width=1),
            fill="toself", fillcolor="rgba(115,192,255,0.06)", showlegend=False, hoverinfo="skip"
        ))

    fig = go.Figure(envs + [base, imp])
    fig.update_layout(
        height=260, margin=dict(l=20,r=20,t=10,b=10), paper_bgcolor="rgba(0,0,0,0)",
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            angularaxis=dict(
                tickmode="array", tickvals=angles, ticktext=labels, rotation=90,
                direction="clockwise", color=PALETTE['muted'], tickfont=dict(size=10)
            ),
            radialaxis=dict(range=[0, maxv], showline=False, gridcolor=PALETTE['grid'], tickfont=dict(size=9, color=PALETTE['muted']))
        ),
        font=dict(color=PALETTE['text']),
        legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center", bgcolor="rgba(0,0,0,0)", font=dict(size=11, color=PALETTE['text'])),
    )
    return fig


def series(city_key: str, scores: dict[str, float]) -> go.Figure:
    """Time-series chart; all traces in blues, distinguished by dash patterns.
    Legend font color explicitly set so labels always appear."""
    s = CITY_DATA[city_key]["time_series"]
    yrs = YEARS
    econ = np.array(s["economy"], dtype=float)
    env  = np.array(s["environment"], dtype=float)
    hlth = np.array(s["health"], dtype=float)

    econ_boost = scores["Economic"] / 100 * 12
    env_drop   = scores["Environmental"] / 100 * 18
    hlth_boost = scores["Social"] / 100 * 14

    econ_adj = econ + np.linspace(0, econ_boost, len(yrs))
    env_adj  = np.maximum(env - np.linspace(0, env_drop, len(yrs)), 20)
    hlth_adj = hlth + np.linspace(0, hlth_boost, len(yrs))

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=yrs, y=econ_adj, name="Economy",
                     mode="lines+markers", line=dict(color=PALETTE['primary'], width=3),
                     marker=dict(size=4)))
    fig.add_trace(go.Scatter(x=yrs, y=env_adj, name="Environment (↓ better)",
                     mode="lines+markers", line=dict(color=PALETTE['primary_2'], width=3, dash="dash"),
                     marker=dict(size=4)))
    fig.add_trace(go.Scatter(x=yrs, y=hlth_adj, name="Health & Wellbeing",
                     mode="lines+markers", line=dict(color=PALETTE['primary_3'], width=3, dash="dot"),
                     marker=dict(size=4)))

    fig.update_layout(
        height=200, margin=dict(l=20, r=6, t=6, b=16), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=PALETTE['text']),
        legend=dict(orientation="h", y=1.12, x=0.5, xanchor="center", bgcolor="rgba(0,0,0,0)", font=dict(size=11, color=PALETTE['text'])),
        xaxis=dict(title="", showgrid=False, zeroline=False, color=PALETTE['muted']),
        yaxis=dict(title="Index", gridcolor=PALETTE['grid'], zeroline=False, color=PALETTE['muted']),
        showlegend=True,
    )
    return fig

# ---------- UI widgets ---------------------------------------------------

def mini_bars(scores: dict[str, float]):
    """Compact category bars used as a visual legend."""
    for cat in CATEGORY_ORDER:
        val = scores.get(cat, 0.0)
        fill = CATEGORY_COLORS.get(cat, PALETTE['primary'])
        st.markdown(
            f"""
            <div class='mini-metric'>
              <div class='mini-label'>{cat}</div>
              <div class='mini-track'><span class='mini-fill' style='width:{val:.0f}%; background:{fill};'></span></div>
              <div class='mini-value'>{val:0.0f}% activation</div>
            </div>
            """, unsafe_allow_html=True
        )


def slider_block(it: dict):
    """One intervention block with a compact main row and collapsible sub-sliders.
    The chevron button sits to the right; sections are tight to fit 16:9."""

    # --- header row (label + main slider + chevron) ---
    cols = st.columns([0.30, 0.62, 0.08], gap="small")
    with cols[0]:
        # Label + live value pill (replaces BaseWeb’s default red value chip)
        _val_now = int(st.session_state.get(f"main_{it['id']}", 0))
        st.markdown(
            f"<div class='column-heading'>{it['label']} "
            f"<span class='value-pill'>{_val_now}</span></div>",
            unsafe_allow_html=True
        )

    with cols[1]:
        # Capture the value so the pill updates live
        v = st.slider("Intensity", 0, 100, _val_now, key=f"main_{it['id']}", label_visibility="collapsed")

    with cols[2]:
        tkey = f"toggle_{it['id']}"
        if tkey not in st.session_state:
            st.session_state[tkey] = False
        st.markdown('<div class="slider-toggle">', unsafe_allow_html=True)
        if st.button("▸" if not st.session_state[tkey] else "▾", key=f"btn_{it['id']}"):
            st.session_state[tkey] = not st.session_state[tkey]
        st.markdown('</div>', unsafe_allow_html=True)

    # --- collapsible sub-sliders ---
    if st.session_state.get(tkey, False):
        subcols = st.columns(len(it["sub_sliders"]))
        for c, s in zip(subcols, it["sub_sliders"]):
            with c:
                # Uppercase caption keeps the grid tidy
                st.caption(s["label"].upper())
                st.slider(
                    "", s["min"], s["max"], 
                    int(st.session_state.get(f"{it['id']}_{s['label']}", 0)),
                    key=f"{it['id']}_{s['label']}", 
                    label_visibility="collapsed"
                )



# ========================================================
# 4) LAYOUT
# ========================================================
# Title (explicit, per request)
st.markdown("<div class='app-title'>Urban Performance Model</div>", unsafe_allow_html=True)

# Keep slide mode; when ON, you still see charts + legend only (fits recording)
#slide_mode = st.checkbox("Slide mode (hide controls, show only charts)", value=True)

# Hero row ---------------------------------------------------------------
left, right = st.columns([0.62, 0.38], gap="large")

with left:
    st.markdown("<div class='section-label'>Search City</div>", unsafe_allow_html=True)
    q = st.text_input("Search City", value=st.session_state.get("city_search", ""), key="city_search", label_visibility="collapsed", placeholder="Type Skyhaven or Harborlight")
    city_key = find_city(q)

    # Scores & KPI prep
    cat_scores = compute_category_scores_from_state()
    kpis = CITY_DATA[city_key]["kpis"]
    kpi_vals = [k["value"] for k in kpis]
    kpi_labels = [k["name"] for k in kpis]
    kpi_cats = [k["category"] for k in kpis]

    # Charts
    ts_fig = series(city_key, cat_scores)
    rd_fig = radar(kpi_vals, improved_kpis(city_key, cat_scores), kpi_labels, kpi_cats)

    st.plotly_chart(ts_fig, use_container_width=True, config={"displayModeBar": False})
    st.plotly_chart(rd_fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown(f"<div class='caption-text'>Available: {' · '.join(CITY_DATA.keys())}</div>", unsafe_allow_html=True)

with right:
    st.markdown("<div class='section-label'>Category Activation</div>", unsafe_allow_html=True)
    mini_bars(cat_scores)

# Controls grid ----------------------------------------------------------

st.markdown("<div class='section-label' style='margin-top:.4rem'>Interventions</div>", unsafe_allow_html=True)
colA, colB, colC = st.columns(3, gap="large")
for c, group in zip((colA, colB, colC), (["upzoning","retrofits","grid"], ["mixed_use","freight","mobility"], ["circular","transit"])):
    with c:
        for gid in group: slider_block(INTERVENTION_LOOKUP[gid])

st.markdown("<hr/>", unsafe_allow_html=True)
st.markdown("<div class='caption-text'>Slide mode shows only charts & legend to avoid scrolling. Toggle off to tune interventions.</div>", unsafe_allow_html=True)
