"""
diesel_tab.py — Diesel-specific tab.
"""

from datetime import date

import streamlit as st
import plotly.graph_objects as go

from data_ingestion_agent.exporter import export_diesel_xlsx


def render_diesel_tab(diesel_raw, start_d, end_d):
    """Render the Diesel tab content."""
    df = diesel_raw[(diesel_raw["Date"] >= start_d) & (diesel_raw["Date"] <= end_d)]

    # ── KPI cards ──
    dc1, dc2, dc3, dc4 = st.columns(4)
    total_dg = df["DG Units Consumed (KWh)"].sum()
    total_cost = df["Total Cost (INR)"].sum()
    total_runtime = df["DG Runtime (hrs)"].sum()
    total_fuel = df["Fuel Consumed (Litres)"].sum()

    dc1.metric("Total DG KWh", f"{total_dg:,.1f}")
    dc2.metric("Total DG Cost", f"₹{total_cost:,.0f}")
    dc3.metric("Total Runtime", f"{total_runtime:,.1f} hrs")
    dc4.metric("Total Fuel Consumed", f"{total_fuel:,.1f} L")

    st.divider()

    # ── Chart ──
    st.subheader("DG Usage by Date")
    dg_daily = df.groupby("Date")["DG Units Consumed (KWh)"].sum().reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=dg_daily["Date"].astype(str), y=dg_daily["DG Units Consumed (KWh)"],
        marker_color="#D32F2F", name="DG KWh",
    ))
    fig.update_layout(xaxis_title="Date", yaxis_title="DG KWh",
                      height=380, margin=dict(t=10, b=40))
    st.plotly_chart(fig, width="stretch")

    # ── DG usage log ──
    st.subheader("DG Usage Log")
    active = df[df["DG Units Consumed (KWh)"] > 0]
    if active.empty:
        st.info("No diesel generator usage in selected period.")
    else:
        log_cols = ["Date", "Day", "Time", "DG ID", "DG Units Consumed (KWh)",
                    "DG Runtime (hrs)", "Fuel Consumed (Litres)", "Total Cost (INR)"]
        st.dataframe(active[[c for c in log_cols if c in active.columns]],
                     height=250, width="stretch")

    xlsx = export_diesel_xlsx(df)
    st.download_button(
        "📥 Download Diesel data",
        data=xlsx,
        file_name=f"Diesel_Data_{date.today().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
