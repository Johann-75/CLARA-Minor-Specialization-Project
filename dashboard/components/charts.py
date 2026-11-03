import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from dashboard.utils.risk_tiers import (
    COLOR_CRITICAL,
    COLOR_HIGH,
    COLOR_MEDIUM,
    COLOR_LOW,
    COLOR_PRIMARY,
    COLOR_DARK,
    COLOR_MUTED,
    TIER_COLORS
)

def check_empty(df: pd.DataFrame, title: str) -> tuple[go.Figure, bool]:
    """
    Helper checking if a DataFrame is empty, returning a placeholder Plotly figure if True.
    """
    if df is None or df.empty:
        fig = go.Figure()
        fig.update_layout(
            title=dict(text=title, font=dict(size=14, color=COLOR_DARK)),
            xaxis={"visible": False},
            yaxis={"visible": False},
            annotations=[{
                "text": "No data available for the selected filters",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {"size": 15, "color": COLOR_MUTED}
            }],
            template="plotly_white",
            margin=dict(l=20, r=20, t=50, b=20)
        )
        return fig, True
    return None, False

def risk_distribution_pie(df: pd.DataFrame) -> go.Figure:
    """
    Plots operational risk category distribution counts (Critical, High, Medium, Low).
    """
    title = "Project-Defined Operational Risk Distribution"
    fig_empty, is_empty = check_empty(df, title)
    if is_empty:
        return fig_empty
        
    fig = px.pie(
        df, 
        values="count", 
        names="risk_category", 
        hole=0.45, 
        title=title,
        color="risk_category",
        color_discrete_map=TIER_COLORS,
        category_orders={"risk_category": ["Critical", "High", "Medium", "Low", "Unknown"]}
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>Instances: %{value}<br>Share: %{percent}<extra></extra>"
    )
    fig.update_layout(
        template="plotly_white", 
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
    )
    return fig

def cost_trend_line(df: pd.DataFrame) -> go.Figure:
    """
    Plots fleet daily cost trends over the past 30 days.
    """
    title = "Fleet Daily Spend Trend (Last 30 Days)"
    fig_empty, is_empty = check_empty(df, title)
    if is_empty:
        return fig_empty
        
    fig = px.line(
        df, 
        x="date", 
        y="daily_cost", 
        title=title,
        labels={"date": "Date", "daily_cost": "Daily Spend ($)"}
    )
    fig.update_traces(
        line=dict(color=COLOR_PRIMARY, width=2.5),
        hovertemplate="Date: %{x|%Y-%m-%d}<br>Spend: $%{y:,.2f}<extra></extra>"
    )
    fig.update_layout(
        template="plotly_white", 
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis_title="Date",
        yaxis_title="Daily Spend ($)",
        yaxis=dict(tickformat="$,.0f")
    )
    return fig

def risk_by_region_heatmap(df: pd.DataFrame) -> go.Figure:
    """
    Plots average composite risk score grouped by provider and region.
    """
    title = "Average Risk Score by Region & Cloud Provider"
    fig_empty, is_empty = check_empty(df, title)
    if is_empty:
        return fig_empty
        
    try:
        pivot_df = df.pivot(index="cloud_provider", columns="region", values="avg_risk_score").fillna(0.0)
        
        fig = go.Figure(data=go.Heatmap(
            z=pivot_df.values,
            x=pivot_df.columns,
            y=pivot_df.index,
            colorscale="YlOrRd",
            zmin=0,
            zmax=100,
            colorbar=dict(title="Avg Risk (0-100)"),
            hovertemplate="Provider: %{y}<br>Region: %{x}<br>Avg Risk: %{z:.1f}<extra></extra>"
        ))
        
        fig.update_layout(
            title=title,
            template="plotly_white",
            margin=dict(l=20, r=20, t=50, b=20),
            xaxis_title="Region",
            yaxis_title="Cloud Provider"
        )
        return fig
    except Exception:
        fig = px.bar(
            df, 
            x="region", 
            y="avg_risk_score", 
            color="cloud_provider",
            barmode="group",
            title=title,
            color_discrete_sequence=[COLOR_PRIMARY, COLOR_HIGH, COLOR_MEDIUM],
            labels={"avg_risk_score": "Avg Risk Score", "region": "Region", "cloud_provider": "Provider"}
        )
        fig.update_layout(
            template="plotly_white", 
            margin=dict(l=20, r=20, t=50, b=20),
            yaxis=dict(range=[0, 100])
        )
        return fig

def port_exposure_bar(df: pd.DataFrame) -> go.Figure:
    """
    Plots frequency distribution of top open network ports across the fleet.
    """
    title = "Top 10 Open Port Occurrences (Fleet-Wide)"
    fig_empty, is_empty = check_empty(df, title)
    if is_empty:
        return fig_empty
        
    top_df = df.head(10).copy()
    fig = px.bar(
        top_df, 
        x="port", 
        y="count", 
        title=title,
        color_discrete_sequence=[COLOR_HIGH],
        labels={"port": "Port Number", "count": "Instance Count"}
    )
    fig.update_traces(
        hovertemplate="Port: %{x}<br>Open on: %{y} instances<extra></extra>"
    )
    fig.update_layout(
        template="plotly_white", 
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis_title="Port Number",
        yaxis_title="Instance Count",
        xaxis=dict(type="category")
    )
    return fig

def vulnerability_breakdown_pie(df: pd.DataFrame) -> go.Figure:
    """
    Plots configurations breakdown aggregates across all instances.
    """
    title = "Security Vulnerability Breakdown (Fleet-Wide)"
    fig_empty, is_empty = check_empty(df, title)
    if is_empty:
        return fig_empty
        
    fig = px.pie(
        df, 
        values="count", 
        names="vulnerability", 
        hole=0.45,
        title=title,
        color="vulnerability",
        color_discrete_map={
            "Internet Exposed": COLOR_CRITICAL,
            "Excessive IAM": COLOR_HIGH,
            "Unencrypted Volume": COLOR_MEDIUM,
            "Brute-force attempts": COLOR_PRIMARY
        }
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>Instances: %{value}<br>Share: %{percent}<extra></extra>"
    )
    fig.update_layout(
        template="plotly_white", 
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
    )
    return fig

def security_events_timeline(df: pd.DataFrame) -> go.Figure:
    """
    Plots a daily histogram/timeline of security events grouped by severity.
    """
    title = "Security Events Daily Timeline (by Severity)"
    fig_empty, is_empty = check_empty(df, title)
    if is_empty:
        return fig_empty
        
    df_copy = df.copy()
    df_copy["date"] = pd.to_datetime(df_copy["timestamp"]).dt.date
    grouped = df_copy.groupby(["date", "severity"]).size().reset_index(name="event_count")
    grouped = grouped.sort_values(by="date")
    
    fig = px.bar(
        grouped,
        x="date",
        y="event_count",
        color="severity",
        title=title,
        color_discrete_map={
            "critical": COLOR_CRITICAL,
            "high": COLOR_HIGH,
            "medium": COLOR_MEDIUM,
            "low": COLOR_LOW
        },
        labels={"event_count": "Event Count", "date": "Date", "severity": "Severity"},
        barmode="stack",
        category_orders={"severity": ["critical", "high", "medium", "low"]}
    )
    fig.update_traces(
        hovertemplate="Date: %{x}<br>Severity: %{fullData.name}<br>Events: %{y}<extra></extra>"
    )
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis_title="Date",
        yaxis_title="Events Count",
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    return fig

def cost_by_type_donut(df: pd.DataFrame) -> go.Figure:
    """
    Spend breakdown donut chart by instance type across the entire fleet (30-day window).
    """
    title = "30-Day Fleet Spend by Instance Type"
    fig_empty, is_empty = check_empty(df, title)
    if is_empty:
        return fig_empty
        
    cost_col = "monthly_cost" if "monthly_cost" in df.columns else "total_cost"
    fig = px.pie(
        df, 
        values=cost_col, 
        names="instance_type", 
        hole=0.45, 
        title=title,
        color_discrete_sequence=[COLOR_PRIMARY, "#14b8a6", "#2dd4bf", "#5eead4", "#99f6e4", "#0f766e", "#115e59"]
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>Spend: $%{value:,.2f}<br>Share: %{percent}<extra></extra>"
    )
    fig.update_layout(
        template="plotly_white", 
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
    )
    return fig

def utilization_scatter(df: pd.DataFrame) -> go.Figure:
    """
    Resource utilization scatter plot across all fleet instances.
    X: CPU Util %, Y: Memory Util %, Bubble Size: Daily Spend ($), Color: Composite Risk Score.
    """
    title = "Fleet Resource Utilization vs. Spend & Risk Score"
    fig_empty, is_empty = check_empty(df, title)
    if is_empty:
        return fig_empty
        
    fig = px.scatter(
        df, 
        x="avg_cpu_utilization_pct", 
        y="avg_memory_utilization_pct",
        size="avg_daily_cost_usd", 
        color="overall_risk_score",
        title=title,
        labels={
            "avg_cpu_utilization_pct": "Avg CPU Utilization (%)", 
            "avg_memory_utilization_pct": "Avg Memory Utilization (%)",
            "overall_risk_score": "Risk Score (0-100)",
            "avg_daily_cost_usd": "Daily Cost ($)"
        },
        color_continuous_scale="YlOrRd",
        range_color=[0, 100],
        hover_name="instance_id"
    )
    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>Avg CPU: %{x:.1f}%<br>Avg Memory: %{y:.1f}%<br>Risk Score: %{marker.color:.1f}<extra></extra>"
    )
    fig.update_layout(
        template="plotly_white", 
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(range=[0, 100]),
        yaxis=dict(range=[0, 100])
    )
    return fig

def recommendation_savings_bar(df: pd.DataFrame) -> go.Figure:
    """
    Plots horizontal bar of top 10 savings recommendations.
    """
    title = "Top 10 Savings Opportunities by Recommendation ($/mo)"
    fig_empty, is_empty = check_empty(df, title)
    if is_empty:
        return fig_empty
        
    top_10 = df.sort_values(by="estimated_savings_usd", ascending=False).head(10).copy()
    fig = px.bar(
        top_10, 
        x="estimated_savings_usd", 
        y="title", 
        orientation="h",
        title=title,
        color="priority",
        color_discrete_map=TIER_COLORS,
        category_orders={"priority": ["Critical", "High", "Medium", "Low", "Unknown"]},
        labels={
            "estimated_savings_usd": "Monthly Savings ($)", 
            "title": "Recommendation Title",
            "priority": "Priority"
        }
    )
    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>Monthly Savings: $%{x:,.2f}<br>Priority: %{fullData.name}<extra></extra>"
    )
    fig.update_layout(
        template="plotly_white", 
        margin=dict(l=20, r=20, t=50, b=20),
        yaxis={"categoryorder": "total ascending"},
        xaxis=dict(tickformat="$,.0f")
    )
    return fig

def utilized_vs_wasted_bar(df_spend: pd.DataFrame) -> go.Figure:
    """
    Plots a stacked bar chart of fleet-wide utilized vs wasted spend ($/Month).
    Accepts DataFrame with 'total_monthly_spend' and 'wasted_spend' (or 'estimated_savings').
    """
    title = "Fleet-Wide Utilized vs. Actionable Wasted Spend ($/Month)"
    fig_empty, is_empty = check_empty(df_spend, title)
    if is_empty:
        return fig_empty
        
    total_spend = float(df_spend["total_monthly_spend"].iloc[0]) if "total_monthly_spend" in df_spend.columns else 0.0
    wasted_spend = float(df_spend["wasted_spend"].iloc[0]) if "wasted_spend" in df_spend.columns else 0.0
    utilized_spend = max(0.0, total_spend - wasted_spend)
    
    plot_df = pd.DataFrame({
        "Category": ["Fleet Monthly Total"],
        "Utilized Spend (Efficient)": [utilized_spend],
        "Actionable Waste (Projected Savings)": [wasted_spend]
    })
    
    fig = px.bar(
        plot_df,
        x="Category",
        y=["Utilized Spend (Efficient)", "Actionable Waste (Projected Savings)"],
        title=title,
        color_discrete_map={
            "Utilized Spend (Efficient)": COLOR_PRIMARY,
            "Actionable Waste (Projected Savings)": COLOR_HIGH
        },
        barmode="stack"
    )
    fig.update_traces(
        hovertemplate="<b>%{fullData.name}</b><br>Amount: $%{y:,.2f}<extra></extra>"
    )
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=20, r=20, t=50, b=20),
        yaxis_title="Spend ($/Month)",
        xaxis_title="",
        legend=dict(title="Spend Classification", orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        yaxis=dict(tickformat="$,.0f")
    )
    return fig

def cost_forecast_chart(historical_df: pd.DataFrame, forecast_days=90) -> go.Figure:
    """
    Plots historical daily spend and projects an unweighted linear baseline forward.
    """
    title = f"Fleet Daily Spend & {forecast_days}-Day Linear Baseline Projection"
    fig_empty, is_empty = check_empty(historical_df, title)
    if is_empty:
        return fig_empty
        
    df = historical_df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(by="date")
    
    start_date = df["date"].min()
    df["days_since_start"] = (df["date"] - start_date).dt.days
    
    x_hist = df["days_since_start"].values
    y_hist = df["daily_cost"].values
    
    if len(x_hist) > 1:
        slope, intercept = np.polyfit(x_hist, y_hist, 1)
    else:
        slope, intercept = 0.0, y_hist[0] if len(y_hist) > 0 else 0.0
        
    last_day = x_hist[-1] if len(x_hist) > 0 else 0
    last_date = df["date"].max()
    
    future_days = np.arange(last_day + 1, last_day + 1 + forecast_days)
    future_dates = [last_date + pd.Timedelta(days=int(d - last_day)) for d in future_days]
    future_cost = slope * future_days + intercept
    future_cost = np.clip(future_cost, 0.0, None)
    
    forecast_df = pd.DataFrame({
        "date": future_dates,
        "daily_cost": future_cost
    })
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["daily_cost"],
        mode="lines",
        name="Historical Daily Spend",
        line=dict(color=COLOR_PRIMARY, width=2.5),
        hovertemplate="Date: %{x|%Y-%m-%d}<br>Historical Spend: $%{y:,.2f}<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=forecast_df["date"],
        y=forecast_df["daily_cost"],
        mode="lines",
        name=f"{forecast_days}-Day Linear Trend",
        line=dict(color=COLOR_HIGH, width=2, dash="dash"),
        hovertemplate="Date: %{x|%Y-%m-%d}<br>Projected Spend: $%{y:,.2f}<extra></extra>"
    ))
    fig.update_layout(
        title=title,
        template="plotly_white",
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis_title="Date",
        yaxis_title="Daily Cost ($)",
        yaxis=dict(tickformat="$,.0f"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    return fig
