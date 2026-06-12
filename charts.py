# charts.py — Olive's Nexus · fully upgraded chart rendering

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Design tokens ──────────────────────────────────────────────────────────────
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
    "chart_colors":   [
        "#5B4FE8",  # violet
        "#10B981",  # emerald
        "#F59E0B",  # amber
        "#EF4444",  # red
        "#0EA5E9",  # sky
        "#9B59F5",  # purple
        "#EC4899",  # pink
        "#14B8A6",  # teal
    ],
}

# ── Plotly base template ───────────────────────────────────────────────────────
def _base_layout() -> dict:
    """Returns a fresh base layout dict for every figure."""
    return dict(
        font          = dict(family=THEME["font"], color=THEME["text_primary"], size=13),
        paper_bgcolor = "rgba(0,0,0,0)",
        plot_bgcolor  = "rgba(0,0,0,0)",
        colorway      = THEME["chart_colors"],
        margin        = dict(t=52, b=36, l=40, r=28),
        title_font    = dict(size=14, color=THEME["text_primary"],
                             family=THEME["font"]),
        title_x       = 0,
        title_pad     = dict(l=2),
        xaxis = dict(
            gridcolor     = THEME["grid"],
            linecolor     = THEME["border"],
            tickfont      = dict(size=11, color=THEME["text_secondary"]),
            title_font    = dict(size=11, color=THEME["text_secondary"]),
            showgrid      = True,
            zeroline      = False,
            ticklen       = 0,
            ticks         = "",
        ),
        yaxis = dict(
            gridcolor     = THEME["grid"],
            linecolor     = "rgba(0,0,0,0)",
            tickfont      = dict(size=11, color=THEME["text_secondary"]),
            title_font    = dict(size=11, color=THEME["text_secondary"]),
            showgrid      = True,
            zeroline      = False,
            ticklen       = 0,
            ticks         = "",
        ),
        legend = dict(
            bgcolor       = "rgba(0,0,0,0)",
            bordercolor   = THEME["border"],
            borderwidth   = 1,
            font          = dict(size=11, color=THEME["text_secondary"]),
            orientation   = "h",
            y             = -0.2,
            x             = 0,
        ),
        hoverlabel = dict(
            bgcolor       = THEME["text_primary"],
            font_color    = "#FFFFFF",
            font_size     = 12,
            font_family   = THEME["font"],
            bordercolor   = THEME["text_primary"],
            namelength    = -1,
        ),
        modebar = dict(
            bgcolor       = "rgba(0,0,0,0)",
            color         = THEME["text_light"],
            activecolor   = THEME["primary"],
        ),
    )


def apply_theme(fig, height: int = 340):
    """Apply full Nexus theme to a Plotly figure."""
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


def safe_col(df: pd.DataFrame, col_name):
    if col_name and col_name in df.columns:
        return col_name
    for c in df.columns:
        if c.lower() == str(col_name).lower():
            return c
    return df.columns[0]


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
            if c.lower() in ["month","date","week","period","quarter","year"]:
                time_col = c
                break

    if time_col is None or time_col not in df.columns:
        return result
    if value_col not in df.columns:
        return result

    series = pd.to_numeric(df[value_col], errors="coerce")
    df2 = df.copy()
    df2["_val"] = series
    df2 = df2.dropna(subset=["_val"])

    if len(df2) < 2:
        return result

    current  = df2["_val"].iloc[-1]
    previous = df2["_val"].iloc[-2]

    if previous != 0:
        pct = ((current - previous) / abs(previous)) * 100
        result["mom"] = {
            "current":    current,
            "previous":   previous,
            "change":     current - previous,
            "pct_change": round(pct, 1),
            "direction":  "up" if pct >= 0 else "down",
        }

    if len(df2) >= 13:
        year_ago = df2["_val"].iloc[-13]
        if year_ago != 0:
            pct_yoy = ((current - year_ago) / abs(year_ago)) * 100
            result["yoy"] = {
                "current":    current,
                "previous":   year_ago,
                "change":     current - year_ago,
                "pct_change": round(pct_yoy, 1),
                "direction":  "up" if pct_yoy >= 0 else "down",
            }

    return result


# ── KPI Cards ─────────────────────────────────────────────────────────────────
def render_kpi_cards(kpi_configs: list, df: pd.DataFrame) -> list:
    """
    Returns list of dicts: {fig, label, value, mom, yoy, prefix, suffix}
    Each KPI gets a clean Indicator figure used in the full-dashboard PNG export.
    """
    cards = []
    for kpi in kpi_configs[:6]:   # support up to 6 KPIs
        col_name = safe_col(df, kpi.get("value_column", df.columns[0]))
        agg      = kpi.get("aggregation", "sum")
        prefix   = kpi.get("prefix") or ""
        suffix   = kpi.get("suffix") or ""
        label    = kpi.get("label", col_name)

        series = pd.to_numeric(df[col_name], errors="coerce").dropna()
        if agg == "sum":     val = series.sum()
        elif agg == "mean":  val = series.mean()
        elif agg == "count": val = len(series)
        elif agg == "max":   val = series.max()
        elif agg == "min":   val = series.min()
        else:                val = series.sum()

        mom_yoy = compute_mom_yoy(df, col_name)
        mom     = mom_yoy.get("mom")
        yoy     = mom_yoy.get("yoy")

        # Determine delta for the indicator figure
        delta_ref = mom["previous"] if mom else None
        direction = (mom["direction"] if mom else "flat")
        accent    = THEME["success"] if direction == "up" else (
                    THEME["danger"]  if direction == "down" else THEME["primary"])

        # Build a compact Indicator figure (used in the full-PNG export)
        indicator_args = dict(
            mode  = "number",
            value = round(val, 2),
            number = dict(
                prefix      = prefix,
                suffix      = suffix,
                font        = dict(size=38, color=THEME["text_primary"],
                                   family=THEME["font"]),
                valueformat = ",.0f",
            ),
            title = dict(
                text = (f"<span style='font-size:11px;font-weight:700;"
                        f"color:{THEME['text_secondary']};letter-spacing:0.04em;"
                        f"text-transform:uppercase'>{label}</span>"),
                font = dict(size=11),
            ),
        )

        if delta_ref is not None:
            indicator_args["mode"] = "number+delta"
            indicator_args["delta"] = dict(
                reference        = delta_ref,
                relative         = True,
                valueformat      = ".1%",
                increasing       = dict(color=THEME["success"], symbol="▲ "),
                decreasing       = dict(color=THEME["danger"],  symbol="▼ "),
                font             = dict(size=13),
            )

        fig = go.Figure(go.Indicator(**indicator_args))
        fig.update_layout(
            height        = 130,
            margin        = dict(t=32, b=8, l=12, r=12),
            paper_bgcolor = "rgba(0,0,0,0)",
            plot_bgcolor  = "rgba(0,0,0,0)",
        )

        cards.append({
            "fig":    fig,
            "label":  label,
            "value":  val,
            "mom":    mom,
            "yoy":    yoy,
            "prefix": prefix,
            "suffix": suffix,
        })

    return cards


# ── Individual chart renderer ──────────────────────────────────────────────────
def render_chart(chart_config: dict, df: pd.DataFrame):
    chart_type  = chart_config.get("chart_type", "bar")
    title       = chart_config.get("title", "Chart")
    x_col       = safe_col(df, chart_config.get("x_column"))
    y_col       = safe_col(df, chart_config.get("y_column"))
    color_col   = chart_config.get("color_column")
    orientation = chart_config.get("orientation")
    barmode     = chart_config.get("barmode")

    color_col = color_col if (color_col and color_col in df.columns) else None

    try:
        # ── Bar chart ──────────────────────────────────────────────────────
        if chart_type == "bar":
            kwargs = dict(
                x                      = x_col,
                y                      = y_col,
                title                  = title,
                color                  = color_col,
                color_discrete_sequence= THEME["chart_colors"],
            )
            if orientation == "h":
                kwargs.update(x=y_col, y=x_col, orientation="h")
            if barmode:
                kwargs["barmode"] = barmode

            fig = px.bar(df, **kwargs)
            fig.update_traces(
                marker_line_width = 0,
                opacity           = 0.93,
                # Rounded top corners via marker pattern (Plotly workaround)
                marker_cornerradius = "4",
            )
            # Single-series: gradient fill using a colorscale trick
            if color_col is None and orientation != "h":
                n = len(df)
                colors = [
                    f"rgba(91,79,232,{0.55 + 0.45 * i / max(n - 1, 1):.2f})"
                    for i in range(n)
                ]
                fig.update_traces(marker_color=colors)

        # ── Line chart ─────────────────────────────────────────────────────
        elif chart_type == "line":
            fig = px.line(
                df, x=x_col, y=y_col, title=title, color=color_col,
                color_discrete_sequence=THEME["chart_colors"],
                markers=True,
            )
            fig.update_traces(
                line       = dict(width=2.8),
                marker     = dict(size=7, line=dict(width=2, color="#FFFFFF")),
            )
            # Soft gradient fill under single-series lines
            if color_col is None:
                fig.update_traces(
                    fill      = "tozeroy",
                    fillcolor = THEME["primary_fill"],
                    line_color= THEME["primary"],
                )

        # ── Area chart ─────────────────────────────────────────────────────
        elif chart_type == "area":
            fig = px.area(
                df, x=x_col, y=y_col, title=title, color=color_col,
                color_discrete_sequence=THEME["chart_colors"],
            )
            fig.update_traces(
                line  = dict(width=2.5),
                fillcolor = THEME["primary_fill"],
            )

        # ── Pie / Donut ────────────────────────────────────────────────────
        elif chart_type == "pie":
            fig = px.pie(
                df, names=x_col, values=y_col, title=title,
                hole=0.54,
                color_discrete_sequence=THEME["chart_colors"],
            )
            fig.update_traces(
                textposition      = "outside",
                textinfo          = "percent+label",
                textfont_size     = 12,
                marker            = dict(line=dict(color="#FFFFFF", width=2.5)),
                pull              = [0.03] * len(df),
            )
            # Centre label
            fig.add_annotation(
                text      = title.split()[0] if title else "",
                x=0.5, y=0.5,
                font      = dict(size=13, color=THEME["text_secondary"],
                                 family=THEME["font"]),
                showarrow = False,
            )

        # ── Scatter ────────────────────────────────────────────────────────
        elif chart_type == "scatter":
            fig = px.scatter(
                df, x=x_col, y=y_col, title=title, color=color_col,
                color_discrete_sequence=THEME["chart_colors"],
                size_max=22,
            )
            fig.update_traces(
                marker = dict(
                    size   = 10,
                    opacity= 0.82,
                    line   = dict(width=1.5, color="#FFFFFF"),
                )
            )

        # ── Histogram ──────────────────────────────────────────────────────
        elif chart_type == "histogram":
            fig = px.histogram(
                df, x=x_col, title=title, color=color_col,
                color_discrete_sequence=THEME["chart_colors"],
                nbins=20,
            )
            fig.update_traces(
                marker_line_width = 0,
                opacity           = 0.88,
                marker_color      = THEME["primary"],
            )

        # ── Funnel ─────────────────────────────────────────────────────────
        elif chart_type == "funnel":
            fig = go.Figure(go.Funnel(
                y            = df[x_col].tolist(),
                x            = df[y_col].tolist(),
                textposition = "inside",
                textinfo     = "value+percent initial",
                textfont     = dict(size=12, color="#FFFFFF"),
                marker       = dict(
                    color     = THEME["chart_colors"][:len(df)],
                    line      = dict(width=0),
                ),
                connector    = dict(line=dict(color=THEME["border"], width=1)),
                opacity      = 0.92,
            ))
            fig.update_layout(title=title)

        # ── Gauge ──────────────────────────────────────────────────────────
        elif chart_type == "gauge":
            series = pd.to_numeric(df[y_col], errors="coerce").dropna()
            val    = series.mean() if not series.empty else 0
            fig    = go.Figure(go.Indicator(
                mode  = "gauge+number+delta",
                value = round(val, 1),
                title = dict(
                    text = title,
                    font = dict(size=14, color=THEME["text_primary"],
                                family=THEME["font"]),
                ),
                number = dict(
                    font = dict(size=36, color=THEME["text_primary"],
                                family=THEME["font"]),
                ),
                delta = dict(
                    reference   = 75,
                    increasing  = dict(color=THEME["success"]),
                    decreasing  = dict(color=THEME["danger"]),
                    font        = dict(size=13),
                ),
                gauge = dict(
                    axis  = dict(
                        range     = [0, 100],
                        tickwidth = 1,
                        tickcolor = THEME["border"],
                        tickfont  = dict(size=10, color=THEME["text_light"]),
                    ),
                    bar         = dict(color=THEME["primary"], thickness=0.3),
                    bgcolor     = THEME["bg"],
                    borderwidth = 0,
                    steps       = [
                        dict(range=[0, 40],  color=THEME["danger_soft"]),
                        dict(range=[40, 70], color=THEME["warning_soft"]),
                        dict(range=[70,100], color=THEME["success_soft"]),
                    ],
                    threshold   = dict(
                        line  = dict(color=THEME["primary"], width=3),
                        thickness=0.85, value=75,
                    ),
                ),
            ))

        # ── Gantt ──────────────────────────────────────────────────────────
        elif chart_type == "gantt":
            if "start_date" in df.columns and "end_date" in df.columns:
                fig = px.timeline(
                    df, x_start="start_date", x_end="end_date",
                    y=x_col, color=color_col, title=title,
                    color_discrete_sequence=THEME["chart_colors"],
                )
            else:
                temp       = df.copy()
                temp["_s"] = pd.to_datetime("2024-01-01")
                pts        = pd.to_numeric(
                    temp.get("story_points", temp[y_col]), errors="coerce"
                ).fillna(3)
                temp["_e"] = pd.to_datetime("2024-01-01") + pd.to_timedelta(pts, unit="D")
                fig = px.timeline(
                    temp, x_start="_s", x_end="_e", y=x_col,
                    color="status" if "status" in temp.columns else None,
                    title=title,
                    color_discrete_sequence=THEME["chart_colors"],
                )
            fig.update_traces(opacity=0.9)

        # ── Fallback ───────────────────────────────────────────────────────
        else:
            fig = px.bar(
                df, x=x_col, y=y_col, title=title,
                color_discrete_sequence=THEME["chart_colors"],
            )

        apply_theme(fig)
        return fig

    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(
            text      = f"Could not render chart: {e}",
            x=0.5, y=0.5,
            showarrow = False,
            font      = dict(size=13, color=THEME["danger"], family=THEME["font"]),
        )
        fig.update_layout(height=220, title=title)
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
        cards = render_kpi_cards(kpi_cards, df)
        figures.append({"type": "kpi", "cards": cards})

    for chart_cfg in config.get("charts", []):
        fig = render_chart(chart_cfg, df)
        figures.append({
            "type":        "chart",
            "fig":         fig,
            "title":       chart_cfg.get("title", ""),
            "description": chart_cfg.get("description", ""),
        })

    return figures, df