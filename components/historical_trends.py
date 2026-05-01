"""
CivicPulse — Historical Voting Trends Component
================================================
Win/loss patterns by party, swing analysis, margin charts using Plotly.
"""

from __future__ import annotations
import streamlit as st

try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# ── Historical data (West Bengal Assembly elections 1977–2021) ─────────────────
WB_HISTORICAL = {
    "years": [1977, 1982, 1987, 1991, 1996, 2001, 2006, 2011, 2016, 2021],
    "parties": {
        "CPI(M) / Left Front": {
            "seats": [230, 238, 251, 188, 202, 143, 235, 62, 32, 0],
            "color": "#CC0000",
        },
        "INC": {
            "seats": [20, 49, 40, 43, 82, 26, 21, 42, 44, 0],
            "color": "#00BFFF",
        },
        "AITC": {
            "seats": [None, None, None, None, None, 60, 30, 184, 211, 213],
            "color": "#00843D",
        },
        "BJP": {
            "seats": [None, None, None, None, None, 0, 0, 4, 3, 77],
            "color": "#FF6600",
        },
    },
    "total_seats": 294,
}

WB_VOTE_SHARE = {
    "years": [2001, 2006, 2011, 2016, 2021],
    "parties": {
        "Left Front": {"share": [48.7, 50.2, 39.7, 25.7, 8.0], "color": "#CC0000"},
        "AITC":       {"share": [38.0, 26.7, 45.6, 44.9, 47.9], "color": "#00843D"},
        "BJP":        {"share": [5.7,  4.7,  4.1,  10.2, 38.1], "color": "#FF6600"},
        "INC":        {"share": [5.0,  14.3, 9.1,  12.3, 2.9],  "color": "#00BFFF"},
    },
}

WB_SWING = {
    "constituencies": [
        "Nandigram", "Bhawanipore", "Ballygunge", "Salt Lake", "Kasba",
        "Joynagar", "Diamond Harbour", "Barrackpore"
    ],
    "aitc_swing": [2.1, 8.4, 5.2, -3.1, 6.7, 4.5, 9.1, 1.3],
    "bjp_swing": [-1.2, -4.3, -2.1, 6.5, -3.4, -2.1, -5.6, 0.8],
}


def _seat_trend_chart() -> None:
    """Stacked bar chart of seat counts by party over elections."""
    if not PLOTLY_AVAILABLE:
        st.warning("Install `plotly` to enable trend charts: `pip install plotly`")
        return

    fig = go.Figure()
    years = WB_HISTORICAL["years"]

    for party, pdata in WB_HISTORICAL["parties"].items():
        seats = [s if s is not None else 0 for s in pdata["seats"]]
        fig.add_trace(go.Bar(
            name=party,
            x=years,
            y=seats,
            marker_color=pdata["color"],
            hovertemplate=f"<b>{party}</b><br>Year: %{{x}}<br>Seats: %{{y}}<extra></extra>",
        ))

    # Majority line
    fig.add_hline(
        y=148,
        line_dash="dash",
        line_color="#C62828",
        annotation_text="Majority (148)",
        annotation_position="right",
        annotation_font_color="#C62828",
    )

    fig.update_layout(
        barmode="stack",
        title=dict(
            text="West Bengal Assembly Seats by Party (1977–2021)",
            font=dict(size=14, color="#E8EAF0"),
        ),
        plot_bgcolor="#141720",
        paper_bgcolor="#141720",
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#E8EAF0"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            bgcolor="rgba(0,0,0,0)",
        ),
        xaxis=dict(
            title="Election Year",
            tickvals=years,
            ticktext=[str(y) for y in years],
            gridcolor="#E8E4DC",
        ),
        yaxis=dict(title="Seats Won", gridcolor="#E8E4DC"),
        height=380,
        margin=dict(l=40, r=20, t=60, b=40),
    )
    st.plotly_chart(fig, use_container_width=True)


def _vote_share_chart() -> None:
    """Line chart of vote share trends."""
    if not PLOTLY_AVAILABLE:
        return

    fig = go.Figure()
    years = WB_VOTE_SHARE["years"]

    for party, pdata in WB_VOTE_SHARE["parties"].items():
        fig.add_trace(go.Scatter(
            name=party,
            x=years,
            y=pdata["share"],
            mode="lines+markers",
            line=dict(color=pdata["color"], width=2.5),
            marker=dict(size=8, color=pdata["color"]),
            hovertemplate=f"<b>{party}</b><br>Year: %{{x}}<br>Vote Share: %{{y:.1f}}%<extra></extra>",
        ))

    fig.update_layout(
        title=dict(
            text="Vote Share Trends by Party (2001–2021)",
            font=dict(size=14, color="#E8EAF0"),
        ),
        plot_bgcolor="#141720",
        paper_bgcolor="#141720",
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#E8EAF0"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            bgcolor="rgba(0,0,0,0)",
        ),
        xaxis=dict(title="Election Year", gridcolor="#E8E4DC"),
        yaxis=dict(title="Vote Share (%)", gridcolor="#E8E4DC", range=[0, 60]),
        height=360,
        margin=dict(l=40, r=20, t=60, b=40),
    )
    st.plotly_chart(fig, use_container_width=True)


def _swing_chart() -> None:
    """Swing chart comparing AITC vs BJP swing in key constituencies."""
    if not PLOTLY_AVAILABLE:
        return

    fig = go.Figure()
    constituencies = WB_SWING["constituencies"]

    fig.add_trace(go.Bar(
        name="AITC Swing",
        x=constituencies,
        y=WB_SWING["aitc_swing"],
        marker_color=["#00843D" if v >= 0 else "#66BB6A" for v in WB_SWING["aitc_swing"]],
        hovertemplate="<b>AITC Swing</b><br>%{x}<br>%{y:+.1f}%<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name="BJP Swing",
        x=constituencies,
        y=WB_SWING["bjp_swing"],
        marker_color=["#FF6600" if v >= 0 else "#FFAA66" for v in WB_SWING["bjp_swing"]],
        hovertemplate="<b>BJP Swing</b><br>%{x}<br>%{y:+.1f}%<extra></extra>",
    ))

    fig.add_hline(y=0, line_color="#E8EAF0", line_width=1)

    fig.update_layout(
        barmode="group",
        title=dict(
            text="Swing Analysis — Key Constituencies (2021 vs 2016)",
            font=dict(size=14, color="#E8EAF0"),
        ),
        plot_bgcolor="#141720",
        paper_bgcolor="#141720",
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#E8EAF0"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(gridcolor="#E8E4DC"),
        yaxis=dict(title="Swing (%)", gridcolor="#E8E4DC", tickformat="+.1f"),
        height=360,
        margin=dict(l=40, r=20, t=60, b=80),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_historical_trends() -> None:
    """Render the full historical voting trends section."""
    st.markdown("### 📈 Historical Voting Trends")
    st.caption("West Bengal Assembly Elections — Data from ECI archives")

    if not PLOTLY_AVAILABLE:
        st.error(
            "⚠️ **Plotly not installed.** Add `plotly>=5.0.0` to `requirements.txt` "
            "and restart to enable charts."
        )
        return

    chart_type = st.radio(
        "Select Chart Type",
        ["🏛️ Seat Trends", "📊 Vote Share", "🔄 Swing Analysis"],
        horizontal=True,
        key="trend_chart_type",
    )

    if chart_type == "🏛️ Seat Trends":
        _seat_trend_chart()
        st.caption(
            "**Key observation:** Left Front's 34-year dominance (1977–2011) ended as "
            "AITC swept to power in 2011. BJP emerged as main opposition by 2021."
        )

    elif chart_type == "📊 Vote Share":
        _vote_share_chart()
        st.caption(
            "**Key observation:** BJP's vote share surged from 4% (2011) to 38% (2021), "
            "largely absorbing the collapsed Left vote bank."
        )

    elif chart_type == "🔄 Swing Analysis":
        _swing_chart()
        st.caption(
            "**Key observation:** AITC gained significantly in most constituencies in 2021, "
            "while BJP recorded negative swings in traditionally strong Left seats."
        )

    # ── Summary stats ──────────────────────────────────────────────────────────
    st.divider()
    st.markdown("#### 📋 Quick Statistics — 2021 vs 2016")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("AITC Seats 2021", "213", "+2 vs 2016")
    with c2:
        st.metric("BJP Seats 2021", "77", "+74 vs 2016")
    with c3:
        st.metric("Left Seats 2021", "0", "-32 vs 2016")
    with c4:
        st.metric("Voter Turnout 2021", "82.1%", "+0.8%")
