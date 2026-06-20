# charts.py — Olive's Nexus · fixed safe_col + KPI nan guard

import math
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

THEME = {
    "primary":        "#5B4FE8",
    "primary_mid":    "#7C6FFF",
    "primary_soft":   "#EDEAFF",
    "primary_fill":   "rgba(91,79,232,0.08)",
    "success":        "#10B981",
    "success_soft":   "#EDFAF3",
    "danger":         "#EF4444",
    "danger_soft":    "#FEF2F2",
    "warning":        "#F59E0B",
    "warning_soft":   "#FFFBEB",
    "neutral":        "#7A82A0",
    "bg":             "#F0F2F8",
    "card_bg":        "#FFFFFF",
    "border":         "#E2E6F0",
    "grid":           "#EEF0F8",
    "text_primary":   "#0D0F1A",
    "text_secondary": "#7A82A0",
    "text_light":     "#A0A9C0",
    "font":           "Space Grotesk, Arial, sans-serif",
    "chart_colors":   ["#5B4FE8","#10B981","#F59E0B","#EF4444",
                       "#0EA5E9","#9B59F5","#EC4899","#14B8A6"],
}

def _base_layout() -> dict:
    return dict(
        font          = dict(family=THEME["font"], color=THEME["text_primary"], size=13),
        paper_bgcolor = "rgba(0,0,0,0)",
        plot_bgcolor  = "rgba(0,0,0,0)",
        colorway      = THEME["chart_colors"],
        margin        = dict(t=10, b=36, l=40, r=28),
        xaxis = dict(
            gridcolor=THEME["grid"], linecolor=THEME["border"],
            tickfont=dict(size=11, color=THEME["text_secondary"]),
            title_font=dict(size=11, color=THEME["text_secondary"]),
            showgrid=True, zeroline=False, ticklen=0, ticks="",
        ),
        yaxis = dict(
            gridcolor=THEME["grid"], linecolor="rgba(0,0,0,0)",
            tickfont=dict(size=11, color=THEME["text_secondary"]),
            title_font=dict(size=11, color=THEME["text_secondary"]),
            showgrid=True, zeroline=False, ticklen=0, ticks="",
        ),
        legend = dict(
            bgcolor="rgba(0,0,0,0)", bordercolor=THEME["border"], borderwidth=1,
            font=dict(size=11, color=THEME["text_secondary"]),
            orientation="h", y=-0.2, x=0,
        ),
        hoverlabel = dict(
            bgcolor=THEME["text_primary"], font_color="#FFFFFF",
            font_size=12, font_family=THEME["font"],
            bordercolor=THEME["text_primary"], namelength=-1,
        ),
        modebar = dict(
            bgcolor="rgba(0,0,0,0)", color=THEME["text_light"],
            activecolor=THEME["primary"],
        ),
    )

def apply_theme(fig, height: int = 340):
    layout = _base_layout()
    layout["height"] = height
    fig.update_layout(**layout)
    return fig


# ── Sample data ────────────────────────────────────────────────────────────────
SAMPLE_DATA = {
    "business_finance": pd.DataFrame({
        "month":      ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
        "revenue":    [120000,135000,128000,142000,155000,149000,163000,171000,158000,182000,195000,210000],
        "profit":     [24000,27000,25600,28400,31000,29800,32600,34200,31600,36400,39000,42000],
        "cost":       [96000,108000,102400,113600,124000,119200,130400,136800,126400,145600,156000,168000],
        "region":     ["North","North","South","South","East","East","West","West","North","South","East","West"],
        "product":    ["Product A","Product B","Product A","Product C","Product B","Product A",
                       "Product C","Product B","Product A","Product C","Product B","Product A"],
        "cac":        [450,420,460,440,410,430,400,390,410,380,370,360],
        "churn_rate": [3.2,2.8,3.5,2.9,2.6,3.1,2.7,2.4,2.8,2.3,2.1,2.0],
    }),
    "hr": pd.DataFrame({
        "department":       ["Engineering","Marketing","Sales","HR","Finance","Operations","Product","Design"],
        "headcount":        [45,18,32,8,12,25,15,10],
        "turnover_rate":    [8.2,12.5,18.3,5.1,6.7,14.2,9.8,7.3],
        "avg_salary":       [95000,72000,68000,61000,78000,58000,88000,82000],
        "engagement_score": [78,72,65,81,76,69,80,83],
        "open_roles":       [5,2,8,1,1,3,2,1],
        "month":            ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug"],
        "hires":            [4,2,6,1,2,3,3,2],
    }),
    "project_management": pd.DataFrame({
        "task":         ["Design","Backend","Frontend","Testing","Deployment","Documentation","Review","Launch"],
        "status":       ["Done","In Progress","In Progress","To Do","To Do","Done","In Progress","To Do"],
        "assignee":     ["Alice","Bob","Carol","Dave","Eve","Alice","Bob","Carol"],
        "priority":     ["High","High","Medium","High","Medium","Low","Medium","High"],
        "story_points": [8,13,10,5,3,4,6,8],
        "completion":   [100,60,45,0,0,100,30,0],
        "week":         ["W1","W2","W3","W4","W5","W6","W7","W8"],
        "velocity":     [21,18,24,19,26,22,28,25],
        "budget":       [8000,13000,10000,5000,3000,4000,6000,8000],
        "actual":       [7800,12500,6200,0,0,4100,1800,0],
    }),
    "general": pd.DataFrame({
        "category": ["A","B","C","D","E"],
        "value":    [100,85,120,95,110],
    }),
}


# ── Helpers ────────────────────────────────────────────────────────────────────
def get_dataframe(domain: str, uploaded_df=None) -> pd.DataFrame:
    if uploaded_df is not None:
        return uploaded_df.copy()
    return SAMPLE_DATA.get(domain, SAMPLE_DATA["general"]).copy()


def _first_numeric(df: pd.DataFrame) -> str:
    """Return first column with actual numeric data."""
    for c in df.columns:
        if pd.to_numeric(df[c], errors="coerce").notna().sum() > 0:
            return c
    return df.columns[0]


def safe_col(df: pd.DataFrame, col_name, numeric_only: bool = False) -> str:
    """
    Robust column lookup with 4 fallback levels:
    1. Exact match
    2. Case-insensitive match
    3. Substring / fuzzy match
    4. Word-overlap match
    Falls back to first numeric col (numeric_only=True) or first col.
    """
    if not col_name:
        return _first_numeric(df) if numeric_only else df.columns[0]

    s = str(col_name).strip()

    # 1. Exact
    if s in df.columns:
        return s

    # 2. Case-insensitive
    sl = s.lower()
    for c in df.columns:
        if c.lower() == sl:
            return c

    # 3. Substring
    for c in df.columns:
        if sl in c.lower() or c.lower() in sl:
            return c

    # 4. Word overlap
    search_words = set(sl.replace("_", " ").split())
    best_col, best_score = None, 0
    for c in df.columns:
        score = len(search_words & set(c.lower().replace("_", " ").split()))
        if score > best_score:
            best_score, best_col = score, c
    if best_col and best_score > 0:
        return best_col

    return _first_numeric(df) if numeric_only else df.columns[0]


def _best_numeric_col(df: pd.DataFrame, col_name) -> str:
    """Like safe_col but guarantees a numeric result column."""
    col = safe_col(df, col_name)
    if pd.to_numeric(df[col], errors="coerce").notna().sum() > 0:
        return col
    return _first_numeric(df)


def detect_filter_columns(df: pd.DataFrame) -> dict:
    filters = {}
    for col in df.columns:
        if df[col].dtype == object:
            unique_vals = df[col].dropna().unique().tolist()
            if 2 <= len(unique_vals) <= 20:
                filters[col] = sorted(unique_vals)
    return filters


def apply_filters(df: pd.DataFrame, active_filters: dict) -> pd.DataFrame:
    filtered = df.copy()
    for col, values in active_filters.items():
        if values and col in filtered.columns:
            filtered = filtered[filtered[col].isin(values)]
    return filtered


# ── MoM / YoY ─────────────────────────────────────────────────────────────────
def compute_mom_yoy(df: pd.DataFrame, value_col: str, time_col: str = None) -> dict:
    result = {"mom": None, "yoy": None}
    if time_col is None:
        for c in df.columns:
            if c.lower() in ["month","date","week","period","quarter","year",
                              "hire_date","date_joined","created_at"]:
                time_col = c
                break
    if time_col is None or value_col not in df.columns:
        return result

    df2 = df.copy()
    df2["_val"] = pd.to_numeric(df2[value_col], errors="coerce")
    df2 = df2.dropna(subset=["_val"])
    if len(df2) < 2:
        return result

    current, previous = df2["_val"].iloc[-1], df2["_val"].iloc[-2]
    if previous != 0:
        pct = ((current - previous) / abs(previous)) * 100
        result["mom"] = {
            "current": current, "previous": previous,
            "change": current - previous,
            "pct_change": round(pct, 1),
            "direction": "up" if pct >= 0 else "down",
        }
    if len(df2) >= 13:
        year_ago = df2["_val"].iloc[-13]
        if year_ago != 0:
            pct_yoy = ((current - year_ago) / abs(year_ago)) * 100
            result["yoy"] = {
                "current": current, "previous": year_ago,
                "change": current - year_ago,
                "pct_change": round(pct_yoy, 1),
                "direction": "up" if pct_yoy >= 0 else "down",
            }
    return result


# ── KPI Cards ─────────────────────────────────────────────────────────────────
def render_kpi_cards(kpi_configs: list, df: pd.DataFrame) -> list:
    cards = []
    for kpi in kpi_configs[:6]:
        raw_col  = kpi.get("value_column", "")
        agg      = kpi.get("aggregation", "sum")
        prefix   = kpi.get("prefix") or ""
        suffix   = kpi.get("suffix") or ""
        label    = kpi.get("label", raw_col)

        col_name = safe_col(df, raw_col) if agg == "count" else _best_numeric_col(df, raw_col)
        series   = pd.to_numeric(df[col_name], errors="coerce").dropna()

        if series.empty:
            val = 0.0
        elif agg == "sum":    val = float(series.sum())
        elif agg == "mean":   val = float(series.mean())
        elif agg == "count":  val = float(len(df[col_name].dropna()))
        elif agg == "max":    val = float(series.max())
        elif agg == "min":    val = float(series.min())
        else:                 val = float(series.sum())

        # Guard nan/inf
        if math.isnan(val) or math.isinf(val):
            val = 0.0

        mom_yoy   = compute_mom_yoy(df, col_name)
        mom       = mom_yoy.get("mom")
        yoy       = mom_yoy.get("yoy")
        delta_ref = mom["previous"] if mom else None
        direction = mom["direction"] if mom else "flat"

        indicator_args = dict(
            mode="number",
            value=round(val, 2),
            number=dict(
                prefix=prefix, suffix=suffix,
                font=dict(size=38, color=THEME["text_primary"], family=THEME["font"]),
                valueformat=",.0f",
            ),
            title=dict(
                text=(f"<span style='font-size:11px;font-weight:700;"
                      f"color:{THEME['text_secondary']};letter-spacing:0.04em;"
                      f"text-transform:uppercase'>{label}</span>"),
                font=dict(size=11),
            ),
        )
        if delta_ref is not None:
            indicator_args["mode"] = "number+delta"
            indicator_args["delta"] = dict(
                reference=delta_ref, relative=True, valueformat=".1%",
                increasing=dict(color=THEME["success"], symbol="▲ "),
                decreasing=dict(color=THEME["danger"],  symbol="▼ "),
                font=dict(size=13),
            )

        fig = go.Figure(go.Indicator(**indicator_args))
        fig.update_layout(
            height=130, margin=dict(t=32, b=8, l=12, r=12),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        )

        cards.append({
            "fig": fig, "label": label, "value": val,
            "mom": mom, "yoy": yoy, "prefix": prefix, "suffix": suffix,
        })
    return cards


# ── Individual chart renderer ──────────────────────────────────────────────────
def render_chart(chart_config: dict, df: pd.DataFrame):
    chart_type  = chart_config.get("chart_type", "bar")
    title       = chart_config.get("title", "Chart")
    x_col       = safe_col(df, chart_config.get("x_column"))
    y_col       = _best_numeric_col(df, chart_config.get("y_column"))
    color_col   = chart_config.get("color_column")
    orientation = chart_config.get("orientation")
    barmode     = chart_config.get("barmode")
    color_col   = color_col if (color_col and color_col in df.columns) else None
    PT          = None   # no internal title — app.py renders it in the card header

    try:
        if chart_type == "bar":
            kwargs = dict(x=x_col, y=y_col, title=PT, color=color_col,
                          color_discrete_sequence=THEME["chart_colors"])
            if orientation == "h":
                kwargs.update(x=y_col, y=x_col, orientation="h")
            if barmode:
                kwargs["barmode"] = barmode
            fig = px.bar(df, **kwargs)
            fig.update_traces(marker_line_width=0, opacity=0.93)
            if color_col is None and orientation != "h":
                n = len(df)
                fig.update_traces(marker_color=[
                    f"rgba(91,79,232,{0.55+0.45*i/max(n-1,1):.2f})" for i in range(n)
                ])

        elif chart_type == "line":
            fig = px.line(df, x=x_col, y=y_col, title=PT, color=color_col,
                          color_discrete_sequence=THEME["chart_colors"], markers=True)
            fig.update_traces(line=dict(width=2.8),
                              marker=dict(size=7, line=dict(width=2, color="#FFFFFF")))
            if color_col is None:
                fig.update_traces(fill="tozeroy", fillcolor=THEME["primary_fill"],
                                  line_color=THEME["primary"])

        elif chart_type == "area":
            fig = px.area(df, x=x_col, y=y_col, title=PT, color=color_col,
                          color_discrete_sequence=THEME["chart_colors"])
            fig.update_traces(line=dict(width=2.5), fillcolor=THEME["primary_fill"])

        elif chart_type == "pie":
            fig = px.pie(df, names=x_col, values=y_col, title=PT, hole=0.54,
                         color_discrete_sequence=THEME["chart_colors"])
            fig.update_traces(
                textposition="outside", textinfo="percent+label", textfont_size=12,
                marker=dict(line=dict(color="#FFFFFF", width=2.5)),
                pull=[0.03] * len(df),
            )

        elif chart_type == "scatter":
            fig = px.scatter(df, x=x_col, y=y_col, title=PT, color=color_col,
                             color_discrete_sequence=THEME["chart_colors"], size_max=22)
            fig.update_traces(marker=dict(size=10, opacity=0.82,
                                          line=dict(width=1.5, color="#FFFFFF")))

        elif chart_type == "histogram":
            fig = px.histogram(df, x=x_col, title=PT, color=color_col,
                               color_discrete_sequence=THEME["chart_colors"], nbins=20)
            fig.update_traces(marker_line_width=0, opacity=0.88,
                              marker_color=THEME["primary"])

        elif chart_type == "funnel":
            fig = go.Figure(go.Funnel(
                y=df[x_col].tolist(), x=df[y_col].tolist(),
                textposition="inside", textinfo="value+percent initial",
                textfont=dict(size=12, color="#FFFFFF"),
                marker=dict(color=THEME["chart_colors"][:len(df)], line=dict(width=0)),
                connector=dict(line=dict(color=THEME["border"], width=1)), opacity=0.92,
            ))

        elif chart_type == "gauge":
            series = pd.to_numeric(df[y_col], errors="coerce").dropna()
            val    = series.mean() if not series.empty else 0
            fig    = go.Figure(go.Indicator(
                mode="gauge+number+delta", value=round(val, 1),
                title=dict(text=title, font=dict(size=14, color=THEME["text_primary"],
                                                  family=THEME["font"])),
                number=dict(font=dict(size=36, color=THEME["text_primary"], family=THEME["font"])),
                delta=dict(reference=75, increasing=dict(color=THEME["success"]),
                           decreasing=dict(color=THEME["danger"]), font=dict(size=13)),
                gauge=dict(
                    axis=dict(range=[0,100], tickwidth=1, tickcolor=THEME["border"],
                              tickfont=dict(size=10, color=THEME["text_light"])),
                    bar=dict(color=THEME["primary"], thickness=0.3),
                    bgcolor=THEME["bg"], borderwidth=0,
                    steps=[dict(range=[0,40],   color=THEME["danger_soft"]),
                           dict(range=[40,70],  color=THEME["warning_soft"]),
                           dict(range=[70,100], color=THEME["success_soft"])],
                    threshold=dict(line=dict(color=THEME["primary"], width=3),
                                   thickness=0.85, value=75),
                ),
            ))

        elif chart_type == "gantt":
            if "start_date" in df.columns and "end_date" in df.columns:
                fig = px.timeline(df, x_start="start_date", x_end="end_date",
                                  y=x_col, color=color_col, title=PT,
                                  color_discrete_sequence=THEME["chart_colors"])
            else:
                temp       = df.copy()
                temp["_s"] = pd.to_datetime("2024-01-01")
                pts        = pd.to_numeric(df.get("story_points", df[y_col]),
                                           errors="coerce").fillna(3)
                temp["_e"] = pd.to_datetime("2024-01-01") + pd.to_timedelta(pts, unit="D")
                fig = px.timeline(temp, x_start="_s", x_end="_e", y=x_col,
                                  color="status" if "status" in temp.columns else None,
                                  title=PT, color_discrete_sequence=THEME["chart_colors"])
            fig.update_traces(opacity=0.9)

        else:
            fig = px.bar(df, x=x_col, y=y_col, title=PT,
                         color_discrete_sequence=THEME["chart_colors"])

        apply_theme(fig)
        return fig

    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(text=f"Could not render chart: {e}", x=0.5, y=0.5,
                           showarrow=False,
                           font=dict(size=13, color=THEME["danger"], family=THEME["font"]))
        apply_theme(fig)
        return fig


# ── Full dashboard renderer ────────────────────────────────────────────────────
def render_dashboard(config: dict, uploaded_df=None, active_filters: dict = None):
    domain = config.get("domain", "general")
    df     = get_dataframe(domain, uploaded_df)
    if active_filters:
        df = apply_filters(df, active_filters)

    figures = []
    kpi_cards = config.get("kpi_cards", [])
    if kpi_cards:
        figures.append({"type": "kpi", "cards": render_kpi_cards(kpi_cards, df)})

    for chart_cfg in config.get("charts", []):
        fig = render_chart(chart_cfg, df)
        figures.append({
            "type": "chart", "fig": fig,
            "title": chart_cfg.get("title", ""),
            "description": chart_cfg.get("description", ""),
        })
    return figures, df


# ── Insights data summary ───────────────────────────────────────────────────
def summarize_for_insights(df: pd.DataFrame, config: dict) -> str:
    """
    Compute real, concrete numbers from the rendered dashboard's data so the
    insights LLM call has actual facts to narrate instead of guessing.
    Returns a plain-text bullet list, one line per KPI/chart.
    """
    lines = []

    # KPI cards — exact aggregated value, plus MoM/YoY if available
    for kpi in config.get("kpi_cards", [])[:6]:
        raw_col  = kpi.get("value_column", "")
        agg      = kpi.get("aggregation", "sum")
        label    = kpi.get("label", raw_col)
        col_name = safe_col(df, raw_col) if agg == "count" else _best_numeric_col(df, raw_col)
        series   = pd.to_numeric(df[col_name], errors="coerce").dropna()
        if series.empty:
            continue

        if agg == "count":   val = float(len(df[col_name].dropna()))
        elif agg == "mean":  val = float(series.mean())
        elif agg == "max":   val = float(series.max())
        elif agg == "min":   val = float(series.min())
        else:                val = float(series.sum())

        line = f"- KPI '{label}': {agg}({col_name}) = {val:,.2f}"
        mom_yoy = compute_mom_yoy(df, col_name)
        if mom_yoy.get("mom"):
            m = mom_yoy["mom"]
            line += f" ({m['direction']} {abs(m['pct_change'])}% month-over-month)"
        lines.append(line)

    # Charts — trend for line/area, top/bottom category for bar/pie
    for chart_cfg in config.get("charts", [])[:8]:
        title  = chart_cfg.get("title", "Chart")
        ctype  = chart_cfg.get("chart_type", "bar")
        x_col  = safe_col(df, chart_cfg.get("x_column"))
        y_col  = _best_numeric_col(df, chart_cfg.get("y_column"))
        try:
            if ctype in ("line", "area"):
                series = pd.to_numeric(df[y_col], errors="coerce").dropna()
                if len(series) >= 2:
                    start, end = series.iloc[0], series.iloc[-1]
                    pct = ((end - start) / abs(start) * 100) if start else 0
                    lines.append(
                        f"- '{title}': {y_col} moved from {start:,.1f} to {end:,.1f} "
                        f"({pct:+.1f}% over the period)"
                    )
            elif ctype in ("bar", "pie", "funnel"):
                grouped = (
                    df.groupby(x_col)[y_col]
                    .apply(lambda s: pd.to_numeric(s, errors="coerce").sum())
                    .sort_values(ascending=False)
                )
                if not grouped.empty:
                    top_name, top_val       = grouped.index[0], grouped.iloc[0]
                    bottom_name, bottom_val = grouped.index[-1], grouped.iloc[-1]
                    lines.append(
                        f"- '{title}': highest {x_col} is {top_name} ({top_val:,.1f}); "
                        f"lowest is {bottom_name} ({bottom_val:,.1f})"
                    )
            elif ctype == "scatter":
                xs = pd.to_numeric(df[x_col], errors="coerce")
                ys = pd.to_numeric(df[y_col], errors="coerce")
                corr = xs.corr(ys)
                if pd.notna(corr):
                    lines.append(f"- '{title}': correlation between {x_col} and {y_col} is {corr:.2f}")
        except Exception:
            continue

    return "\n".join(lines) if lines else "No numeric summary could be computed from this data."