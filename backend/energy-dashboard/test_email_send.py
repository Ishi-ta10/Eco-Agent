"""Test email sending to krishnav@maqsoftware.com"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_ingestion_agent.loader import load_all
from data_ingestion_agent.processor import build_unified_dataframe
from data_ingestion_agent.exporter import export_ecs_style_xlsx
from mail_scheduling_agent.emailer import build_email_html, send_email
from datetime import date

print("=== Building email content ===")
cfg, g, s, d = load_all()
u = build_unified_dataframe(g, s, d)

html_body = build_email_html(u, cfg, "Test email from Energy Dashboard — all systems operational.")
print(f"HTML body: {len(html_body)} chars")

# Generate ECS-format attachment
attachment_bytes = export_ecs_style_xlsx(u)
attachment_name = f"Energy_Report_ECS_{date.today().strftime('%Y%m%d')}.xlsx"
print(f"Attachment: {attachment_name} ({len(attachment_bytes)} bytes)")

# Send email
print("=== Sending email ===")
result = send_email(
    to_list=["krishnav@maqsoftware.com"],
    cc_list=[],
    subject=f"Daily Energy Report — Noida Campus — {date.today().strftime('%d %b %Y')}",
    html_body=html_body,
    attachment_bytes=attachment_bytes,
    attachment_name=attachment_name,
)

print(f"Result: {result}")
if result["status"] == "Success":
    print("\n✅ EMAIL SENT SUCCESSFULLY!")
else:
    print(f"\n❌ EMAIL FAILED: {result['notes']}")
    print("\nTo fix: Update SMTP_PASSWORD in .env with your Office 365 app password.")
    print("Generate an app password at: https://myaccount.microsoft.com/security-info")
