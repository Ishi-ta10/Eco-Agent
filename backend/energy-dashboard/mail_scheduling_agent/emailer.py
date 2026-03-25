"""
emailer.py — Build HTML email, send via SMTP, and log results.
Part of the Mail Scheduling Agent.
The email table follows the Electrical Optimization (1) Excel ECS sheet format.
"""

import os
import json
import smtplib
from datetime import datetime, date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

import pandas as pd
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv

from data_ingestion_agent.loader import load_all, load_solar_last7_data
from data_ingestion_agent.processor import build_unified_dataframe, compute_overview_kpis
from data_ingestion_agent.exporter import export_ecs_style_xlsx


DEFAULT_CURRENT_DATE = "2026-03-22"


def _normalize_date_label(value: str) -> str:
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return value
    return parsed.strftime("%d-%m-%Y")


def _filter_current_day_rows(df: pd.DataFrame, current_date: str = DEFAULT_CURRENT_DATE) -> pd.DataFrame:
    if df is None or df.empty or "Date" not in df.columns:
        return df.copy() if isinstance(df, pd.DataFrame) else pd.DataFrame()

    working = df.copy()
    working["_date_norm"] = pd.to_datetime(working["Date"], errors="coerce").dt.strftime("%Y-%m-%d")
    filtered = working[working["_date_norm"] == current_date].drop(columns=["_date_norm"], errors="ignore")
    return filtered


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
    """Build the mail table in the updated format shown in the scheduler UI preview."""
    columns = [
        {
            "header": "Date",
            "sources": ["Date"],
            "align": "left",
            "format": "date",
        },
        {
            "header": "Day",
            "sources": ["Day"],
            "align": "left",
            "format": "text",
        },
        {
            "header": "Time",
            "sources": ["Time"],
            "align": "left",
            "format": "time",
        },
        {
            "header": "Ambient Temperature °C",
            "sources": ["Ambient Temp (°C)", "Ambient Temperature °C"],
            "align": "left",
            "format": "text",
        },
        {
            "header": "Grid Units Consumed (KWh)",
            "sources": ["Grid KWh", "Grid Units Consumed (KWh)"],
            "align": "right",
            "format": "number",
        },
        {
            "header": "Solar Units Consumed(KWh)",
            "sources": ["Solar KWh", "Solar Units Generated (KWh)"],
            "align": "right",
            "format": "number",
        },
        {
            "header": "Total Units Consumed (KWh)",
            "sources": ["Total KWh", "Total Units Consumed (KWh)"],
            "align": "right",
            "format": "number",
        },
        {
            "header": "Total Units Consumed in INR",
            "sources": ["Total Cost (INR)", "Total Units Consumed in INR"],
            "align": "right",
            "format": "currency",
        },
        {
            "header": "Energy Saving in INR",
            "sources": ["Energy Saving (INR)", "Grid Energy Saving (INR)", "Energy Saving in INR"],
            "align": "right",
            "format": "currency",
        },
        {
            "header": "Diesel consumed",
            "sources": ["Diesel consumed", "Fuel Consumed (Litres)", "Diesel Consumed (Litres)"],
            "align": "right",
            "format": "number",
        },
    ]

    def _pick_source(spec):
        for source in spec["sources"]:
            if source in unified.columns:
                return source
        return None

    def _format_cell(value, fmt):
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return ""

        if fmt == "date":
            parsed = pd.to_datetime(value, errors="coerce")
            if pd.isna(parsed):
                return str(value)
            return parsed.strftime("%d-%b-%y")

        if fmt == "time":
            text = str(value)
            if text.startswith("0") and len(text) >= 4 and text[1].isdigit():
                return text[1:]
            return text

        if fmt in {"number", "currency"}:
            numeric = pd.to_numeric(value, errors="coerce")
            if pd.isna(numeric):
                return ""
            rounded = round(float(numeric), 2)
            if abs(rounded - int(rounded)) < 1e-9:
                return str(int(rounded))
            return f"{rounded:.2f}"

        return str(value)

    parts = [
        '<table width="100%" cellpadding="0" cellspacing="0" '
        'style="border-collapse:collapse; font-size:12px; background-color:#2b2b2b; color:#f2f2f2;">'
    ]

    parts.append("<tr>")
    for spec in columns:
        parts.append(
            f'<th style="background-color:#2f2f2f; color:#f7f7f7; padding:8px 8px; '
            f'text-align:left; border:1px solid #5a5a5a; font-size:13px; font-weight:bold;">{spec["header"]}</th>'
        )
    parts.append("</tr>")

    for _, row in unified.iterrows():
        parts.append("<tr>")
        for spec in columns:
            source_col = _pick_source(spec)
            if source_col:
                raw_value = row[source_col]
            elif spec["format"] in {"number", "currency"}:
                raw_value = 0
            else:
                raw_value = ""
            cell_text = _format_cell(raw_value, spec["format"])
            parts.append(
                f'<td style="padding:8px 6px; border:1px solid #555; text-align:{spec["align"]}; '
                f'background-color:#2b2b2b; color:#f2f2f2;">{cell_text}</td>'
            )
        parts.append("</tr>")

    parts.append("</table>")
    return "\n".join(parts)


def _derive_smb_statuses(unified: pd.DataFrame) -> dict:
    """Derive latest SMB status snapshot from unified data."""
    smb_names = ["SMB1", "SMB2", "SMB3", "SMB4", "SMB5"]
    statuses_local = {smb: "unknown" for smb in smb_names}

    if "Inverter Status" not in unified.columns:
        return statuses_local

    status_rows = unified[unified["Inverter Status"].notna()].copy()
    if status_rows.empty:
        return statuses_local

    # Use latest status row so stale historical faults don't dominate the summary.
    status_rows["Date"] = pd.to_datetime(status_rows["Date"], errors="coerce")
    status_rows = status_rows.sort_values(["Date", "Time"], ascending=[False, False])
    latest_status = str(status_rows.iloc[0].get("Inverter Status", "")).strip()
    normalized = latest_status.lower()

    if normalized == "all online":
        return {smb: "online" for smb in smb_names}

    statuses_local = {smb: "online" for smb in smb_names}
    if "fault" in normalized:
        matched_any = False
        for smb in smb_names:
            if smb.lower() in normalized:
                statuses_local[smb] = "fault"
                matched_any = True
        if not matched_any:
            statuses_local = {smb: "fault" for smb in smb_names}

    return statuses_local


def _extract_json_object(text: str) -> dict | None:
    """Best-effort extraction of a JSON object from model text output."""
    if not text:
        return None

    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()

    try:
        parsed = json.loads(cleaned)
        return parsed if isinstance(parsed, dict) else None
    except Exception:
        pass

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None

    snippet = cleaned[start : end + 1]
    try:
        parsed = json.loads(snippet)
        return parsed if isinstance(parsed, dict) else None
    except Exception:
        return None


def _coerce_bullet_list(value, fallback: list[str]) -> list[str]:
    if isinstance(value, list):
        items = [str(v).strip() for v in value if str(v).strip()]
        return items[:6] if items else fallback
    if isinstance(value, str):
        lines = []
        for line in value.splitlines():
            item = line.strip().lstrip("-*").strip()
            if item:
                lines.append(item)
        return lines[:6] if lines else fallback
    return fallback


def _generate_ai_summary(unified: pd.DataFrame, kpis: dict, smb_statuses: dict, diesel_total: float, current_date: str = DEFAULT_CURRENT_DATE) -> dict | None:
    """Generate insights/recommendations from Groq SDK chat completions API based on current day data."""
    _load_env()
    api_key = (os.getenv("GROQ_API_KEY") or os.getenv("GROK_API_KEY") or "").strip()
    if not api_key:
        return None

    try:
        from groq import Groq
    except Exception as err:
        print(f"[WARN] Groq SDK not available: {err}")
        return None

    configured_model = (os.getenv("GROQ_MODEL") or "llama3-70b-8192").strip()
    model_candidates = []
    for model_name in [
        configured_model,
        "llama3-70b-8192",
        "llama-3.1-8b-instant",
        "llama-3.3-70b-versatile",
        "groq/compound-mini",
    ]:
        if model_name and model_name not in model_candidates:
            model_candidates.append(model_name)

    client = Groq(api_key=api_key)

    # Filter data to current day only for insights
    current_day_data = _filter_current_day_rows(unified, current_date)

    grid_col = "Grid KWh" if "Grid KWh" in current_day_data.columns else "Grid Units Consumed (KWh)"
    solar_col = "Solar KWh" if "Solar KWh" in current_day_data.columns else "Solar Units Generated (KWh)"

    # Calculate current day metrics
    current_day_grid = float(pd.to_numeric(current_day_data.get(grid_col, 0), errors="coerce").fillna(0).sum()) if grid_col in current_day_data.columns else 0.0
    current_day_solar = float(pd.to_numeric(current_day_data.get(solar_col, 0), errors="coerce").fillna(0).sum()) if solar_col in current_day_data.columns else 0.0
    current_day_total = current_day_grid + current_day_solar
    current_day_solar_pct = (current_day_solar / current_day_total * 100) if current_day_total > 0 else 0.0

    diesel_col = "Diesel consumed" if "Diesel consumed" in current_day_data.columns else "Fuel Consumed (Litres)"
    current_day_diesel = float(pd.to_numeric(current_day_data.get(diesel_col, 0), errors="coerce").fillna(0).sum()) if diesel_col in current_day_data.columns else 0.0

    payload = {
        "current_date": current_date,
        "current_day_summary": {
            "total_kwh": float(current_day_total),
            "grid_kwh": float(current_day_grid),
            "solar_kwh": float(current_day_solar),
            "solar_pct": float(current_day_solar_pct),
            "diesel_consumed": float(current_day_diesel),
        },
        "inverter_status": smb_statuses,
        "current_day_records": (
            current_day_data[
                [
                    c
                    for c in [
                        "Date",
                        "Day",
                        "Time",
                        "Grid KWh",
                        "Solar KWh",
                        "Total KWh",
                        "Energy Saving (INR)",
                        "Diesel consumed",
                        "Inverter Status",
                    ]
                    if c in current_day_data.columns
                ]
            ]
            .fillna(0)
            .to_dict(orient="records")
        ),
    }

    user_prompt = (
        f"Using the given energy consumption data FOR {current_date} (current day), generate insights and recommendations.\n\n"
        "Interpret total energy consumption strictly as Grid + Solar only. Do not include diesel in total energy consumed.\n\n"
        "This may include:\n"
        "- Comparison of the energy generated/consumed source wise (Grid vs Solar)\n"
        "- Current day solar contribution percentage\n"
        "- Status of the inverters (active/inactive/faulted)\n"
        "- Diesel consumption patterns\n"
        "- RECOMMENDATIONS for optimizing the performance (e.g., cleaning may be needed, hardware failure issues, load management)\n\n"
        "CRITICAL REQUIREMENTS:\n"
        f"1. ALL insights should mention they are 'as of today' or 'for today' or include the date '{current_date}, any of the three not all'\n"
        "2. Base insights ONLY on the current day data provided\n"
        "3. DO NOT HALLUCINATE - insights and recommendations should STRICTLY be based on the information provided\n"
        "4. Use specific numbers from the data when available\n\n"
        "GUIDELINES: Return concise, actionable insights that are clearly marked as today's observations."
    )

    last_err = None
    for model in model_candidates:
        try:
            response = client.chat.completions.create(
                model=model,
                temperature=0.2,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an intelligent agent.",
                    },
                    {
                        "role": "user",
                        "content": (
                            f"{user_prompt}\n\nSOURCE OF KNOWLEDGE:\n{json.dumps(payload, default=str)}\n\n"
                            "Return strict JSON only with this schema: "
                            '{"insights":["..."],"recommendations":["..."]}. '
                            "Do not include markdown or extra keys."
                        ),
                    },
                ],
            )

            content = ""
            if getattr(response, "choices", None):
                content = response.choices[0].message.content or ""

            parsed = _extract_json_object(content)
            if not parsed:
                continue

            insights = _coerce_bullet_list(parsed.get("insights"), [])
            recommendations = _coerce_bullet_list(parsed.get("recommendations"), [])
            if not insights and not recommendations:
                continue

            return {
                "insights": insights,
                "recommendations": recommendations,
            }
        except Exception as err:
            last_err = err
            continue

    if last_err is not None:
        print(f"[WARN] AI summary generation failed: {last_err}")
    return None


def generate_smart_summary(unified: pd.DataFrame, kpis: dict, current_date: str = DEFAULT_CURRENT_DATE) -> dict:
    """Build smart insights/recommendations using LLM with deterministic fallback based on current day data."""
    # Filter to current day data for insights
    current_day_data = _filter_current_day_rows(unified, current_date)

    smb_statuses = _derive_smb_statuses(current_day_data)
    total_inverters = len(smb_statuses) if smb_statuses else 5
    fault_count = max(total_inverters - sum(1 for s in smb_statuses.values() if s == "online"), 0)

    diesel_col = None
    for candidate in ["Diesel consumed", "Fuel Consumed (Litres)"]:
        if candidate in current_day_data.columns:
            diesel_col = candidate
            break
    diesel_total = (
        float(pd.to_numeric(current_day_data[diesel_col], errors="coerce").fillna(0).sum())
        if diesel_col
        else 0.0
    )

    # Calculate current day solar contribution
    grid_col = "Grid KWh" if "Grid KWh" in current_day_data.columns else "Grid Units Consumed (KWh)"
    solar_col = "Solar KWh" if "Solar KWh" in current_day_data.columns else "Solar Units Generated (KWh)"

    current_day_grid = float(pd.to_numeric(current_day_data.get(grid_col, 0), errors="coerce").fillna(0).sum()) if grid_col in current_day_data.columns else 0.0
    current_day_solar = float(pd.to_numeric(current_day_data.get(solar_col, 0), errors="coerce").fillna(0).sum()) if solar_col in current_day_data.columns else 0.0
    current_day_total = current_day_grid + current_day_solar
    solar_pct = (current_day_solar / current_day_total * 100) if current_day_total > 0 else 0.0

    insights = []
    recommendations = []

    if fault_count > 0:
        insights.append(f"As of today ({current_date}), {fault_count} of {total_inverters} inverters are not online.")
        recommendations.append("Inspect faulted inverter lines and restore all SMB units to online status.")
    else:
        insights.append(f"As of today ({current_date}), all {total_inverters} inverters are online and available for generation.")
        recommendations.append("Maintain current inverter health with preventive checks.")

    insights.append(f"Solar contribution for today ({current_date}) is {solar_pct:.1f}% of total energy consumption.")
    if solar_pct < 20:
        recommendations.append("Increase panel cleaning frequency and shift daytime loads toward solar generation.")

    if diesel_total > 0:
        insights.append(f"Diesel consumption for today ({current_date}) is {diesel_total:.1f} litres.")
        recommendations.append("Analyze DG usage intervals and reduce generator dependency where possible.")
    else:
        insights.append(f"No diesel consumption is recorded for today ({current_date}).")

    ai_summary = _generate_ai_summary(current_day_data, kpis, smb_statuses, diesel_total, current_date)
    if ai_summary:
        insights = _coerce_bullet_list(ai_summary.get("insights"), insights)
        recommendations = _coerce_bullet_list(ai_summary.get("recommendations"), recommendations)
        source = "llm"
    else:
        source = "fallback"

    # Enforce current-day context in every line for email readability and correctness.
    def _ensure_current_context(items: list[str]) -> list[str]:
        normalized = []
        for text in items:
            value = str(text or "").strip()
            if not value:
                continue
            lower = value.lower()
            mentions_today = "today" in lower
            mentions_date = current_date in value
            if not mentions_today and not mentions_date:
                value = f"As of today ({current_date}), {value[0].lower() + value[1:] if len(value) > 1 else value.lower()}"
            normalized.append(value)
        return normalized

    insights = _ensure_current_context(insights)
    recommendations = _ensure_current_context(recommendations)

    return {
        "insights": insights,
        "recommendations": recommendations,
        "source": source,
    }


def _build_executive_summary_html(unified: pd.DataFrame, kpis: dict, current_date: str = DEFAULT_CURRENT_DATE) -> str:
    """Create executive summary with insights and recommendations based on current day data."""
    summary = generate_smart_summary(unified, kpis, current_date)
    insights = summary.get("insights", [])
    recommendations = summary.get("recommendations", [])

    parts = [
        '<table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse; background:#F8FBFF; border:1px solid #D7E4F2;">',
        '<tr><td style="padding:12px 14px; font-size:13px; color:#1F3864; font-weight:bold;">Executive Summary</td></tr>',
        f'<tr><td style="padding:0 14px 10px 14px; font-size:11px; color:#5a6f85;">All insights and recommendations are based on current date: {_normalize_date_label(current_date)}</td></tr>',
        '<tr><td style="padding:0 14px 10px 14px;">',
        '<div style="font-size:12px; color:#2f2f2f; font-weight:bold; margin-bottom:4px;">Insights</div>',
        '<ul style="margin:0 0 10px 18px; padding:0; font-size:12px; color:#333;">',
    ]

    for item in insights:
        parts.append(f"<li style=\"margin:0 0 4px 0;\">{item}</li>")

    parts.extend([
        '</ul>',
        '<div style="font-size:12px; color:#2f2f2f; font-weight:bold; margin-bottom:4px;">Recommendations</div>',
        '<ul style="margin:0 0 2px 18px; padding:0; font-size:12px; color:#333;">',
    ])

    for item in recommendations:
        parts.append(f"<li style=\"margin:0 0 4px 0;\">{item}</li>")

    parts.extend([
        '</ul>',
        '</td></tr>',
        '</table>',
    ])

    return "\n".join(parts)


def _build_inverter_table_html(unified: pd.DataFrame) -> str:
    """Build inverter status as card-style blocks for email-safe rendering."""
    smb_names = ["SMB1", "SMB2", "SMB3", "SMB4", "SMB5"]
    statuses = _derive_smb_statuses(unified)

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
                     include_sections: dict = None, current_date: str = DEFAULT_CURRENT_DATE) -> str:
    """
    Render the Jinja2 email template.
    Dynamic HTML tables are pre-built in Python so the template has
    no Jinja2 expressions inside style attributes (avoids VS Code linter warnings).
    """
    templates_dir = os.path.join(_project_root(), "mail_scheduling_agent", "templates")
    env = Environment(loader=FileSystemLoader(templates_dir), autoescape=False)
    template = env.get_template("email_body.html")

    current_day_unified = _filter_current_day_rows(unified, current_date)
    kpi_source = current_day_unified if not current_day_unified.empty else unified
    kpis = compute_overview_kpis(kpi_source, config)

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
    executive_summary_html = _build_executive_summary_html(kpi_source, kpis, current_date)

    if include_sections is None:
        include_sections = {
            "executive_summary": True,
            "summary_kpis": True,
            "unified_table": True,
            "grid_summary": True,
            "solar_summary": True,
            "diesel_summary": True,
            "inverter_status": True,
        }

    html = template.render(
        report_date=_normalize_date_label(current_date),
        current_date_display=_normalize_date_label(current_date),
        custom_message=custom_message,
        kpi_total_kwh=kpi_total_kwh,
        kpi_solar_kwh=kpi_solar_kwh,
        kpi_solar_pct=kpi_solar_pct,
        kpi_total_cost=kpi_total_cost,
        kpi_energy_saved=kpi_energy_saved,
        kpi_avg_temp=kpi_avg_temp,
        executive_summary_html=executive_summary_html,
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

    # Keep email data aligned to the same 7-day date set shown in dashboard tabs.
    day_data = unified.copy()
    try:
        solar_last7_df = load_solar_last7_data(config)
        if len(solar_last7_df) > 0 and "Date" in solar_last7_df.columns:
            allowed_dates = set(pd.to_datetime(solar_last7_df["Date"], errors="coerce").dt.normalize().dropna())
            unified_dates = pd.to_datetime(day_data["Date"], errors="coerce").dt.normalize()
            day_data = day_data[unified_dates.isin(allowed_dates)].copy()
    except Exception as err:
        print(f"[WARN] Could not align email report to dashboard 7-day date set: {err}")

    # Fallback to latest 7 dates if alignment source is unavailable.
    if day_data.empty and len(unified) > 0:
        working = unified.copy()
        working["_date_norm"] = pd.to_datetime(working["Date"], errors="coerce").dt.normalize()
        unique_dates = sorted([d for d in working["_date_norm"].dropna().unique()])
        keep_dates = set(unique_dates[-7:])
        day_data = working[working["_date_norm"].isin(keep_dates)].drop(columns=["_date_norm"], errors="ignore")

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

    current_date = DEFAULT_CURRENT_DATE
    html_body = build_email_html(day_data, config, custom_message, include_sections, current_date)

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
