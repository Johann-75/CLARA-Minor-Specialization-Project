import streamlit as st

def metric_card(
    label: str, 
    value, 
    delta=None, 
    format_as_currency: bool = False, 
    format_as_percent: bool = False,
    help_text: str = None
):
    """
    A thin, standardized wrapper helper around st.metric that adds consistent formatting
    for currency, percentages, and standard KPI visual layouts.
    """
    formatted_value = value
    
    if format_as_currency:
        try:
            formatted_value = f"${float(value):,.2f}"
        except (ValueError, TypeError):
            formatted_value = f"${value}"
            
    elif format_as_percent:
        try:
            formatted_value = f"{float(value):.1f}%"
        except (ValueError, TypeError):
            formatted_value = f"{value}%"
            
    st.metric(label=label, value=formatted_value, delta=delta, help=help_text)
