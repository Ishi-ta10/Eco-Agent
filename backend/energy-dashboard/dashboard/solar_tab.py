"""
solar_tab.py — Solar-specific tab.
"""

from datetime import date

import streamlit as st
import plotly.graph_objects as go

from data_ingestion_agent.exporter import export_solar_xlsx


def render_solar_tab(solar_raw, cfg, start_d, end_d):
    """Render the Solar tab content."""
    sf = solar_raw[(solar_raw["Date"] >= start_d) & (solar_raw["Date"] <= end_d)]
    daily_target = cfg["solar"]["daily_target_kwh"]

    # ── KPI cards ──
    sc1, sc2, sc3, sc4, sc5 = st.columns(5)
    total_solar = sf["Solar Units Generated (KWh)"].sum()
    n_days = sf["Date"].nunique()
    daily_avg = total_solar / n_days if n_days > 0 else 0
    target_pct = round((daily_avg / daily_target) * 100, 1) if daily_target > 0 else 0
    peak_row = sf.loc[sf["Solar Units Generated (KWh)"].idxmax()] if not sf.empty else None
    total_saved = total_solar * 7.11
    fault_count = (sf["Inverter Status"] != "All Online").sum()

    sc1.metric("Total Solar KWh", f"{total_solar:,.0f}")
    sc2.metric("Daily Avg vs Target", f"{target_pct}%",
               delta=f"{daily_avg:,.0f} / {daily_target:,} KWh")
    sc3.metric("Peak Generation",
               f"{peak_row['Date']}" if peak_row is not None else "N/A",
               delta=f"{peak_row['Solar Units Generated (KWh)']:,.0f} KWh" if peak_row is not None else None)
    sc4.metric("Energy Saved", f"₹{total_saved:,.0f}")
    sc5.metric("Inverter Faults", f"{fault_count} events",
               delta="⚠️ Check needed" if fault_count > 0 else "✅ All OK",
               delta_color="inverse" if fault_count > 0 else "normal")

    st.divider()

    # ── Inverter status indicators ──
    st.subheader("Inverter SMB Status")
    smb_cols = ["SMB1 (KWh)", "SMB2 (KWh)", "SMB3 (KWh)", "SMB4 (KWh)", "SMB5 (KWh)"]
    smb_status_cols = st.columns(5)
    for i, smb_col in enumerate(smb_cols):
        smb_name = smb_col.split(" ")[0]
        all_positive = (sf[smb_col] > 0).all() if not sf.empty else False
        with smb_status_cols[i]:
            if all_positive:
                st.markdown(
                    f"<div style='text-align:center; padding:12px; background:#E8F5E9; "
                    f"border-radius:8px; border:2px solid #2E7D32;'>"
                    f"<span style='font-size:28px;'>🟢</span><br>"
                    f"<b>{smb_name}</b><br><span style='color:#2E7D32;'>Online</span></div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"<div style='text-align:center; padding:12px; background:#FFEBEE; "
                    f"border-radius:8px; border:2px solid #D32F2F;'>"
                    f"<span style='font-size:28px;'>🔴</span><br>"
                    f"<b>{smb_name}</b><br><span style='color:#D32F2F;'>Fault</span></div>",
                    unsafe_allow_html=True,
                )

    st.divider()

    # ── Chart: Solar generation by day ──
    st.subheader("Solar Generation by Day")
    solar_daily = sf.groupby("Date")["Solar Units Generated (KWh)"].sum().reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=solar_daily["Date"].astype(str), y=solar_daily["Solar Units Generated (KWh)"],
        fill="tozeroy", mode="lines+markers", name="Solar KWh",
        line=dict(color="#FFB300"), fillcolor="rgba(255,179,0,0.3)",
    ))
    fig.add_hline(y=daily_target, line_dash="dash", line_color="red",
                  annotation_text=f"Daily Target: {daily_target:,} KWh")
    fig.update_layout(xaxis_title="Date", yaxis_title="Solar KWh",
                      height=380, margin=dict(t=10, b=40))
    st.plotly_chart(fig, width="stretch")

    # ── Chart: SMB contribution ──
    st.subheader("Inverter Contribution Breakdown")
    smb_daily = sf.groupby("Date")[smb_cols].sum().reset_index()
    fig2 = go.Figure()
    colors = ["#1F77B4", "#FF7F0E", "#2CA02C", "#D62728", "#9467BD"]
    for j, col in enumerate(smb_cols):
        fig2.add_trace(go.Bar(
            x=smb_daily["Date"].astype(str), y=smb_daily[col],
            name=col.split(" ")[0], marker_color=colors[j],
        ))
    fig2.update_layout(barmode="stack", xaxis_title="Date", yaxis_title="KWh",
                       height=380, margin=dict(t=10, b=40))
    st.plotly_chart(fig2, width="stretch")

    # ── Data table ──
    st.subheader("Solar Data")
    st.dataframe(sf, height=350, width="stretch")

    xlsx = export_solar_xlsx(sf)
    st.download_button(
        "📥 Download Solar data",
        data=xlsx,
        file_name=f"Solar_Data_{date.today().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
