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
    """Apply all custom CSS styling."""
    st.markdown(f"""
    <style>
        /* Base Styles */
        html, body {{
            background: {COLORS['bg']};
            color: {COLORS['text']};
        }}
        
        header[data-testid="stHeader"] {{
            background: {COLORS['bg']};
            visibility: hidden;
            height: 0;
        }}
        
        .stApp {{
            background: {COLORS['bg']};
            color: {COLORS['text']};
            font-family: 'Inter', 'Montserrat', system-ui, sans-serif;
        }}
        
        .block-container {{
            max-width: 1600px;
            padding: 2rem 2rem 1rem;
        }}
        
        /* Typography */
        h1, h2, h3, h4 {{
            letter-spacing: 0.02em;
            font-weight: 600;
            color: {COLORS['text']};
        }}
        
        .app-title {{
            font-size: 2.2rem;
            letter-spacing: 0.20em;
            text-transform: uppercase;
            margin: 0 0 1.5rem 0;
            color: {COLORS['text']};
        }}
        
        .section-label {{
            text-transform: uppercase;
            letter-spacing: 0.22em;
            color: {COLORS['primary_light']};
            font-size: 0.7rem;
            margin: 1.5rem 0 0.8rem;
            font-weight: 600;
        }}
        
        .caption-text {{
            color: {COLORS['muted']};
            font-size: 0.75rem;
            letter-spacing: 0.10em;
            text-transform: uppercase;
            margin-top: 0.5rem;
        }}
        
        /* Search Input */
        div[data-testid="stTextInput"] input {{
            background: rgba(8,18,28,0.6);
            border: 1px solid rgba(115,192,255,0.25);
            color: {COLORS['text']};
            font-size: 0.95rem;
            padding: 0.6rem 0.8rem;
            border-radius: 8px;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }}
        
        div[data-testid="stTextInput"] input::placeholder {{
            color: {COLORS['muted']};
        }}
        
        /* Mini Metric Bars */
        .mini-metric {{
            display: grid;
            grid-template-columns: 1fr auto;
            gap: 0.3rem 0.8rem;
            align-items: center;
            margin-bottom: 0.8rem;
        }}
        
        .mini-label {{
            font-size: 0.7rem;
            letter-spacing: 0.16em;
            text-transform: uppercase;
            color: {COLORS['muted']};
            font-weight: 500;
        }}
        
        .mini-track {{
            grid-column: 1 / -1;
            width: 100%;
            height: 8px;
            border-radius: 999px;
            background: rgba(115,192,255,0.15);
            position: relative;
            overflow: hidden;
        }}
        
        .mini-fill {{
            position: absolute;
            inset: 0 auto 0 0;
            height: 100%;
            border-radius: 999px;
        }}
        
        .mini-value {{
            font-size: 0.7rem;
            letter-spacing: 0.10em;
            color: {COLORS['muted']};
            font-weight: 500;
        }}
        
        /* Slider Container */
        .slider-container {{
            margin-bottom: 1.5rem;
        }}
        
        .slider-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.5rem;
        }}
        
        .slider-title {{
            font-size: 0.75rem;
            letter-spacing: 0.18em;
            text-transform: uppercase;
            color: {COLORS['text']};
            font-weight: 600;
        }}
        
        .slider-value {{
            display: inline-block;
            min-width: 32px;
            padding: 3px 8px;
            border-radius: 6px;
            text-align: center;
            font-size: 0.75rem;
            font-weight: 600;
            color: {COLORS['bg']};
            background: {COLORS['primary_mid']};
            border: 1px solid rgba(115,192,255,0.45);
        }}
        
        .expand-button {{
            color: {COLORS['text']};
            font-size: 1rem;
            cursor: pointer;
            user-select: none;
            opacity: 0.7;
            transition: opacity 0.2s;
        }}
        
        .expand-button:hover {{
            opacity: 1;
        }}
        
        /* Slider Styling */
        div[data-testid="stSlider"] {{
            margin: 0.5rem 0 1rem;
        }}
        
        /* Slider rail */
        div[data-testid="stSlider"] [data-baseweb="slider"] > div[style*="height"] {{
            height: 3px !important;
            background: rgba(115,192,255,0.28);
            border-radius: 999px;
        }}
        
        /* Active track (blue fill) */
        div[data-testid="stSlider"] [data-baseweb="slider"] > div[style*="height"]:not(:first-of-type) {{
            background: {COLORS['primary_mid']} !important;
        }}
        
        /* Slider thumb */
        div[data-testid="stSlider"] [role="slider"] {{
            width: 14px;
            height: 14px;
            border-radius: 999px;
            background: {COLORS['primary_mid']};
            border: 2px solid {COLORS['bg']};
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }}
        
        /* Hide default value bubble */
        div[data-testid="stSlider"] [data-baseweb="slider"] div[aria-hidden="true"] {{
            display: none !important;
        }}
        
        /* Slider label colors */
        div[data-testid="stSlider"] label {{
            color: {COLORS['primary_light']} !important;
            font-weight: 600;
        }}
        
        /* Sub-slider caption */
        .stCaption {{
            color: {COLORS['muted']};
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            margin-bottom: 0.3rem;
        }}
        
        /* Divider */
        hr {{
            border-color: rgba(115,192,255,0.15);
            margin: 1.5rem 0;
        }}
        
        /* Video Container */
        .video-container {{
            border-radius: 12px;
            overflow: hidden;
            background: rgba(0,0,0,0.3);
            border: 1px solid rgba(115,192,255,0.2);
        }}
    </style>
    """, unsafe_allow_html=True)


# ============================================================================
# DATA DEFINITIONS
# ============================================================================

CITY_DATA = {
    "Skyhaven": {
        "video_path": "city_skyhaven.mp4",  # Place your video file in the same directory
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
        "video_path": "city_harborlight.mp4",  # Place your video file in the same directory
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
        "label": "Building Retrofits & Standards",
        "impact_weights": {"Economic": 0.25, "Environmental": 0.55, "Social": 0.20},
        "sub_sliders": [
            {"label": "Net-Zero Retrofits (per yr)", "min": 0, "max": 200, "value": 40},
            {"label": "Local Workforce Share (%)", "min": 0, "max": 100, "value": 20}
        ]
    },
    {
        "id": "grid",
        "label": "Clean Energy & Grid Modernization",
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
        "label": "Urban Freight Transition",
        "impact_weights": {"Economic": 0.35, "Environmental": 0.45, "Social": 0.20},
        "sub_sliders": [
            {"label": "EV Fleets Converted (%)", "min": 0, "max": 100, "value": 20},
            {"label": "Consolidation Hubs (#)", "min": 0, "max": 40, "value": 8}
        ]
    },
    {
        "id": "mobility",
        "label": "Active Mobility Networks",
        "impact_weights": {"Economic": 0.25, "Environmental": 0.40, "Social": 0.35},
        "sub_sliders": [
            {"label": "Protected Lanes (km)", "min": 0, "max": 120, "value": 20},
            {"label": "Mode Share Target (%)", "min": 0, "max": 60, "value": 12}
        ]
    },
    {
        "id": "circular",
        "label": "Circular Waste & Materials",
        "impact_weights": {"Economic": 0.10, "Environmental": 0.60, "Social": 0.30},
        "sub_sliders": [
            {"label": "Organic Diversion (%)", "min": 0, "max": 90, "value": 20},
            {"label": "Recycling Coverage (%)", "min": 0, "max": 100, "value": 35}
        ]
    },
    {
        "id": "transit",
        "label": "Public Transit Expansion",
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
        # Get main slider value
        main_value = float(st.session_state.get(f"main_{intervention['id']}", 0))
        
        # Get sub-slider values and normalize
        sub_values = []
        for sub in intervention["sub_sliders"]:
            key = f"{intervention['id']}_{sub['label']}"
            value = float(st.session_state.get(key, sub["value"]))
            normalized = (value / sub["max"] * 100) if sub["max"] else 0
            sub_values.append(normalized)
        
        # Calculate intensity (average of main and sub-sliders)
        if sub_values:
            intensity = (main_value + np.mean(sub_values)) / 2
        else:
            intensity = main_value
        
        # Apply to categories based on weights
        for category, weight in intervention["impact_weights"].items():
            scores[category] += intensity * weight
    
    # Cap at 100
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
    """Create radar chart comparing current vs improved KPIs."""
    max_value = 10
    n_points = len(labels)
    angles = np.linspace(0, 360, n_points, endpoint=False)
    theta_values = angles.tolist() + [angles[0]]
    
    # Create category envelopes
    traces = []
    for cat in CATEGORIES:
        indices = [i for i, c in enumerate(categories) if c == cat]
        if indices:
            cat_theta = [angles[i] for i in indices] + [angles[indices[0]]]
            traces.append(go.Scatterpolar(
                r=[max_value] * len(cat_theta),
                theta=cat_theta,
                mode="lines",
                line=dict(color="rgba(115,192,255,0.16)", width=1),
                fill="toself",
                fillcolor="rgba(115,192,255,0.06)",
                showlegend=False,
                hoverinfo="skip"
            ))
    
    # Current performance
    traces.append(go.Scatterpolar(
        r=current + [current[0]],
        theta=theta_values,
        name="Current",
        mode="lines",
        line=dict(color=COLORS["primary_mid"], width=2),
        fill="toself",
        fillcolor="rgba(115,192,255,0.20)"
    ))
    
    # Improved performance
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
        height=320,
        margin=dict(l=20, r=20, t=20, b=20),
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
                tickfont=dict(size=10)
            ),
            radialaxis=dict(
                range=[0, max_value],
                showline=False,
                gridcolor=COLORS['grid'],
                tickfont=dict(size=9, color=COLORS['muted'])
            )
        ),
        font=dict(color=COLORS['text']),
        legend=dict(
            orientation="h",
            y=1.12,
            x=0.5,
            xanchor="center",
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=11, color=COLORS['text'])
        )
    )
    
    return fig


def create_time_series_chart(city_key: str, category_scores: dict):
    """Create time series chart showing projected trends."""
    ts_data = CITY_DATA[city_key]["time_series"]
    
    # Get base data
    economy = np.array(ts_data["economy"], dtype=float)
    environment = np.array(ts_data["environment"], dtype=float)
    health = np.array(ts_data["health"], dtype=float)
    
    # Calculate adjustments based on category scores
    econ_boost = category_scores["Economic"] / 100 * 12
    env_reduction = category_scores["Environmental"] / 100 * 18
    health_boost = category_scores["Social"] / 100 * 14
    
    # Apply adjustments
    economy_adj = economy + np.linspace(0, econ_boost, len(YEARS))
    environment_adj = np.maximum(environment - np.linspace(0, env_reduction, len(YEARS)), 20)
    health_adj = health + np.linspace(0, health_boost, len(YEARS))
    
    # Create figure
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=YEARS, y=economy_adj,
        name="Economy",
        mode="lines+markers",
        line=dict(color=COLORS['primary'], width=3),
        marker=dict(size=5)
    ))
    
    fig.add_trace(go.Scatter(
        x=YEARS, y=environment_adj,
        name="Environment (↓ better)",
        mode="lines+markers",
        line=dict(color=COLORS['primary_mid'], width=3, dash="dash"),
        marker=dict(size=5)
    ))
    
    fig.add_trace(go.Scatter(
        x=YEARS, y=health_adj,
        name="Health & Wellbeing",
        mode="lines+markers",
        line=dict(color=COLORS['primary_light'], width=3, dash="dot"),
        marker=dict(size=5)
    ))
    
    fig.update_layout(
        height=240,
        margin=dict(l=20, r=10, t=10, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=COLORS['text']),
        legend=dict(
            orientation="h",
            y=1.15,
            x=0.5,
            xanchor="center",
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=11, color=COLORS['text'])
        ),
        xaxis=dict(
            title="",
            showgrid=False,
            zeroline=False,
            color=COLORS['muted']
        ),
        yaxis=dict(
            title="Index",
            gridcolor=COLORS['grid'],
            zeroline=False,
            color=COLORS['muted']
        )
    )
    
    return fig


# ============================================================================
# UI COMPONENTS
# ============================================================================

def render_category_bars(scores: dict):
    """Render mini category activation bars."""
    for category in CATEGORIES:
        value = scores.get(category, 0.0)
        color = CATEGORY_COLORS.get(category, COLORS['primary'])
        
        st.markdown(f"""
        <div class='mini-metric'>
            <div class='mini-label'>{category}</div>
            <div class='mini-track'>
                <span class='mini-fill' style='width:{value:.0f}%; background:{color};'></span>
            </div>
            <div class='mini-value'>{value:.0f}% activation</div>
        </div>
        """, unsafe_allow_html=True)


def render_intervention_slider(intervention: dict):
    """Render a single intervention slider with optional sub-sliders."""
    # Get current value
    main_key = f"main_{intervention['id']}"
    current_value = int(st.session_state.get(main_key, 0))
    
    # Create container
    st.markdown('<div class="slider-container">', unsafe_allow_html=True)
    
    # Header row
    header_col1, header_col2 = st.columns([4, 1])
    with header_col1:
        st.markdown(f"""
        <div class="slider-header">
            <span class="slider-title">{intervention['label']}</span>
            <span class="slider-value">{current_value}</span>
        </div>
        """, unsafe_allow_html=True)
    
    with header_col2:
        toggle_key = f"toggle_{intervention['id']}"
        if toggle_key not in st.session_state:
            st.session_state[toggle_key] = False
        
        # Simple expand button
        if st.button("›" if not st.session_state[toggle_key] else "‹", 
                    key=f"btn_{intervention['id']}",
                    help="Show details"):
            st.session_state[toggle_key] = not st.session_state[toggle_key]
    
    # Main slider
    st.slider(
        "Intensity",
        0, 100, current_value,
        key=main_key,
        label_visibility="collapsed"
    )
    
    # Sub-sliders (if expanded)
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
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application function."""
    apply_custom_css()
    
    # Title
    st.markdown("<div class='app-title'>Urban Performance Model</div>", unsafe_allow_html=True)
    
    # ========================================================================
    # TOP SECTION: Charts and Video
    # ========================================================================
    
    left_col, right_col = st.columns([0.58, 0.42], gap="large")
    
    with left_col:
        # City Search
        st.markdown("<div class='section-label'>Search City</div>", unsafe_allow_html=True)
        search_query = st.text_input(
            "Search City",
            value=st.session_state.get("city_search", ""),
            key="city_search",
            label_visibility="collapsed",
            placeholder="Type Skyhaven or Harborlight"
        )
        
        city_key = find_city(search_query)
        
        # Calculate scores
        category_scores = compute_category_scores()
        
        # Get KPI data
        kpis = CITY_DATA[city_key]["kpis"]
        current_values = [k["value"] for k in kpis]
        improved_values = calculate_improved_kpis(city_key, category_scores)
        labels = [k["name"] for k in kpis]
        categories = [k["category"] for k in kpis]
        
        # Time Series Chart
        ts_chart = create_time_series_chart(city_key, category_scores)
        st.plotly_chart(ts_chart, use_container_width=True, config={"displayModeBar": False})
        
        # Radar Chart
        radar_chart = create_radar_chart(current_values, improved_values, labels, categories)
        st.plotly_chart(radar_chart, use_container_width=True, config={"displayModeBar": False})
        
        # Available cities caption
        st.markdown(
            f"<div class='caption-text'>Available: {' · '.join(CITY_DATA.keys())}</div>",
            unsafe_allow_html=True
        )
    
    with right_col:
        # Category Activation Bars
        st.markdown("<div class='section-label'>Category Activation</div>", unsafe_allow_html=True)
        render_category_bars(category_scores)
        
        # Video
        st.markdown("<div class='section-label' style='margin-top: 2rem;'>City Overview</div>", 
                   unsafe_allow_html=True)
        
        try:
            video_path = CITY_DATA[city_key]["video_path"]
            st.markdown('<div class="video-container">', unsafe_allow_html=True)
            st.video(video_path)
            st.markdown('</div>', unsafe_allow_html=True)
        except Exception as e:
            st.info(f"📹 Place your video file as '{CITY_DATA[city_key]['video_path']}' in the app directory")
    
    # ========================================================================
    # INTERVENTIONS SECTION
    # ========================================================================
    
    st.markdown("<div class='section-label'>Interventions</div>", unsafe_allow_html=True)
    
    # Create three columns for interventions
    col1, col2, col3 = st.columns(3, gap="large")
    
    intervention_groups = [
        ["upzoning", "retrofits", "grid"],
        ["mixed_use", "freight", "mobility"],
        ["circular", "transit"]
    ]
    
    for col, group in zip([col1, col2, col3], intervention_groups):
        with col:
            for intervention_id in group:
                # Find intervention config
                intervention = next(i for i in INTERVENTIONS if i["id"] == intervention_id)
                render_intervention_slider(intervention)
    
    # ========================================================================
    # FOOTER
    # ========================================================================
    
    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown(
        "<div class='caption-text'>Adjust intervention intensities to see projected impacts on city performance metrics.</div>",
        unsafe_allow_html=True
    )


# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    main()