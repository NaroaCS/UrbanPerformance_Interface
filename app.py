import json
import pathlib
import uuid

import numpy as np
import streamlit as st
from plotly import graph_objects as go
from functools import partial

# ============================================================================
# CONFIGURATION
# ============================================================================

st.set_page_config(page_title="Urban Performance", layout="wide")

# Color Palette
COLORS = {
    "bg": "#08121C",
    "text": "#EAF4FF",
    "muted": "rgba(234,244,255,0.72)",
    "primary": "#39A8FF",
    "primary_mid": "#73C0FF",
    "primary_light": "#B9DDFF",
    "grid": "rgba(255,255,255,0.10)",
}

# Category Colors
CATEGORIES = ["Economic", "Environmental", "Social"]
CATEGORY_COLORS = {
    "Economic": COLORS["primary"],
    "Environmental": "#4FB7FF",
    "Social": "#9AD2FF",
}

# Years Range
YEARS = list(range(2025, 2036))


# ============================================================================
# STYLING
# ============================================================================


def apply_custom_css():
    st.markdown("""
    <style>
        /* ===== Base ===== */
        html, body { background: #08121C; color: #EAF4FF; }
        header[data-testid="stHeader"] { background: #08121C; visibility: hidden; height: 0; }
        .stApp { background: #08121C; color: #EAF4FF; font-family: 'Inter','Montserrat',system-ui,sans-serif; }
        .block-container { max-width: 1600px; padding: 1rem 1.5rem 0.5rem; }

        /* ===== Typography ===== */
        .app-title { font-size: 1.9rem; letter-spacing: .20em; text-transform: uppercase; margin: 0 0 .8rem 0; }
        .section-label { text-transform: uppercase; letter-spacing: .22em; color: #B9DDFF; font-size: .7rem; margin: .9rem 0 .45rem; font-weight: 600; }

        /* ===== Search (shorter so chart fits on the right) ===== */
        .search-wrap{ max-width: 420px; }   /* << shorter */
        div[data-testid="stTextInput"] input{
            background: rgba(8,18,28,.6); border:1px solid rgba(115,192,255,.25);
            color:#EAF4FF; font-size:.95rem; padding:.55rem .7rem; border-radius:8px;
            text-transform:uppercase; letter-spacing:.08em;
        }
        div[data-testid="stTextInput"] input::placeholder{ color: rgba(234,244,255,.72); }

        /* ===== Video ===== */
        .video-container{ border-radius:10px; overflow:hidden; background:rgba(0,0,0,.3);
            border:1px solid rgba(115,192,255,.2); margin-top:.5rem; }
        div[data-testid="stVideo"] video, div[data-testid="stVideo"] iframe{
            max-height: 220px !important; width:100% !important; object-fit: cover; border-radius: 10px;
        }

        /* ===== Slider UI ===== */
        .slider-container { margin-bottom: 0.9rem; user-select: none; }
        .slider-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:.35rem; }
        .slider-title { font-size:.78rem; letter-spacing:.16em; text-transform:uppercase; color:#EAF4FF; font-weight:600; }
        .slider-value { display:none !important; } /* remove chip */

        button[kind="secondary"]{
            background:transparent!important; border:none!important; box-shadow:none!important; padding:0!important;
            min-width:20px!important; width:20px!important; height:20px!important; color:#EAF4FF!important; font-size:1.2rem!important;
        }
        button[kind="secondary"]:hover{ background:rgba(115,192,255,.1)!important; }
        button[kind="secondary"]:focus{ box-shadow:none!important; }

        div[data-testid="stSlider"] { margin:.35rem 0 .9rem; }
        div[data-testid="stSlider"] *:focus,
        div[data-testid="stSlider"] *:focus-visible{ outline:none!important; box-shadow:none!important; }

        /* strip boxes/wrappers */
        div[data-testid="stSlider"] > div,
        div[data-testid="stSlider"] [data-baseweb="slider"],
        div[data-testid="stSlider"] [data-baseweb="slider"] > div{
            background:transparent!important; border:none!important; box-shadow:none!important; padding:0!important;
        }

        /* rail + active track */
        div[data-testid="stSlider"] [data-baseweb="slider"] > div:first-child{
            height:3px!important; background:rgba(115,192,255,.28)!important; border-radius:999px!important;
        }
        div[data-testid="stSlider"] [data-baseweb="slider"] > div:nth-child(2){
            height:3px!important; background:#73C0FF!important; border-radius:999px!important;
        }

        /* thumb */
        div[data-testid="stSlider"] [role="slider"]{
            width:14px!important; height:14px!important; border-radius:999px!important;
            background:#73C0FF!important; border:2px solid #08121C!important;
            box-shadow:0 2px 4px rgba(0,0,0,.3)!important;
            transition: transform .12s ease, box-shadow .12s ease, background .12s ease;
            cursor: ew-resize !important;
        }
        div[data-testid="stSlider"] [role="slider"]:hover{ transform: scale(1.12); box-shadow:0 3px 6px rgba(0,0,0,.35)!important; }
        div[data-testid="stSlider"] [role="slider"]:active{ transform: scale(1.22); background:#39A8FF!important; }

        div[data-testid="stSlider"] label{ color:#B9DDFF!important; font-weight:600!important; }

        /* ===== HARD overrides to remove hand + value/tick artifacts across builds ===== */
        /* kill tick bars, inline value labels, tooltips, and stray SVG tick layers */
        [data-baseweb="tick-bar"],
        div[data-testid="stSlider"] [class*="TickBar"],
        div[data-testid="stSlider"] [class*="tick"],
        div[data-testid="stSlider"] [class*="Value"],
        div[data-testid="stSlider"] [class*="value"],
        div[data-testid="stSlider"] [role="tooltip"],
        div[data-testid="stSlider"] svg{ display:none!important; }

        /* remove hand pointer anywhere except the thumb */
        div[data-testid="stSlider"] [data-baseweb="slider"],
        div[data-testid="stSlider"] [data-baseweb="slider"] *{ cursor: default !important; }
        /* some builds place a separate overlay for the live value — hide it */
        div[data-testid="stSlider"] [data-baseweb="slider"] > div:nth-child(3){ display:none!important; }

        [data-testid="column"]{ padding:0 .5rem; }
        .js-plotly-plot{ margin-bottom:0!important; }
    </style>
    """, unsafe_allow_html=True)




# ============================================================================
# DATA DEFINITIONS
# ============================================================================

CITY_DATA = {
    "Boston": {
        "map_query": "Boston, Massachusetts, USA",
        "map_area_km": 2.0,
        "kpis": [
                    # ENVIRONMENTAL
                    {"name": "GHG reduction",              "category": "Environmental", "value": 5.6},
                    {"name": "Energy efficiency",          "category": "Environmental", "value": 6.2},
                    {"name": "Sustainable mode share",     "category": "Environmental", "value": 5.0},
                    {"name": "Waste diversion",            "category": "Environmental", "value": 4.0},
                    # ECONOMIC
                    {"name": "Household savings",          "category": "Economic",      "value": 5.4},
                    {"name": "Jobs created",               "category": "Economic",      "value": 5.1},
                    {"name": "Productivity gains",         "category": "Economic",      "value": 4.8},
                    {"name": "Locally-owned businesses",   "category": "Economic",      "value": 5.0},
                    # SOCIAL
                    {"name": "Housing affordability",      "category": "Social",        "value": 4.7},
                    {"name": "Public health",              "category": "Social",        "value": 5.5},
                    {"name": "Equity of Accessibility",    "category": "Social",        "value": 4.9},
                ],
        "time_series": {
            "economy": [98, 100, 103, 105, 108, 111, 114, 118, 121, 124, 128],
            "environment": [152, 149, 145, 142, 138, 134, 131, 126, 122, 119, 116],
            "health": [84, 86, 88, 90, 92, 94, 97, 99, 101, 103, 106],
        },
    },
    "San Sebastian": {
        "map_query": "Donostia-San Sebastian, Spain",
        "map_area_km": 1.5,
        "kpis": [
            # ENVIRONMENTAL
            {"name": "GHG reduction",              "category": "Environmental", "value": 4.8},
            {"name": "Energy efficiency",          "category": "Environmental", "value": 5.4},
            {"name": "Sustainable mode share",     "category": "Environmental", "value": 4.6},
            {"name": "Waste diversion",            "category": "Environmental", "value": 3.6},
            # ECONOMIC
            {"name": "Household savings",          "category": "Economic",      "value": 4.9},
            {"name": "Jobs created",               "category": "Economic",      "value": 4.7},
            {"name": "Productivity gains",         "category": "Economic",      "value": 4.2},
            {"name": "Locally-owned businesses",   "category": "Economic",      "value": 4.6},
            # SOCIAL
            {"name": "Housing affordability",      "category": "Social",        "value": 4.2},
            {"name": "Public health",              "category": "Social",        "value": 4.9},
            {"name": "Equity of Accessibility",    "category": "Social",        "value": 4.4},
        ],
        "time_series": {
            "economy": [93, 95, 96, 99, 101, 103, 106, 109, 112, 114, 118],
            "environment": [164, 161, 158, 154, 151, 147, 144, 140, 136, 133, 130],
            "health": [79, 80, 82, 83, 85, 87, 89, 91, 93, 95, 98],
        },
    },
}


@st.cache_data(show_spinner=False)
def load_city_visual_template() -> str:
    template_path = pathlib.Path("visuals/city_test.html")
    return template_path.read_text(encoding="utf-8")


def render_city_visual(city_config: dict, height_scale: float, *, height: int = 520) -> None:
    frame_id = st.session_state.setdefault(
        "city_visual_frame_id",
        f"city-viz-{uuid.uuid4().hex}",
    )

    html_template = load_city_visual_template()
    marker = "const EMBEDDED_CONFIG = {}; // __CITY_VIZ_EMBED_CONFIG__"

    city_query = city_config.get("map_query") or ""
    try:
        area_value = float(city_config.get("map_area_km", 1.5))
    except (TypeError, ValueError):
        area_value = 1.5
    height_value = round(float(height_scale), 3)

    defaults = {
        "autoBootstrap": True,
        "hideUI": True,
        "cityQuery": city_query,
        "areaKm": area_value,
        "agentCount": 100,
        "tallModeOnly": True,
        "heightScale": height_value,
        "agentSpeedMin": 85,
        "agentSpeedSpread": 35,
    }

    config_json = json.dumps(defaults).replace("</", "<\\/")
    html = html_template.replace("__FRAME_ID__", frame_id)
    if marker in html:
        html = html.replace(marker, f"const EMBEDDED_CONFIG = {config_json};")
    st.components.v1.html(html, height=height)

    payload = {
        "hideUI": True,
        "cityQuery": city_query,
        "areaKm": area_value,
        "agentCount": 100,
        "tallModeOnly": True,
        "heightScale": height_value,
        "agentSpeedMin": 85,
        "agentSpeedSpread": 35,
    }

    prev_city = st.session_state.get("city_visual_prev_city")
    prev_area = st.session_state.get("city_visual_prev_area")
    current_city = payload["cityQuery"].lower()
    try:
        prev_area_val = float(prev_area) if prev_area is not None else None
    except (TypeError, ValueError):
        prev_area_val = None
    try:
        current_area_val = float(payload["areaKm"])
    except (TypeError, ValueError):
        current_area_val = None

    payload["forceReload"] = (
        prev_city is None
        or prev_area_val is None
        or prev_city.lower() != current_city
        or prev_area_val != current_area_val
    )

    st.session_state["city_visual_prev_city"] = payload["cityQuery"]
    st.session_state["city_visual_prev_area"] = current_area_val

    send_city_visual_config(frame_id, payload)


def send_city_visual_config(frame_id: str, payload: dict) -> None:
    message = {
        "__cityViz": True,
        "action": "setConfig",
        "config": payload,
    }
    message_json = json.dumps(message).replace("</", "<\\/")
    script = f"""
    <script>
    (function() {{
        const payload = {message_json};
        const frameId = "{frame_id}";
        let attempts = 0;
        const maxAttempts = 25;
        const delayMs = 200;
        let acknowledged = false;

        const handleAck = (event) => {{
            const data = event.data;
            if (data && data.__cityVizAck && data.frameId === frameId) {{
                acknowledged = true;
                window.removeEventListener('message', handleAck);
                if (window.parent) try {{ window.parent.removeEventListener('message', handleAck); }} catch (_) {{}}
            }}
        }};
        window.addEventListener('message', handleAck);
        if (window.parent) try {{ window.parent.addEventListener('message', handleAck); }} catch (_) {{}}

        const send = () => {{
            if (acknowledged || attempts >= maxAttempts) return;
            attempts += 1;
            try {{
                const doc = window.parent && window.parent.document;
                if (!doc) throw new Error('no parent document');
                const frame = doc.getElementById(frameId);
                if (frame && frame.contentWindow && frame.contentWindow.postMessage) {{
                    frame.contentWindow.postMessage(payload, '*');
                }}
            }} catch (err) {{
                console.warn('city viz dispatch attempt failed', err);
            }}
            if (!acknowledged && attempts < maxAttempts) {{
                setTimeout(send, delayMs);
            }}
        }};
        send();
    }})();
    </script>
    """
    st.components.v1.html(script, height=0, width=0)


INTERVENTIONS = [
    {
        "id": "urban_form",
        "label": "Urban Form",
        "impact_weights": {"Economic": 0.45, "Environmental": 0.15, "Social": 0.40},
        "sub_sliders": [
            {"label": "Upzoning", "min": 0, "max": 100, "value": 0},
            {"label": "Mixed-Use Development", "min": 0, "max": 100, "value": 0}
        ]
    },
    {
        "id": "building_efficiency",
        "label": "Building Efficiency",
        "impact_weights": {"Economic": 0.25, "Environmental": 0.55, "Social": 0.20},
        "sub_sliders": [
            {"label": "Retrofits", "min": 0, "max": 100, "value": 0},
            {"label": "Standards", "min": 0, "max": 100, "value": 0}
        ]
    },
    {
        "id": "clean_energy",
        "label": "Clean Energy",
        "impact_weights": {"Economic": 0.35, "Environmental": 0.45, "Social": 0.20},
        "sub_sliders": [
            {"label": "Solar", "min": 0, "max": 100, "value": 0},
            {"label": "Wind", "min": 0, "max": 100, "value": 0},
            {"label": "Geothermal", "min": 0, "max": 100, "value": 0},
            {"label": "Hydro", "min": 0, "max": 100, "value": 0},
            {"label": "Nuclear", "min": 0, "max": 100, "value": 0}
        ]
    },
    {
        "id": "urban_freight",
        "label": "Urban Freight",
        "impact_weights": {"Economic": 0.35, "Environmental": 0.45, "Social": 0.20},
        "sub_sliders": [
            {"label": "Cargo Bikes", "min": 0, "max": 100, "value": 0},
            {"label": "Consolidation", "min": 0, "max": 100, "value": 0},
            {"label": "Restrictions", "min": 0, "max": 100, "value": 0},
            {"label": "Fees", "min": 0, "max": 100, "value": 0}
        ]
    },
    {
        "id": "active_mobility",
        "label": "Active Mobility",
        "impact_weights": {"Economic": 0.25, "Environmental": 0.40, "Social": 0.35},
        "sub_sliders": [
            {"label": "Coverage", "min": 0, "max": 100, "value": 0},
            {"label": "Connectivity", "min": 0, "max": 100, "value": 0},
            {"label": "Safety", "min": 0, "max": 100, "value": 0}
        ]
    },
    {
        "id": "public_transit",
        "label": "Public Transit",
        "impact_weights": {"Economic": 0.20, "Environmental": 0.35, "Social": 0.45},
        "sub_sliders": [
            {"label": "Electrification", "min": 0, "max": 100, "value": 0},
            {"label": "Coverage", "min": 0, "max": 100, "value": 0},
            {"label": "Fare Subsidies", "min": 0, "max": 100, "value": 0}
        ]
    },
    {
        "id": "waste",
        "label": "Waste Systems",
        "impact_weights": {"Economic": 0.10, "Environmental": 0.60, "Social": 0.30},
        "sub_sliders": [
            {"label": "Recycling", "min": 0, "max": 100, "value": 0},
            {"label": "Composting", "min": 0, "max": 100, "value": 0},
            {"label": "Digestion", "min": 0, "max": 100, "value": 0}
        ]
    }
]

# ----------------------------------------------------------------------------
# KPI influence matrix (H/M/L from the grid; blanks are Low)
# ----------------------------------------------------------------------------

INFLUENCE_NUM = {"none": 0.0, "L": 0.35, "M": 0.70, "H": 1.00}


# keys: KPI name -> intervention_id -> "H"/"M"/"L"
KPI_INFLUENCE = {
    # ENVIRONMENTAL
    "GHG reduction": {
        "urban_form": "H", "building_efficiency": "H", "clean_energy": "H",
        "urban_freight": "M", "active_mobility": "H", "public_transit": "H",
        "waste": "M",
    },
    "Energy efficiency": {
        "urban_form": "L", "building_efficiency": "H", "clean_energy": "L",
        "urban_freight": "M", "active_mobility": "M", "public_transit": "M",
        "waste": "M",
    },
    "Sustainable mode share": {
        "urban_form": "H", "building_efficiency": "L", "clean_energy": "L",
        "urban_freight": "L", "active_mobility": "H", "public_transit": "H",
        "waste": "L",
    },
    "Waste diversion": {
        "urban_form": "L", "building_efficiency": "L", "clean_energy": "L",
        "urban_freight": "L", "active_mobility": "L", "public_transit": "L",
        "waste": "H",
    },

    # ECONOMIC
    "Household savings": {
        "urban_form": "M", "building_efficiency": "H", "clean_energy": "L",
        "urban_freight": "L", "active_mobility": "M", "public_transit": "M",
        "waste": "L",
    },
    "Jobs created": {
        "urban_form": "L", "building_efficiency": "H", "clean_energy": "H",
        "urban_freight": "M", "active_mobility": "L", "public_transit": "M",
        "waste": "M",
    },
    "Productivity gains": {
        "urban_form": "M", "building_efficiency": "L", "clean_energy": "L",
        "urban_freight": "M", "active_mobility": "H", "public_transit": "H",
        "waste": "L",
    },
    "Locally-owned businesses": {
        "urban_form": "H", "building_efficiency": "L", "clean_energy": "L",
        "urban_freight": "M", "active_mobility": "H", "public_transit": "L",
        "waste": "L",
    },

    # SOCIAL
    "Housing affordability": {
        "urban_form": "H", "building_efficiency": "H", "clean_energy": "L",
        "urban_freight": "L", "active_mobility": "L", "public_transit": "L",
        "waste": "L",
    },
    "Public health": {
        "urban_form": "H", "building_efficiency": "L", "clean_energy": "H",
        "urban_freight": "M", "active_mobility": "H", "public_transit": "H",
        "waste": "M",
    },
    "Equity of Accessibility": {
        "urban_form": "H", "building_efficiency": "L", "clean_energy": "L",
        "urban_freight": "L", "active_mobility": "H", "public_transit": "H",
        "waste": "L",
    },
}


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def find_city(search_text: str) -> str:
    """Find city by search text or return first city."""
    if not search_text:
        return list(CITY_DATA.keys())[0]
    search_lower = search_text.strip().lower()
    for city in CITY_DATA:
        if city.lower().startswith(search_lower):
            return city
    return list(CITY_DATA.keys())[0]


def compute_category_scores() -> dict:
    """Calculate category scores based on intervention settings."""
    scores = {cat: 0.0 for cat in CATEGORIES}
    for intervention in INTERVENTIONS:
        main_value = float(st.session_state.get(f"main_{intervention['id']}", 0))
        sub_values = []
        for sub in intervention["sub_sliders"]:
            key = f"{intervention['id']}_{sub['label']}"
            value = float(st.session_state.get(key, sub["value"]))
            normalized = (value / sub["max"] * 100) if sub["max"] else 0
            sub_values.append(normalized)
        intensity = (main_value + np.mean(sub_values)) / 2 if sub_values else main_value
        for category, weight in intervention["impact_weights"].items():
            scores[category] += intensity * weight
    return {k: min(v, 100.0) for k, v in scores.items()}


#for time series chart
def category_improvement_from_kpis(current_vals, improved_vals, kpi_categories):
    cats = ["Economic", "Environmental", "Social"]
    out = {c: 0.0 for c in cats}
    for c in cats:
        cur = [cv for cv, cat in zip(current_vals, kpi_categories) if cat == c]
        imp = [iv for iv, cat in zip(improved_vals, kpi_categories) if cat == c]
        if not cur:
            continue
        cur_mean = float(np.mean(cur))
        imp_mean = float(np.mean(imp))
        delta = max(0.0, (imp_mean - cur_mean) / 10.0)  # 0..1
        out[c] = min(delta, 1.0)
    return out




def get_intervention_intensities() -> dict:
    return {it["id"]: float(st.session_state.get(f"main_{it['id']}", 0))
            for it in INTERVENTIONS}

def calculate_improved_kpis(city_key: str) -> list:
    intensities = get_intervention_intensities()

    # ↑ make the radar more sensitive by increasing this
    IMPACT_TO_LIFT = 1.40            # was 0.35

    improved = []
    for kpi in CITY_DATA[city_key]["kpis"]:
        base = float(kpi["value"])
        name = kpi["name"]

        # collect only interventions that actually influence this KPI
        parts = []
        max_parts = []
        for it in INTERVENTIONS:
            level = KPI_INFLUENCE.get(name, {}).get(it["id"], "none")
            w = INFLUENCE_NUM[level]
            if w > 0:
                parts.append((intensities[it["id"]] / 100.0) * w)
                max_parts.append(1.0)  # this intervention could contribute up to 1.0

        if not parts:
            improved.append(base)  # no links → no change
            continue

        # optional: slightly convex response so high sliders punch more
        total = sum((p ** 0.9) for p in parts)     # 0.9 → gentle convexity
        max_possible = sum(max_parts)              # count ONLY linked interventions
        normalized = min(total / max_possible, 1.0)

        lift = 1.0 + normalized * IMPACT_TO_LIFT   # 0%..80% boost
        improved.append(round(min(base * lift, 10.0), 2))
    return improved


def slider_to_height_scale(value: float) -> float:
    value = max(0.0, min(100.0, float(value)))
    base = 0.5
    span = 2.5
    return base + (value / 100.0) * span



# ============================================================================
# CHART FUNCTIONS
# ============================================================================

def create_radar_chart(current: list, improved: list, labels: list, categories: list):
    """Readable radar: bigger KPI labels, more padding, legend moved out of the plot."""
    max_value = 10
    n_points = len(labels)
    angles = np.linspace(0, 360, n_points, endpoint=False)
    theta_values = angles.tolist() + [angles[0]]

    traces = [
        go.Scatterpolar(
            r=current + [current[0]],
            theta=theta_values,
            name="Current",
            mode="lines",
            line=dict(color=COLORS["primary_mid"], width=2.5),
            fill="toself",
            fillcolor="rgba(115,192,255,0.20)",
        ),
        go.Scatterpolar(
            r=improved + [improved[0]],
            theta=theta_values,
            name="2035",
            mode="lines",
            line=dict(color=COLORS["primary"], width=3.5),
            fill="toself",
            fillcolor="rgba(57,168,255,0.28)",
        ),
    ]

    fig = go.Figure(traces)
    fig.update_layout(
        height=500,                                   # more canvas for labels
        margin=dict(l=64, r=64, t=48, b=48),          # extra breathing room
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=COLORS["text"]),
        # Legend: move outside, top-left, larger font, subtle background
        legend=dict(
            orientation="h",
            x=0.0, xanchor="left",
            y=1.18, yanchor="top",
            bgcolor="rgba(8,18,28,0.6)",
            bordercolor="rgba(115,192,255,0.25)",
            borderwidth=1,
            font=dict(size=13, color=COLORS["text"]),
            itemsizing="constant",
        ),
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            # rotate so long labels sit left/right (least clipping)
            angularaxis=dict(
                tickmode="array",
                tickvals=angles,
                ticktext=labels,
                rotation=58,
                direction="clockwise",
                color=COLORS["muted"],
                tickfont=dict(size=13, family="Inter, Montserrat, system-ui, sans-serif"),
            ),
            radialaxis=dict(
                range=[0, max_value],
                showline=False,
                gridcolor=COLORS["grid"],
                tickfont=dict(size=11, color=COLORS["muted"], family="Inter, Montserrat, system-ui, sans-serif"),
            ),
        ),
    )
    return fig



def create_time_series_chart(city_key: str, cat_deltas: dict):
    """
    Time series with improved readability:
    - larger legend
    - thicker lines and bigger markers
    - bigger year labels (every year shown)
    """
    ts = CITY_DATA[city_key]["time_series"]
    n = len(YEARS)
    t = np.arange(n)

    econ_start = float(ts["economy"][0])
    env_start  = float(ts["environment"][0])
    soc_start  = float(ts["health"][0])

    TOTAL_RANGE = {"Economic": 40.0, "Environmental": 50.0, "Social": 30.0}

    econ_step = (TOTAL_RANGE["Economic"] * cat_deltas.get("Economic", 0.0)) / max(1, n - 1)
    env_step  = (-TOTAL_RANGE["Environmental"] * cat_deltas.get("Environmental", 0.0)) / max(1, n - 1)
    soc_step  = (TOTAL_RANGE["Social"] * cat_deltas.get("Social", 0.0)) / max(1, n - 1)

    NOISE_LEVEL = float(st.session_state.get("noise_level", 0.10))
    rng = np.random.default_rng(abs(hash(city_key)) % (2**32))

    def smooth_noise(step, delta):
        if delta <= 1e-12 or NOISE_LEVEL <= 1e-6:
            return np.zeros(n)
        amp = abs(step) * 0.25 * NOISE_LEVEL
        sinus = np.sin(np.linspace(0, 2 * np.pi, n)) * amp * 0.85
        rand = rng.normal(0, amp * 0.15, size=n)
        return (sinus + rand) * delta

    econ = econ_start + t * econ_step + smooth_noise(econ_step, cat_deltas.get("Economic", 0.0))
    env  = env_start  + t * env_step  + smooth_noise(env_step,  cat_deltas.get("Environmental", 0.0))
    soc  = soc_start  + t * soc_step  + smooth_noise(soc_step,  cat_deltas.get("Social", 0.0))

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=YEARS, y=econ, name="Economy", mode="lines+markers",
        line=dict(color=COLORS["primary"], width=3), marker=dict(size=5)
    ))
    fig.add_trace(go.Scatter(
        x=YEARS, y=env, name="Environment", mode="lines+markers",
        line=dict(color=COLORS["primary_mid"], width=3, dash="dash"), marker=dict(size=5)
    ))
    fig.add_trace(go.Scatter(
        x=YEARS, y=soc, name="Health/Social", mode="lines+markers",
        line=dict(color=COLORS["primary_light"], width=3, dash="dot"), marker=dict(size=5)
    ))

    fig.update_layout(
        height=200,
        margin=dict(l=24, r=12, t=8, b=36),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=COLORS["text"]),
        legend=dict(
            orientation="h",
            y=1.28, x=0.5, xanchor="center",
            bgcolor="rgba(8,18,28,0.6)",
            bordercolor="rgba(115,192,255,0.25)",
            borderwidth=1,
            font=dict(size=13, color=COLORS["text"]),
            itemsizing="constant",
        ),
        xaxis=dict(
            title="",
            tickvals=YEARS,                 # show every year
            ticktext=[str(y) for y in YEARS],
            tickangle=0,
            showgrid=False, zeroline=False,
            color=COLORS["muted"],
            tickfont=dict(size=12, family="Inter, Montserrat, system-ui, sans-serif"),
        ),
        yaxis=dict(
            title="Index",
            gridcolor=COLORS["grid"], zeroline=False,
            color=COLORS["muted"],
            tickfont=dict(size=11, family="Inter, Montserrat, system-ui, sans-serif"),
        ),
    )
    return fig

def _wrap_label(s: str) -> str:
    # short, readable polar tick labels
    replacements = {
        "Sustainable mode share": "Sustainable<br>mode share",
        "Locally-owned businesses": "Locally-owned<br>businesses",
        "Housing affordability": "Housing<br>affordability",
        "Public health": "Public<br>health",
        "Equity of Accessibility": "Equity of<br>Accessibility",
        "GHG reduction": "GHG<br>reduction",
        "Energy efficiency": "Energy<br>efficiency",
        "Waste diversion": "Waste<br>diversion",
        "Jobs created": "Jobs<br>created",
    }
    return replacements.get(s, s)

def init_state(key, default):
    if key not in st.session_state:
        st.session_state[key] = default

# ============================================================================
# UI COMPONENTS
# ============================================================================

from functools import partial

def init_state(key, default):
    """Initialize a session key once (prevents 'default + session state' warning)."""
    if key not in st.session_state:
        st.session_state[key] = default

def _clamp(v, lo, hi):
    return max(lo, min(hi, v))

def _on_main_change(iid, sub_defs):
    """When main slider moves, scale sub-sliders so their average == main."""
    main_key = f"main_{iid}"
    main = float(st.session_state.get(main_key, 0))
    if not sub_defs:
        return

    # current sub values
    vals = []
    for sd in sub_defs:
        sk = f"{iid}_{sd['label']}"
        vals.append(float(st.session_state.get(sk, sd["value"])))
    avg = np.mean(vals) if vals else 0.0

    if avg <= 0:
        # distribute evenly if subs are zero/undefined
        for sd in sub_defs:
            st.session_state[f"{iid}_{sd['label']}"] = int(round(_clamp(main, sd["min"], sd["max"])))
    else:
        scale = main / avg
        for sd, v in zip(sub_defs, vals):
            new_v = _clamp(v * scale, sd["min"], sd["max"])
            st.session_state[f"{iid}_{sd['label']}"] = int(round(new_v))

def _on_sub_change(iid, sub_defs):
    """When any sub slider moves, set main to the average of subs."""
    if not sub_defs:
        return
    vals = [float(st.session_state[f"{iid}_{sd['label']}"]) for sd in sub_defs]
    st.session_state[f"main_{iid}"] = int(round(np.mean(vals)))

def render_intervention_slider(intervention: dict):
    """
    Renders one intervention with:
      - a main slider (no value=; uses session state)
      - optional sub-sliders when expanded
      - two-way syncing between main and subs
      - no Streamlit 'default + session state' warning
    """
    iid = intervention['id']
    main_key = f"main_{iid}"
    init_state(main_key, 0)  # init BEFORE widget creation

    st.markdown('<div class="slider-container">', unsafe_allow_html=True)
    col1, col2 = st.columns([0.9, 0.1])
    with col1:
        st.markdown(
            f"<div class='slider-header'><span class='slider-title'>{intervention['label']}</span></div>",
            unsafe_allow_html=True
        )
    with col2:
        toggle_key = f"toggle_{iid}"
        init_state(toggle_key, False)
        if st.button("›" if not st.session_state[toggle_key] else "‹",
                     key=f"btn_{iid}", type="secondary"):
            st.session_state[toggle_key] = not st.session_state[toggle_key]

    # MAIN slider — no `value=`; on_change scales sub-sliders
    st.slider(
        "Intensity", 0, 100,
        key=main_key, label_visibility="collapsed",
        on_change=partial(_on_main_change, iid, intervention["sub_sliders"])
    )

    # SUB sliders (only when expanded) — init once; no `value=`
    if st.session_state.get(toggle_key, False):
        sub_cols = st.columns(len(intervention["sub_sliders"])) if intervention["sub_sliders"] else [st]
        for col, sub in zip(sub_cols, intervention["sub_sliders"]):
            with col:
                st.caption(sub["label"].upper())
                sub_key = f"{iid}_{sub['label']}"
                init_state(sub_key, sub["value"])
                st.slider(
                    sub["label"], sub["min"], sub["max"],
                    key=sub_key, label_visibility="collapsed",
                    on_change=partial(_on_sub_change, iid, intervention["sub_sliders"])
                )

    st.markdown('</div>', unsafe_allow_html=True)



# ============================================================================
# MAIN APPLICATION - UPDATED LAYOUT
# ============================================================================

def main():
    """Compact header row with aligned search/time-series, followed by city visual, radar, and interventions."""
    apply_custom_css()

    header_left, header_mid, header_right = st.columns([0.26, 0.26, 0.48], gap="medium")

    with header_left:
        st.markdown("<div class='app-title'>Urban Performance Model</div>", unsafe_allow_html=True)

    with header_mid:
        st.markdown("<div class='section-label'>City Search</div>", unsafe_allow_html=True)
        st.markdown("<div class='search-wrap'>", unsafe_allow_html=True)
        search_query = st.text_input(
            "Search City",
            value=st.session_state.get("city_search", ""),
            key="city_search",
            label_visibility="collapsed",
            placeholder="Search for a city...",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    has_city_input = bool(search_query.strip())
    city_key = find_city(search_query) if has_city_input else None

    if city_key:
        kpis = CITY_DATA[city_key]["kpis"]
        current_values  = [k["value"] for k in kpis]
        improved_values = calculate_improved_kpis(city_key)
        labels          = [k["name"] for k in kpis]
        categories      = [k["category"] for k in kpis]
        cat_deltas = category_improvement_from_kpis(current_values, improved_values, categories)
        category_scores = compute_category_scores()
    else:
        kpis = []
        current_values = []
        improved_values = []
        labels = []
        categories = []
        cat_deltas = {}
        category_scores = None

    with header_right:
        st.markdown("<div class='section-label'>Time Series Projection</div>", unsafe_allow_html=True)
        if city_key:
            ts_chart = create_time_series_chart(city_key, category_scores)
            st.plotly_chart(ts_chart, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("Enter a city to view projections.")




    urban_form_value = float(st.session_state.get("main_urban_form", 0))
    height_scale = slider_to_height_scale(urban_form_value)

    # -------------------------------
    # ROW 2: City Visual + KPI Radar
    # -------------------------------
    row2_left, row2_right = st.columns([0.42, 0.58], gap="medium")

    with row2_left:
        st.markdown("<div class='section-label'>Overview</div>", unsafe_allow_html=True)
        if city_key:
            try:
                render_city_visual(CITY_DATA[city_key], height_scale)
            except Exception as exc:
                st.error("🗺️ Unable to load the city visualization.")
                st.exception(exc)
        else:
            st.info("Type a city name to load the 3D overview.")

    with row2_right:
        st.markdown("<div class='section-label'>KPI Radar</div>", unsafe_allow_html=True)
        if city_key:
            labels_wrapped = [_wrap_label(k["name"]) for k in kpis]
            radar_chart = create_radar_chart(current_values, improved_values, labels_wrapped, categories)
            st.plotly_chart(radar_chart, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("KPI radar will appear after selecting a city.")

    # -------------------------------
    # INTERVENTIONS
    # -------------------------------
    st.markdown("<div class='section-label'>Interventions</div>", unsafe_allow_html=True)
    int_col1, int_col2, int_col3, int_col4 = st.columns(4, gap="small")
    intervention_groups = [
        ["urban_form", "building_efficiency"],
        ["clean_energy", "urban_freight"],
        ["active_mobility", "public_transit"],
        ["waste"]
    ]
    for col, group in zip([int_col1, int_col2, int_col3, int_col4], intervention_groups):
        with col:
            for intervention_id in group:
                intervention = next(i for i in INTERVENTIONS if i["id"] == intervention_id)
                render_intervention_slider(intervention)


if __name__ == "__main__":
    main()
