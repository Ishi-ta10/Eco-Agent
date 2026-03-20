"""
scheduler_tab.py — Job Scheduler tab for configuring and controlling email reports.
"""

import os
from datetime import datetime, time

import streamlit as st
import pandas as pd

from mail_scheduling_agent.scheduler import (
    start_background_scheduler, stop_scheduler, get_next_run,
    save_scheduler_config, load_scheduler_config, load_scheduler_log,
)
from mail_scheduling_agent.emailer import send_daily_report


def render_scheduler_tab(cfg, project_root):
    """Render the Job Scheduler tab content."""
    existing_cfg = load_scheduler_config(project_root)

    # ── Section A — Email configuration ──
    st.subheader("📧 Email Configuration")

    col_to, col_cc = st.columns(2)
    with col_to:
        email_to = st.text_input(
            "Recipient(s) — To:",
            value=existing_cfg.get("to", cfg["email"]["default_to"]),
            help="Comma-separated email addresses",
        )
    with col_cc:
        email_cc = st.text_input(
            "Recipients — CC:",
            value=existing_cfg.get("cc", cfg["email"]["default_cc"]),
            help="Comma-separated email addresses",
        )

    send_time_str = existing_cfg.get("send_time", cfg["email"]["send_time_ist"])
    try:
        default_time = datetime.strptime(send_time_str, "%H:%M").time()
    except ValueError:
        default_time = time(10, 0)

    send_time_input = st.time_input("Send time (IST):", value=default_time)

    st.divider()

    # ── Section B — Upload template ──
    st.subheader("📎 Upload Excel Template (optional)")
    uploaded_file = st.file_uploader("Upload custom Excel template", type=["xlsx"])
    uploaded_template_path = existing_cfg.get("uploaded_template_path", None)

    if uploaded_file is not None:
        upload_dir = os.path.join(project_root, "uploaded_templates")
        os.makedirs(upload_dir, exist_ok=True)
        uploaded_template_path = os.path.join(upload_dir, uploaded_file.name)
        with open(uploaded_template_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        st.success(f"Template saved: {uploaded_file.name}")
        try:
            preview_df = pd.read_excel(uploaded_file)
            st.dataframe(preview_df, height=200)
        except Exception as e:
            st.warning(f"Could not preview: {e}")

    st.divider()

    # ── Section C — Email body customisation ──
    st.subheader("✏️ Email Body Customisation")

    email_subject = st.text_input(
        "Email subject:",
        value=existing_cfg.get("subject", cfg["email"]["subject"]),
    )

    st.markdown("**Include sections:**")
    inc_col1, inc_col2, inc_col3 = st.columns(3)
    with inc_col1:
        inc_summary = st.checkbox("Summary KPI cards",
                                  value=existing_cfg.get("include_sections", {}).get("summary_kpis", True))
        inc_table = st.checkbox("Unified data table",
                                value=existing_cfg.get("include_sections", {}).get("unified_table", True))
    with inc_col2:
        inc_grid = st.checkbox("Grid summary",
                               value=existing_cfg.get("include_sections", {}).get("grid_summary", True))
        inc_solar = st.checkbox("Solar summary",
                                value=existing_cfg.get("include_sections", {}).get("solar_summary", True))
    with inc_col3:
        inc_diesel = st.checkbox("Diesel summary",
                                 value=existing_cfg.get("include_sections", {}).get("diesel_summary", True))
        inc_inverter = st.checkbox("Inverter status",
                                   value=existing_cfg.get("include_sections", {}).get("inverter_status", True))
        inc_raw = st.checkbox("Full raw data attachment",
                              value=existing_cfg.get("include_sections", {}).get("raw_data", False))

    custom_message = st.text_area(
        "Custom message (optional):",
        value=existing_cfg.get("custom_message", ""),
        placeholder="Add a note to the top of the email body...",
    )

    st.divider()

    # ── Section D — Status and controls ──
    st.subheader("⏰ Schedule Status & Controls")

    status_col, info_col = st.columns(2)
    with status_col:
        if st.session_state.get("scheduler_running", False):
            st.markdown("**Scheduler status:** :green[● RUNNING]")
        else:
            st.markdown("**Scheduler status:** :red[● STOPPED]")
    with info_col:
        st.markdown(f"**Next scheduled run:** {get_next_run()}")
        logs = load_scheduler_log(project_root)
        if logs:
            last = logs[-1]
            st.markdown(f"**Last run:** {last.get('timestamp', 'N/A')} — {last.get('status', 'N/A')}")
        else:
            st.markdown("**Last run:** No runs yet")

    btn1, btn2, btn3 = st.columns(3)

    with btn1:
        if st.button("💾 Save schedule", use_container_width=True, key="save_schedule_btn"):
            new_config = {
                "to": email_to,
                "cc": email_cc,
                "send_time": send_time_input.strftime("%H:%M"),
                "subject": email_subject,
                "custom_message": custom_message,
                "uploaded_template_path": uploaded_template_path,
                "auto_start": st.session_state.get("scheduler_running", False),
                "include_sections": {
                    "summary_kpis": inc_summary,
                    "unified_table": inc_table,
                    "grid_summary": inc_grid,
                    "solar_summary": inc_solar,
                    "diesel_summary": inc_diesel,
                    "inverter_status": inc_inverter,
                    "raw_data": inc_raw,
                },
            }
            save_scheduler_config(new_config, project_root)
            st.success("✅ Schedule configuration saved!")

    with btn2:
        if st.button("📤 Send now (test)", use_container_width=True, key="send_now_btn"):
            with st.spinner("Sending email..."):
                try:
                    result = send_daily_report()
                    if result["status"] == "Success":
                        st.success(f"✅ Email sent to {result['recipients']} at {result['timestamp']}")
                    else:
                        st.error(f"❌ Failed: {result['notes']}")
                except Exception as e:
                    st.error(f"❌ Failed: {e}")

    with btn3:
        if st.session_state.get("scheduler_running", False):
            if st.button("⏹️ Stop scheduler", use_container_width=True):
                stop_scheduler()
                st.session_state["scheduler_running"] = False
                st.session_state["scheduler_started"] = False
                sched_data = load_scheduler_config(project_root)
                sched_data["auto_start"] = False
                save_scheduler_config(sched_data, project_root)
                st.info("Scheduler stopped.")
                st.rerun()
        else:
            if st.button("▶️ Start scheduler", use_container_width=True):
                send_t = send_time_input.strftime("%H:%M")
                start_background_scheduler(send_daily_report, send_t)
                st.session_state["scheduler_started"] = True
                st.session_state["scheduler_running"] = True
                sched_data = load_scheduler_config(project_root)
                sched_data["auto_start"] = True
                sched_data["send_time"] = send_t
                save_scheduler_config(sched_data, project_root)
                st.success(f"Scheduler started! Next run at {send_t} IST daily.")
                st.rerun()

    st.divider()

    # ── Section E — History log ──
    st.subheader("📋 Schedule History Log")
    logs = load_scheduler_log(project_root)
    if logs:
        log_df = pd.DataFrame(logs[-10:])
        display_cols = ["timestamp", "status", "recipients", "attachment", "notes"]
        avail = [c for c in display_cols if c in log_df.columns]
        st.dataframe(log_df[avail], width="stretch", height=280)
    else:
        st.info("No scheduler runs recorded yet.")
