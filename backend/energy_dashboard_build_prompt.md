# Build Prompt — Energy Consumption Unified Dashboard & Scheduled Report Agent
## Streamlit Application · Phase 1 · Noida Campus · Energy Optimization Agent

---

## What you are building

A **Streamlit multi-page web application** that serves as the unified energy dashboard for the Noida campus. It ingests data from three energy sources — Grid (Excel), Solar (Suryalogix/API), and Diesel Generator (Excel) — normalises them into a single data model, displays a unified live dashboard with source-specific tabs, and runs a configurable scheduled job that curates and sends a formatted HTML email report every morning.

The app has five tabs:
1. **Overview** — unified dashboard across all three sources
2. **Grid** — Grid-specific data and metrics
3. **Solar** — Solar-specific data and metrics
4. **Diesel** — Diesel-specific data and metrics
5. **Job Scheduler** — configure, edit, and trigger the scheduled email job

---

## Dummy data files — seed these three files on first run

Create the following three CSV files in `./data/` if they do not already exist. These simulate the real data sources for development and demo purposes.

### `./data/grid_data.csv`
```
Date,Day,Time,Ambient Temperature °C,Grid Units Consumed (KWh),Cost per Unit (INR),Total Cost (INR)
2026-03-13,Thursday,08:00,29.5,210.4,7.5,1578.0
2026-03-13,Thursday,10:00,31.2,198.7,7.5,1490.25
2026-03-13,Thursday,12:00,33.8,225.1,7.5,1688.25
2026-03-13,Thursday,14:00,35.1,240.3,7.5,1802.25
2026-03-13,Thursday,16:00,34.6,215.8,7.5,1618.5
2026-03-13,Thursday,18:00,32.0,188.2,7.5,1411.5
2026-03-14,Friday,08:00,28.9,205.6,7.5,1542.0
2026-03-14,Friday,10:00,30.5,192.3,7.5,1442.25
2026-03-14,Friday,12:00,32.7,218.9,7.5,1641.75
2026-03-14,Friday,14:00,34.2,235.7,7.5,1767.75
2026-03-14,Friday,16:00,33.8,210.4,7.5,1578.0
2026-03-14,Friday,18:00,31.4,185.6,7.5,1392.0
2026-03-15,Saturday,08:00,27.3,180.2,7.5,1351.5
2026-03-15,Saturday,10:00,29.1,168.5,7.5,1263.75
2026-03-15,Saturday,12:00,31.4,195.3,7.5,1464.75
2026-03-15,Saturday,14:00,33.0,210.8,7.5,1581.0
2026-03-15,Saturday,16:00,32.5,198.6,7.5,1489.5
2026-03-15,Saturday,18:00,30.2,172.4,7.5,1293.0
2026-03-16,Sunday,08:00,26.8,145.3,7.5,1089.75
2026-03-16,Sunday,10:00,28.4,132.7,7.5,995.25
2026-03-16,Sunday,12:00,30.6,158.9,7.5,1191.75
2026-03-16,Sunday,14:00,32.1,175.4,7.5,1315.5
2026-03-16,Sunday,16:00,31.7,162.8,7.5,1221.0
2026-03-16,Sunday,18:00,29.5,138.5,7.5,1038.75
2026-03-17,Monday,08:00,29.2,212.5,7.5,1593.75
2026-03-17,Monday,10:00,31.8,225.8,7.5,1693.5
2026-03-17,Monday,12:00,34.5,248.3,7.5,1862.25
2026-03-17,Monday,14:00,36.2,262.1,7.5,1965.75
2026-03-17,Monday,16:00,35.8,240.5,7.5,1803.75
2026-03-17,Monday,18:00,33.1,218.9,7.5,1641.75
2026-03-18,Tuesday,08:00,30.1,215.2,7.5,1614.0
2026-03-18,Tuesday,10:00,32.4,228.6,7.5,1714.5
2026-03-18,Tuesday,12:00,35.0,251.4,7.5,1885.5
2026-03-18,Tuesday,14:00,36.8,268.7,7.5,2015.25
2026-03-18,Tuesday,16:00,36.2,245.3,7.5,1839.75
2026-03-18,Tuesday,18:00,33.7,222.1,7.5,1665.75
```

### `./data/solar_data.csv`
```
Date,Day,Time,Solar Units Generated (KWh),Inverter Status,SMB1 (KWh),SMB2 (KWh),SMB3 (KWh),SMB4 (KWh),SMB5 (KWh),Plant Capacity (KW),Irradiance (W/m²)
2026-03-13,Thursday,08:00,45.2,All Online,9.8,9.5,9.2,8.9,7.8,598,320
2026-03-13,Thursday,10:00,112.8,All Online,24.5,23.8,22.9,22.1,19.5,598,650
2026-03-13,Thursday,12:00,168.5,All Online,36.8,35.9,34.5,33.2,28.1,598,820
2026-03-13,Thursday,14:00,155.3,SMB3 Fault,36.2,35.4,0.0,42.8,40.9,598,780
2026-03-13,Thursday,16:00,98.4,SMB3 Fault,22.8,22.1,0.0,27.6,25.9,598,520
2026-03-13,Thursday,18:00,28.6,SMB3 Fault,6.8,6.5,0.0,8.2,7.1,598,180
2026-03-14,Friday,08:00,42.5,All Online,9.2,9.0,8.7,8.4,7.2,598,310
2026-03-14,Friday,10:00,108.3,All Online,23.5,22.9,22.1,21.4,18.4,598,625
2026-03-14,Friday,12:00,162.7,All Online,35.5,34.7,33.4,32.2,26.9,598,800
2026-03-14,Friday,14:00,149.8,All Online,32.8,32.1,30.9,29.8,24.2,598,755
2026-03-14,Friday,16:00,94.2,All Online,20.6,20.1,19.4,18.7,15.4,598,498
2026-03-14,Friday,18:00,25.4,All Online,5.6,5.4,5.2,5.0,4.2,598,162
2026-03-15,Saturday,08:00,38.2,All Online,8.4,8.1,7.8,7.5,6.4,598,282
2026-03-15,Saturday,10:00,95.6,All Online,20.9,20.4,19.6,18.9,15.8,598,558
2026-03-15,Saturday,12:00,143.8,All Online,31.4,30.7,29.6,28.5,23.6,598,712
2026-03-15,Saturday,14:00,132.5,All Online,29.0,28.3,27.2,26.2,21.8,598,672
2026-03-15,Saturday,16:00,84.3,All Online,18.4,18.0,17.3,16.7,13.9,598,446
2026-03-15,Saturday,18:00,22.1,All Online,4.8,4.7,4.5,4.4,3.7,598,145
2026-03-16,Sunday,08:00,12.4,All Online,2.7,2.6,2.5,2.4,2.2,598,95
2026-03-16,Sunday,10:00,28.5,All Online,6.2,6.1,5.8,5.6,4.8,598,215
2026-03-16,Sunday,12:00,42.8,All Online,9.4,9.1,8.8,8.5,7.0,598,318
2026-03-16,Sunday,14:00,38.2,All Online,8.4,8.1,7.8,7.5,6.4,598,285
2026-03-16,Sunday,16:00,22.5,All Online,4.9,4.8,4.6,4.4,3.8,598,172
2026-03-16,Sunday,18:00,6.2,All Online,1.4,1.3,1.2,1.2,1.1,598,52
2026-03-17,Monday,08:00,48.5,All Online,10.6,10.3,9.9,9.6,8.1,598,348
2026-03-17,Monday,10:00,121.4,All Online,26.5,25.9,24.9,24.0,20.1,598,695
2026-03-17,Monday,12:00,181.2,All Online,39.6,38.6,37.2,35.8,30.0,598,878
2026-03-17,Monday,14:00,167.5,All Online,36.6,35.7,34.4,33.2,27.6,598,835
2026-03-17,Monday,16:00,105.8,All Online,23.1,22.6,21.8,21.0,17.3,598,558
2026-03-17,Monday,18:00,30.4,All Online,6.6,6.5,6.2,6.0,5.1,598,195
2026-03-18,Tuesday,08:00,50.2,All Online,11.0,10.7,10.3,9.9,8.3,598,362
2026-03-18,Tuesday,10:00,125.6,All Online,27.4,26.8,25.8,24.9,20.7,598,718
2026-03-18,Tuesday,12:00,187.3,All Online,40.9,39.9,38.5,37.1,30.9,598,908
2026-03-18,Tuesday,14:00,173.1,All Online,37.8,36.9,35.6,34.3,28.5,598,862
2026-03-18,Tuesday,16:00,109.5,All Online,23.9,23.4,22.5,21.7,18.0,598,578
2026-03-18,Tuesday,18:00,31.8,All Online,6.9,6.8,6.5,6.2,5.4,598,202
```

### `./data/diesel_data.csv`
```
Date,Day,Time,DG Units Consumed (KWh),DG Runtime (hrs),Fuel Consumed (Litres),Cost per Unit (INR),Total Cost (INR),DG ID
2026-03-13,Thursday,08:00,0.0,0.0,0.0,30.0,0.0,DG1
2026-03-13,Thursday,10:00,0.0,0.0,0.0,30.0,0.0,DG1
2026-03-13,Thursday,12:00,0.0,0.0,0.0,30.0,0.0,DG1
2026-03-13,Thursday,14:00,45.8,1.0,12.5,30.0,1374.0,DG2
2026-03-13,Thursday,16:00,0.0,0.0,0.0,30.0,0.0,DG1
2026-03-13,Thursday,18:00,0.0,0.0,0.0,30.0,0.0,DG1
2026-03-14,Friday,08:00,0.0,0.0,0.0,30.0,0.0,DG1
2026-03-14,Friday,10:00,0.0,0.0,0.0,30.0,0.0,DG1
2026-03-14,Friday,12:00,0.0,0.0,0.0,30.0,0.0,DG1
2026-03-14,Friday,14:00,0.0,0.0,0.0,30.0,0.0,DG1
2026-03-14,Friday,16:00,0.0,0.0,0.0,30.0,0.0,DG1
2026-03-14,Friday,18:00,0.0,0.0,0.0,30.0,0.0,DG1
2026-03-15,Saturday,08:00,0.0,0.0,0.0,30.0,0.0,DG1
2026-03-15,Saturday,10:00,0.0,0.0,0.0,30.0,0.0,DG1
2026-03-15,Saturday,12:00,0.0,0.0,0.0,30.0,0.0,DG1
2026-03-15,Saturday,14:00,0.0,0.0,0.0,30.0,0.0,DG1
2026-03-15,Saturday,16:00,0.0,0.0,0.0,30.0,0.0,DG1
2026-03-15,Saturday,18:00,0.0,0.0,0.0,30.0,0.0,DG1
2026-03-16,Sunday,08:00,0.0,0.0,0.0,30.0,0.0,DG1
2026-03-16,Sunday,10:00,0.0,0.0,0.0,30.0,0.0,DG1
2026-03-16,Sunday,12:00,0.0,0.0,0.0,30.0,0.0,DG1
2026-03-16,Sunday,14:00,0.0,0.0,0.0,30.0,0.0,DG1
2026-03-16,Sunday,16:00,0.0,0.0,0.0,30.0,0.0,DG1
2026-03-16,Sunday,18:00,0.0,0.0,0.0,30.0,0.0,DG1
2026-03-17,Monday,08:00,0.0,0.0,0.0,30.0,0.0,DG1
2026-03-17,Monday,10:00,0.0,0.0,0.0,30.0,0.0,DG1
2026-03-17,Monday,12:00,0.0,0.0,0.0,30.0,0.0,DG1
2026-03-17,Monday,14:00,0.0,0.0,0.0,30.0,0.0,DG1
2026-03-17,Monday,16:00,0.0,0.0,0.0,30.0,0.0,DG1
2026-03-17,Monday,18:00,0.0,0.0,0.0,30.0,0.0,DG1
2026-03-18,Tuesday,08:00,0.0,0.0,0.0,30.0,0.0,DG1
2026-03-18,Tuesday,10:00,0.0,0.0,0.0,30.0,0.0,DG1
2026-03-18,Tuesday,12:00,62.4,1.5,17.2,30.0,1872.0,DG2
2026-03-18,Tuesday,14:00,78.5,2.0,21.8,30.0,2355.0,DG3
2026-03-18,Tuesday,16:00,0.0,0.0,0.0,30.0,0.0,DG1
2026-03-18,Tuesday,18:00,0.0,0.0,0.0,30.0,0.0,DG1
```

---

## Data processing — unified model

After loading all three CSVs, merge them on `Date + Day + Time` into a single master DataFrame with these columns:

```
Date | Day | Time | Ambient Temp (°C) |
Grid KWh | Solar KWh | Diesel KWh | Total KWh |
Grid Cost (INR) | Diesel Cost (INR) | Solar Cost (INR) [= 0] |
Total Cost (INR) | Energy Saving (INR) | Solar % | Source
```

**Derived columns:**
- `Total KWh` = Grid KWh + Solar KWh + Diesel KWh
- `Solar Cost (INR)` = 0 always (self-generated)
- `Total Cost (INR)` = Grid Cost + Diesel Cost
- `Energy Saving (INR)` = Solar KWh × 7.5 (what grid would have cost)
- `Solar %` = (Solar KWh / Total KWh) × 100, rounded to 1 decimal

---

## App structure — five tabs

```python
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview", "Grid", "Solar", "Diesel", "Job Scheduler"
])
```

---

### Tab 1 — Overview (unified dashboard)

**Top row — six KPI metric cards using `st.columns(6)`:**

| Card | Value | Delta hint |
|---|---|---|
| Total consumption | `{value} KWh` | vs previous day |
| Solar generated | `{value} KWh` | vs daily target (3,000 units) |
| Solar contribution | `{value}%` | vs previous day |
| Total cost | `₹{value:,.0f}` | vs previous day |
| Energy saved | `₹{value:,.0f}` | — |
| Avg temperature | `{value:.1f}°C` | — |

Use `st.metric()` with `delta` for cards that have a day-over-day comparison.

**Date range filter** — `st.date_input("Select date range", value=(min_date, max_date))` above the charts. All charts and the table below respond to this filter.

**Row 2 — two charts side by side using `st.columns(2)`:**

Left chart — **Daily energy mix bar chart** (stacked):
- X axis: Date
- Bars: Grid KWh (blue), Solar KWh (amber), Diesel KWh (red)
- Use `st.bar_chart()` or plotly `go.Bar` with `barmode="stack"`

Right chart — **Source cost comparison line chart**:
- X axis: Date
- Lines: Grid cost (INR), Diesel cost (INR), Energy saved (INR)
- Use plotly `go.Scatter`

**Row 3 — full unified data table:**
- `st.dataframe()` with all columns, height=350
- Download button: **Download unified report** → `Unified_Energy_Report_{YYYYMMDD}.xlsx`

---

### Tab 2 — Grid

**Top row — four KPI cards:**
- Total Grid KWh consumed (selected period)
- Total Grid cost (INR)
- Peak consumption time (time slot with highest Grid KWh)
- Average Grid KWh per slot

**Chart — Grid consumption by time of day:**
- X axis: Time slot
- Y axis: Avg Grid KWh across all dates
- Bar chart using plotly

**Data table:** Grid-only rows with columns: Date, Day, Time, Ambient Temp, Grid KWh, Cost per Unit, Total Cost
Download button: **Download Grid data**

---

### Tab 3 — Solar

**Top row — five KPI cards:**
- Total Solar KWh generated (selected period)
- Daily average vs 3,000 unit target (show as %)
- Peak generation time
- Total energy saved (INR)
- Inverter fault events (count of rows where Inverter Status ≠ "All Online")

**Inverter status indicator:**
Display a row of five coloured squares for SMB1–SMB5 using `st.columns(5)`.
- Green square if all readings for that SMB are > 0
- Red square if any reading for that SMB is 0 (indicates fault)
Label each: `SMB1`, `SMB2`, etc.

**Chart — Solar generation by day:**
- Area chart: Solar KWh per day
- Overlay horizontal dashed line at daily target (3,000 ÷ 6 time slots per day × filter days)

**Chart — Inverter contribution breakdown:**
- Stacked bar chart: SMB1–SMB5 contribution per day

**Data table:** Solar-only rows with all solar columns
Download button: **Download Solar data**

---

### Tab 4 — Diesel

**Top row — four KPI cards:**
- Total DG KWh consumed
- Total DG cost (INR)
- Total runtime hours
- Total fuel consumed (Litres)

**Chart — DG usage by date:**
- Bar chart of DG KWh per day (most days should be 0, spikes are visible)

**DG usage log table:** Only rows where DG KWh > 0, showing Date, Time, DG ID, KWh, Runtime, Fuel, Cost
If no DG usage in selected period: show `st.info("No diesel generator usage in selected period.")`

Download button: **Download Diesel data**

---

### Tab 5 — Job Scheduler

This tab controls the automated daily email report.

**Section A — Email configuration:**

```
Recipient(s) — To:     [text_input, comma-separated emails]
Recipients — CC:       [text_input, comma-separated emails]
Send time (IST):       [time_input, default 10:00]
```

**Section B — Upload Excel template (optional):**

```
[ Upload custom Excel template ]   ← file_uploader, .xlsx only
```

If a template is uploaded, use it as the attachment instead of the auto-generated report.
Show a preview of the uploaded file: `st.dataframe(pd.read_excel(uploaded_file), height=200)`

**Section C — Email body customisation:**

```
Email subject:   [text_input, default: "Daily Energy Report — Noida Campus — {date}"]

Include sections:
  [x] Summary KPI cards
  [x] Unified data table (previous day)
  [x] Grid summary
  [x] Solar summary
  [x] Diesel summary
  [x] Inverter status
  [ ] Full raw data attachment

Custom message (optional):
  [text_area, placeholder: "Add a note to the top of the email body..."]
```

**Section D — Schedule status and controls:**

```
Scheduler status:   [ RUNNING / STOPPED ]   ← st.status or coloured badge

Next scheduled run: 10:00 IST tomorrow ({date})
Last run:           {date} at 10:02 IST — Sent successfully to 3 recipients

[ Save schedule ]      ← saves config to scheduler_config.json
[ Send now (test) ]    ← sends immediately to the To list
[ Stop scheduler ]  /  [ Start scheduler ]
```

After clicking **Send now (test)**:
- Show `st.spinner("Sending email...")` while sending
- Show `st.success("Email sent to {recipients} at {timestamp}")` on success
- Show `st.error("Failed: {error_detail}")` on failure

**Section E — Schedule history log:**

Show last 10 scheduler run entries in a small table:
```
Timestamp | Status | Recipients | Attachment | Notes
```
Read from `./output/scheduler_log.json`.

---

## Scheduler implementation

Use Python's `schedule` library running in a **background thread** alongside Streamlit.

```python
# scheduler.py
import schedule
import threading
import time

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(30)

def start_background_scheduler(send_fn, run_time: str):
    schedule.every().day.at(run_time).do(send_fn)
    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()
```

Start the background thread once at app startup using `st.session_state` to prevent multiple threads:

```python
if "scheduler_started" not in st.session_state:
    start_background_scheduler(send_daily_report, config["send_time"])
    st.session_state["scheduler_started"] = True
```

The `send_daily_report` function:
1. Loads all three CSVs
2. Filters for **previous day's data** (`date == today - 1 day`)
3. Builds the unified master DataFrame for that day
4. Computes summary metrics
5. Renders the HTML email using Jinja2
6. Attaches the custom template if uploaded, else attaches auto-generated `.xlsx`
7. Sends via SMTP
8. Appends result to `./output/scheduler_log.json`

---

## Email — HTML report format

Build in `./templates/email_body.html` using Jinja2.

**Structure:**

```
┌─────────────────────────────────────────────────┐
│  ENERGY CONSUMPTION REPORT — NOIDA CAMPUS        │
│  {date}  ·  Auto-generated by Energy Agent       │
├─────────────────────────────────────────────────┤
│  {custom_message if provided}                    │
├─────────────────────────────────────────────────┤
│  [ KPI CARDS — 5 metric boxes inline ]          │
├─────────────────────────────────────────────────┤
│  YESTERDAY'S SUMMARY TABLE                       │
│  (Grid + Solar + Diesel merged rows)             │
├─────────────────────────────────────────────────┤
│  INVERTER STATUS                                 │
│  SMB1 ● SMB2 ● SMB3 ○ SMB4 ● SMB5 ●           │
│  (● green = online, ○ red = fault)               │
├─────────────────────────────────────────────────┤
│  Generated by Energy Optimization Agent          │
│  Noida Campus · Do not reply                     │
└─────────────────────────────────────────────────┘
```

HTML table styling (inline CSS):
- Header row: `background-color:#1F3864; color:#ffffff; font-weight:bold`
- Alternating rows: `background-color:#EBF2FB` and `background-color:#ffffff`
- Numeric columns: `text-align:right`
- Font: `font-family: Arial, sans-serif; font-size: 13px`
- KPI cards: `display:inline-block; padding:12px 20px; margin:4px; background:#EBF2FB; border-left:4px solid #1F3864`

---

## Project structure

```
energy-dashboard/
├── app.py                      ← Streamlit entry point
├── scheduler.py                ← background schedule thread
├── config.yaml                 ← app and email defaults
├── scheduler_config.json       ← editable by user in the app (auto-created)
├── .env                        ← SMTP credentials (never commit)
├── .env.example
├── .gitignore
│
├── agent/
│   ├── loader.py               ← read and validate all three CSVs
│   ├── processor.py            ← merge, derive columns, compute metrics
│   ├── emailer.py              ← build HTML, send SMTP, log result
│   └── exporter.py             ← generate .xlsx attachments
│
├── templates/
│   └── email_body.html         ← Jinja2 email template
│
├── data/
│   ├── grid_data.csv           ← dummy Grid data (seed on first run)
│   ├── solar_data.csv          ← dummy Solar data (seed on first run)
│   └── diesel_data.csv         ← dummy Diesel data (seed on first run)
│
├── output/
│   ├── scheduler_log.json      ← auto-created, records every send
│   └── *.xlsx                  ← generated reports
│
├── requirements.txt
└── README.md
```

---

## `requirements.txt`

```
streamlit==1.33.0
pandas==2.2.0
openpyxl==3.1.2
plotly==5.20.0
jinja2==3.1.3
python-dotenv==1.0.1
pyyaml==6.0.1
schedule==1.2.1
```

---

## `config.yaml`

```yaml
data:
  grid_file: ./data/grid_data.csv
  solar_file: ./data/solar_data.csv
  diesel_file: ./data/diesel_data.csv

costs:
  grid_per_unit_inr: 7.5
  diesel_per_unit_inr: 30.0
  solar_per_unit_inr: 0.0

solar:
  daily_target_kwh: 3000
  inverter_ids: [SMB1, SMB2, SMB3, SMB4, SMB5]

email:
  subject: "Daily Energy Report — Noida Campus — {date}"
  default_to: "naveen@company.com, rajeev@company.com"
  default_cc: "rohit@company.com"
  send_time_ist: "10:00"

output:
  directory: ./output
  log_file: ./output/scheduler_log.json

app:
  title: "Energy Consumption Dashboard — Noida Campus"
  version: "1.0"
  page_icon: "⚡"
```

---

## `.env.example`

```
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=sender@company.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=sender@company.com
```

---

## README

```markdown
## Quick start

python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

pip install -r requirements.txt
cp .env.example .env            # fill in SMTP credentials
streamlit run app.py            # opens at http://localhost:8501

## Dummy data
Three sample CSV files are pre-seeded in ./data/ covering 13–18 Mar 2026.
Replace or append to these files with real data as the source feeds come online.

## Scheduled email
Configure recipients, send time, and email body in the Job Scheduler tab.
Click "Save schedule" — the job runs automatically in the background.
Click "Send now (test)" to dispatch immediately without waiting for the schedule.
```

---

## Out of scope for this build

- Live API integration with Suryalogix portal (replace solar CSV with API call in Phase 2)
- Real-time streaming or auto-refresh from live meters (Phase 2)
- Anomaly detection and root-cause alerts (Phase 2)
- LLM reasoning and NL Q&A interface (Phase 3)
- User authentication and login (add in Phase 2 if deploying to wider network)

---

## Acceptance checklist

- [ ] `streamlit run app.py` launches with no errors and all five tabs visible
- [ ] Overview tab shows all six KPI cards with correct values from the dummy data
- [ ] Date range filter updates all charts and the table on the Overview tab
- [ ] Stacked bar chart shows Grid, Solar, and Diesel correctly colour-coded
- [ ] Solar tab shows inverter status with green/red indicators for each SMB
- [ ] Diesel tab shows `No diesel generator usage` message when DG KWh = 0 for selected period
- [ ] Job Scheduler tab saves config to `scheduler_config.json` on clicking Save
- [ ] Send now (test) dispatches an email with the correct prior-day data and attachment
- [ ] Background scheduler fires at the configured time without restarting the app
- [ ] Scheduler log is written to `./output/scheduler_log.json` after each send attempt
- [ ] All three download buttons produce correctly named and formatted `.xlsx` files
- [ ] Uploading a custom Excel template in the Scheduler tab uses it as the email attachment
- [ ] App runs cleanly on Python 3.10 and 3.11
- [ ] No credentials or data files committed to the repository

---

*Prompt version: 2.0 · Phase 1 · Energy Consumption Optimization & Sustainability Agent · Noida Campus*
