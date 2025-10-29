import numpy as np
import streamlit as st
from plotly import graph_objects as go


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
    "Skyhaven": {
        "video_path": "city_skyhaven.mp4",
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
        "video_path": "city_harborlight.mp4",
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
    {
        "id": "upzoning",
        "label": "Upzoning",
        "impact_weights": {"Economic": 0.45, "Environmental": 0.15, "Social": 0.40},
        "sub_sliders": [
            {"label": "Housing Units Added (per yr)", "min": 0, "max": 1800, "value": 400},
            {"label": "Inclusionary %", "min": 0, "max": 60, "value": 12}
        ]
    },
    {
        "id": "retrofits",
        "label": "Building Retrofits",
        "impact_weights": {"Economic": 0.25, "Environmental": 0.55, "Social": 0.20},
        "sub_sliders": [
            {"label": "Net-Zero Retrofits (per yr)", "min": 0, "max": 200, "value": 40},
            {"label": "Local Workforce Share (%)", "min": 0, "max": 100, "value": 20}
        ]
    },
    {
        "id": "grid",
        "label": "Clean Energy Grid",
        "impact_weights": {"Economic": 0.35, "Environmental": 0.45, "Social": 0.20},
        "sub_sliders": [
            {"label": "Renewables Added (MW)", "min": 0, "max": 600, "value": 120},
            {"label": "Storage Capacity (MWh)", "min": 0, "max": 800, "value": 150}
        ]
    },
    {
        "id": "mixed_use",
        "label": "Mixed Use Zoning",
        "impact_weights": {"Economic": 0.50, "Environmental": 0.25, "Social": 0.25},
        "sub_sliders": [
            {"label": "Transit Parcels (%)", "min": 0, "max": 60, "value": 15},
            {"label": "Community Amenities (#)", "min": 0, "max": 50, "value": 10}
        ]
    },
    {
        "id": "freight",
        "label": "Urban Freight",
        "impact_weights": {"Economic": 0.35, "Environmental": 0.45, "Social": 0.20},
        "sub_sliders": [
            {"label": "EV Fleets Converted (%)", "min": 0, "max": 100, "value": 20},
            {"label": "Consolidation Hubs (#)", "min": 0, "max": 40, "value": 8}
        ]
    },
    {
        "id": "mobility",
        "label": "Active Mobility",
        "impact_weights": {"Economic": 0.25, "Environmental": 0.40, "Social": 0.35},
        "sub_sliders": [
            {"label": "Protected Lanes (km)", "min": 0, "max": 120, "value": 20},
            {"label": "Mode Share Target (%)", "min": 0, "max": 60, "value": 12}
        ]
    },
    {
        "id": "circular",
        "label": "Circular Economy",
        "impact_weights": {"Economic": 0.10, "Environmental": 0.60, "Social": 0.30},
        "sub_sliders": [
            {"label": "Organic Diversion (%)", "min": 0, "max": 90, "value": 20},
            {"label": "Recycling Coverage (%)", "min": 0, "max": 100, "value": 35}
        ]
    },
    {
        "id": "transit",
        "label": "Public Transit",
        "impact_weights": {"Economic": 0.20, "Environmental": 0.35, "Social": 0.45},
        "sub_sliders": [
            {"label": "New Routes (#)", "min": 0, "max": 25, "value": 5},
            {"label": "Service Frequency (%)", "min": 0, "max": 80, "value": 15}
        ]
    },
]


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


def calculate_improved_kpis(city_key: str, category_scores: dict) -> list:
    """Calculate improved KPI values based on category scores."""
    improved = []
    for kpi in CITY_DATA[city_key]["kpis"]:
        base_value = kpi["value"]
        lift_factor = 1 + (category_scores[kpi["category"]] / 100) * 0.35
        improved_value = min(base_value * lift_factor, 10.0)
        improved.append(round(improved_value, 2))
    return improved


# ============================================================================
# CHART FUNCTIONS
# ============================================================================

def create_radar_chart(current: list, improved: list, labels: list, categories: list):
    """Create compact radar chart for slide format."""
    max_value = 10
    n_points = len(labels)
    angles = np.linspace(0, 360, n_points, endpoint=False)
    theta_values = angles.tolist() + [angles[0]]

    traces = []
    # Current
    traces.append(go.Scatterpolar(
        r=current + [current[0]],
        theta=theta_values,
        name="Current",
        mode="lines",
        line=dict(color=COLORS["primary_mid"], width=2),
        fill="toself",
        fillcolor="rgba(115,192,255,0.20)"
    ))
    # Improved
    traces.append(go.Scatterpolar(
        r=improved + [improved[0]],
        theta=theta_values,
        name="2035",
        mode="lines",
        line=dict(color=COLORS["primary"], width=3),
        fill="toself",
        fillcolor="rgba(57,168,255,0.28)"
    ))

    fig = go.Figure(traces)
    fig.update_layout(
        height=400,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            angularaxis=dict(
                tickmode="array",
                tickvals=angles,
                ticktext=labels,
                rotation=90,
                direction="clockwise",
                color=COLORS['muted'],
                tickfont=dict(size=9)
            ),
            radialaxis=dict(
                range=[0, max_value],
                showline=False,
                gridcolor=COLORS['grid'],
                tickfont=dict(size=8, color=COLORS['muted'])
            )
        ),
        font=dict(color=COLORS['text']),
        legend=dict(
            orientation="h",
            y=1.08,
            x=0.5,
            xanchor="center",
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=10, color=COLORS['text'])
        )
    )
    return fig


def create_time_series_chart(city_key: str, category_scores: dict):
    """Create compact time series chart (smaller footprint)."""
    ts_data = CITY_DATA[city_key]["time_series"]
    economy = np.array(ts_data["economy"], dtype=float)
    environment = np.array(ts_data["environment"], dtype=float)
    health = np.array(ts_data["health"], dtype=float)
    econ_boost = category_scores["Economic"] / 100 * 12
    env_reduction = category_scores["Environmental"] / 100 * 18
    health_boost = category_scores["Social"] / 100 * 14
    economy_adj = economy + np.linspace(0, econ_boost, len(YEARS))
    environment_adj = np.maximum(environment - np.linspace(0, env_reduction, len(YEARS)), 20)
    health_adj = health + np.linspace(0, health_boost, len(YEARS))

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=YEARS, y=economy_adj, name="Economy", mode="lines+markers", line=dict(color=COLORS['primary'], width=2), marker=dict(size=3)))
    fig.add_trace(go.Scatter(x=YEARS, y=environment_adj, name="Environment", mode="lines+markers", line=dict(color=COLORS['primary_mid'], width=2, dash="dash"), marker=dict(size=3)))
    fig.add_trace(go.Scatter(x=YEARS, y=health_adj, name="Health", mode="lines+markers", line=dict(color=COLORS['primary_light'], width=2, dash="dot"), marker=dict(size=3)))

    fig.update_layout(
        height=180,
        margin=dict(l=20, r=10, t=5, b=25),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=COLORS['text']),
        legend=dict(orientation="h", y=1.2, x=0.5, xanchor="center", bgcolor="rgba(0,0,0,0)", font=dict(size=9, color=COLORS['text'])),
        xaxis=dict(title="", showgrid=False, zeroline=False, color=COLORS['muted'], tickfont=dict(size=9)),
        yaxis=dict(title="Index", gridcolor=COLORS['grid'], zeroline=False, color=COLORS['muted'], tickfont=dict(size=9))
    )
    return fig


# ============================================================================
# UI COMPONENTS
# ============================================================================

def render_intervention_slider(intervention: dict):
    """Render intervention slider with upgraded header/value and optional sub-sliders."""
    main_key = f"main_{intervention['id']}"
    current_value = int(st.session_state.get(main_key, 0))

    st.markdown('<div class="slider-container">', unsafe_allow_html=True)

    # Header with title + value and compact expand button on the right
    col1, col2 = st.columns([0.9, 0.1])
    with col1:
        st.markdown(f"""
        <div class="slider-header">
            <span class="slider-title">{intervention['label']}</span>

        </div>
        """, unsafe_allow_html=True)
    with col2:
        toggle_key = f"toggle_{intervention['id']}"
        if toggle_key not in st.session_state:
            st.session_state[toggle_key] = False
        if st.button("›" if not st.session_state[toggle_key] else "‹", key=f"btn_{intervention['id']}", type="secondary"):
            st.session_state[toggle_key] = not st.session_state[toggle_key]

    # Main slider
    st.slider("Intensity", 0, 100, current_value, key=main_key, label_visibility="collapsed")

    # Sub-sliders
    if st.session_state.get(toggle_key, False):
        sub_cols = st.columns(len(intervention["sub_sliders"]))
        for col, sub in zip(sub_cols, intervention["sub_sliders"]):
            with col:
                st.caption(sub["label"].upper())
                sub_key = f"{intervention['id']}_{sub['label']}"
                st.slider(
                    sub["label"],
                    sub["min"],
                    sub["max"],
                    int(st.session_state.get(sub_key, sub["value"])),
                    key=sub_key,
                    label_visibility="collapsed"
                )

    st.markdown('</div>', unsafe_allow_html=True)


# ============================================================================
# MAIN APPLICATION - UPDATED LAYOUT
# ============================================================================

def main():
    """Main application with search+video (left) | time series (right) on the top row,
    radar full-width below, then interventions."""
    apply_custom_css()

   # Title
    st.markdown("<div class='app-title'>Urban Performance Model</div>", unsafe_allow_html=True)

    # -------------------------------
    # ROW 1: Search + Time Series
    # -------------------------------
    st.markdown("<div class='section-label'>City Search</div>", unsafe_allow_html=True)
    row1_left, row1_right = st.columns([0.42, 0.58], gap="medium")

    with row1_left:
        # Short search input (width constrained by CSS .search-wrap)
        st.markdown("<div class='search-wrap'>", unsafe_allow_html=True)
        search_query = st.text_input(
            "Search City",
            value=st.session_state.get("city_search", ""),
            key="city_search",
            label_visibility="collapsed",
            placeholder="Skyhaven or Harborlight"
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # Resolve selected city
        city_key = find_city(search_query)

    # Compute scores once (used by both charts below)
    category_scores = compute_category_scores()

    with row1_right:
        st.markdown("<div class='section-label'>Time Series Projection</div>", unsafe_allow_html=True)
        ts_chart = create_time_series_chart(city_key, category_scores)
        st.plotly_chart(ts_chart, use_container_width=True, config={"displayModeBar": False})

    # Pre-compute KPI vectors for radar (used in Row 2)
    kpis = CITY_DATA[city_key]["kpis"]
    current_values = [k["value"] for k in kpis]
    improved_values = calculate_improved_kpis(city_key, category_scores)
    labels = [k["name"] for k in kpis]
    categories = [k["category"] for k in kpis]

    # -------------------------------
    # ROW 2: Video + KPI Radar
    # -------------------------------
    row2_left, row2_right = st.columns([0.42, 0.58], gap="medium")

    with row2_left:
        st.markdown("<div class='section-label'>Overview</div>", unsafe_allow_html=True)
        try:
            video_path = CITY_DATA[city_key]["video_path"]
            st.markdown('<div class="video-container">', unsafe_allow_html=True)
            st.video(video_path)
            st.markdown('</div>', unsafe_allow_html=True)
        except Exception:
            st.info(f"📹 Place '{CITY_DATA[city_key]['video_path']}' here")

    with row2_right:
        st.markdown("<div class='section-label'>KPI Radar</div>", unsafe_allow_html=True)
        radar_chart = create_radar_chart(current_values, improved_values, labels, categories)
        st.plotly_chart(radar_chart, use_container_width=True, config={"displayModeBar": False})

    # -------------------------------
    # INTERVENTIONS
    # -------------------------------
    st.markdown("<div class='section-label'>Interventions</div>", unsafe_allow_html=True)
    int_col1, int_col2, int_col3, int_col4 = st.columns(4, gap="small")
    intervention_groups = [
        ["upzoning", "retrofits"],
        ["grid", "mixed_use"],
        ["freight", "mobility"],
        ["circular", "transit"]
    ]
    for col, group in zip([int_col1, int_col2, int_col3, int_col4], intervention_groups):
        with col:
            for intervention_id in group:
                intervention = next(i for i in INTERVENTIONS if i["id"] == intervention_id)
                render_intervention_slider(intervention)


if __name__ == "__main__":
    main()

