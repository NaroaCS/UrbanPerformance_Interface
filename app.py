import numpy as np
import streamlit as st
from plotly import graph_objects as go

# ---------------------------------------------------------------------------
# Streamlit configuration & look-and-feel
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Urban Performance Interface",
    page_icon="🌆",
    layout="wide",
)

CUSTOM_STYLE = """
<style>
/* Overall canvas --------------------------------------------------------- */
.block-container {
    max-width: 1360px;
    padding: 1.6rem 2.0rem 0.9rem;
}
.stApp {
    background: #010103;
    color: #f4fbff;
    font-family: "Montserrat", "Inter", "Source Sans Pro", sans-serif;
    overflow-x: hidden;
}
h1, h2, h3, h4 {
    font-weight: 600;
    letter-spacing: 0.02em;
}
.app-title {
    font-size: 2.28rem;
    text-transform: uppercase;
    letter-spacing: 0.22em;
    color: #f4fbff;
    margin-bottom: 1.1rem;
}

/* Search + labels -------------------------------------------------------- */
.section-label {
    text-transform: uppercase;
    letter-spacing: 0.28em;
    color: #6bcdfc;
    font-size: 0.74rem;
    margin-bottom: 0.3rem;
}
div[data-testid="stTextInput"] input {
    background: rgba(2, 4, 8, 0.78);
    border: 1px solid rgba(109, 209, 252, 0.55);
    color: #f4fbff;
    font-size: 0.94rem;
    padding: 0.5rem 0.78rem;
    border-radius: 0;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
div[data-testid="stTextInput"] input::placeholder {
    color: rgba(244, 251, 255, 0.38);
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* Chart headings --------------------------------------------------------- */
.chart-title,
.panel-title {
    font-size: 0.82rem;
    text-transform: uppercase;
    letter-spacing: 0.24em;
    color: rgba(155, 222, 255, 0.95);
    margin-bottom: 0.55rem;
}

/* Mini bar legend -------------------------------------------------------- */
.mini-metric {
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 0.35rem 0.75rem;
    align-items: center;
}
.mini-label {
    font-size: 0.74rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: rgba(242, 251, 255, 0.75);
}
.mini-track {
    grid-column: 1 / -1;
    width: 100%;
    height: 6px;
    border-radius: 999px;
    background: rgba(107, 205, 252, 0.18);
    position: relative;
    overflow: hidden;
}
.mini-fill {
    position: absolute;
    top: 0;
    left: 0;
    height: 100%;
    border-radius: 999px;
}
.mini-value {
    font-size: 0.72rem;
    letter-spacing: 0.12em;
    color: rgba(242, 251, 255, 0.7);
}

/* Expanders -------------------------------------------------------------- */
.st-expander {
    border: 1px solid rgba(107, 205, 252, 0.28);
    background: rgba(5, 8, 15, 0.58);
}
.st-expander:hover {
    border-color: rgba(107, 205, 252, 0.48);
}

/* Slider labels ---------------------------------------------------------- */
.slider-label {
    display: flex;
    align-items: center;
    gap: 0.35rem;
    font-size: 0.82rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: rgba(242, 251, 255, 0.9);
    margin-bottom: 0.28rem;
}
.slider-icon {
    font-size: 0.65rem;
    color: rgba(229, 190, 255, 0.75);
}
.sub-slider-label {
    font-size: 0.66rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: rgba(242, 251, 255, 0.62);
    margin-bottom: 0.18rem;
}

/* === Slider wrapper === */
div[data-testid="stSlider"] {
  margin-bottom: 1rem;   /* spacing below slider */
  padding: 0;
}

/* === Slider container === */
div[data-testid="stSlider"] [data-baseweb="slider"] {
  background: transparent;
  padding: 0;
  box-shadow: none;
}

/* === Slider rail (inactive line) === */
div[data-testid="stSlider"] [data-baseweb="slider"] > div[style*="height"] {
  height: 2px !important;
  border-radius: 999px;
  background: rgba(107, 205, 252, 0.24);   /* light blue rail */
}

/* === Active track (filled portion) === */
div[data-testid="stSlider"] [data-baseweb="slider"] > div[style*="height"]:not(:first-of-type) {
  background: #6bcdfc !important;          /* solid blue fill */
}

/* === Thumb (handle) === */
div[data-testid="stSlider"] [role="slider"] {
  width: 14px;
  height: 14px;
  border-radius: 999px;
  background: #6bcdfc;                     /* blue thumb */
  border: 1px solid #010103;               /* subtle dark outline */
  box-shadow: none;
  transition: transform 0.15s ease, background 0.15s ease, box-shadow 0.15s ease;
}

div[data-testid="stSlider"] [role="slider"]:hover {
  background: #8dd6ff;                     /* brighter blue hover */
  transform: scale(1.06);                  /* small grow on hover */
}

div[data-testid="stSlider"] [role="slider"]:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(107,205,252,0.35); /* soft blue focus ring */
}

/* === Number label above slider === */
div[data-testid="stSlider"] label {
  color: #6bcdfc !important;               /* make number text blue */
  font-weight: 600;                        /* optional: slightly bolder */
}

/* === Reset any leftover Streamlit defaults === */
.stSlider > div > div { 
  background: transparent !important; 
  height: auto !important; 
}

/* Section titles --------------------------------------------------------- */
.intervention-heading {
    font-size: 1.02rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #f4fbff;
    margin: 0.2rem 0 0.8rem 0;
}
.column-heading {
    font-size: 0.74rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: rgba(242, 251, 255, 0.7);
    margin-bottom: 0.4rem;
}
.caption-text {
    color: rgba(242, 251, 255, 0.55);
    font-size: 0.74rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}
.stMarkdown hr {
    border-color: rgba(107, 205, 252, 0.12);
}

/* Support program card --------------------------------------------------- */
.support-card {
    margin-top: 0.35rem;
    padding: 0.85rem 0.85rem 0.75rem;
    border: 1px solid rgba(107, 205, 252, 0.28);
    border-radius: 12px;
    background: rgba(2, 6, 12, 0.72);
    box-shadow: 0 10px 22px rgba(0, 0, 0, 0.42);
    display: flex;
    flex-direction: column;
    gap: 0.6rem;
}
.support-card-title {
    font-size: 0.72rem;
    letter-spacing: 0.24em;
    text-transform: uppercase;
    color: rgba(155, 222, 255, 0.95);
}
.support-row {
    display: flex;
    flex-direction: column;
    gap: 0.22rem;
}
.support-label {
    font-size: 0.68rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: rgba(244, 251, 255, 0.7);
}
.support-track {
    width: 100%;
    height: 6px;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.15);
    position: relative;
}
.support-fill {
    position: absolute;
    top: 0;
    left: 0;
    height: 100%;
    border-radius: 999px;
}
.stProgress > div > div {
    background: rgba(107, 205, 252, 0.65);
}

/* Embedded video --------------------------------------------------------- */
.video-frame {
    margin-top: 0.95rem;
    max-width: 400px;
}
.video-frame iframe {
    border: 1px solid rgba(107, 205, 252, 0.28);
    border-radius: 6px;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.48);
}

/* Slider toggle icon ----------------------------------------------------- */
.slider-toggle {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    padding-top: 0.2rem;
}
.slider-toggle .stButton > button {
    background: #7c5fa2;
    color: #010103;
    width: 24px;
    height: 24px;
    border-radius: 4px;
    border: 0;
    padding: 0;
    font-size: 0.9rem;
    line-height: 0.9rem;
    box-shadow: none;
}
.slider-toggle .stButton > button:hover {
    background: #8d6db5;
}
.slider-toggle .stButton > button:focus:not(:active) {
    box-shadow: 0 0 0 0 rgba(0,0,0,0);
    outline: none;
}
.slider-group {
    margin-bottom: 0.4rem;
}
</style>
"""
st.markdown(CUSTOM_STYLE, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Source data (all inline for easy maintenance)
# ---------------------------------------------------------------------------
YEARS = list(range(2025, 2036))
CATEGORY_ORDER = ["Economic", "Environmental", "Social"]
CATEGORY_COLORS = {
    "Economic": "#39c0f5",
    "Environmental": "#6a4c93",
    "Social": "#ffd166",
}

# --- City scenario data ----------------------------------------------------
# Each city object bundles KPI values, chart series, and media. Update here to
# refresh demo content while keeping the plotting logic untouched.
# KPI definition keeps the display order consistent across charts.
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

# --- Intervention controls -------------------------------------------------
# Sliders below drive the KPI boosts. Adjust labels, weights, or sub-sliders
# here whenever the UX team wants a new lever or different assumptions.
INTERVENTIONS = [
    {
        "id": "upzoning",
        "label": "Upzoning",
        "impact_weights": {"Economic": 0.45, "Environmental": 0.15, "Social": 0.40},
        "sub_sliders": [
            {"label": "Housing Units Added (per yr)", "min": 0, "max": 1800, "value": 400},
            {"label": "Inclusionary %", "min": 0, "max": 60, "value": 12},
        ],
    },
    {
        "id": "retrofits",
        "label": "Building Retrofits & Standards",
        "impact_weights": {"Economic": 0.25, "Environmental": 0.55, "Social": 0.20},
        "sub_sliders": [
            {"label": "Net-Zero Retrofits (per yr)", "min": 0, "max": 200, "value": 40},
            {"label": "Local Workforce Share (%)", "min": 0, "max": 100, "value": 20},
        ],
    },
    {
        "id": "grid",
        "label": "Clean Energy & Grid Modernization",
        "impact_weights": {"Economic": 0.35, "Environmental": 0.45, "Social": 0.20},
        "sub_sliders": [
            {"label": "Renewables Added (MW)", "min": 0, "max": 600, "value": 120},
            {"label": "Storage Capacity (MWh)", "min": 0, "max": 800, "value": 150},
        ],
    },
    {
        "id": "mixed_use",
        "label": "Mixed Use Zoning",
        "impact_weights": {"Economic": 0.5, "Environmental": 0.25, "Social": 0.25},
        "sub_sliders": [
            {"label": "Transit Parcels (%)", "min": 0, "max": 60, "value": 15},
            {"label": "Community Amenities (#)", "min": 0, "max": 50, "value": 10},
        ],
    },
    {
        "id": "freight",
        "label": "Urban Freight Transition",
        "impact_weights": {"Economic": 0.35, "Environmental": 0.45, "Social": 0.20},
        "sub_sliders": [
            {"label": "EV Fleets Converted (%)", "min": 0, "max": 100, "value": 20},
            {"label": "Consolidation Hubs (#)", "min": 0, "max": 40, "value": 8},
        ],
    },
    {
        "id": "mobility",
        "label": "Active Mobility Networks",
        "impact_weights": {"Economic": 0.25, "Environmental": 0.4, "Social": 0.35},
        "sub_sliders": [
            {"label": "Protected Lanes (km)", "min": 0, "max": 120, "value": 20},
            {"label": "Mode Share Target (%)", "min": 0, "max": 60, "value": 12},
        ],
    },
    {
        "id": "circular",
        "label": "Circular Waste & Materials",
        "impact_weights": {"Economic": 0.1, "Environmental": 0.6, "Social": 0.3},
        "sub_sliders": [
            {"label": "Organic Diversion (%)", "min": 0, "max": 90, "value": 20},
            {"label": "Recycling Coverage (%)", "min": 0, "max": 100, "value": 35},
        ],
    },
    {
        "id": "transit",
        "label": "Public Transit Expansion",
        "impact_weights": {"Economic": 0.2, "Environmental": 0.35, "Social": 0.45},
        "sub_sliders": [
            {"label": "New Routes (#)", "min": 0, "max": 25, "value": 5},
            {"label": "Service Frequency (%)", "min": 0, "max": 80, "value": 15},
        ],
    },
]

# --- Support programs card -------------------------------------------------
# The annotation card in the lower-right uses this list (label + progress %).
ADDITIONAL_PROGRAMS = [
    {"name": "Electrify", "value": 84, "color": "#5AC5F7"},
    {"name": "Expand Coverage", "value": 72, "color": "#F5AF3C"},
    {"name": "Subsidies", "value": 58, "color": "#F5AF3C"},
]

# Precompute lookups so UI code can stay tidy.
INTERVENTION_LOOKUP = {item["id"]: item for item in INTERVENTIONS}


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------
def find_city(match: str) -> str:
    """Return the canonical city key given free text input, defaulting to the first city."""
    if not match:
        return list(CITY_DATA.keys())[0]
    for city in CITY_DATA:
        if city.lower() == match.strip().lower():
            return city
    # Support partial match on start of the name for a friendly search experience.
    for city in CITY_DATA:
        if city.lower().startswith(match.strip().lower()):
            return city
    return list(CITY_DATA.keys())[0]


def compute_category_scores_from_state() -> dict[str, float]:
    """Aggregate intervention intensity scores using current slider state."""
    category_scores = {category: 0.0 for category in CATEGORY_ORDER}
    for intervention in INTERVENTIONS:
        main_key = f"main_{intervention['id']}"
        main_value = float(st.session_state.get(main_key, 0))

        sub_values = []
        for sub_slider in intervention["sub_sliders"]:
            sub_key = f"{intervention['id']}_{sub_slider['label']}"
            sub_values.append(float(st.session_state.get(sub_key, 0)))

        if sub_values:
            sub_normalised = [
                (value / sub_slider["max"]) * 100 if sub_slider["max"] else 0
                for value, sub_slider in zip(sub_values, intervention["sub_sliders"])
            ]
            sub_average = float(np.mean(sub_normalised))
            combined_intensity = (main_value + sub_average) / 2
        else:
            combined_intensity = main_value

        for category, weight in intervention["impact_weights"].items():
            category_scores[category] += combined_intensity * weight

    return {cat: min(score, 100.0) for cat, score in category_scores.items()}


def toggle_flag(key: str) -> None:
    """Flip a boolean session flag used for slider detail visibility."""
    st.session_state[key] = not st.session_state.get(key, False)


def render_single_intervention(intervention: dict) -> None:
    """Render one intervention slider and its assumption expander."""
    toggle_key = f"toggle_{intervention['id']}"
    if toggle_key not in st.session_state:
        st.session_state[toggle_key] = False

    st.markdown('<div class="slider-group">', unsafe_allow_html=True)
    row_cols = st.columns([0.36, 0.54, 0.10], gap="small")

    with row_cols[0]:
        st.markdown(
            f'<div class="slider-label">{intervention["label"]}</div>',
            unsafe_allow_html=True,
        )

    with row_cols[1]:
        st.slider(
            "",
            min_value=0,
            max_value=100,
            value=0,
            key=f"main_{intervention['id']}",
            label_visibility="collapsed",
        )

    with row_cols[2]:
        arrow = "▾" if st.session_state[toggle_key] else "▸"
        st.markdown('<div class="slider-toggle">', unsafe_allow_html=True)
        st.button(
            arrow,
            key=f"toggle_btn_{intervention['id']}",
            on_click=toggle_flag,
            args=(toggle_key,),
        )
        st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state[toggle_key]:
        sub_cols = st.columns(len(intervention["sub_sliders"]), gap="small")
        for col, sub_slider in zip(sub_cols, intervention["sub_sliders"]):
            with col:
                st.markdown(
                    f'<div class="sub-slider-label">{sub_slider["label"]}</div>',
                    unsafe_allow_html=True,
                )
                st.slider(
                    "",
                    min_value=sub_slider["min"],
                    max_value=sub_slider["max"],
                    value=0,
                    key=f"{intervention['id']}_{sub_slider['label']}",
                    label_visibility="collapsed",
                )
    st.markdown("</div>", unsafe_allow_html=True)


def render_support_card() -> None:
    """Simple supporting program breakdown card for the right column."""
    st.markdown('<div class="support-card">', unsafe_allow_html=True)
    st.markdown('<div class="support-card-title">Program Focus</div>', unsafe_allow_html=True)
    for program in ADDITIONAL_PROGRAMS:
        st.markdown(
            f"""
            <div class="support-row">
                <div class="support-label">{program["name"]}</div>
                <div class="support-track">
                    <span class="support-fill" style="width:{program["value"]}%; background:{program["color"]};"></span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


def render_intervention_controls() -> None:
    """Display interventions in three columns mirroring the reference layout."""
    columns = st.columns([1, 1, 1], gap="large")
    # Update layout_groups to move sliders between columns or change their order.
    layout_groups = [
        ["upzoning", "retrofits", "grid"],
        ["mixed_use", "freight", "mobility"],
        ["circular", "transit"],
    ]

    for idx, (column, group) in enumerate(zip(columns, layout_groups)):
        with column:
            if idx == 0:
                st.markdown('<div class="column-heading">Economic / Environmental</div>', unsafe_allow_html=True)
            elif idx == 1:
                st.markdown('<div class="column-heading">Mobility & Freight</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="column-heading">Social</div>', unsafe_allow_html=True)
            for intervention_id in group:
                render_single_intervention(INTERVENTION_LOOKUP[intervention_id])
            if idx == len(layout_groups) - 1:
                render_support_card()


def render_category_summary(category_scores: dict[str, float]) -> None:
    """Draw compact bars to echo the visual legend in the example layout."""
    for category in CATEGORY_ORDER:
        value = category_scores.get(category, 0.0)
        fill = CATEGORY_COLORS.get(category, "#39c0f5")
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


def build_radar(current_values: list[float], improved_values: list[float], labels: list[str], categories: list[str]) -> go.Figure:
    """Create a radar chart with category wraps and textual headers."""
    max_value = 10
    count = len(labels)
    angles = np.linspace(0, 360, count, endpoint=False)
    theta_loop = angles.tolist() + [angles[0]]

    base_trace = go.Scatterpolar(
        r=current_values + [current_values[0]],
        theta=theta_loop,
        fill="toself",
        name="Current",
        line=dict(color="#39c0f5"),
        fillcolor="rgba(57, 192, 245, 0.28)",
    )

    improved_trace = go.Scatterpolar(
        r=improved_values + [improved_values[0]],
        theta=theta_loop,
        fill="toself",
        name="2035",
        line=dict(color="#ffd166"),
        fillcolor="rgba(255, 209, 102, 0.35)",
    )

    envelope_traces = []
    text_traces = []
    for category in CATEGORY_ORDER:
        cat_indices = [i for i, cat in enumerate(categories) if cat == category]
        if not cat_indices:
            continue
        cat_theta = [angles[i] for i in cat_indices]
        cat_theta.append(cat_theta[0])
        envelope_traces.append(
            go.Scatterpolar(
                r=[max_value] * len(cat_theta),
                theta=cat_theta,
                name=f"{category} envelope",
                mode="lines",
                line=dict(color="rgba(108, 205, 252, 0.14)", width=2),
                fill="toself",
                fillcolor="rgba(108, 205, 252, 0.05)",
                hoverinfo="skip",
                showlegend=False,
            )
        )
        anchor_angle = float(np.mean([angles[i] for i in cat_indices]))
        text_traces.append(
            go.Scatterpolar(
                r=[max_value + 0.8],
                theta=[anchor_angle],
                mode="text",
                text=[category],
                textfont=dict(size=14, color="rgba(244, 251, 255, 0.85)"),
                showlegend=False,
                hoverinfo="skip",
            )
        )

    fig = go.Figure(data=envelope_traces + [base_trace, improved_trace] + text_traces)
    angularaxis = dict(
        tickmode="array",
        tickvals=angles,
        ticktext=labels,
        rotation=90,
        direction="clockwise",
        showline=False,
        color="rgba(244, 251, 255, 0.65)",
        tickfont=dict(size=11, family="Montserrat"),
    )
    radialaxis = dict(
        range=[0, max_value],
        showline=False,
        gridcolor="rgba(255, 255, 255, 0.12)",
        tickfont=dict(size=10, color="rgba(244, 251, 255, 0.65)"),
    )

    fig.update_layout(
        template=None,
        polar=dict(
            bgcolor="rgba(0, 0, 0, 0)",
            angularaxis=angularaxis,
            radialaxis=radialaxis,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="rgba(244, 251, 255, 0.92)", family="Montserrat"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=10),
            bgcolor="rgba(0,0,0,0)",
        ),
        margin=dict(l=30, r=30, t=24, b=14),
        height=290,
    )
    return fig


def build_time_series(city_key: str, category_scores: dict[str, float]) -> go.Figure:
    """Generate the year-by-year performance curves influenced by interventions."""
    city_series = CITY_DATA[city_key]["time_series"]
    years = YEARS

    economy = np.array(city_series["economy"], dtype=float)
    environment = np.array(city_series["environment"], dtype=float)
    health = np.array(city_series["health"], dtype=float)

    econ_boost = category_scores["Economic"] / 100 * 12
    env_drop = category_scores["Environmental"] / 100 * 18
    health_boost = category_scores["Social"] / 100 * 14

    economy_adjusted = economy + np.linspace(0, econ_boost, len(years))
    environment_adjusted = np.maximum(
        environment - np.linspace(0, env_drop, len(years)),
        20,
    )
    health_adjusted = health + np.linspace(0, health_boost, len(years))

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=years,
            y=economy_adjusted,
            name="Economy",
            mode="lines+markers",
            line=dict(color="#39c0f5", width=3),
            marker=dict(size=4),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=years,
            y=environment_adjusted,
            name="Environment (↓ is better)",
            mode="lines+markers",
            line=dict(color="#6a4c93", width=3),
            marker=dict(size=4),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=years,
            y=health_adjusted,
            name="Health & Wellbeing",
            mode="lines+markers",
            line=dict(color="#ffd166", width=3),
            marker=dict(size=4),
        )
    )

    fig.update_layout(
        height=185,
        margin=dict(l=20, r=6, t=26, b=16),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        font=dict(color="rgba(244, 251, 255, 0.9)", family="Montserrat"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.12,
            x=0.5,
            xanchor="center",
            font=dict(size=10),
            bgcolor="rgba(0,0,0,0)",
        ),
        xaxis=dict(
            title="",
            showgrid=False,
            zeroline=False,
            color="rgba(244, 251, 255, 0.7)",
        ),
        yaxis=dict(
            title="Index",
            gridcolor="rgba(255, 255, 255, 0.09)",
            zeroline=False,
            color="rgba(244, 251, 255, 0.7)",
        ),
    )
    return fig


def compute_improved_kpis(city_key: str, category_scores: dict[str, float]) -> list[float]:
    """Scale each KPI by its category lift while keeping values bounded."""
    kpis = CITY_DATA[city_key]["kpis"]
    improved_values = []
    for kpi in kpis:
        base = kpi["value"]
        boost_factor = 1 + (category_scores[kpi["category"]] / 100) * 0.35
        improved = min(base * boost_factor, 10.0)
        improved_values.append(round(improved, 2))
    return improved_values


# ---------------------------------------------------------------------------
# Interface
# ---------------------------------------------------------------------------
st.markdown('<div class="app-title">Urban Performance Model</div>', unsafe_allow_html=True)

# --- Hero row: title/search (left) + trajectory chart (right) -------------
search_default = st.session_state.get("city_search", "")
category_scores_live = compute_category_scores_from_state()
selected_city = find_city(search_default)
time_series_fig = None
radar_fig = None
city = CITY_DATA[selected_city]

top_left, top_right = st.columns([0.56, 0.44], gap="large")

with top_left:
    # Title block: adjust column width ratios above to shift horizontal balance.
    st.markdown('<div class="section-label">Search City</div>', unsafe_allow_html=True)
    search_input = st.text_input(
        "Search City",
        value=search_default,
        key="city_search",
        label_visibility="collapsed",
        placeholder="Type Skyhaven or Harborlight",
    )
    selected_city = find_city(search_input)
    city = CITY_DATA[selected_city]
    kpi_values = [entry["value"] for entry in city["kpis"]]
    kpi_labels = [entry["name"] for entry in city["kpis"]]
    kpi_categories = [entry["category"] for entry in city["kpis"]]
    time_series_fig = build_time_series(selected_city, category_scores_live)
    improved_kpi_values = compute_improved_kpis(selected_city, category_scores_live)
    radar_fig = build_radar(kpi_values, improved_kpi_values, kpi_labels, kpi_categories)

    city_options = " · ".join(CITY_DATA.keys())
    st.markdown(
        f'<div class="caption-text">Available: {city_options}</div>',
        unsafe_allow_html=True,
    )
    video_id = city["video_url"].split("v=")[-1]
    video_id = video_id.split("&")[0]
    # Embedded video occupies the lower-left quadrant; tweak iframe width/height if needed.
    st.markdown(
        f"""
        <div class="video-frame">
            <iframe width="400" height="220"
                src="https://www.youtube.com/embed/{video_id}"
                title="{selected_city} overview"
                frameborder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                allowfullscreen></iframe>
        </div>
        """,
        unsafe_allow_html=True,
    )

with top_right:
    # Trajectory chart lives in the hero row. Adjust build_time_series() for sizing tweaks.
    st.plotly_chart(
        time_series_fig,
        use_container_width=True,
        config={"displayModeBar": False},
    )
    st.plotly_chart(
        radar_fig,
        use_container_width=True,
        config={"displayModeBar": False},
    )

# --- Intervention grid ----------------------------------------------------
st.markdown('<div class="section-label" style="margin-top: 1.1rem;">Interventions</div>', unsafe_allow_html=True)
st.markdown('<div class="intervention-heading">Interventions</div>', unsafe_allow_html=True)
render_intervention_controls()

# --- Footer note ----------------------------------------------------------
st.markdown('<hr style="margin-top: 1rem; margin-bottom: 0.5rem;"/>', unsafe_allow_html=True)
st.markdown(
    '<div class="caption-text">Data inputs live inside this file as Python lists for quick manual edits.</div>',
    unsafe_allow_html=True,
)
