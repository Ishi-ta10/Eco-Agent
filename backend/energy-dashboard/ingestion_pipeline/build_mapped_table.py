import json
import csv
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INPUT_CAPTURED = BASE_DIR / "captured_api_data.json"
INPUT_30DAY = BASE_DIR / "filtered_30day_data.json"
INPUT_7DAY = BASE_DIR / "filtered_7day_values.json"
INPUT_SOLAR = BASE_DIR / "filtered_solar_panel_data.json"
OUTPUT_TABLE = BASE_DIR / "mapped_ingestion_table.json"
OUTPUT_TABLE_CSV = BASE_DIR / "mapped_ingestion_table.csv"


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def parse_date(date_str: str) -> str:
    return datetime.strptime(date_str, "%Y-%m-%d").strftime("%A")


def _safe_float(value, default=0.0) -> float:
    try:
        if value is None:
            return float(default)
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def build_table_rows(captured_data: list, data_30day: dict, data_7day: dict, solar_data: dict) -> list[dict]:
    daily_values = data_7day.get("daily_values", {})
    solar_timeline = solar_data.get("daily_generation_timeline", {})

    rows = []
    for date_key in sorted(daily_values.keys()):
        date_block = daily_values.get(date_key, {})
        records = date_block.get("records", [])

        solar_day = solar_timeline.get(date_key, {})

        solar_daily_kwh = _safe_float(solar_day.get("generation_kwh"), 0)

        for record in records:
            value_wh = _safe_float(record.get("value", 0), 0)
            row = {
                "Date": date_key,
                "Day": parse_date(date_key),
                "Time": record.get("time"),
                "Start Value": record.get("start_value"),
                "End Value": record.get("end_value"),
                "Generation Interval (Wh)": value_wh,
                "Generation Interval (kWh)": round(value_wh / 1000, 3),
                "Daily Generation Solar (kWh)": solar_daily_kwh,
            }
            rows.append(row)

    rows.sort(key=lambda item: (item["Date"], item["Time"] or ""))
    return rows


def write_csv(path: Path, rows: list[dict], columns: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    captured_data = load_json(INPUT_CAPTURED)
    data_30day = load_json(INPUT_30DAY)
    data_7day = load_json(INPUT_7DAY)
    solar_data = load_json(INPUT_SOLAR)

    columns = [
        "Date",
        "Day",
        "Time",
        "Start Value",
        "End Value",
        "Generation Interval (Wh)",
        "Generation Interval (kWh)",
        "Daily Generation Solar (kWh)",
    ]

    mapped = {
        "table_info": {
            "created_at": datetime.now().isoformat(),
            "source_files": [
                INPUT_CAPTURED.name,
                INPUT_30DAY.name,
                INPUT_7DAY.name,
                INPUT_SOLAR.name,
            ],
            "row_count": 0,
            "columns": columns,
        },
        "summary": solar_data.get("generation_summary", {}),
        "table": [],
    }

    rows = build_table_rows(captured_data, data_30day, data_7day, solar_data)
    mapped["table"] = rows
    mapped["table_info"]["row_count"] = len(rows)

    with OUTPUT_TABLE.open("w", encoding="utf-8") as f:
        json.dump(mapped, f, indent=2)

    write_csv(OUTPUT_TABLE_CSV, rows, columns)

    print(f"Mapped table written: {OUTPUT_TABLE.name}")
    print(f"Mapped table CSV written: {OUTPUT_TABLE_CSV.name}")
    print(f"Rows: {len(rows)}")
    if rows:
        print("Sample rows:")
        for row in rows[:5]:
            print(
                f"  {row['Date']} {row['Time']} | "
                f"{row['Generation Interval (Wh)']} Wh ({row['Generation Interval (kWh)']} kWh)"
            )


if __name__ == "__main__":
    main()
