"""
emailer.py — Build HTML email, send via SMTP, and log results.
Part of the Mail Scheduling Agent.
The email table follows the Electrical Optimization (1) Excel ECS sheet format.
"""

import os
import json
import smtplib
from datetime import datetime, date, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

import pandas as pd
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv

from data_ingestion_agent.loader import load_all
from data_ingestion_agent.processor import build_unified_dataframe, compute_overview_kpis
from data_ingestion_agent.exporter import export_ecs_style_xlsx


def _project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load_env():
    load_dotenv(os.path.join(_project_root(), ".env"))


def _read_scheduler_config() -> dict:
    path = os.path.join(_project_root(), "scheduler_config.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _append_log(entry: dict):
    """Append a scheduler run entry to the log file."""
    log_path = os.path.join(_project_root(), "output", "scheduler_log.json")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    logs = []
    if os.path.exists(log_path):
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except (json.JSONDecodeError, ValueError):
            logs = []
    logs.append(entry)
    logs = logs[-100:]
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2, default=str)


def _build_ecs_table_html(unified: pd.DataFrame) -> str:
    """Build the ECS-format data table as a raw HTML string (no Jinja2 needed)."""
    ecs_columns = [
        "Date", "Day", "Time", "Ambient Temp (°C)",
        "Grid KWh", "Solar KWh", "Total KWh",
        "Total Cost (INR)", "Energy Saving (INR)",
    ]
    ecs_display_headers = [
        "Date", "Day", "Time", "Ambient Temperature °C",
        "Grid Units Consumed (KWh)", "Solar Farm Energy (KWh)",
        "Total Units Consumed (KWh)",
        "Total Units Consumed in INR", "Energy Saving in INR",
    ]
    right_align_cols = {"Grid KWh", "Solar KWh", "Total KWh", "Total Cost (INR)", "Energy Saving (INR)"}
    currency_cols = {"Total Cost (INR)", "Energy Saving (INR)"}

    avail_cols = [c for c in ecs_columns if c in unified.columns]
    avail_headers = [ecs_display_headers[ecs_columns.index(c)] for c in avail_cols]

    rows_data = unified[avail_cols].to_dict("records")

    # Totals row
    totals = {}
    for col in avail_cols:
        if col in ["Date", "Day", "Time", "Ambient Temp (°C)"]:
            totals[col] = "Total" if col == "Date" else ""
        else:
            totals[col] = round(unified[col].sum(), 2)

    parts = ['<table width="100%" cellpadding="0" cellspacing="0" '
             'style="border-collapse:collapse; font-size:12px;">']

    # Header row
    parts.append("<tr>")
    for hdr in avail_headers:
        parts.append(
            f'<th style="background-color:#1F3864; color:#ffffff; padding:8px 10px; '
            f'text-align:left; border:1px solid #ccc; font-size:11px;">{hdr}</th>'
        )
    parts.append("</tr>")

    # Data rows
    for idx, row in enumerate(rows_data):
        bg = "#EBF2FB" if idx % 2 == 0 else "#ffffff"
        parts.append("<tr>")
        for col in avail_cols:
            val = row.get(col, "")
            align = "right" if col in right_align_cols else "left"
            if col in currency_cols and isinstance(val, (int, float)):
                cell_text = f"\u20b9{val:,.2f}"
            elif isinstance(val, float):
                cell_text = f"{val:,.2f}"
            else:
                cell_text = str(val)
            parts.append(
                f'<td style="padding:6px 10px; border:1px solid #ddd; '
                f'text-align:{align}; background-color:{bg};">{cell_text}</td>'
            )
        parts.append("</tr>")

    # Total row
    parts.append("<tr>")
    for col in avail_cols:
        val = totals[col]
        align = "right" if col in right_align_cols else "left"
        if col in currency_cols and isinstance(val, (int, float)):
            cell_text = f"\u20b9{val:,.2f}"
        elif isinstance(val, float):
            cell_text = f"{val:,.2f}"
        else:
            cell_text = str(val)
        parts.append(
            f'<td style="padding:8px 10px; border:1px solid #ccc; '
            f'text-align:{align}; background-color:#D6E4F0; '
            f'font-weight:bold; border-top:2px solid #1F3864;">{cell_text}</td>'
        )
    parts.append("</tr>")

    parts.append("</table>")
    return "\n".join(parts)


def _build_inverter_table_html(unified: pd.DataFrame) -> str:
    """Build inverter status as card-style blocks for email-safe rendering."""
    smb_names = ["SMB1", "SMB2", "SMB3", "SMB4", "SMB5"]
    statuses = {}
    for smb in smb_names:
        col = f"{smb} (KWh)"
        if col in unified.columns:
            statuses[smb] = "online" if (unified[col].fillna(0) > 0).all() else "fault"
        else:
            statuses[smb] = "unknown"

    parts = ['<table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:separate; border-spacing:8px 0;">']
    parts.append("<tr>")
    for smb, status in statuses.items():
        if status == "online":
            color = "#2E7D32"
            emoji = "&#9679;"  # green circle
            label = "Online"
        else:
            color = "#D32F2F"
            emoji = "&#9679;"  # red circle
            label = status.title()
        parts.append(
            f'<td width="20%" style="padding:10px 8px; text-align:center; border:1px solid #dfe5ec; background-color:#ffffff;">'
            f'<span style="font-size:16px; line-height:1; color:{color};">{emoji}</span><br>'
            f'<span style="display:inline-block; margin-top:6px; font-size:14px; font-weight:bold; color:#1F3864;">{smb}</span><br>'
            f'<span style="display:inline-block; margin-top:2px; font-size:11px; color:{color};">{label}</span>'
            f'</td>'
        )
    parts.append("</tr></table>")
    return "\n".join(parts)


def build_email_html(unified: pd.DataFrame, config: dict, custom_message: str = "",
                     include_sections: dict = None) -> str:
    """
    Render the Jinja2 email template.
    Dynamic HTML tables are pre-built in Python so the template has
    no Jinja2 expressions inside style attributes (avoids VS Code linter warnings).
    """
    templates_dir = os.path.join(_project_root(), "mail_scheduling_agent", "templates")
    env = Environment(loader=FileSystemLoader(templates_dir), autoescape=False)
    template = env.get_template("email_body.html")

    kpis = compute_overview_kpis(unified, config)

    # Pre-format KPI values as strings
    kpi_total_kwh = f"{kpis.get('total_kwh', 0):,.1f}"
    kpi_solar_kwh = f"{kpis.get('solar_kwh', 0):,.1f}"
    kpi_solar_pct = f"{kpis.get('solar_pct', 0):.1f}"
    kpi_total_cost = f"{kpis.get('total_cost', 0):,.0f}"
    kpi_energy_saved = f"{kpis.get('energy_saved', 0):,.0f}"
    kpi_avg_temp = f"{kpis.get('avg_temp', 0):.1f}"

    # Pre-render complex HTML tables in Python
    ecs_table_html = _build_ecs_table_html(unified)
    inverter_table_html = _build_inverter_table_html(unified)

    if include_sections is None:
        include_sections = {
            "summary_kpis": True,
            "unified_table": True,
            "grid_summary": True,
            "solar_summary": True,
            "diesel_summary": True,
            "inverter_status": True,
        }

    html = template.render(
        report_date=date.today().strftime("%d %B %Y"),
        custom_message=custom_message,
        kpi_total_kwh=kpi_total_kwh,
        kpi_solar_kwh=kpi_solar_kwh,
        kpi_solar_pct=kpi_solar_pct,
        kpi_total_cost=kpi_total_cost,
        kpi_energy_saved=kpi_energy_saved,
        kpi_avg_temp=kpi_avg_temp,
        ecs_table_html=ecs_table_html,
        inverter_table_html=inverter_table_html,
        include=include_sections,
    )
    return html


def send_email(to_list: list, cc_list: list, subject: str, html_body: str,
               attachment_bytes: bytes = None, attachment_name: str = None) -> dict:
    """Send an HTML email with optional attachment via SMTP."""
    _load_env()

    smtp_host = os.getenv("SMTP_HOST", "smtp.office365.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USERNAME", "")
    smtp_pass = os.getenv("SMTP_PASSWORD", "")
    email_from = os.getenv("EMAIL_FROM", smtp_user)

    msg = MIMEMultipart("mixed")
    msg["From"] = email_from
    msg["To"] = ", ".join(to_list)
    if cc_list:
        msg["Cc"] = ", ".join(cc_list)
    msg["Subject"] = subject

    msg.attach(MIMEText(html_body, "html"))

    if attachment_bytes and attachment_name:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment_bytes)
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f'attachment; filename="{attachment_name}"')
        msg.attach(part)

    all_recipients = to_list + (cc_list or [])

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            if smtp_user and smtp_pass:
                server.login(smtp_user, smtp_pass)
            server.sendmail(email_from, all_recipients, msg.as_string())

        result = {
            "timestamp": datetime.now().isoformat(),
            "status": "Success",
            "recipients": ", ".join(all_recipients),
            "attachment": attachment_name or "None",
            "notes": f"Sent to {len(all_recipients)} recipients",
        }
    except Exception as e:
        result = {
            "timestamp": datetime.now().isoformat(),
            "status": "Failed",
            "recipients": ", ".join(all_recipients),
            "attachment": attachment_name or "None",
            "notes": str(e),
        }

    _append_log(result)
    return result


def send_daily_report():
    """
    The main function called by the scheduler.
    Loads data, filters for yesterday, builds email (ECS format), sends it.
    """
    config, grid, solar, diesel = load_all()
    unified = build_unified_dataframe(grid, solar, diesel)

    # Last 30 days of data
    cutoff = date.today() - timedelta(days=30)
    day_data = unified[unified["Date"] >= cutoff]
    if day_data.empty:
        day_data = unified  # fallback to all data

    sched_config = _read_scheduler_config()
    to_raw = sched_config.get("to", config.get("email", {}).get("default_to", ""))
    cc_raw = sched_config.get("cc", config.get("email", {}).get("default_cc", ""))
    to_list = [e.strip() for e in to_raw.split(",") if e.strip()]
    cc_list = [e.strip() for e in cc_raw.split(",") if e.strip()]

    subject_template = sched_config.get(
        "subject",
        config.get("email", {}).get("subject", "Daily Energy Report — Noida Campus — {date}"),
    )
    subject = subject_template.replace("{date}", date.today().strftime("%d %b %Y"))
    custom_message = sched_config.get("custom_message", "")
    include_sections = sched_config.get("include_sections", None)

    html_body = build_email_html(day_data, config, custom_message, include_sections)

    # Attachment: custom template or ECS-format xlsx
    uploaded_path = sched_config.get("uploaded_template_path")
    if uploaded_path and os.path.exists(uploaded_path):
        with open(uploaded_path, "rb") as f:
            attachment_bytes = f.read()
        attachment_name = os.path.basename(uploaded_path)
    else:
        attachment_bytes = export_ecs_style_xlsx(day_data)
        attachment_name = f"Energy_Report_ECS_{date.today().strftime('%Y%m%d')}.xlsx"

    return send_email(to_list, cc_list, subject, html_body, attachment_bytes, attachment_name)
