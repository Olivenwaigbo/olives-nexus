# app.py — Olive's Nexus · v3 · centered header, diamond logo, fixed prompt, full PNG export

import io
import base64
import hashlib
import pandas as pd
import streamlit as st

from rag    import retrieve_with_metadata
from llm    import ask_llm
from charts import render_dashboard, detect_filter_columns, THEME

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Olive's Nexus",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700;800&display=swap');

  html, body, [class*="css"] {
    font-family: 'Space Grotesk', -apple-system, sans-serif;
  }

  /* ── Page */
  .stApp { background: #F0F2F8; }
  section[data-testid="stSidebar"] {
    background: #FFFFFF;
    border-right: 1.5px solid #E2E6F0;
  }

  /* ── Hide Streamlit chrome + default top padding */
  #MainMenu, footer, header { visibility: hidden; }
  .block-container {
    padding-top: 0 !important;
    padding-left: 2rem;
    padding-right: 2rem;
    padding-bottom: 2.5rem;
    max-width: 1440px;
  }

  /* ────────────────────────────────────────────────
     GHOST BAR FIX:
     Streamlit renders st.text_input as a <div> with
     an inner <label> + <input>. When we inject an
     open <div class="prompt-wrap"> via st.markdown
     BEFORE the input, that wrapper div becomes a
     separate Streamlit element and the browser shows
     its bottom border/bg as a "bar" above the real
     input card. Fix: we don't use an open/close div
     pair around the input — instead we style the
     Streamlit input container directly, and use a
     CSS pseudo-element hero card look.
  ──────────────────────────────────────────────── */

  /* Target the specific stTextInput block to card-ify it */
  div[data-testid="stTextInput"] {
    background: #FFFFFF;
    border: 1.5px solid #E2E6F0;
    border-radius: 14px;
    padding: 1rem 1.3rem 0.8rem;
    box-shadow: 0 2px 10px rgba(91,79,232,0.08);
    margin-bottom: 0.5rem;
  }
  div[data-testid="stTextInput"] input {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    font-size: 15px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    color: #0D0F1A !important;
    padding: 0 !important;
  }
  div[data-testid="stTextInput"] input::placeholder {
    color: #A0A9C0 !important;
  }
  /* Remove the default Streamlit input wrapper border/bg */
  div[data-testid="stTextInput"] > div > div {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
  }

  /* ── Centered hero header */
  .hero {
    text-align: center;
    padding: 2.2rem 0 1.6rem;
    border-bottom: 2px solid #E2E6F0;
    margin-bottom: 2rem;
  }
  .hero-logo {
    display: inline-block;
    margin-bottom: 0.6rem;
  }
  .hero-title {
    font-size: 2.4rem;
    font-weight: 900;
    color: #0D0F1A;
    letter-spacing: -0.04em;
    line-height: 1;
    margin-bottom: 0.35rem;
  }
  .hero-title span {
    background: linear-gradient(135deg, #5B4FE8 0%, #9B59F5 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .nexus-badge {
    display: inline-block;
    background: linear-gradient(135deg, #5B4FE8 0%, #9B59F5 100%);
    color: #FFFFFF;
    font-size: 10px; font-weight: 800;
    padding: 3px 10px; border-radius: 20px;
    letter-spacing: 0.08em; text-transform: uppercase;
    vertical-align: middle; margin-left: 8px;
    position: relative; top: -4px;
  }
  .hero-sub {
    font-size: 14px; color: #7A82A0;
    margin-top: 4px;
  }

  /* ── Prompt label above input */
  .prompt-label {
    font-size: 11px; font-weight: 800; color: #5B4FE8;
    text-transform: uppercase; letter-spacing: 0.09em;
    margin-bottom: 6px;
  }

  /* ── Dashboard section title */
  .dash-title {
    font-size: 1.2rem; font-weight: 700; color: #0D0F1A;
    margin: 0.6rem 0 1.1rem;
    display: flex; align-items: center; gap: 10px;
    letter-spacing: -0.01em;
  }
  .dash-title::before {
    content: "";
    display: inline-block;
    width: 5px; height: 22px;
    background: linear-gradient(180deg, #5B4FE8, #9B59F5);
    border-radius: 3px;
  }

  /* ── KPI card */
  .kpi-card {
    background: #FFFFFF;
    border: 1.5px solid #E2E6F0;
    border-radius: 14px;
    padding: 1.1rem 1.4rem 0.9rem;
    box-shadow: 0 2px 6px rgba(13,15,26,0.05);
    position: relative; overflow: hidden;
  }
  .kpi-label {
    font-size: 11px; font-weight: 700;
    color: #7A82A0; text-transform: uppercase;
    letter-spacing: 0.06em; margin-bottom: 5px;
  }
  .kpi-value {
    font-size: 2.1rem; font-weight: 800; color: #0D0F1A;
    line-height: 1.1; margin-bottom: 9px;
    letter-spacing: -0.03em;
  }
  .kpi-badge {
    display: inline-flex; align-items: center; gap: 4px;
    font-size: 11px; font-weight: 700;
    padding: 3px 9px; border-radius: 20px;
    margin-right: 6px;
  }
  .kpi-badge.up   { background: #EDFAF3; color: #1A7A4A; }
  .kpi-badge.down { background: #FEF2F2; color: #B91C1C; }
  .kpi-badge.flat { background: #EEF0FA; color: #5B4FE8; }
  .kpi-compare { font-size: 11px; color: #A0A9C0; margin-top: 4px; }
  .kpi-accent {
    position: absolute; top: 0; right: 0;
    width: 5px; height: 100%;
    border-radius: 0 14px 14px 0;
  }
  .kpi-accent.up   { background: linear-gradient(180deg,#34D399,#10B981); }
  .kpi-accent.down { background: linear-gradient(180deg,#F87171,#EF4444); }
  .kpi-accent.flat { background: linear-gradient(180deg,#5B4FE8,#9B59F5); }

  /* ── Chart card */
  .chart-card {
    background: #FFFFFF;
    border: 1.5px solid #E2E6F0;
    border-radius: 14px;
    padding: 1.1rem 1.3rem 0.6rem;
    box-shadow: 0 2px 6px rgba(13,15,26,0.05);
    margin-bottom: 1.1rem;
  }
  .chart-card-title {
    font-size: 13px; font-weight: 700; color: #0D0F1A;
    margin-bottom: 2px;
  }
  .chart-desc {
    font-size: 12px; color: #A0A9C0;
    margin: 0 0 6px;
  }

  /* ── Filter bar */
  .filter-bar {
    background: #FFFFFF;
    border: 1.5px solid #E2E6F0;
    border-radius: 12px;
    padding: 0.9rem 1.2rem;
    margin-bottom: 1.3rem;
    box-shadow: 0 1px 4px rgba(13,15,26,0.04);
  }
  .filter-title {
    font-size: 11px; font-weight: 700;
    color: #7A82A0; text-transform: uppercase;
    letter-spacing: 0.07em; margin-bottom: 9px;
  }

  /* ── Reasoning / error */
  .reasoning-box {
    background: #EDEAFF; border-left: 4px solid #5B4FE8;
    border-radius: 0 10px 10px 0;
    padding: 11px 15px; margin: 8px 0 12px;
    font-size: 13px; color: #3B2FA8;
  }
  .error-box {
    background: #FEF2F2; border-left: 4px solid #EF4444;
    border-radius: 0 10px 10px 0;
    padding: 11px 15px;
    font-size: 13px; color: #B91C1C;
  }

  /* ── Sidebar */
  .sidebar-section {
    font-size: 10px; font-weight: 800;
    color: #A0A9C0; text-transform: uppercase;
    letter-spacing: 0.09em; margin: 1.3rem 0 0.5rem;
  }
  .sidebar-title {
    font-size: 1.05rem; font-weight: 800; color: #0D0F1A;
    letter-spacing: -0.01em; display: flex; align-items: center; gap: 8px;
  }

  /* ── Buttons */
  .stButton > button {
    border-radius: 9px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    transition: all 0.15s !important;
  }
  .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #5B4FE8 0%, #9B59F5 100%) !important;
    border: none !important;
    padding: 0.55rem 1.5rem !important;
    font-size: 14px !important;
  }
  .stButton > button[kind="primary"]:hover {
    opacity: 0.9 !important;
    box-shadow: 0 6px 18px rgba(91,79,232,0.38) !important;
    transform: translateY(-1px) !important;
  }

  /* ── Data table */
  .data-section {
    background: #FFFFFF; border: 1.5px solid #E2E6F0;
    border-radius: 14px; padding: 1.1rem 1.3rem;
    margin-top: 0.5rem;
  }

  /* ── Divider */
  hr { border: none; border-top: 1.5px solid #E2E6F0; margin: 1.3rem 0; }

  /* ── Download link */
  .dl-link {
    display: inline-flex; align-items: center; gap: 6px;
    background: #F0F2F8; border: 1.5px solid #E2E6F0;
    border-radius: 8px; padding: 5px 13px;
    font-size: 12px; font-weight: 600; color: #5B4FE8;
    text-decoration: none;
    font-family: 'Space Grotesk', sans-serif;
    transition: background 0.15s;
    margin-top: 4px; margin-right: 6px;
  }
  .dl-link:hover { background: #EDEAFF; border-color: #C4BEFF; }

  /* ── Full-dashboard export bar */
  .export-bar {
    display: flex; align-items: center; gap: 10px;
    background: #FFFFFF; border: 1.5px solid #E2E6F0;
    border-radius: 12px; padding: 0.65rem 1.1rem;
    margin-bottom: 1.2rem;
    font-size: 12px; color: #7A82A0; font-weight: 600;
  }
</style>
""", unsafe_allow_html=True)


# ── Session state ──────────────────────────────────────────────────────────────
for key, default in [
    ("history",        []),
    ("last_config",    None),
    ("last_df",        None),
    ("active_filters", {}),
    ("prompt_cache",   {}),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ── Cache helpers ──────────────────────────────────────────────────────────────
def prompt_hash(prompt: str, df_shape: tuple) -> str:
    raw = f"{prompt.strip().lower()}_{df_shape}"
    return hashlib.md5(raw.encode()).hexdigest()

@st.cache_resource(show_spinner=False)
def load_rag_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("all-MiniLM-L6-v2")

@st.cache_data(show_spinner=False, ttl=3600)
def cached_retrieve(prompt: str):
    from rag import retrieve_with_metadata
    return retrieve_with_metadata(prompt)

@st.cache_data(show_spinner=False, ttl=3600)
def cached_llm(prompt: str, context: str):
    return ask_llm(prompt, context)


# ── PNG export helpers ─────────────────────────────────────────────────────────
def fig_to_png_b64(fig, width=900, height=480) -> str:
    img_bytes = fig.to_image(format="png", width=width, height=height, scale=2)
    return base64.b64encode(img_bytes).decode()

def download_link(b64: str, filename: str, label: str) -> str:
    return f'<a class="dl-link" href="data:image/png;base64,{b64}" download="{filename}">⬇ {label}</a>'


# ── Build full-dashboard PNG (KPI cards + charts stacked) ─────────────────────
def build_full_dashboard_png(figures, dash_title: str):
    """
    Combines KPI indicator figures + all chart figures into one PNG.
    Returns (bytes, None) on success or (None, error_str) on failure.
    Indicator traces need type="indicator" specs, xy traces need type="xy".
    """
    try:
        from plotly.subplots import make_subplots

        all_figs   = []
        all_titles = []

        for item in figures:
            if item["type"] == "kpi":
                for card in item["cards"]:
                    all_figs.append(card["fig"])
                    all_titles.append(card["label"])
            elif item["type"] == "chart":
                all_figs.append(item["fig"])
                all_titles.append(item.get("title", ""))

        if not all_figs:
            return None, "No figures to export."

        n      = len(all_figs)
        cols_n = min(n, 2)
        rows_n = (n + cols_n - 1) // cols_n

        # Build specs — Plotly needs the right subplot type per trace family:
        #   indicator traces  → {"type": "indicator"}
        #   pie/donut traces  → {"type": "domain"}
        #   everything else   → {"type": "xy"}
        DOMAIN_TYPES = {"pie", "funnelarea", "sunburst", "treemap", "icicle"}
        def subplot_spec(fig):
            if not fig.data:
                return {"type": "xy"}
            types = {t.type for t in fig.data}
            if types <= {"indicator"}:
                return {"type": "indicator"}
            if types & DOMAIN_TYPES:
                return {"type": "domain"}
            return {"type": "xy"}

        specs = []
        for r in range(rows_n):
            row_specs = []
            for c in range(cols_n):
                idx = r * cols_n + c
                row_specs.append(subplot_spec(all_figs[idx]) if idx < len(all_figs) else {"type": "xy"})
            specs.append(row_specs)

        combined = make_subplots(
            rows               = rows_n,
            cols               = cols_n,
            subplot_titles     = all_titles,
            specs              = specs,
            vertical_spacing   = 0.1,
            horizontal_spacing = 0.06,
        )

        for idx, fig in enumerate(all_figs):
            r = idx // cols_n + 1
            c = idx % cols_n + 1
            for trace in fig.data:
                combined.add_trace(trace, row=r, col=c)

        row_h   = 300
        total_h = row_h * rows_n + 100

        combined.update_layout(
            height           = total_h,
            showlegend       = False,
            paper_bgcolor    = "#FFFFFF",
            plot_bgcolor     = "#F8F9FC",
            font             = dict(family="Arial, sans-serif",
                                    color="#0D0F1A", size=12),
            title_text       = f"<b>{dash_title}</b>",
            title_font_size  = 22,
            title_font_color = "#0D0F1A",
            title_x          = 0.01,
            margin           = dict(t=75, b=35, l=45, r=35),
        )
        combined.update_xaxes(gridcolor="#EEF0F8", linecolor="#E2E6F0",
                               showgrid=True, zeroline=False)
        combined.update_yaxes(gridcolor="#EEF0F8", linecolor="rgba(0,0,0,0)",
                               showgrid=True, zeroline=False)

        img_bytes = combined.to_image(format="png", width=1400,
                                      height=total_h, scale=2)
        return img_bytes, None

    except Exception as e:
        return None, str(e)


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    # Diamond SVG logo in sidebar
    st.markdown("""
    <div class="sidebar-title">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
        <path d="M12 2L2 9l10 13L22 9 12 2z" fill="url(#sdg)" stroke="#5B4FE8" stroke-width="1.2"/>
        <defs>
          <linearGradient id="sdg" x1="2" y1="2" x2="22" y2="22" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stop-color="#5B4FE8"/>
            <stop offset="100%" stop-color="#9B59F5"/>
          </linearGradient>
        </defs>
      </svg>
      Olive's Nexus
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">Data Source</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed")
    uploaded_df   = None
    df_shape      = (0, 0)

    if uploaded_file:
        try:
            uploaded_df = pd.read_csv(uploaded_file)
            df_shape    = uploaded_df.shape
            st.success(f"✓ {df_shape[0]} rows · {df_shape[1]} columns")
            with st.expander("Preview data"):
                st.dataframe(uploaded_df.head(4), use_container_width=True)
                st.caption("Columns: " + ", ".join(uploaded_df.columns.tolist()))
        except Exception as e:
            st.error(f"CSV error: {e}")

    st.markdown('<div class="sidebar-section">Example Prompts</div>', unsafe_allow_html=True)
    examples = {
        "💰 Finance": [
            "Give me a financial overview dashboard",
            "Show monthly revenue trend",
            "Compare revenue by region",
            "Show profit vs cost breakdown",
        ],
        "👥 HR": [
            "Give me an HR overview dashboard",
            "Show headcount by department",
            "Which team has highest turnover?",
            "Compare salaries across departments",
        ],
        "📋 Projects": [
            "Give me a project overview dashboard",
            "Show task status breakdown",
            "Who has the most work assigned?",
            "Show sprint velocity trend",
        ],
    }
    for group, prompts in examples.items():
        with st.expander(group):
            for p in prompts:
                if st.button(p, key=p, use_container_width=True):
                    st.session_state["_queued_prompt"] = p

    st.markdown('<div class="sidebar-section">Display</div>', unsafe_allow_html=True)
    show_reasoning = st.toggle("Show AI reasoning",      value=False)
    show_json      = st.toggle("Show raw JSON config",   value=False)
    show_sources   = st.toggle("Show knowledge sources", value=False)
    show_data      = st.toggle("Show data table",        value=False)

    st.markdown("---")
    st.caption("Powered by Ollama · ChromaDB · Plotly · Streamlit")


# ── Hero header (centered, bold, diamond logo) ─────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-logo">
    <svg width="52" height="52" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M24 3L3 18l21 27L45 18 24 3z" fill="url(#hg1)"/>
      <path d="M24 3L3 18h42L24 3z" fill="url(#hg2)" opacity="0.6"/>
      <path d="M3 18l21 27V18H3z" fill="url(#hg3)" opacity="0.45"/>
      <path d="M45 18L24 45V18h21z" fill="url(#hg4)" opacity="0.3"/>
      <defs>
        <linearGradient id="hg1" x1="3" y1="3" x2="45" y2="45" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stop-color="#7C6FFF"/>
          <stop offset="100%" stop-color="#9B59F5"/>
        </linearGradient>
        <linearGradient id="hg2" x1="3" y1="3" x2="45" y2="18" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stop-color="#A89DFF"/>
          <stop offset="100%" stop-color="#C4B8FF"/>
        </linearGradient>
        <linearGradient id="hg3" x1="3" y1="18" x2="24" y2="45" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stop-color="#5B4FE8"/>
          <stop offset="100%" stop-color="#4039C4"/>
        </linearGradient>
        <linearGradient id="hg4" x1="45" y1="18" x2="24" y2="45" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stop-color="#7C6FFF"/>
          <stop offset="100%" stop-color="#5B4FE8"/>
        </linearGradient>
      </defs>
    </svg>
  </div>
  <div class="hero-title"><span>Olive's Nexus</span> <span class="nexus-badge">AI</span></div>
  <div class="hero-sub">Describe what you want to see — get a live dashboard instantly</div>
</div>
""", unsafe_allow_html=True)


# ── Prompt input ───────────────────────────────────────────────────────────────
# The prompt-label sits above the input as its own st.markdown element.
# The stTextInput div is styled directly via CSS (see above) — no open/close
# wrapper divs, which eliminates the ghost bar entirely.

default_val = st.session_state.pop("_queued_prompt", "")
st.markdown('<div class="prompt-label">✦ What dashboard do you need?</div>', unsafe_allow_html=True)
user_prompt = st.text_input(
    "prompt",
    placeholder="e.g.  Give me a financial overview dashboard",
    value=default_val,
    label_visibility="collapsed",
    key="main_prompt",
)
col_gen, col_clr, col_space = st.columns([1.2, 0.9, 5.9])
with col_gen:
    generate = st.button("✨  Generate", type="primary", use_container_width=True)
with col_clr:
    if st.button("Clear", use_container_width=True):
        st.session_state.history        = []
        st.session_state.last_config    = None
        st.session_state.active_filters = {}
        st.session_state.prompt_cache   = {}
        st.rerun()


# ── KPI card HTML renderer ─────────────────────────────────────────────────────
def kpi_html(card: dict) -> str:
    label   = card["label"]
    val     = card["value"]
    prefix  = card.get("prefix") or ""
    suffix  = card.get("suffix") or ""
    mom     = card.get("mom")
    yoy     = card.get("yoy")

    if abs(val) >= 1_000_000:
        val_str = f"{prefix}{val/1_000_000:.1f}M{suffix}"
    elif abs(val) >= 1_000:
        val_str = f"{prefix}{val/1_000:.1f}K{suffix}"
    else:
        val_str = f"{prefix}{val:,.1f}{suffix}"

    badges    = ""
    direction = "flat"
    if mom:
        direction = mom["direction"]
        arrow     = "↑" if direction == "up" else "↓"
        badges   += f'<span class="kpi-badge {direction}">{arrow} {abs(mom["pct_change"])}% MoM</span>'
    if yoy:
        yoy_dir = yoy["direction"]
        arrow   = "↑" if yoy_dir == "up" else "↓"
        badges += f'<span class="kpi-badge {yoy_dir}">{arrow} {abs(yoy["pct_change"])}% YoY</span>'

    compare_line = ""
    if mom:
        prev_fmt     = f"{prefix}{mom['previous']:,.0f}{suffix}"
        compare_line = f'<div class="kpi-compare">vs {prev_fmt} last period</div>'

    return f"""
<div class="kpi-card">
  <div class="kpi-accent {direction}"></div>
  <div class="kpi-label">{label}</div>
  <div class="kpi-value">{val_str}</div>
  <div>{badges}</div>
  {compare_line}
</div>"""


# ── Filter bar ─────────────────────────────────────────────────────────────────
def render_filter_bar(df: pd.DataFrame):
    filter_cols = detect_filter_columns(df)
    if not filter_cols:
        return {}
    st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
    st.markdown('<div class="filter-title">🔽 Filters</div>', unsafe_allow_html=True)
    n_cols = min(len(filter_cols), 4)
    cols   = st.columns(n_cols)
    active = {}
    for i, (col_name, options) in enumerate(list(filter_cols.items())[:4]):
        with cols[i % n_cols]:
            selected = st.multiselect(
                col_name.replace("_", " ").title(),
                options=options, default=options,
                key=f"filter_{col_name}",
            )
            if selected and len(selected) < len(options):
                active[col_name] = selected
    st.markdown('</div>', unsafe_allow_html=True)
    return active


# ── Main generation ────────────────────────────────────────────────────────────
if generate and user_prompt.strip():

    cache_key = prompt_hash(user_prompt, df_shape)

    if cache_key in st.session_state.prompt_cache:
        config = st.session_state.prompt_cache[cache_key]
        st.toast("⚡ Loaded from cache", icon="⚡")
    else:
        with st.spinner("🔍 Searching knowledge base…"):
            try:
                context, domains, sources = cached_retrieve(user_prompt)
            except Exception as e:
                st.markdown(f'<div class="error-box">⚠️ ChromaDB error: {e}<br>Have you run <code>python ingest.py</code> yet?</div>', unsafe_allow_html=True)
                st.stop()

        with st.spinner("🤖 Designing your dashboard…"):
            result = cached_llm(user_prompt, context)

        if not result["success"]:
            st.markdown(f'<div class="error-box">⚠️ {result["error"]}</div>', unsafe_allow_html=True)
            if result.get("raw"):
                with st.expander("Raw LLM output"):
                    st.code(result["raw"])
            st.stop()

        config = result["config"]
        st.session_state.prompt_cache[cache_key] = config
        st.session_state.history.append({"prompt": user_prompt, "config": config})
        st.session_state.last_config = config

    # ── Optional debug panels ────────────────────────────────────────────────
    if show_reasoning and config.get("reasoning"):
        st.markdown(f'<div class="reasoning-box">💭 <strong>AI reasoning:</strong> {config["reasoning"]}</div>', unsafe_allow_html=True)
    if show_sources and "sources" in dir():
        with st.expander(f"📚 Knowledge sources ({', '.join(domains)})"):
            for s in sources:
                st.caption(f"[{s['domain']}] relevance: {s['score']}")
                st.text(s["text"][:300] + "…")
                st.divider()
    if show_json:
        with st.expander("🔧 Raw JSON config"):
            st.json(config)

    # ── Render ───────────────────────────────────────────────────────────────
    dash_title = config.get("dashboard_title", "Dashboard")

    with st.spinner("📊 Rendering dashboard…"):
        try:
            figures, df = render_dashboard(config, uploaded_df, active_filters={})
        except Exception as e:
            st.error(f"Render error: {e}")
            st.stop()

    st.session_state.last_df = df

    # ── Filter bar ───────────────────────────────────────────────────────────
    active_filters = render_filter_bar(df)
    if active_filters:
        try:
            figures, df = render_dashboard(config, uploaded_df, active_filters=active_filters)
        except Exception as e:
            st.error(f"Filter render error: {e}")

    # ── Dashboard title + full export ────────────────────────────────────────
    title_col, export_col = st.columns([5, 3])
    with title_col:
        st.markdown(f'<div class="dash-title">{dash_title}</div>', unsafe_allow_html=True)
    with export_col:
        img_bytes, export_err = build_full_dashboard_png(figures, dash_title)
        fname = dash_title.replace(" ", "_").lower()
        if img_bytes:
            st.download_button(
                label     = "⬇ Download Full Dashboard PNG",
                data      = img_bytes,
                file_name = f"{fname}_dashboard.png",
                mime      = "image/png",
                use_container_width = True,
            )
        elif export_err:
            st.caption(f"⚠ Export unavailable: {export_err}")

    # ── KPI cards ────────────────────────────────────────────────────────────
    for item in figures:
        if item["type"] == "kpi":
            cards = item["cards"]
            cols  = st.columns(len(cards))
            for col, card in zip(cols, cards):
                with col:
                    st.markdown(kpi_html(card), unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts grid ──────────────────────────────────────────────────────────
    chart_items = [i for i in figures if i["type"] == "chart"]

    if len(chart_items) == 1:
        item = chart_items[0]
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="chart-card-title">{item["title"]}</div>', unsafe_allow_html=True)
        if item.get("description"):
            st.markdown(f'<div class="chart-desc">{item["description"]}</div>', unsafe_allow_html=True)
        st.plotly_chart(item["fig"], use_container_width=True)
        try:
            b64 = fig_to_png_b64(item["fig"])
            st.markdown(download_link(b64, f"{item['title'].replace(' ','_')}.png", "Save chart as PNG"), unsafe_allow_html=True)
        except Exception:
            pass
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        for i in range(0, len(chart_items), 2):
            col_a, col_b = st.columns(2, gap="medium")
            for col, idx in [(col_a, i), (col_b, i + 1)]:
                if idx < len(chart_items):
                    item = chart_items[idx]
                    with col:
                        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
                        st.markdown(f'<div class="chart-card-title">{item["title"]}</div>', unsafe_allow_html=True)
                        if item.get("description"):
                            st.markdown(f'<div class="chart-desc">{item["description"]}</div>', unsafe_allow_html=True)
                        st.plotly_chart(item["fig"], use_container_width=True)
                        try:
                            b64 = fig_to_png_b64(item["fig"])
                            st.markdown(download_link(b64, f"{item['title'].replace(' ','_')}.png", "Save chart as PNG"), unsafe_allow_html=True)
                        except Exception:
                            pass
                        st.markdown('</div>', unsafe_allow_html=True)

    # ── Data table ───────────────────────────────────────────────────────────
    if show_data:
        st.markdown('<div class="data-section">', unsafe_allow_html=True)
        st.markdown("**Data used for this dashboard**")
        st.dataframe(df, use_container_width=True, height=250)
        st.markdown('</div>', unsafe_allow_html=True)


elif generate and not user_prompt.strip():
    st.warning("Please type a prompt first.")


# ── Prompt history ─────────────────────────────────────────────────────────────
if st.session_state.history:
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("**Recent prompts**")
    cols = st.columns(min(len(st.session_state.history[-5:]), 5))
    for i, item in enumerate(st.session_state.history[-5:]):
        with cols[i]:
            short = item["prompt"][:35] + "…" if len(item["prompt"]) > 35 else item["prompt"]
            if st.button(short, key=f"hist_{i}", use_container_width=True):
                st.session_state["_queued_prompt"] = item["prompt"]
                st.rerun()