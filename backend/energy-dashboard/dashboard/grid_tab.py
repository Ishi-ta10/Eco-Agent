"""
grid_tab.py — Grid-specific tab.
"""

from datetime import date

import streamlit as st
import plotly.graph_objects as go

from data_ingestion_agent.exporter import export_grid_xlsx


def render_grid_tab(grid_raw, start_d, end_d):
    """Render the Grid tab content."""
    gf = grid_raw[(grid_raw["Date"] >= start_d) & (grid_raw["Date"] <= end_d)]

    # ── KPI cards ──
    gc1, gc2, gc3, gc4 = st.columns(4)
    total_grid_kwh = gf["Grid Units Consumed (KWh)"].sum()
    total_grid_cost = gf["Total Units Consumed in INR"].sum()

    if not gf.empty:
        peak_row = gf.loc[gf["Grid Units Consumed (KWh)"].idxmax()]
        avg_grid_kwh = gf["Grid Units Consumed (KWh)"].mean()
    else:
        peak_row = None
        avg_grid_kwh = 0

    gc1.metric("Total Grid KWh", f"{total_grid_kwh:,.0f}")
    gc2.metric("Total Grid Cost", f"₹{total_grid_cost:,.0f}")
    gc3.metric("Peak Consumption",
               f"{peak_row['Date']}" if peak_row is not None else "N/A",
               delta=f"{peak_row['Grid Units Consumed (KWh)']:,.0f} KWh" if peak_row is not None else None)
    gc4.metric("Avg Grid KWh/day", f"{avg_grid_kwh:,.0f}")

    st.divider()

    # ── Chart: Grid consumption by date ──
    st.subheader("Grid Consumption by Date")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=gf["Date"].astype(str), y=gf["Grid Units Consumed (KWh)"],
                         marker_color="#1F77B4"))
    fig.update_layout(xaxis_title="Date", yaxis_title="Grid KWh",
                      height=380, margin=dict(t=10, b=40))
    st.plotly_chart(fig, width="stretch")

    # ── Data table (ECS format — no solar column) ──
    st.subheader("Grid Data")
    display_cols = ["Date", "Day", "Time", "Ambient Temperature °C",
                    "Grid Units Consumed (KWh)",
                    "Total Units Consumed (KWh)",
                    "Total Units Consumed in INR",
                    "Energy Saving in INR"]
    avail = [c for c in display_cols if c in gf.columns]
    st.dataframe(gf[avail], height=350, width="stretch")

    grid_xlsx = export_grid_xlsx(gf)
    st.download_button(
        "📥 Download Grid data",
        data=grid_xlsx,
        file_name=f"Grid_Data_{date.today().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
