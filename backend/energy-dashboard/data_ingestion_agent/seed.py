"""
seed.py — Seed dummy CSV files in ./data/ on first run.
Part of the Data Ingestion Agent.
Generates grid data matching the Electrical Optimization (1) Excel format
(Solar column omitted from grid), plus solar and diesel seed data.
"""

import os

def _project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def seed_data_files():
    """Create seed CSV files in ./data/ if they do not already exist."""
    data_dir = os.path.join(_project_root(), "data")
    os.makedirs(data_dir, exist_ok=True)

    # ── Grid data — matching ECS sheet format (Solar column omitted) ──
    grid_path = os.path.join(data_dir, "grid_data.csv")
    if not os.path.exists(grid_path):
        with open(grid_path, "w", encoding="utf-8") as f:
            f.write(
                "Date,Day,Time,Ambient Temperature °C,"
                "Grid Units Consumed (KWh),"
                "Total Units Consumed (KWh),"
                "Total Units Consumed in INR,"
                "Energy Saving in INR\n"
            )
            rows = [
                ("2026-03-19","Thursday","09:00","9-29",4088,4878,29065.68,5616.90),
                ("2026-03-18","Wednesday","09:00","11-31",4186,4957,29762.46,5481.81),
                ("2026-03-17","Tuesday","09:00","11-31",3584,4421,25482.24,5951.07),
                ("2026-03-16","Monday","09:00","11-31",1400,2391,9954.00,7046.01),
                ("2026-03-15","Sunday","09:00","11-31",3612,3859,25681.32,1756.17),
                ("2026-03-14","Saturday","09:00","11-31",3612,4114,25681.32,3569.22),
                ("2026-03-13","Friday","09:00","11-31",4242,4939,30160.62,4955.67),
                ("2026-03-12","Thursday","09:00","11-31",4368,4988,31056.48,4408.20),
                ("2026-03-11","Wednesday","09:00","11-31",4592,5294,32649.12,4991.22),
                ("2026-03-10","Tuesday","09:00","11-31",3976,4405,28269.36,3050.19),
                ("2026-03-09","Monday","09:00","11-31",1582,1981,11248.02,2836.89),
                ("2026-03-08","Sunday","09:00","12-37",2590,3134,18414.90,3867.84),
                ("2026-03-07","Saturday","09:00","11-36",4032,4566,28667.52,3796.74),
                ("2026-03-06","Friday","09:00","11-31",4046,4612,28767.06,4024.26),
                ("2026-03-05","Thursday","09:00","11-31",1876,2496,13338.36,4408.20),
                ("2026-03-04","Wednesday","09:00","10-29",2730,3349,19410.30,4401.09),
                ("2026-03-03","Tuesday","09:00","11-32",3388,4098,24088.68,5048.10),
                ("2026-03-02","Monday","09:00","11-29",1610,2089,11447.10,3405.69),
                ("2026-03-01","Sunday","09:00","10-30",2450,3117,17419.50,4742.37),
                ("2026-02-28","Saturday","09:00","11-29",2884,3509,20505.24,4443.75),
                ("2026-02-27","Friday","09:00","11-31",2842,3543,20206.62,4984.11),
                ("2026-02-26","Thursday","09:00","11-29",3262,3976,23192.82,5076.54),
                ("2026-02-25","Wednesday","09:00","11-29",3220,3833,22894.20,4358.43),
                ("2026-02-24","Tuesday","09:00","9-29",3150,3848,22396.50,4962.78),
                ("2026-02-23","Monday","09:00","8-24",1540,2151,10949.40,4344.21),
                ("2026-02-22","Sunday","09:00","8-26",2100,2894,14931.00,5645.34),
                ("2026-02-21","Saturday","09:00","8-24",3024,3630,21500.64,4308.66),
                ("2026-02-20","Friday","09:00","9-28",2940,3681,20903.40,5268.51),
                ("2026-02-19","Thursday","09:00","8-24",3654,3791,25979.94,974.07),
                ("2026-02-18","Wednesday","09:00","8-23",2968,3681,21102.48,5069.43),
                ("2026-02-17","Tuesday","09:00","8-29",2632,3458,18713.52,5872.86),
                ("2026-02-16","Monday","09:00","8-24",1722,2174,12243.42,3213.72),
            ]
            for r in rows:
                f.write(",".join(str(v) for v in r) + "\n")

    # ── Solar data ──
    solar_path = os.path.join(data_dir, "solar_data.csv")
    if not os.path.exists(solar_path):
        with open(solar_path, "w", encoding="utf-8") as f:
            f.write(
                "Date,Day,Time,Solar Units Generated (KWh),Inverter Status,"
                "SMB1 (KWh),SMB2 (KWh),SMB3 (KWh),SMB4 (KWh),SMB5 (KWh),"
                "Plant Capacity (KW),Irradiance (W/m²)\n"
            )
            rows = [
                ("2026-03-19","Thursday","09:00",790,"All Online",172,167,161,155,135,598,580),
                ("2026-03-18","Wednesday","09:00",771,"All Online",168,163,158,152,130,598,565),
                ("2026-03-17","Tuesday","09:00",837,"All Online",182,177,171,165,142,598,610),
                ("2026-03-16","Monday","09:00",991,"All Online",216,210,203,195,167,598,720),
                ("2026-03-15","Sunday","09:00",247,"SMB3 Fault",57,55,0,72,63,598,180),
                ("2026-03-14","Saturday","09:00",502,"All Online",109,106,103,99,85,598,368),
                ("2026-03-13","Friday","09:00",697,"All Online",152,148,143,137,117,598,510),
                ("2026-03-12","Thursday","09:00",620,"All Online",135,131,127,122,105,598,455),
                ("2026-03-11","Wednesday","09:00",702,"All Online",153,149,144,138,118,598,515),
                ("2026-03-10","Tuesday","09:00",429,"All Online",94,91,88,84,72,598,314),
                ("2026-03-09","Monday","09:00",399,"All Online",87,84,82,79,67,598,292),
                ("2026-03-08","Sunday","09:00",544,"All Online",119,115,111,107,92,598,398),
                ("2026-03-07","Saturday","09:00",534,"All Online",116,113,109,105,91,598,391),
                ("2026-03-06","Friday","09:00",566,"All Online",123,120,116,111,96,598,415),
                ("2026-03-05","Thursday","09:00",620,"All Online",135,131,127,122,105,598,455),
                ("2026-03-04","Wednesday","09:00",619,"All Online",135,131,127,122,104,598,454),
                ("2026-03-03","Tuesday","09:00",710,"All Online",155,150,145,140,120,598,520),
                ("2026-03-02","Monday","09:00",479,"All Online",104,101,98,94,82,598,351),
                ("2026-03-01","Sunday","09:00",667,"All Online",145,141,137,131,113,598,489),
                ("2026-02-28","Saturday","09:00",625,"All Online",136,132,128,123,106,598,458),
                ("2026-02-27","Friday","09:00",701,"All Online",153,149,143,138,118,598,514),
                ("2026-02-26","Thursday","09:00",714,"All Online",156,151,146,140,121,598,523),
                ("2026-02-25","Wednesday","09:00",613,"All Online",134,130,125,121,103,598,449),
                ("2026-02-24","Tuesday","09:00",698,"All Online",152,148,143,137,118,598,512),
                ("2026-02-23","Monday","09:00",611,"All Online",133,129,125,120,104,598,448),
                ("2026-02-22","Sunday","09:00",794,"All Online",173,168,162,156,135,598,582),
                ("2026-02-21","Saturday","09:00",606,"All Online",132,128,124,119,103,598,444),
                ("2026-02-20","Friday","09:00",741,"All Online",162,157,152,146,124,598,543),
                ("2026-02-19","Thursday","09:00",137,"SMB3 Fault",32,31,0,40,34,598,100),
                ("2026-02-18","Wednesday","09:00",713,"All Online",155,151,146,140,121,598,522),
                ("2026-02-17","Tuesday","09:00",826,"All Online",180,175,169,163,139,598,605),
                ("2026-02-16","Monday","09:00",452,"All Online",99,96,92,89,76,598,331),
            ]
            for r in rows:
                f.write(",".join(str(v) for v in r) + "\n")

    # ── Diesel data ──
    diesel_path = os.path.join(data_dir, "diesel_data.csv")
    if not os.path.exists(diesel_path):
        with open(diesel_path, "w", encoding="utf-8") as f:
            f.write(
                "Date,Day,Time,DG Units Consumed (KWh),DG Runtime (hrs),"
                "Fuel Consumed (Litres),Cost per Unit (INR),Total Cost (INR),DG ID\n"
            )
            # Most days 0; only few DG events
            dates_info = [
                ("2026-03-19","Thursday","09:00",0,0,0,30,0,"DG1"),
                ("2026-03-18","Wednesday","09:00",0,0,0,30,0,"DG1"),
                ("2026-03-17","Tuesday","09:00",0,0,0,30,0,"DG1"),
                ("2026-03-16","Monday","09:00",0,0,0,30,0,"DG1"),
                ("2026-03-15","Sunday","09:00",0,0,0,30,0,"DG1"),
                ("2026-03-14","Saturday","09:00",0,0,0,30,0,"DG1"),
                ("2026-03-13","Friday","09:00",0,0,0,30,0,"DG1"),
                ("2026-03-12","Thursday","09:00",0,0,0,30,0,"DG1"),
                ("2026-03-11","Wednesday","09:00",0,0,0,30,0,"DG1"),
                ("2026-03-10","Tuesday","09:00",0,0,0,30,0,"DG1"),
                ("2026-03-09","Monday","09:00",0,0,0,30,0,"DG1"),
                ("2026-03-08","Sunday","09:00",0,0,0,30,0,"DG1"),
                ("2026-03-07","Saturday","09:00",0,0,0,30,0,"DG1"),
                ("2026-03-06","Friday","09:00",0,0,0,30,0,"DG1"),
                ("2026-03-05","Thursday","09:00",62.4,1.5,17.2,30,1872,"DG2"),
                ("2026-03-04","Wednesday","09:00",0,0,0,30,0,"DG1"),
                ("2026-03-03","Tuesday","09:00",0,0,0,30,0,"DG1"),
                ("2026-03-02","Monday","09:00",0,0,0,30,0,"DG1"),
                ("2026-03-01","Sunday","09:00",0,0,0,30,0,"DG1"),
                ("2026-02-28","Saturday","09:00",0,0,0,30,0,"DG1"),
                ("2026-02-27","Friday","09:00",0,0,0,30,0,"DG1"),
                ("2026-02-26","Thursday","09:00",0,0,0,30,0,"DG1"),
                ("2026-02-25","Wednesday","09:00",0,0,0,30,0,"DG1"),
                ("2026-02-24","Tuesday","09:00",0,0,0,30,0,"DG1"),
                ("2026-02-23","Monday","09:00",0,0,0,30,0,"DG1"),
                ("2026-02-22","Sunday","09:00",0,0,0,30,0,"DG1"),
                ("2026-02-21","Saturday","09:00",0,0,0,30,0,"DG1"),
                ("2026-02-20","Friday","09:00",78.5,2.0,21.8,30,2355,"DG3"),
                ("2026-02-19","Thursday","09:00",45.8,1.0,12.5,30,1374,"DG2"),
                ("2026-02-18","Wednesday","09:00",0,0,0,30,0,"DG1"),
                ("2026-02-17","Tuesday","09:00",0,0,0,30,0,"DG1"),
                ("2026-02-16","Monday","09:00",0,0,0,30,0,"DG1"),
            ]
            for r in dates_info:
                f.write(",".join(str(v) for v in r) + "\n")

    # Ensure output dir exists
    output_dir = os.path.join(_project_root(), "output")
    os.makedirs(output_dir, exist_ok=True)
    log_path = os.path.join(output_dir, "scheduler_log.json")
    if not os.path.exists(log_path):
        with open(log_path, "w", encoding="utf-8") as f:
            f.write("[]")
