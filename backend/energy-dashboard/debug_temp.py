"""Debug temperature column."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_ingestion_agent.loader import load_all
from data_ingestion_agent.processor import build_unified_dataframe

cfg, g, s, d = load_all()
u = build_unified_dataframe(g, s, d)

# Find the ambient temp column
temp_cols = [c for c in u.columns if 'Ambient' in c or 'Temp' in c or 'temp' in c.lower()]
print(f"Temp columns: {temp_cols}")

for col in temp_cols:
    print(f"\nColumn: '{col}' (repr: {repr(col)})")
    print(f"  dtype: {u[col].dtype}")
    print(f"  first 5 values: {u[col].head(5).tolist()}")
    print(f"  first value type: {type(u[col].iloc[0])}")
    val = u[col].iloc[0]
    print(f"  repr: {repr(val)}")

# Try parsing manually
val = u[temp_cols[0]].iloc[0]
print(f"\nParsing test on value: {repr(val)}")
if isinstance(val, str):
    parts = [p.strip() for p in val.split("-") if p.strip()]
    print(f"  Split parts: {parts}")
    if len(parts) == 2:
        avg = (float(parts[0]) + float(parts[1])) / 2
        print(f"  Average: {avg}")
else:
    print(f"  Not a string! It's {type(val)}, value={val}")
