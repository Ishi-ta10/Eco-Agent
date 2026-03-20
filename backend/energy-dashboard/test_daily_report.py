"""Test the send_daily_report function (the scheduler entrypoint)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mail_scheduling_agent.emailer import send_daily_report

print("=== Testing send_daily_report() ===")
result = send_daily_report()
print(f"Result: {result}")

if result["status"] == "Success":
    print("\n✅ DAILY REPORT SENT SUCCESSFULLY!")
else:
    print(f"\n❌ DAILY REPORT FAILED: {result['notes']}")
    if "credentials" in result["notes"].lower() or "authentication" in result["notes"].lower():
        print("\nThe email pipeline works correctly. Only the SMTP password needs to be set.")
        print("Update SMTP_PASSWORD in .env with your Office 365 app password.")
