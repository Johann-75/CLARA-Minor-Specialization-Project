import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Consistent Dashboard Color Scheme
COLOR_CRITICAL = "#EF4444"
COLOR_HIGH = "#F59E0B"
COLOR_MEDIUM = "#EAB308"
COLOR_LOW = "#22C55E"
COLOR_PRIMARY = "#0D9488"
COLOR_DARK = "#0D1B2A"

def check_empty(df: pd.DataFrame, title: str) -> tuple[go.Figure, bool]:
    """
    Helper checking if a DataFrame is empty, returning a placeholder Plotly figure if True.
    """
    if df is None or df.empty:
        fig = go.Figure()
        fig.update_layout(
            title=title,
            xaxis={"visible": False},
            yaxis={"visible": False},
            annotations=[{
                "text": "No data available in this view",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {"size": 16, "color": "#64748b"}
            }],
            template="plotly_white"
        )
        return fig, True
    return None, False

def risk_distribution_pie(df: pd.DataFrame) -> go.Figure:
    """
    Plots overall risk category distribution counts.
    """
    fig_empty, is_empty = check_empty(df, "Overall Risk Distribution")
    if is_empty:
        return fig_empty
        
    fig = px.pie(
        df, 
        values="count", 
        names="risk_category", 
        hole=0.4, 
        title="Overall Risk Distribution",
        color="risk_category",
        color_discrete_map={
            "Critical": COLOR_CRITICAL,
            "High": COLOR_HIGH,
            "Medium": COLOR_MEDIUM,
            "Low": COLOR_LOW
        }
    )
    fig.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
    return fig

def cost_trend_line(df: pd.DataFrame) -> go.Figure:
    """
    Plots total cost trends over time.
    """
    fig_empty, is_empty = check_empty(df, "Daily Spend Trend ($)")
    if is_empty:
        return fig_empty
        
    fig = px.line(df, x="date", y="daily_cost", title="Daily Spend Trend ($)")
    fig.update_traces(line_color=COLOR_PRIMARY, line_width=2.5)
    fig.update_layout(
        template="plotly_white", 
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis_title="Date",
        yaxis_title="Daily Cost ($)"
    )
    return fig

def risk_by_region_heatmap(df: pd.DataFrame) -> go.Figure:
    """
    Plots a 2D Heatmap of average risk score by provider and region.
    """
    fig_empty, is_empty = check_empty(df, "Risk Heatmap by Region & Provider")
    if is_empty:
        return fig_empty
        
    try:
        # Pivot dataframe to get 2D matrix
        pivot_df = df.pivot(index="cloud_provider", columns="region", values="avg_risk_score").fillna(0.0)
        
        fig = go.Figure(data=go.Heatmap(
            z=pivot_df.values,
            x=pivot_df.columns,
            y=pivot_df.index,
            colorscale="YlOrRd",
            zmin=0,
            zmax=100,
            colorbar=dict(title="Avg Risk")
        ))
        
        fig.update_layout(
            title="Risk Heatmap by Region & Provider",
            template="plotly_white",
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis_title="Region",
            yaxis_title="Cloud Provider"
        )
        return fig
    except Exception:
        # Fallback if pivot fails (e.g. empty or duplicate elements)
        fig = px.bar(
            df, 
            x="region", 
            y="avg_risk_score", 
            color="cloud_provider",
            barmode="group",
            title="Average Risk Score by Region",
            color_discrete_sequence=[COLOR_PRIMARY, COLOR_HIGH, COLOR_MEDIUM]
        )
        fig.update_layout(
            template="plotly_white", 
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis_title="Region",
            yaxis_title="Average Risk Score"
        )
        return fig

def port_exposure_bar(df: pd.DataFrame) -> go.Figure:
    """
    Plots frequency distribution of open network ports.
    """
    fig_empty, is_empty = check_empty(df, "Top Open Port Occurrences")
    if is_empty:
        return fig_empty
        
    top_df = df.head(10)
    fig = px.bar(
        top_df, 
        x="port", 
        y="count", 
        title="Top Open Port Occurrences",
        color_discrete_sequence=[COLOR_HIGH]
    )
    fig.update_layout(
        template="plotly_white", 
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis_title="Port Number",
        yaxis_title="Active Instances Count"
    )
    return fig

def vulnerability_breakdown_pie(df: pd.DataFrame) -> go.Figure:
    """
    Plots configurations breakdown aggregates.
    """
    fig_empty, is_empty = check_empty(df, "Security Vulnerability Breakdown")
    if is_empty:
        return fig_empty
        
    fig = px.pie(
        df, 
        values="count", 
        names="vulnerability", 
        title="Security Vulnerability Breakdown",
        color_discrete_sequence=[COLOR_CRITICAL, COLOR_HIGH, COLOR_MEDIUM, COLOR_PRIMARY]
    )
    fig.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
    return fig

def security_events_timeline(df: pd.DataFrame) -> go.Figure:
    """
    Plots a daily histogram/timeline of security events grouped by severity.
    """
    fig_empty, is_empty = check_empty(df, "Security Events Daily Timeline")
    if is_empty:
        return fig_empty
        
    df = df.copy()
    # Convert timestamps to daily dates
    df["date"] = pd.to_datetime(df["timestamp"]).dt.date
    
    # Group by date and severity and count events
    grouped = df.groupby(["date", "severity"]).size().reset_index(name="event_count")
    # Sort chronologically
    grouped = grouped.sort_values(by="date")
    
    fig = px.bar(
        grouped,
        x="date",
        y="event_count",
        color="severity",
        title="Security Events Daily Timeline",
        color_discrete_map={
            "critical": COLOR_CRITICAL,
            "high": COLOR_HIGH,
            "medium": COLOR_MEDIUM,
            "low": COLOR_LOW
        },
        labels={"event_count": "Events Count", "date": "Date", "severity": "Severity"},
        barmode="stack"
    )
    
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis_title="Date",
        yaxis_title="Events Count",
        xaxis=dict(tickangle=0)
    )
    return fig

def cost_by_type_donut(df: pd.DataFrame) -> go.Figure:
    """
    Spend breakdown donut chart by instance type.
    """
    fig_empty, is_empty = check_empty(df, "Monthly Spend by Instance Type")
    if is_empty:
        return fig_empty
        
    fig = px.pie(
        df, 
        values="total_cost", 
        names="instance_type", 
        hole=0.4, 
        title="Monthly Spend by Instance Type",
        color_discrete_sequence=[COLOR_PRIMARY, "#14b8a6", "#2dd4bf", "#5eead4", "#99f6e4"]
    )
    fig.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
    return fig

def utilization_scatter(df: pd.DataFrame) -> go.Figure:
    """
    3D resource utilization bubble plot.
    """
    fig_empty, is_empty = check_empty(df, "Resource Utilization Scatter")
    if is_empty:
        return fig_empty
        
    fig = px.scatter(
        df, 
        x="avg_cpu_utilization_pct", 
        y="avg_memory_utilization_pct",
        size="avg_daily_cost_usd", 
        color="overall_risk_score",
        title="Resource Utilization vs. Cost & Risk Score",
        labels={
            "avg_cpu_utilization_pct": "Avg CPU Util %", 
            "avg_memory_utilization_pct": "Avg Memory Util %"
        },
        color_continuous_scale="Viridis",
        hover_name="instance_id"
    )
    fig.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
    return fig

def recommendation_savings_bar(df: pd.DataFrame) -> go.Figure:
    """
    Plots horizontal bar of top 10 savings recommendations.
    """
    fig_empty, is_empty = check_empty(df, "Top 10 Savings Opportunities")
    if is_empty:
        return fig_empty
        
    top_10 = df.sort_values(by="estimated_savings_usd", ascending=False).head(10)
    fig = px.bar(
        top_10, 
        x="estimated_savings_usd", 
        y="title", 
        orientation="h",
        title="Top 10 Savings Opportunities by Recommendation ($)",
        color="priority",
        color_discrete_map={
            "Critical": COLOR_CRITICAL,
            "High": COLOR_HIGH,
            "Medium": COLOR_MEDIUM,
            "Low": COLOR_LOW
        },
        labels={
            "estimated_savings_usd": "Monthly Savings ($)", 
            "title": "Recommendation"
        }
    )
    fig.update_layout(
        template="plotly_white", 
        margin=dict(l=20, r=20, t=40, b=20),
        yaxis={"categoryorder": "total ascending"}
    )
    return fig

def utilized_vs_wasted_bar(df: pd.DataFrame) -> go.Figure:
    """
    Plots a stacked bar chart of utilized vs wasted spend.
    """
    fig_empty, is_empty = check_empty(df, "Utilized vs. Wasted Spend ($/Month)")
    if is_empty:
        return fig_empty
        
    total_spend = df["monthly_cost"].sum()
    total_savings = df["estimated_savings"].sum()
    utilized_spend = max(0.0, total_spend - total_savings)
    
    plot_df = pd.DataFrame({
        "Category": ["Monthly Spend Breakdown"],
        "Utilized Spend (Efficient)": [utilized_spend],
        "Wasted Spend (Potential Savings)": [total_savings]
    })
    
    fig = px.bar(
        plot_df,
        x="Category",
        y=["Utilized Spend (Efficient)", "Wasted Spend (Potential Savings)"],
        title="Utilized vs. Wasted Spend ($/Month)",
        color_discrete_map={
            "Utilized Spend (Efficient)": COLOR_PRIMARY,
            "Wasted Spend (Potential Savings)": COLOR_CRITICAL
        },
        barmode="stack"
    )
    
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=20, r=20, t=40, b=20),
        yaxis_title="Spend ($/Month)",
        xaxis_title="",
        legend_title="Spend Type",
        yaxis=dict(tickformat="$,.2f"),
        xaxis=dict(tickangle=0)
    )
    return fig

def cost_forecast_chart(historical_df: pd.DataFrame, forecast_days=90) -> go.Figure:
    """
    Fits a simple linear trend on historical daily spend and forecasts it forward.
    """
    fig_empty, is_empty = check_empty(historical_df, f"Daily Spend & {forecast_days}-Day Forecast")
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
        name="Historical Spend",
        line=dict(color=COLOR_PRIMARY, width=2.5)
    ))
    
    fig.add_trace(go.Scatter(
        x=forecast_df["date"],
        y=forecast_df["daily_cost"],
        mode="lines",
        name=f"{forecast_days}-Day Forecast",
        line=dict(color=COLOR_HIGH, width=2, dash="dash")
    ))
    
    fig.update_layout(
        title=f"Daily Spend & {forecast_days}-Day Forecast ($)",
        template="plotly_white",
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis_title="Date",
        yaxis_title="Daily Cost ($)",
        yaxis=dict(tickformat="$,.2f")
    )
    return fig
