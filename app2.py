import numpy as np
import streamlit as st
from plotly import graph_objects as go

# =============================================================================
# Streamlit configuration
# =============================================================================
st.set_page_config(
    page_title="Urban Performance Interface",
    page_icon="🌆",
    layout="wide",
)

# =============================================================================
# Design system (one cool-blue palette) + sizing for slide recording
# =============================================================================
PALETTE = {
    "bg": "#0a0f14",
    "text": "#e8f4ff",
    # Blues, light → dark
    "b100": "#cfefff",
    "b200": "#a8dffc",
    "b300": "#7fcdf7",
    "b400": "#56ccf2",
    "b500": "#39b4e6",
    "b600": "#2d9cdb",
    "b700": "#187bb4",
    "b800": "#0f5c8b",
}

# category → color (monochrome blues)
CATEGORY_ORDER = ["Economic", "Environmental", "Social"]
CATEGORY_COLORS = {
    "Economic": PALETTE["b600"],     # strong blue
    "Environmental": PALETTE["b400"], # lighter blue
    "Social": PALETTE["b200"],        # pale blue
}

# Target canvas size to fit inside a 1280×720 (or 1366×768) recording window
CANVAS = {
    "max_width_px": 1280,
    "gutter": "small",
    "ts_height": 170,   # time series plot height
    "radar_height": 250,
}

# =============================================================================
# Minimal, tidy CSS (trimmed, monochrome, slide-aware)
# =============================================================================
CUSTOM_STYLE = f"""
<style>
.block-container {{
    max-width: {CANVAS['max_width_px']}px;
    padding: 1.0rem 1.2rem 0.6rem;
}}
.stApp {{
    background: {PALETTE['bg']};
    color: {PALETTE['text']};
    font-family: "Inter", "Montserrat", system-ui, -apple-system, sans-serif;
}}

h1, h2, h3, h4 {{ font-weight: 600; letter-spacing: .02em; }}
.app-title {{
    font-size: 1.9rem; text-transform: uppercase; letter-spacing: .2em;
    color: {PALETTE['text']}; margin: 0 0 .6rem 0;
}}
.section-label {{ text-transform: uppercase; letter-spacing: .22em; color: {PALETTE['b400']}; font-size: .72rem; margin-bottom: .3rem; }}
.caption-text {{ color: rgba(232,244,255,.65); font-size: .72rem; letter-spacing: .1em; text-transform: uppercase; }}

/* Text inputs */
div[data-testid="stTextInput"] input {{
    background: rgba(10, 15, 20, .6);
    border: 1px solid rgba(168, 223, 252, .45);
    color: {PALETTE['text']}; font-size: .95rem; padding: .5rem .75rem; border-radius: 6px;
    text-transform: uppercase; letter-spacing: .08em;
}}
div[data-testid="stTextInput"] input::placeholder {{ color: rgba(232,244,255,.4); }}

/* Mini bar legend */
.mini-metric {{ display: grid; grid-template-columns: 1fr auto; gap: .3rem .6rem; align-items: center; }}
.mini-label {{ font-size: .72rem; letter-spacing: .18em; text-transform: uppercase; color: rgba(232,244,255,.8); }}
.mini-track {{ grid-column: 1/-1; width: 100%; height: 6px; border-radius: 999px; background: rgba(127,205,247,.18); position: relative; overflow: hidden; }}
.mini-fill {{ position: absolute; inset: 0 auto 0 0; height: 100%; border-radius: 999px; }}
.mini-value {{ font-size: .7rem; letter-spacing: .1em; color: rgba(232,244,255,.7); }}

/* Sliders (monochrome) */
div[data-testid="stSlider"] [data-baseweb="slider"] > div[style*="height"] {{ height: 2px !important; border-radius: 999px; background: rgba(86,204,242,.25); }}
div[data-testid="stSlider"] [data-baseweb="slider"] > div[style*="height"]:not(:first-of-type) {{ background: {PALETTE['b600']} !important; }}
div[data-testid="stSlider"] [role="slider"] {{ width: 14px; height: 14px; border-radius: 999px; background: {PALETTE['b600']}; border: 1px solid #000; }}

/* Card */
.support-card {{ margin-top: .4rem; padding: .7rem; border: 1px solid rgba(168,223,252,.28); border-radius: 10px; background: rgba(15,25,35,.55); box-shadow: 0 10px 22px rgba(0,0,0,.35); display: flex; flex-direction: column; gap: .5rem; }}
.support-card-title {{ font-size: .7rem; letter-spacing: .22em; text-transform: uppercase; color: {PALETTE['b400']}; }}
.support-label {{ font-size: .68rem; letter-spacing: .16em; text-transform: uppercase; color: rgba(232,244,255,.8); }}
.support-track {{ width: 100%; height: 6px; border-radius: 999px; background: rgba(255,255,255,.12); position: relative; }}
.support-fill {{ position: absolute; inset: 0 auto 0 0; border-radius: 999px; background: {PALETTE['b400']}; }}

hr {{ border-color: rgba(168,223,252,.14); }}

/* Slide mode: slightly tighter spacing */
.slide .block-container {{ padding-top: .6rem; }}
</style>
"""

st.markdown(CUSTOM_STYLE, unsafe_allow_html=True)

# =============================================================================
# Data (unchanged values, grouped for clarity)
# =============================================================================
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

INTERVENTIONS = [
    {"id": "upzoning",   "label": "Upzoning",                        "impact_weights": {"Economic": .45, "Environmental": .15, "Social": .40},
     "sub_sliders": [{"label": "Housing Units Added (per yr)", "min": 0,  "max": 1800, "value": 400}, {"label": "Inclusionary %", "min": 0,  "max": 60,  "value": 12}]},
    {"id": "retrofits",  "label": "Building Retrofits & Standards",  "impact_weights": {"Economic": .25, "Environmental": .55, "Social": .20},
     "sub_sliders": [{"label": "Net-Zero Retrofits (per yr)", "min": 0,  "max": 200,  "value": 40},  {"label": "Local Workforce Share (%)", "min": 0,  "max": 100, "value": 20}]},
    {"id": "grid",       "label": "Clean Energy & Grid Modernization","impact_weights": {"Economic": .35, "Environmental": .45, "Social": .20},
     "sub_sliders": [{"label": "Renewables Added (MW)",      "min": 0,  "max": 600,  "value": 120}, {"label": "Storage Capacity (MWh)",    "min": 0,  "max": 800,  "value": 150}]},
    {"id": "mixed_use",  "label": "Mixed Use Zoning",               "impact_weights": {"Economic": .50, "Environmental": .25, "Social": .25},
     "sub_sliders": [{"label": "Transit Parcels (%)",         "min": 0,  "max": 60,   "value": 15},  {"label": "Community Amenities (#)",   "min": 0,  "max": 50,  "value": 10}]},
    {"id": "freight",    "label": "Urban Freight Transition",        "impact_weights": {"Economic": .35, "Environmental": .45, "Social": .20},
     "sub_sliders": [{"label": "EV Fleets Converted (%)",     "min": 0,  "max": 100,  "value": 20},  {"label": "Consolidation Hubs (#)",   "min": 0,  "max": 40,  "value": 8}]},
    {"id": "mobility",   "label": "Active Mobility Networks",        "impact_weights": {"Economic": .25, "Environmental": .40, "Social": .35},
     "sub_sliders": [{"label": "Protected Lanes (km)",        "min": 0,  "max": 120,  "value": 20},  {"label": "Mode Share Target (%)",   "min": 0,  "max": 60,  "value": 12}]},
    {"id": "circular",   "label": "Circular Waste & Materials",       "impact_weights": {"Economic": .10, "Environmental": .60, "Social": .30},
     "sub_sliders": [{"label": "Organic Diversion (%)",       "min": 0,  "max": 90,   "value": 20},  {"label": "Recycling Coverage (%)",  "min": 0,  "max": 100, "value": 35}]},
    {"id": "transit",    "label": "Public Transit Expansion",        "impact_weights": {"Economic": .20, "Environmental": .35, "Social": .45},
     "sub_sliders": [{"label": "New Routes (#)",              "min": 0,  "max": 25,   "value": 5},   {"label": "Service Frequency (%)",   "min": 0,  "max": 80,  "value": 15}]},
]

ADDITIONAL_PROGRAMS = [
    {"name": "Electrify",        "value": 84},
    {"name": "Expand Coverage",  "value": 72},
    {"name": "Subsidies",        "value": 58},
]

INTERVENTION_LOOKUP = {i["id"]: i for i in INTERVENTIONS}

# =============================================================================
# Helpers
# =============================================================================

def find_city(match: str) -> str:
    if not match:
        return list(CITY_DATA.keys())[0]
    for city in CITY_DATA:
        if city.lower() == match.strip().lower():
            return city
    for city in CITY_DATA:
        if city.lower().startswith(match.strip().lower()):
            return city
    return list(CITY_DATA.keys())[0]


def compute_category_scores_from_state() -> dict[str, float]:
    scores = {c: 0.0 for c in CATEGORY_ORDER}
    for it in INTERVENTIONS:
        main = float(st.session_state.get(f"main_{it['id']}", 0))
        subs = []
        for sub in it["sub_sliders"]:
            subs.append(float(st.session_state.get(f"{it['id']}_{sub['label']}", 0)))
        sub_avg = 0 if not subs else float(np.mean([
            (v / sub['max']) * 100 if sub['max'] else 0
            for v, sub in zip(subs, it['sub_sliders'])
        ]))
        intensity = (main + sub_avg) / 2 if subs else main
        for cat, w in it["impact_weights"].items():
            scores[cat] += intensity * w
    return {k: min(v, 100.0) for k, v in scores.items()}


def compute_improved_kpis(city_key: str, category_scores: dict[str, float]) -> list[float]:
    improved = []
    for kpi in CITY_DATA[city_key]["kpis"]:
        base = kpi["value"]
        boost = 1 + (category_scores[kpi["category"]] / 100) * 0.35
        improved.append(round(min(base * boost, 10.0), 2))
    return improved

# --- Rendering primitives -------------------------------------------------

def mini_bars(category_scores: dict[str, float]) -> None:
    for category in CATEGORY_ORDER:
        value = category_scores.get(category, 0.0)
        fill = CATEGORY_COLORS.get(category, PALETTE["b600"])
        st.markdown(
            f"""
            <div class="mini-metric">
                <div class="mini-label">{category}</div>
                <div class="mini-track">
                    <span class="mini-fill" style="width:{value:.0f}%; background:{fill};"></span>
                </div>
                <div class="mini-value">{value:0.0f}% activation</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def build_radar(curr: list[float], improved: list[float], labels: list[str], cats: list[str]) -> go.Figure:
    max_v = 10
    n = len(labels)
    angles = np.linspace(0, 360, n, endpoint=False)
    theta_loop = angles.tolist() + [angles[0]]

    fig = go.Figure()

    # category envelopes (thin blue halos)
    for cat in CATEGORY_ORDER:
        idx = [i for i, c in enumerate(cats) if c == cat]
        if not idx:
            continue
        cat_theta = [angles[i] for i in idx] + [angles[idx[0]]]
        fig.add_trace(go.Scatterpolar(
            r=[max_v] * len(cat_theta), theta=cat_theta, mode="lines",
            line=dict(color="rgba(127,205,247,.18)", width=2), fill="toself",
            fillcolor="rgba(127,205,247,.06)", hoverinfo="skip", showlegend=False,
        ))

    # series (both blue family)
    fig.add_trace(go.Scatterpolar(
        r=curr + [curr[0]], theta=theta_loop, fill="toself", name="Current",
        line=dict(color=PALETTE["b600"]), fillcolor="rgba(45,156,219,.28)",
    ))
    fig.add_trace(go.Scatterpolar(
        r=improved + [improved[0]], theta=theta_loop, fill="toself", name="2035",
        line=dict(color=PALETTE["b400"]), fillcolor="rgba(86,204,242,.35)",
    ))

    fig.update_layout(
        template=None,
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            angularaxis=dict(
                tickmode="array", tickvals=angles, ticktext=labels, rotation=90,
                direction="clockwise", showline=False, color="rgba(232,244,255,.8)",
                tickfont=dict(size=10),
            ),
            radialaxis=dict(range=[0, max_v], showline=False, gridcolor="rgba(255,255,255,0)", ticks=""),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=PALETTE["text"]),
        legend=dict(orientation="v", y=0.5, yanchor="middle", x=1.02, xanchor="left", bgcolor="rgba(0,0,0,0)", font=dict(size=10)),
        margin=dict(l=30, r=140, t=16, b=8),
        height=CANVAS["radar_height"],
    )
    return fig


def build_time_series(city_key: str, scores: dict[str, float]) -> go.Figure:
    series = CITY_DATA[city_key]["time_series"]
    years = YEARS

    economy = np.array(series["economy"], dtype=float)
    environment = np.array(series["environment"], dtype=float)