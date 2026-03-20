"""
overview.py — Overview (unified dashboard) tab.
"""

from datetime import date

import streamlit as st
import plotly.graph_objects as go

from data_ingestion_agent.processor import compute_daily_summary, compute_overview_kpis
from data_ingestion_agent.exporter import export_unified_xlsx


def render_overview_tab(unified_all, cfg, start_d, end_d):
    """Render the Overview tab content."""
    unified = unified_all[(unified_all["Date"] >= start_d) & (unified_all["Date"] <= end_d)]
    kpis = compute_overview_kpis(unified, cfg)

    # ── KPI cards ──
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total Consumption", f"{kpis['total_kwh']:,.1f} KWh",
              delta=f"{kpis['delta_kwh']:+,.1f} KWh" if kpis['delta_kwh'] is not None else None)
    c2.metric("Solar Generated", f"{kpis['solar_kwh']:,.1f} KWh",
              delta=f"{kpis['delta_solar_gen']:+,.1f} vs target")
    c3.metric("Solar Contribution", f"{kpis['solar_pct']}%",
              delta=f"{kpis['delta_solar_pct']:+.1f}%" if kpis['delta_solar_pct'] is not None else None)
    c4.metric("Total Cost", f"₹{kpis['total_cost']:,.0f}",
              delta=f"₹{kpis['delta_cost']:+,.0f}" if kpis['delta_cost'] is not None else None,
              delta_color="inverse")
    c5.metric("Energy Saved", f"₹{kpis['energy_saved']:,.0f}")
    c6.metric("Avg Temperature", f"{kpis['avg_temp']:.1f}°C")

    st.divider()

    # ── Charts ──
    chart_l, chart_r = st.columns(2)
    daily = compute_daily_summary(unified)

    with chart_l:
        st.subheader("Daily Energy Mix")
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(x=daily["Date"].astype(str), y=daily["Grid KWh"],
                                 name="Grid KWh", marker_color="#1F77B4"))
        fig_bar.add_trace(go.Bar(x=daily["Date"].astype(str), y=daily["Solar KWh"],
                                 name="Solar KWh", marker_color="#FFB300"))
        fig_bar.add_trace(go.Bar(x=daily["Date"].astype(str), y=daily["Diesel KWh"],
                                 name="Diesel KWh", marker_color="#D32F2F"))
        fig_bar.update_layout(barmode="stack", xaxis_title="Date", yaxis_title="KWh",
                              height=380, margin=dict(t=10, b=40))
        st.plotly_chart(fig_bar, width="stretch")

    with chart_r:
        st.subheader("Source Cost Comparison")
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(x=daily["Date"].astype(str), y=daily["Grid Cost (INR)"],
                                      name="Grid Cost", mode="lines+markers", line=dict(color="#1F77B4")))
        fig_line.add_trace(go.Scatter(x=daily["Date"].astype(str), y=daily["Diesel Cost (INR)"],
                                      name="Diesel Cost", mode="lines+markers", line=dict(color="#D32F2F")))
        fig_line.add_trace(go.Scatter(x=daily["Date"].astype(str), y=daily["Energy Saving (INR)"],
                                      name="Energy Saved", mode="lines+markers",
                                      line=dict(color="#2E7D32", dash="dash")))
        fig_line.update_layout(xaxis_title="Date", yaxis_title="INR (₹)",
                               height=380, margin=dict(t=10, b=40))
        st.plotly_chart(fig_line, width="stretch")

    # ── Data table ──
    st.subheader("Unified Data Table")
    display_cols = [
        "Date", "Day", "Time", "Ambient Temp (°C)",
        "Grid KWh", "Solar KWh", "Diesel KWh", "Total KWh",
        "Grid Cost (INR)", "Diesel Cost (INR)", "Solar Cost (INR)",
        "Total Cost (INR)", "Energy Saving (INR)", "Solar %", "Source",
    ]
    avail = [c for c in display_cols if c in unified.columns]
    st.dataframe(unified[avail], height=350, width="stretch")

    xlsx_bytes = export_unified_xlsx(unified)
    st.download_button(
        "📥 Download unified report",
        data=xlsx_bytes,
        file_name=f"Unified_Energy_Report_{date.today().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
