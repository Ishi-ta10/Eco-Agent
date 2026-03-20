"""Quick test suite for the energy dashboard pipeline and emailer."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_ingestion_agent.seed import seed_data_files
from data_ingestion_agent.loader import load_all
from data_ingestion_agent.processor import build_unified_dataframe, compute_overview_kpis
from data_ingestion_agent.exporter import export_unified_xlsx, export_ecs_style_xlsx
from mail_scheduling_agent.emailer import build_email_html, send_email

def test_pipeline():
    print("=== Test 1: Seed data ===")
    seed_data_files()
    print("OK")

    print("=== Test 2: Load data ===")
    cfg, g, s, d = load_all()
    print(f"Grid: {g.shape}, Solar: {s.shape}, Diesel: {d.shape}")
    assert g.shape[0] == 32
    assert s.shape[0] == 32
    assert d.shape[0] == 32
    print("OK")

    print("=== Test 3: Process data ===")
    u = build_unified_dataframe(g, s, d)
    print(f"Unified: {u.shape}, cols: {u.columns.tolist()}")
    assert u.shape[0] == 32
    assert "Grid KWh" in u.columns
    assert "Solar KWh" in u.columns
    assert "Total KWh" in u.columns
    assert "Energy Saving (INR)" in u.columns
    print("OK")

    print("=== Test 4: KPIs ===")
    kpis = compute_overview_kpis(u, cfg)
    print(f"total_kwh={kpis['total_kwh']}, solar_kwh={kpis['solar_kwh']}")
    print(f"avg_temp={kpis['avg_temp']}, total_cost={kpis['total_cost']}")
    print(f"energy_saved={kpis['energy_saved']}, solar_pct={kpis['solar_pct']}")
    assert kpis['avg_temp'] > 0, f"avg_temp should be > 0, got {kpis['avg_temp']}"
    assert kpis['total_kwh'] > 0
    print("OK")

    print("=== Test 5: Exports ===")
    b1 = export_unified_xlsx(u)
    b2 = export_ecs_style_xlsx(u)
    assert len(b1) > 100
    assert len(b2) > 100
    print(f"Unified xlsx: {len(b1)} bytes, ECS xlsx: {len(b2)} bytes")
    print("OK")

    print("=== Test 6: Email HTML ===")
    html = build_email_html(u, cfg, "Test message from pipeline test")
    assert len(html) > 100
    assert "ENERGY CONSUMPTION REPORT" in html
    assert "Test message from pipeline test" in html
    # Check number formatting works
    assert "₹" in html  # currency symbol present
    print(f"HTML: {len(html)} chars")
    print("OK")

    print("\n=== ALL TESTS PASSED ===")
    return cfg, u, html

if __name__ == "__main__":
    cfg, u, html = test_pipeline()
    
    # Save HTML for inspection
    with open("output/test_email.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Saved test email HTML to output/test_email.html")
