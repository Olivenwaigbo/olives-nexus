# app.py — Olive's Nexus · no RAG/ChromaDB · Groq only

import math
import base64
import hashlib
import pandas as pd
import streamlit as st

from llm    import ask_llm, extract_table_from_text, generate_insights
from charts import render_dashboard, detect_filter_columns, summarize_for_insights, THEME
from file_loader import load_any, SUPPORTED_TYPES

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

  .stApp { background: #F0F2F8; }
  section[data-testid="stSidebar"] {
    background: #FFFFFF;
    border-right: 1.5px solid #E2E6F0;
  }

  #MainMenu, footer, header { visibility: hidden; }
  .block-container {
    padding-top: 0 !important;
    padding-left: 2rem;
    padding-right: 2rem;
    padding-bottom: 2.5rem;
    max-width: 1440px;
  }

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
  div[data-testid="stTextInput"] input::placeholder { color: #A0A9C0 !important; }
  div[data-testid="stTextInput"] > div > div {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
  }

  .hero {
    text-align: center;
    padding: 2.2rem 0 1.6rem;
    border-bottom: 2px solid #E2E6F0;
    margin-bottom: 2rem;
  }
  .hero-logo { display: inline-block; margin-bottom: 0.6rem; }
  .hero-title {
    font-size: 2.4rem; font-weight: 900; color: #0D0F1A;
    letter-spacing: -0.04em; line-height: 1; margin-bottom: 0.35rem;
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
    color: #FFFFFF; font-size: 10px; font-weight: 800;
    padding: 3px 10px; border-radius: 20px;
    letter-spacing: 0.08em; text-transform: uppercase;
    vertical-align: middle; margin-left: 8px; position: relative; top: -4px;
  }
  .hero-sub { font-size: 14px; color: #7A82A0; margin-top: 4px; }

  .prompt-label {
    font-size: 11px; font-weight: 800; color: #5B4FE8;
    text-transform: uppercase; letter-spacing: 0.09em; margin-bottom: 6px;
  }

  .dash-title {
    font-size: 1.2rem; font-weight: 700; color: #0D0F1A;
    margin: 0.6rem 0 1.1rem;
    display: flex; align-items: center; gap: 10px;
    letter-spacing: -0.01em;
  }
  .dash-title::before {
    content: ""; display: inline-block;
    width: 5px; height: 22px;
    background: linear-gradient(180deg, #5B4FE8, #9B59F5);
    border-radius: 3px;
  }

  .kpi-card {
    background: #FFFFFF; border: 1.5px solid #E2E6F0;
    border-radius: 14px; padding: 1.1rem 1.4rem 0.9rem;
    box-shadow: 0 2px 6px rgba(13,15,26,0.05);
    position: relative; overflow: hidden;
  }
  .kpi-label {
    font-size: 11px; font-weight: 700; color: #7A82A0;
    text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 5px;
  }
  .kpi-value {
    font-size: 2.1rem; font-weight: 800; color: #0D0F1A;
    line-height: 1.1; margin-bottom: 9px; letter-spacing: -0.03em;
  }
  .kpi-badge {
    display: inline-flex; align-items: center; gap: 4px;
    font-size: 11px; font-weight: 700;
    padding: 3px 9px; border-radius: 20px; margin-right: 6px;
  }
  .kpi-badge.up   { background: #EDFAF3; color: #1A7A4A; }
  .kpi-badge.down { background: #FEF2F2; color: #B91C1C; }
  .kpi-badge.flat { background: #EEF0FA; color: #5B4FE8; }
  .kpi-compare { font-size: 11px; color: #A0A9C0; margin-top: 4px; }
  .kpi-accent {
    position: absolute; top: 0; right: 0;
    width: 5px; height: 100%; border-radius: 0 14px 14px 0;
  }
  .kpi-accent.up   { background: linear-gradient(180deg,#34D399,#10B981); }
  .kpi-accent.down { background: linear-gradient(180deg,#F87171,#EF4444); }
  .kpi-accent.flat { background: linear-gradient(180deg,#5B4FE8,#9B59F5); }

  .chart-card {
    background: #FFFFFF; border: 1.5px solid #E2E6F0;
    border-radius: 14px; padding: 1.1rem 1.3rem 0.6rem;
    box-shadow: 0 2px 6px rgba(13,15,26,0.05); margin-bottom: 1.1rem;
  }
  .chart-card-title { font-size: 13px; font-weight: 700; color: #0D0F1A; margin-bottom: 2px; }
  .chart-desc { font-size: 12px; color: #A0A9C0; margin: 0 0 6px; }

  .filter-bar {
    background: #FFFFFF; border: 1.5px solid #E2E6F0;
    border-radius: 12px; padding: 0.9rem 1.2rem; margin-bottom: 1.3rem;
    box-shadow: 0 1px 4px rgba(13,15,26,0.04);
  }
  .filter-title {
    font-size: 11px; font-weight: 700; color: #7A82A0;
    text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 9px;
  }

  .reasoning-box {
    background: #EDEAFF; border-left: 4px solid #5B4FE8;
    border-radius: 0 10px 10px 0; padding: 11px 15px;
    margin: 8px 0 12px; font-size: 13px; color: #3B2FA8;
  }
  .insights-box {
    background: #FFFFFF; border: 1.5px solid #E2E6F0; border-left: 4px solid #10B981;
    border-radius: 0 14px 14px 0; padding: 14px 18px;
    margin: 0 0 1.3rem; box-shadow: 0 2px 6px rgba(13,15,26,0.05);
  }
  .insights-title {
    font-size: 12px; font-weight: 800; color: #0D0F1A;
    text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 8px;
  }
  .insights-box ul { margin: 0; padding-left: 1.1rem; }
  .insights-box li { font-size: 13.5px; color: #333A52; margin-bottom: 5px; line-height: 1.45; }
  .doc-note-box {
    background: #FFFBEB; border-left: 4px solid #F59E0B;
    border-radius: 0 10px 10px 0; padding: 10px 14px;
    margin: 6px 0 10px; font-size: 12.5px; color: #8A5A00;
  }
  .error-box {
    background: #FEF2F2; border-left: 4px solid #EF4444;
    border-radius: 0 10px 10px 0; padding: 11px 15px;
    font-size: 13px; color: #B91C1C;
  }

  .sidebar-section {
    font-size: 10px; font-weight: 800; color: #A0A9C0;
    text-transform: uppercase; letter-spacing: 0.09em; margin: 1.3rem 0 0.5rem;
  }
  .sidebar-title {
    font-size: 1.05rem; font-weight: 800; color: #0D0F1A;
    letter-spacing: -0.01em; display: flex; align-items: center; gap: 8px;
  }

  .stButton > button {
    border-radius: 9px !important; font-size: 13px !important;
    font-weight: 600 !important; font-family: 'Space Grotesk', sans-serif !important;
    transition: all 0.15s !important;
  }
  .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #5B4FE8 0%, #9B59F5 100%) !important;
    border: none !important; padding: 0.55rem 1.5rem !important; font-size: 14px !important;
  }
  .stButton > button[kind="primary"]:hover {
    opacity: 0.9 !important;
    box-shadow: 0 6px 18px rgba(91,79,232,0.38) !important;
    transform: translateY(-1px) !important;
  }

  .data-section {
    background: #FFFFFF; border: 1.5px solid #E2E6F0;
    border-radius: 14px; padding: 1.1rem 1.3rem; margin-top: 0.5rem;
  }
  hr { border: none; border-top: 1.5px solid #E2E6F0; margin: 1.3rem 0; }
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


# ── Helpers ────────────────────────────────────────────────────────────────────
def prompt_hash(prompt: str, df_shape: tuple) -> str:
    return hashlib.md5(f"{prompt.strip().lower()}_{df_shape}".encode()).hexdigest()

@st.cache_data(show_spinner=False, ttl=3600)
def cached_llm(prompt: str, context: str):
    return ask_llm(prompt, context)


# ── PNG / HTML export helpers ──────────────────────────────────────────────────
def fig_to_png_bytes(fig, width=900, height=480):
    try:
        return fig.to_image(format="png", width=width, height=height, scale=2)
    except Exception:
        return None

def fig_to_html(fig) -> str:
    return fig.to_html(full_html=True, include_plotlyjs="cdn")


# ── Full dashboard export ──────────────────────────────────────────────────────
def build_full_dashboard_png(figures, dash_title: str):
    try:
        from plotly.subplots import make_subplots

        all_figs, all_titles = [], []
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
            rows=rows_n, cols=cols_n,
            subplot_titles=all_titles, specs=specs,
            vertical_spacing=0.1, horizontal_spacing=0.06,
        )
        for idx, fig in enumerate(all_figs):
            r, c = idx // cols_n + 1, idx % cols_n + 1
            for trace in fig.data:
                combined.add_trace(trace, row=r, col=c)

        total_h = 300 * rows_n + 100
        combined.update_layout(
            height=total_h, showlegend=False,
            paper_bgcolor="#FFFFFF", plot_bgcolor="#F8F9FC",
            font=dict(family="Arial, sans-serif", color="#0D0F1A", size=12),
            title_text=f"<b>{dash_title}</b>",
            title_font_size=22, title_font_color="#0D0F1A",
            title_x=0.01, margin=dict(t=75, b=35, l=45, r=35),
        )
        combined.update_xaxes(gridcolor="#EEF0F8", showgrid=True, zeroline=False)
        combined.update_yaxes(gridcolor="#EEF0F8", showgrid=True, zeroline=False)

        img_bytes = fig_to_png_bytes(combined, width=1400, height=total_h)
        if img_bytes:
            return img_bytes, "png"
        # kaleido not available — HTML fallback
        return fig_to_html(combined).encode("utf-8"), "html"

    except Exception as e:
        return None, str(e)


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
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
    uploaded_file = st.file_uploader(
        "Upload data file",
        type=SUPPORTED_TYPES,
        label_visibility="collapsed",
        help="CSV, Excel, PDF, Word, or plain text",
    )
    uploaded_df, df_shape, doc_text, doc_note = None, (0, 0), None, None

    if uploaded_file:
        try:
            result    = load_any(uploaded_file)
            uploaded_df = result["df"]
            doc_text    = result["text"]

            # PDF/Word/TXT with no embedded table -> ask the LLM to pull
            # structured numbers out of the narrative text instead.
            if uploaded_df is None and doc_text:
                with st.spinner("Looking for data inside the document…"):
                    extraction = extract_table_from_text(doc_text)
                if extraction.get("found_table") and extraction.get("records"):
                    uploaded_df = pd.DataFrame(extraction["records"])
                    doc_note = extraction.get("note", "Extracted data from the document text.")
                else:
                    doc_note = (
                        "No tabular data found in this document — its text will be used "
                        "as context, and charts will fall back to sample data."
                    )

            if uploaded_df is not None:
                df_shape = uploaded_df.shape
                st.success(f"✓ {df_shape[0]} rows · {df_shape[1]} columns")
                with st.expander("Preview data"):
                    st.dataframe(uploaded_df.head(4), use_container_width=True)
                    st.caption("Columns: " + ", ".join(str(c) for c in uploaded_df.columns.tolist()))
                if doc_note:
                    st.caption(f"📄 {doc_note}")
            elif doc_note:
                st.warning(doc_note)
        except Exception as e:
            st.error(f"File error: {e}")

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
    show_insights  = st.toggle("Show AI insights",     value=True)
    show_reasoning = st.toggle("Show AI reasoning",    value=False)
    show_json      = st.toggle("Show raw JSON config", value=False)
    show_data      = st.toggle("Show data table",      value=False)

    st.markdown("---")
    st.caption("Powered by Groq · Plotly · Streamlit")


# ── Hero header ────────────────────────────────────────────────────────────────
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
          <stop offset="0%" stop-color="#7C6FFF"/><stop offset="100%" stop-color="#9B59F5"/>
        </linearGradient>
        <linearGradient id="hg2" x1="3" y1="3" x2="45" y2="18" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stop-color="#A89DFF"/><stop offset="100%" stop-color="#C4B8FF"/>
        </linearGradient>
        <linearGradient id="hg3" x1="3" y1="18" x2="24" y2="45" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stop-color="#5B4FE8"/><stop offset="100%" stop-color="#4039C4"/>
        </linearGradient>
        <linearGradient id="hg4" x1="45" y1="18" x2="24" y2="45" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stop-color="#7C6FFF"/><stop offset="100%" stop-color="#5B4FE8"/>
        </linearGradient>
      </defs>
    </svg>
  </div>
  <div class="hero-title"><span>Olive's Nexus</span> <span class="nexus-badge">AI</span></div>
  <div class="hero-sub">Describe what you want to see — get a live dashboard instantly</div>
</div>
""", unsafe_allow_html=True)


# ── Prompt input ───────────────────────────────────────────────────────────────
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


# ── KPI card HTML ──────────────────────────────────────────────────────────────
def kpi_html(card: dict) -> str:
    label  = card["label"]
    val    = card["value"]
    prefix = card.get("prefix") or ""
    suffix = card.get("suffix") or ""
    mom    = card.get("mom")
    yoy    = card.get("yoy")

    # Guard against nan/inf
    if not isinstance(val, (int, float)) or math.isnan(val) or math.isinf(val):
        val = 0.0

    if abs(val) >= 1_000_000:
        val_str = f"{prefix}{val/1_000_000:.1f}M{suffix}"
    elif abs(val) >= 1_000:
        val_str = f"{prefix}{val/1_000:.1f}K{suffix}"
    else:
        val_str = f"{prefix}{val:,.1f}{suffix}"

    badges, direction = "", "flat"
    if mom:
        direction = mom["direction"]
        arrow     = "↑" if direction == "up" else "↓"
        badges   += f'<span class="kpi-badge {direction}">{arrow} {abs(mom["pct_change"])}% MoM</span>'
    if yoy:
        d = yoy["direction"]
        badges += f'<span class="kpi-badge {d}">{"↑" if d=="up" else "↓"} {abs(yoy["pct_change"])}% YoY</span>'

    compare_line = ""
    if mom:
        compare_line = f'<div class="kpi-compare">vs {prefix}{mom["previous"]:,.0f}{suffix} last period</div>'

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
    st.markdown('<div class="filter-bar"><div class="filter-title">🔽 Filters</div>', unsafe_allow_html=True)
    cols, active = st.columns(min(len(filter_cols), 4)), {}
    for i, (col_name, options) in enumerate(list(filter_cols.items())[:4]):
        with cols[i % len(cols)]:
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
        # Build a context string from the uploaded file (and, for PDFs/Word
        # docs, the raw extracted text too) so the LLM understands the data
        if uploaded_df is not None:
            col_info = ", ".join(str(c) for c in uploaded_df.columns.tolist())
            dtypes   = "; ".join(f"{c}:{str(uploaded_df[c].dtype)}" for c in uploaded_df.columns)
            context  = f"Uploaded data columns: {col_info}\nColumn types: {dtypes}"
            if doc_text:
                context += f"\n\nDocument excerpt (for extra context):\n{doc_text[:1500]}"
        elif doc_text:
            context = f"No tabular data found, but the uploaded document contains this text:\n{doc_text[:2500]}"
        else:
            context = "No file uploaded — use sample data."

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

    if show_reasoning and config.get("reasoning"):
        st.markdown(f'<div class="reasoning-box">💭 <strong>AI reasoning:</strong> {config["reasoning"]}</div>', unsafe_allow_html=True)
    if show_json:
        with st.expander("🔧 Raw JSON config"):
            st.json(config)

    dash_title = config.get("dashboard_title", "Dashboard")

    with st.spinner("📊 Rendering dashboard…"):
        try:
            figures, df = render_dashboard(config, uploaded_df, active_filters={})
        except Exception as e:
            st.error(f"Render error: {e}")
            st.stop()

    st.session_state.last_df = df

    active_filters = render_filter_bar(df)
    if active_filters:
        try:
            figures, df = render_dashboard(config, uploaded_df, active_filters=active_filters)
        except Exception as e:
            st.error(f"Filter render error: {e}")

    # ── Title + export ────────────────────────────────────────────────────────
    title_col, export_col = st.columns([5, 3])
    with title_col:
        st.markdown(f'<div class="dash-title">{dash_title}</div>', unsafe_allow_html=True)
    with export_col:
        export_data, export_type = build_full_dashboard_png(figures, dash_title)
        fname = dash_title.replace(" ", "_").lower()
        if export_data and export_type == "png":
            st.download_button(
                "⬇ Download Dashboard PNG", data=export_data,
                file_name=f"{fname}_dashboard.png", mime="image/png",
                use_container_width=True,
            )
        elif export_data and export_type == "html":
            st.download_button(
                "⬇ Download Dashboard (HTML)", data=export_data,
                file_name=f"{fname}_dashboard.html", mime="text/html",
                use_container_width=True,
            )
        elif export_type:
            st.caption(f"⚠ Export error: {export_type}")

    # ── AI Insights ────────────────────────────────────────────────────────
    if show_insights:
        insights_key = f"insights_{prompt_hash(user_prompt, df.shape)}"
        if insights_key not in st.session_state.prompt_cache:
            with st.spinner("🔍 Analyzing dashboard…"):
                stats_summary = summarize_for_insights(df, config)
                insights_result = generate_insights(dash_title, stats_summary, user_prompt)
            st.session_state.prompt_cache[insights_key] = insights_result
        else:
            insights_result = st.session_state.prompt_cache[insights_key]

        if insights_result.get("success") and insights_result.get("insights"):
            bullets = "".join(f"<li>{b}</li>" for b in insights_result["insights"])
            st.markdown(
                f'<div class="insights-box"><div class="insights-title">🔍 AI Insights</div>'
                f'<ul>{bullets}</ul></div>',
                unsafe_allow_html=True,
            )
        elif not insights_result.get("success"):
            st.caption(f"⚠ Couldn't generate insights: {insights_result.get('error', 'unknown error')}")

    # ── KPI cards ────────────────────────────────────────────────────────────
    for item in figures:
        if item["type"] == "kpi":
            cols = st.columns(len(item["cards"]))
            for col, card in zip(cols, item["cards"]):
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
        png = fig_to_png_bytes(item["fig"])
        fname_c = item["title"].replace(" ", "_")
        if png:
            st.download_button("⬇ Save chart as PNG", data=png,
                file_name=f"{fname_c}.png", mime="image/png", key="dl_single")
        else:
            st.download_button("⬇ Save chart as HTML", data=fig_to_html(item["fig"]).encode(),
                file_name=f"{fname_c}.html", mime="text/html", key="dl_single_html")
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
                        png = fig_to_png_bytes(item["fig"])
                        fname_c = item["title"].replace(" ", "_")
                        if png:
                            st.download_button("⬇ Save as PNG", data=png,
                                file_name=f"{fname_c}.png", mime="image/png", key=f"dl_{idx}")
                        else:
                            st.download_button("⬇ Save as HTML", data=fig_to_html(item["fig"]).encode(),
                                file_name=f"{fname_c}.html", mime="text/html", key=f"dl_{idx}_html")
                        st.markdown('</div>', unsafe_allow_html=True)

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