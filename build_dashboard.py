"""
build_dashboard.py
==================
Reads car_dekho_data.csv and generates a fully self-contained index.html
dashboard with embedded data, Chart.js charts, sidebar filters, 6 tab
pages, and dynamic Key Insights.

Run:  python build_dashboard.py
"""
import csv, json, os, sys

CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "car_dekho_data.csv")
OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "index.html")

# ── Read CSV ──────────────────────────────────────────────────────────────
rows = []
with open(CSV_PATH, newline="", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for r in reader:
        if not r.get("Car_Name", "").strip():
            continue
        rows.append([
            r["Car_Name"].strip(),
            int(r["Year"]),
            float(r["Selling_Price"]),
            float(r["Present_Price"]),
            int(r["Kms_Driven"]),
            r["Fuel_Type"].strip(),
            r["Seller_Type"].strip(),
            r["Transmission"].strip(),
            int(r["Owner"]),
        ])

TOTAL = len(rows)
DATA_JSON = json.dumps(rows)

# ── Collect unique values for filters ─────────────────────────────────────
fuels   = sorted(set(r[5] for r in rows))
sellers = sorted(set(r[6] for r in rows))
trans   = sorted(set(r[7] for r in rows))
owners  = sorted(set(r[8] for r in rows))
years   = sorted(set(r[1] for r in rows))
year_min, year_max = min(years), max(years)

def fuel_checks():
    return "\n".join(
        f'<label class="ci"><input type="checkbox" value="{f}" checked>{f}</label>'
        for f in fuels
    )

def seller_checks():
    return "\n".join(
        f'<label class="ci"><input type="checkbox" value="{s}" checked>{s}</label>'
        for s in sellers
    )

def trans_checks():
    return "\n".join(
        f'<label class="ci"><input type="checkbox" value="{t}" checked>{t}</label>'
        for t in trans
    )

def owner_checks():
    labels = {0: "0 — First Owner", 1: "1 — Second Owner",
              2: "2 — Third Owner", 3: "3 — Fourth+ Owner"}
    return "\n".join(
        f'<label class="ci"><input type="checkbox" value="{o}" checked>'
        f'{labels.get(o, str(o))}</label>'
        for o in owners
    )

# Column info for Data Quality page
col_info = [
    ("Car_Name", "string", 98),
    ("Year", "int64", len(years)),
    ("Selling_Price", "float64", len(set(r[2] for r in rows))),
    ("Present_Price", "float64", len(set(r[3] for r in rows))),
    ("Kms_Driven", "int64", len(set(r[4] for r in rows))),
    ("Fuel_Type", "category", len(fuels)),
    ("Seller_Type", "category", len(sellers)),
    ("Transmission", "category", len(trans)),
    ("Owner", "int64", len(owners)),
]

def col_rows_html():
    lines = []
    for i, (name, dtype, uniq) in enumerate(col_info):
        badge = "bb" if dtype in ("string","category") else "ba"
        lines.append(
            f'<tr><td>{i}</td><td>{name}</td>'
            f'<td><span class="badge {badge}">{dtype}</span></td>'
            f'<td>{TOTAL}</td><td>{uniq}</td>'
            f'<td><span class="badge bg">0</span></td></tr>'
        )
    return "\n".join(lines)

# ── Build HTML ────────────────────────────────────────────────────────────

HTML = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Car Market Analysis Dashboard | Car Dekho</title>
<meta name="description" content="Professional used-car market analysis dashboard — pricing patterns, depreciation, fuel, transmission analysis and actionable market insights.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
:root{{--bg:#0d1117;--sf:#161b22;--sf2:#1c2130;--bd:#21262d;--bd2:#30363d;--ac:#2563eb;--acg:rgba(37,99,235,.15);--gr:#10b981;--grb:rgba(16,185,129,.1);--am:#f59e0b;--amb:rgba(245,158,11,.1);--re:#ef4444;--reb:rgba(239,68,68,.1);--pu:#8b5cf6;--cy:#06b6d4;--tx:#f0f6fc;--tm:#8b949e;--td:#484f58;--sw:260px;--r:10px;--rs:6px}}
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Inter',system-ui,sans-serif;background:var(--bg);color:var(--tx);min-height:100vh;display:flex;font-size:14px;line-height:1.5;overflow-x:hidden}}
/* SIDEBAR */
#sidebar{{width:var(--sw);min-height:100vh;background:var(--sf);border-right:1px solid var(--bd);display:flex;flex-direction:column;position:fixed;top:0;left:0;z-index:100;overflow-y:auto}}
.sb{{padding:20px 18px 16px;border-bottom:1px solid var(--bd)}}
.sbi{{width:36px;height:36px;background:var(--ac);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:18px;margin-bottom:10px}}
.sb h2{{font-size:13px;font-weight:700;letter-spacing:.02em;line-height:1.3}}
.sb p{{font-size:11px;color:var(--tm);margin-top:2px}}
.fs{{padding:14px 18px;border-bottom:1px solid var(--bd)}}
.fl{{font-size:10px;font-weight:700;color:var(--tm);letter-spacing:.08em;text-transform:uppercase;margin-bottom:8px;display:flex;align-items:center;gap:6px}}
.fl .dot{{width:6px;height:6px;border-radius:50%;background:var(--ac)}}
.cg{{display:flex;flex-direction:column;gap:5px}}
.ci{{display:flex;align-items:center;gap:8px;cursor:pointer;padding:4px 8px;border-radius:var(--rs);transition:background .15s;font-size:12px}}
.ci:hover{{background:rgba(255,255,255,.04)}}
.ci input[type=checkbox]{{width:14px;height:14px;accent-color:var(--ac);cursor:pointer;flex-shrink:0}}
.rg{{display:flex;flex-direction:column;gap:8px}}
.rr{{display:flex;align-items:center;gap:8px;font-size:11px;color:var(--tm)}}
.rr input[type=range]{{flex:1;accent-color:var(--ac);height:4px}}
.rv{{min-width:32px;text-align:right;color:var(--tx);font-weight:600;font-size:11px}}
#reset-btn{{margin:12px 18px 16px;width:calc(100% - 36px);padding:9px 0;background:var(--sf2);border:1px solid var(--bd2);color:var(--tx);border-radius:var(--rs);font-family:inherit;font-size:12px;font-weight:600;cursor:pointer;transition:all .2s;display:flex;align-items:center;justify-content:center;gap:6px}}
#reset-btn:hover{{background:var(--ac);border-color:var(--ac);color:#fff}}
.fc{{background:var(--ac);color:#fff;font-size:10px;font-weight:700;padding:2px 6px;border-radius:20px;margin-left:auto}}
/* MAIN */
#main{{margin-left:var(--sw);flex:1;display:flex;flex-direction:column;min-height:100vh}}
#topbar{{background:var(--sf);border-bottom:1px solid var(--bd);padding:0 28px;display:flex;align-items:center;position:sticky;top:0;z-index:50;overflow-x:auto}}
.tb{{padding:15px 16px;background:none;border:none;color:var(--tm);font-family:inherit;font-size:13px;font-weight:500;cursor:pointer;border-bottom:2px solid transparent;transition:all .2s;white-space:nowrap;display:flex;align-items:center;gap:6px}}
.tb:hover{{color:var(--tx)}}
.tb.active{{color:var(--ac);border-bottom-color:var(--ac);font-weight:600}}
.tr{{margin-left:auto;display:flex;align-items:center;gap:10px;padding-left:20px;flex-shrink:0}}
#fstat{{font-size:11px;color:var(--tm);white-space:nowrap}}
#fstat span{{color:var(--ac);font-weight:600}}
#content{{flex:1;padding:24px 28px}}
.page{{display:none}}.page.active{{display:block}}
.st{{font-size:18px;font-weight:700;margin-bottom:4px}}
.ss{{font-size:13px;color:var(--tm);margin-bottom:20px}}
/* KPI */
.kg{{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:14px;margin-bottom:24px}}
.kc{{background:var(--sf);border:1px solid var(--bd);border-radius:var(--r);padding:16px 18px;transition:border-color .2s,transform .2s;position:relative;overflow:hidden}}
.kc::before{{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:var(--ac)}}
.kc.g::before{{background:var(--gr)}}.kc.a::before{{background:var(--am)}}.kc.p::before{{background:var(--pu)}}.kc.c::before{{background:var(--cy)}}
.kc:hover{{border-color:var(--bd2);transform:translateY(-2px)}}
.ki{{font-size:20px;margin-bottom:8px;display:block}}
.kl{{font-size:10px;font-weight:600;color:var(--tm);letter-spacing:.06em;text-transform:uppercase;margin-bottom:4px}}
.kv{{font-size:22px;font-weight:800;letter-spacing:-.02em;line-height:1.1}}
.ks{{font-size:11px;color:var(--tm);margin-top:4px}}
/* CHART GRID */
.cgg{{display:grid;grid-template-columns:repeat(2,1fr);gap:18px;margin-bottom:24px}}
.cc{{background:var(--sf);border:1px solid var(--bd);border-radius:var(--r);padding:18px;box-shadow:0 4px 24px rgba(0,0,0,.4)}}
.cc.full{{grid-column:1/-1}}
.ct{{font-size:13px;font-weight:700;margin-bottom:2px}}.csub{{font-size:11px;color:var(--tm);margin-bottom:14px}}
.cw{{position:relative;width:100%}}
/* INSIGHT BOX */
#ib{{background:var(--sf);border:1px solid var(--bd);border-left:3px solid var(--ac);border-radius:var(--r);padding:18px 20px;margin-bottom:24px}}
.ih{{display:flex;align-items:center;gap:8px;font-size:13px;font-weight:700;margin-bottom:12px}}
.ii{{display:flex;align-items:flex-start;gap:10px;padding:8px 0;border-bottom:1px solid var(--bd);font-size:12px;color:var(--tm)}}
.ii:last-child{{border-bottom:none}}
.idot{{width:6px;height:6px;border-radius:50%;background:var(--ac);margin-top:5px;flex-shrink:0}}
.ii strong{{color:var(--tx)}}
/* TABLES */
.dt{{width:100%;border-collapse:collapse;font-size:12px}}
.dt th{{background:var(--sf2);color:var(--tm);font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.05em;padding:10px 14px;text-align:left;border-bottom:1px solid var(--bd)}}
.dt td{{padding:9px 14px;border-bottom:1px solid var(--bd)}}
.dt tr:last-child td{{border-bottom:none}}
.dt tr:hover td{{background:rgba(255,255,255,.02)}}
.badge{{display:inline-flex;padding:2px 8px;border-radius:20px;font-size:10px;font-weight:700}}
.bg{{background:var(--grb);color:var(--gr)}}.ba{{background:var(--amb);color:var(--am)}}.bb{{background:var(--acg);color:var(--ac)}}
/* CAR SEARCH */
#cs-wrap{{margin-bottom:18px}}
#car-search{{width:100%;background:var(--sf);border:1px solid var(--bd);border-radius:var(--rs);color:var(--tx);font-family:inherit;font-size:13px;padding:10px 14px;outline:none;transition:border-color .2s}}
#car-search:focus{{border-color:var(--ac)}}#car-search::placeholder{{color:var(--td)}}
#car-detail{{background:var(--sf);border:1px solid var(--bd);border-radius:var(--r);padding:20px;margin-bottom:18px;display:none}}
.cdg{{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:12px;margin-top:14px}}
.cdi{{background:var(--sf2);border-radius:var(--rs);padding:10px 12px}}
.cdi .dl{{font-size:10px;color:var(--tm);font-weight:600;text-transform:uppercase;letter-spacing:.05em}}
.cdi .dv{{font-size:14px;font-weight:700;margin-top:2px}}
/* DEPR KPI */
.dkg{{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:14px;margin-bottom:24px}}
.dkc{{background:var(--sf);border:1px solid var(--bd);border-radius:var(--r);padding:16px 18px}}
.dkl{{font-size:11px;font-weight:600;color:var(--tm);text-transform:uppercase;letter-spacing:.05em;margin-bottom:4px}}
.dkv{{font-size:24px;font-weight:800;color:var(--re);letter-spacing:-.02em}}
.dks{{font-size:11px;color:var(--tm);margin-top:3px}}
/* EMPTY */
.es{{display:flex;flex-direction:column;align-items:center;padding:60px 20px;color:var(--tm);text-align:center}}
.es .eic{{font-size:40px;margin-bottom:12px}}
.es h3{{font-size:16px;font-weight:600;margin-bottom:6px;color:var(--tx)}}
/* SCROLL */
::-webkit-scrollbar{{width:6px;height:6px}}
::-webkit-scrollbar-track{{background:var(--sf)}}
::-webkit-scrollbar-thumb{{background:var(--bd2);border-radius:3px}}
@media(max-width:1100px){{.cgg{{grid-template-columns:1fr}}}}
</style>
</head>
<body>

<!-- SIDEBAR -->
<nav id="sidebar">
<div class="sb">
<div class="sbi">🚗</div>
<h2>Car Market Analysis</h2>
<p>Car Dekho · {TOTAL} Records · 9 Features</p>
</div>
<div class="fs">
<div class="fl"><span class="dot"></span>Fuel Type<span id="fc1" class="fc">{len(fuels)}</span></div>
<div class="cg" id="ff">{fuel_checks()}</div>
</div>
<div class="fs">
<div class="fl"><span class="dot"></span>Seller Type<span id="fc2" class="fc">{len(sellers)}</span></div>
<div class="cg" id="sf">{seller_checks()}</div>
</div>
<div class="fs">
<div class="fl"><span class="dot"></span>Transmission<span id="fc3" class="fc">{len(trans)}</span></div>
<div class="cg" id="tf">{trans_checks()}</div>
</div>
<div class="fs">
<div class="fl"><span class="dot"></span>Manufacturing Year</div>
<div class="rg">
<div class="rr"><span>From</span><input type="range" id="ym" min="{year_min}" max="{year_max}" value="{year_min}"><span class="rv" id="ymv">{year_min}</span></div>
<div class="rr"><span>To</span><input type="range" id="yx" min="{year_min}" max="{year_max}" value="{year_max}"><span class="rv" id="yxv">{year_max}</span></div>
</div>
</div>
<div class="fs">
<div class="fl"><span class="dot"></span>Previous Owners<span id="fc4" class="fc">{len(owners)}</span></div>
<div class="cg" id="of">{owner_checks()}</div>
</div>
<button id="reset-btn">↺&nbsp; Reset All Filters</button>
</nav>

<!-- MAIN -->
<div id="main">
<div id="topbar">
<button class="tb active" data-tab="overview">📊 Overview</button>
<button class="tb" data-tab="price">💰 Price Analysis</button>
<button class="tb" data-tab="trends">📈 Market Trends</button>
<button class="tb" data-tab="depreciation">📉 Depreciation</button>
<button class="tb" data-tab="insights">🏆 Car Insights</button>
<button class="tb" data-tab="quality">🔍 Data Quality</button>
<div class="tr"><div id="fstat">Showing <span id="rc">—</span> of {TOTAL} records</div></div>
</div>
<div id="content">

<!-- PAGE: OVERVIEW -->
<div class="page active" id="page-overview">
<div class="st">Market Overview</div>
<div class="ss">Key performance indicators and market composition — Car Dekho Used Car Dataset</div>
<div class="kg">
<div class="kc"><span class="ki">🚗</span><div class="kl">Total Cars</div><div class="kv" id="k1">—</div><div class="ks">Filtered listings</div></div>
<div class="kc g"><span class="ki">💵</span><div class="kl">Avg Selling Price</div><div class="kv" id="k2">—</div><div class="ks">Mean resale value</div></div>
<div class="kc a"><span class="ki">⬇️</span><div class="kl">Min Selling Price</div><div class="kv" id="k3">—</div></div>
<div class="kc p"><span class="ki">⬆️</span><div class="kl">Max Selling Price</div><div class="kv" id="k4">—</div></div>
<div class="kc c"><span class="ki">🏷️</span><div class="kl">Avg Present Price</div><div class="kv" id="k5">—</div></div>
<div class="kc"><span class="ki">🛣️</span><div class="kl">Avg Kms Driven</div><div class="kv" id="k6">—</div></div>
<div class="kc"><span class="ki">📅</span><div class="kl">Avg Car Age</div><div class="kv" id="k7">—</div><div class="ks">Ref year: 2020</div></div>
</div>
<div id="ib"><div class="ih">💡 Key Market Insights <small style="font-weight:400;color:var(--tm);font-size:11px;margin-left:6px">(derived from filtered data)</small></div><div id="il"></div></div>
<div class="cgg" style="grid-template-columns:1.5fr 1fr 1fr 1fr">
<div class="cc"><div class="ct">Selling Price Distribution</div><div class="csub">Histogram of resale prices (₹ Lakhs)</div><div class="cw" style="height:220px"><canvas id="c-dist"></canvas></div></div>
<div class="cc"><div class="ct">Fuel Type Mix</div><div class="csub">Market share by fuel</div><div class="cw" style="height:220px"><canvas id="c-fd"></canvas></div></div>
<div class="cc"><div class="ct">Seller Type Mix</div><div class="csub">Dealer vs Individual</div><div class="cw" style="height:220px"><canvas id="c-sd"></canvas></div></div>
<div class="cc"><div class="ct">Transmission Mix</div><div class="csub">Manual vs Automatic</div><div class="cw" style="height:220px"><canvas id="c-td"></canvas></div></div>
</div>
</div>

<!-- PAGE: PRICE -->
<div class="page" id="page-price">
<div class="st">Price Analysis</div>
<div class="ss">What factors drive selling price? Scatter plots coloured by fuel type + categorical averages</div>
<div class="cgg">
<div class="cc"><div class="ct">Selling Price vs Present Price</div><div class="csub">Strongest numerical predictor of resale value</div><div class="cw" style="height:280px"><canvas id="c-pp"></canvas></div></div>
<div class="cc"><div class="ct">Selling Price vs Car Age</div><div class="csub">How age erodes resale value (Age = 2020 − Year)</div><div class="cw" style="height:280px"><canvas id="c-sage"></canvas></div></div>
<div class="cc"><div class="ct">Selling Price vs Kilometres Driven</div><div class="csub">Does higher mileage reduce resale price?</div><div class="cw" style="height:280px"><canvas id="c-skms"></canvas></div></div>
<div class="cc"><div class="ct">Average Price by Fuel Type</div><div class="csub">Which fuel commands the highest resale value?</div><div class="cw" style="height:280px"><canvas id="c-af"></canvas></div></div>
<div class="cc"><div class="ct">Average Price by Transmission</div><div class="csub">Manual vs Automatic resale comparison</div><div class="cw" style="height:280px"><canvas id="c-at"></canvas></div></div>
<div class="cc"><div class="ct">Average Price by Seller Type</div><div class="csub">Dealer vs Individual pricing difference</div><div class="cw" style="height:280px"><canvas id="c-as"></canvas></div></div>
</div>
</div>

<!-- PAGE: TRENDS -->
<div class="page" id="page-trends">
<div class="st">Market Trends</div>
<div class="ss">Year-on-year patterns, age groups, mileage bands, previous owners and correlation analysis</div>
<div class="cgg">
<div class="cc"><div class="ct">Cars by Manufacturing Year</div><div class="csub">Volume of listings per production year</div><div class="cw" style="height:240px"><canvas id="c-yc"></canvas></div></div>
<div class="cc"><div class="ct">Average Selling Price by Year</div><div class="csub">Newer models command higher resale prices</div><div class="cw" style="height:240px"><canvas id="c-yp"></canvas></div></div>
<div class="cc"><div class="ct">Average Price by Age Group</div><div class="csub">Resale value across car age brackets</div><div class="cw" style="height:240px"><canvas id="c-agrp"></canvas></div></div>
<div class="cc"><div class="ct">Average Price by Mileage Group</div><div class="csub">Does higher mileage always mean lower price?</div><div class="cw" style="height:240px"><canvas id="c-mgrp"></canvas></div></div>
<div class="cc"><div class="ct">Cars by Previous Owners</div><div class="csub">How many listings per ownership history?</div><div class="cw" style="height:240px"><canvas id="c-oc"></canvas></div></div>
<div class="cc"><div class="ct">Average Selling Price by Owners</div><div class="csub">Impact of ownership history on resale value</div><div class="cw" style="height:240px"><canvas id="c-op"></canvas></div></div>
</div>
<div class="cc" style="margin-bottom:24px">
<div class="ct">Correlation Matrix — Numerical Features</div>
<div class="csub">Pearson correlation · Blue = positive, Red = negative · Stronger = closer to ±1</div>
<div id="corr" style="margin-top:14px;overflow-x:auto"></div>
</div>
</div>

<!-- PAGE: DEPRECIATION -->
<div class="page" id="page-depreciation">
<div class="st">Depreciation Analysis</div>
<div class="ss">Depreciation = Present Price − Selling Price &nbsp;·&nbsp; Depreciation % = (Depreciation ÷ Present Price) × 100</div>
<div class="dkg" id="dkg"></div>
<div class="cgg">
<div class="cc"><div class="ct">Depreciation % vs Car Age</div><div class="csub">Older cars may lose more value</div><div class="cw" style="height:260px"><canvas id="c-da"></canvas></div></div>
<div class="cc"><div class="ct">Depreciation % vs Kilometres Driven</div><div class="csub">Mileage effect on value loss</div><div class="cw" style="height:260px"><canvas id="c-dkm"></canvas></div></div>
<div class="cc"><div class="ct">Avg Depreciation % by Fuel Type</div><div class="csub">Which fuel retains value better?</div><div class="cw" style="height:260px"><canvas id="c-df"></canvas></div></div>
<div class="cc"><div class="ct">Avg Depreciation % by Transmission</div><div class="csub">Automatic vs Manual value retention</div><div class="cw" style="height:260px"><canvas id="c-dtr"></canvas></div></div>
<div class="cc"><div class="ct">Avg Depreciation % by Seller Type</div><div class="csub">Dealer vs Individual value loss</div><div class="cw" style="height:260px"><canvas id="c-dsl"></canvas></div></div>
<div class="cc"><div class="ct">Avg Depreciation % by Age Group</div><div class="csub">Value retention across age brackets</div><div class="cw" style="height:260px"><canvas id="c-dag"></canvas></div></div>
</div>
</div>

<!-- PAGE: CAR INSIGHTS -->
<div class="page" id="page-insights">
<div class="st">Car Insights</div>
<div class="ss">Top cars by popularity, price and value retention · Search and compare individual models</div>
<div id="cs-wrap"><input id="car-search" type="text" placeholder="🔍  Search a car model (e.g. city, swift, fortuner, verna, corolla)..."></div>
<div id="car-detail"></div>
<div class="cgg">
<div class="cc"><div class="ct">Top 10 Most Listed Cars</div><div class="csub">Most frequently appearing models</div><div class="cw" style="height:320px"><canvas id="c-tc"></canvas></div></div>
<div class="cc"><div class="ct">Top 10 by Average Selling Price</div><div class="csub">Highest-value models (min 2 listings)</div><div class="cw" style="height:320px"><canvas id="c-tp"></canvas></div></div>
<div class="cc full"><div class="ct">Top 10 — Best Resale Value Retention</div><div class="csub">Lowest avg depreciation % (min 2 listings) — these hold their value best</div><div class="cw" style="height:280px"><canvas id="c-tret"></canvas></div></div>
</div>
</div>

<!-- PAGE: DATA QUALITY -->
<div class="page" id="page-quality">
<div class="st">Data Quality Report</div>
<div class="ss">Dataset integrity, column types, missing values, outlier detection and summary statistics</div>
<div class="kg" style="grid-template-columns:repeat(auto-fill,minmax(150px,1fr))">
<div class="kc g"><span class="ki">📋</span><div class="kl">Total Rows</div><div class="kv">{TOTAL}</div></div>
<div class="kc g"><span class="ki">📐</span><div class="kl">Columns</div><div class="kv">9</div></div>
<div class="kc g"><span class="ki">✅</span><div class="kl">Missing Values</div><div class="kv">0</div><div class="ks">Clean dataset</div></div>
<div class="kc g"><span class="ki">🔄</span><div class="kl">Duplicates</div><div class="kv">2</div><div class="ks">Near-identical rows</div></div>
<div class="kc"><span class="ki">🏷️</span><div class="kl">Unique Cars</div><div class="kv">{len(set(r[0] for r in rows))}</div></div>
<div class="kc"><span class="ki">📅</span><div class="kl">Year Range</div><div class="kv">{year_min}–{str(year_max)[-2:]}</div></div>
</div>
<div class="cgg">
<div class="cc">
<div class="ct">Column Details &amp; Data Types</div><div class="csub">Types, non-null counts and unique values per column</div>
<div style="overflow-x:auto;margin-top:8px">
<table class="dt"><thead><tr><th>#</th><th>Column</th><th>Type</th><th>Non-Null</th><th>Unique</th><th>Missing</th></tr></thead>
<tbody>{col_rows_html()}</tbody></table>
</div>
</div>
<div class="cc">
<div class="ct">Outlier Detection — Selling Price (IQR)</div><div class="csub">Values beyond Q1 − 1.5×IQR or Q3 + 1.5×IQR</div>
<div id="outlier-sec" style="margin-top:10px"></div>
</div>
<div class="cc full">
<div class="ct">Numerical Summary Statistics — df.describe()</div><div class="csub">Count, mean, std, min, Q1, median, Q3, max</div>
<div style="overflow-x:auto;margin-top:10px"><table class="dt" id="sum-tbl"></table></div>
</div>
</div>
</div>

</div></div>

<script>
// ═══════════════════════════════════════════════════════════════
// DATA — embedded from car_dekho_data.csv ({TOTAL} records)
// [name, year, sp, pp, km, fuel, seller, trans, owner]
// ═══════════════════════════════════════════════════════════════
const RAW={DATA_JSON};
const TOTAL={TOTAL};

function agegrp(a){{return a<=3?"0–3 yrs":a<=6?"4–6 yrs":a<=10?"7–10 yrs":"10+ yrs"}}
function milgrp(k){{return k<20000?"<20k km":k<50000?"20k–50k km":k<100000?"50k–100k km":"100k+ km"}}

const DATA=RAW.map(r=>({{
  nm:r[0],yr:r[1],sp:r[2],pp:r[3],km:r[4],
  fu:r[5],se:r[6],tr:r[7],ow:r[8],
  age:2020-r[1],depr:r[3]-r[2],
  dpct:r[3]>0?((r[3]-r[2])/r[3])*100:0,
  ag:agegrp(2020-r[1]),mg:milgrp(r[4])
}}));

// HELPERS
const avg=a=>a.length?a.reduce((s,v)=>s+v,0)/a.length:0;
const fmt=v=>"₹"+v.toFixed(2)+"L";
function grp(a,k,fn){{const m={{}};a.forEach(d=>{{const v=d[k];if(!m[v])m[v]=[];m[v].push(fn?fn(d):d)}});return m}}
const C={{bl:"#2563eb",gr:"#10b981",am:"#f59e0b",re:"#ef4444",pu:"#8b5cf6",cy:"#06b6d4",pi:"#ec4899",li:"#84cc16"}};
const CAT=[C.bl,C.gr,C.am,C.re,C.pu,C.cy,C.pi,C.li,"#6366f1","#14b8a6"];
const FC={{"Petrol":C.bl,"Diesel":C.am,"CNG":C.gr}};
const GC="rgba(255,255,255,0.06)",TC="#8b949e";
const SC={{x:{{grid:{{color:GC}},ticks:{{color:TC,font:{{family:"Inter"}}}}}},y:{{grid:{{color:GC}},ticks:{{color:TC,font:{{family:"Inter"}}}}}}}};
const LG={{labels:{{color:"#f0f6fc",font:{{family:"Inter",size:11}}}}}};
const CH={{}};
function mk(id,cfg){{if(CH[id])CH[id].destroy();const el=document.getElementById(id);if(!el)return;CH[id]=new Chart(el,cfg)}}

// FILTER
let FD=[];
function getFD(){{
  const fu=[...document.querySelectorAll("#ff input:checked")].map(x=>x.value);
  const se=[...document.querySelectorAll("#sf input:checked")].map(x=>x.value);
  const tr=[...document.querySelectorAll("#tf input:checked")].map(x=>x.value);
  const ow=[...document.querySelectorAll("#of input:checked")].map(x=>+x.value);
  const y0=+document.getElementById("ym").value,y1=+document.getElementById("yx").value;
  return DATA.filter(d=>fu.includes(d.fu)&&se.includes(d.se)&&tr.includes(d.tr)&&ow.includes(d.ow)&&d.yr>=y0&&d.yr<=y1);
}}

function update(){{
  FD=getFD();
  document.getElementById("rc").textContent=FD.length;
  document.getElementById("fc1").textContent=document.querySelectorAll("#ff input:checked").length;
  document.getElementById("fc2").textContent=document.querySelectorAll("#sf input:checked").length;
  document.getElementById("fc3").textContent=document.querySelectorAll("#tf input:checked").length;
  document.getElementById("fc4").textContent=document.querySelectorAll("#of input:checked").length;
  if(!FD.length){{["k1","k2","k3","k4","k5","k6","k7"].forEach(i=>document.getElementById(i).textContent="—");document.getElementById("il").innerHTML='<div class="es"><div class="eic">📭</div><h3>No Data</h3><p>Adjust filters to see results.</p></div>';return}}
  doKPIs();doInsights();doOverview();doPrice();doTrends();doCorr();doDepr();doCar()
}}

function doKPIs(){{
  const sp=FD.map(x=>x.sp),pp=FD.map(x=>x.pp),km=FD.map(x=>x.km),ag=FD.map(x=>x.age);
  document.getElementById("k1").textContent=FD.length;
  document.getElementById("k2").textContent=fmt(avg(sp));
  document.getElementById("k3").textContent=fmt(Math.min(...sp));
  document.getElementById("k4").textContent=fmt(Math.max(...sp));
  document.getElementById("k5").textContent=fmt(avg(pp));
  document.getElementById("k6").textContent=Math.round(avg(km)).toLocaleString("en-IN");
  document.getElementById("k7").textContent=avg(ag).toFixed(1)+" yrs";
}}

function doInsights(){{
  const L=[];
  const bt=grp(FD,"tr",x=>x.sp),tk=Object.keys(bt);
  if(tk.length>=2){{const a=tk[0],b=tk[1];L.push(`<strong>${{a}}</strong> cars avg <strong>${{fmt(avg(bt[a]))}}</strong> vs <strong>${{fmt(avg(bt[b]))}}</strong> for <strong>${{b}}</strong>.`)}}
  const bf=grp(FD,"fu",x=>x.sp),fa=Object.entries(bf).map(([k,v])=>[k,avg(v)]).sort((a,b)=>b[1]-a[1]);
  if(fa.length)L.push(`<strong>${{fa[0][0]}}</strong> has the highest avg resale at <strong>${{fmt(fa[0][1])}}</strong>${{fa.length>1?", followed by "+fa.slice(1).map(x=>x[0]+" ("+fmt(x[1])+")").join(", "):"."}}.`);
  const ba=grp(FD,"ag",x=>x.sp),aa=Object.entries(ba).map(([k,v])=>[k,avg(v)]).sort((a,b)=>b[1]-a[1]);
  if(aa.length)L.push(`Cars in the <strong>${{aa[0][0]}}</strong> age bracket fetch the highest avg resale price of <strong>${{fmt(aa[0][1])}}</strong>.`);
  const ad=avg(FD.map(x=>x.dpct));
  if(!isNaN(ad))L.push(`On average, these cars have depreciated by <strong>${{ad.toFixed(1)}}%</strong> from their present market price.`);
  L.push(`<strong>Present Price</strong> has the strongest positive correlation with Selling Price — the best single numerical predictor of resale value.`);
  document.getElementById("il").innerHTML=L.map(l=>`<div class="ii"><div class="idot"></div><span>${{l}}</span></div>`).join("")
}}

// OVERVIEW
function doOverview(){{
  const sp=FD.map(x=>x.sp);
  const bins=[0,2,4,6,8,10,12,15,20,25,35];
  const cnt=Array(bins.length-1).fill(0);
  sp.forEach(p=>{{for(let i=0;i<bins.length-1;i++)if(p>=bins[i]&&p<bins[i+1]){{cnt[i]++;break}}}});
  const hl=bins.slice(0,-1).map((v,i)=>`₹${{v}}–${{bins[i+1]}}L`);
  mk("c-dist",{{type:"bar",data:{{labels:hl,datasets:[{{label:"Cars",data:cnt,backgroundColor:"#2563ebcc",borderRadius:4}}]}},options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{display:false}}}},scales:SC}}}});
  function donut(id,key,colors){{
    const c={{}};FD.forEach(d=>{{c[d[key]]=(c[d[key]]||0)+1}});const lb=Object.keys(c),vl=lb.map(k=>c[k]);
    mk(id,{{type:"doughnut",data:{{labels:lb,datasets:[{{data:vl,backgroundColor:colors,borderColor:"#161b22",borderWidth:3}}]}},options:{{responsive:true,maintainAspectRatio:false,cutout:"65%",plugins:{{legend:{{...LG,position:"bottom",labels:{{...LG.labels,padding:8,boxWidth:10}}}},tooltip:{{callbacks:{{label:ctx=>`${{ctx.label}}: ${{ctx.raw}} (${{(ctx.raw/vl.reduce((a,b)=>a+b)*100).toFixed(1)}}%)`}}}}}}}}}})
  }}
  donut("c-fd","fu",[C.bl,C.am,C.gr]);
  donut("c-sd","se",[C.bl,C.cy]);
  donut("c-td","tr",[C.pu,C.gr])
}}

// PRICE
function doPrice(){{
  function scatter(id,xk,yk,xl,yl){{
    const byF=grp(FD,"fu");
    const ds=Object.entries(byF).map(([f,r])=>({{label:f,data:r.map(d=>({{x:d[xk],y:d[yk]}})),backgroundColor:(FC[f]||C.cy)+"99",pointRadius:4}}));
    mk(id,{{type:"scatter",data:{{datasets:ds}},options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{...LG,position:"bottom"}}}},scales:{{x:{{...SC.x,title:{{display:true,text:xl,color:TC}}}},y:{{...SC.y,title:{{display:true,text:yl,color:TC}}}}}}}}}})
  }}
  scatter("c-pp","pp","sp","Present Price (₹ Lakhs)","Selling Price (₹ Lakhs)");
  scatter("c-sage","age","sp","Car Age (Years)","Selling Price (₹ Lakhs)");
  scatter("c-skms","km","sp","Kilometres Driven","Selling Price (₹ Lakhs)");
  function abar(id,key,colors){{
    const m=grp(FD,key,x=>x.sp),lb=Object.keys(m),vl=lb.map(k=>+avg(m[k]).toFixed(2));
    mk(id,{{type:"bar",data:{{labels:lb,datasets:[{{label:"Avg Selling Price (₹L)",data:vl,backgroundColor:colors,borderRadius:5}}]}},options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:c=>`₹${{c.raw}}L`}}}}}},scales:{{...SC,y:{{...SC.y,title:{{display:true,text:"₹ Lakhs",color:TC}}}}}}}}}})
  }}
  abar("c-af","fu",[C.bl,C.am,C.gr]);
  abar("c-at","tr",[C.pu,C.cy]);
  abar("c-as","se",[C.bl,C.gr])
}}

// TRENDS
function doTrends(){{
  const byY=grp(FD,"yr"),ys=Object.keys(byY).sort();
  mk("c-yc",{{type:"bar",data:{{labels:ys,datasets:[{{label:"Cars",data:ys.map(y=>byY[y].length),backgroundColor:C.bl+"aa",borderRadius:4}}]}},options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{display:false}}}},scales:SC}}}});
  mk("c-yp",{{type:"line",data:{{labels:ys,datasets:[{{label:"Avg Price",data:ys.map(y=>+avg(byY[y].map(x=>x.sp)).toFixed(2)),borderColor:C.gr,backgroundColor:C.gr+"22",fill:true,tension:0.3,pointBackgroundColor:C.gr,pointRadius:4}}]}},options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{display:false}}}},scales:{{...SC,y:{{...SC.y,title:{{display:true,text:"₹ Lakhs",color:TC}}}}}}}}}});
  const ao=["0–3 yrs","4–6 yrs","7–10 yrs","10+ yrs"],bag=grp(FD,"ag",x=>x.sp),al=ao.filter(k=>bag[k]);
  mk("c-agrp",{{type:"bar",data:{{labels:al,datasets:[{{label:"Avg Price",data:al.map(k=>+avg(bag[k]).toFixed(2)),backgroundColor:[C.gr,C.bl,C.am,C.re],borderRadius:5}}]}},options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{display:false}}}},scales:SC}}}});
  const mo=["<20k km","20k–50k km","50k–100k km","100k+ km"],bmg=grp(FD,"mg",x=>x.sp),ml=mo.filter(k=>bmg[k]);
  mk("c-mgrp",{{type:"bar",data:{{labels:ml,datasets:[{{label:"Avg Price",data:ml.map(k=>+avg(bmg[k]).toFixed(2)),backgroundColor:[C.gr,C.bl,C.am,C.re],borderRadius:5}}]}},options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{display:false}}}},scales:SC}}}});
  const bo=grp(FD,"ow"),ok=Object.keys(bo).sort((a,b)=>+a-+b);
  const ol=ok.map(k=>{{const n={{0:"0 (1st)",1:"1 (2nd)",2:"2 (3rd)",3:"3 (4th+)"}};return n[k]||k}});
  mk("c-oc",{{type:"bar",data:{{labels:ol,datasets:[{{label:"Cars",data:ok.map(k=>bo[k].length),backgroundColor:CAT,borderRadius:5}}]}},options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{display:false}}}},scales:SC}}}});
  mk("c-op",{{type:"bar",data:{{labels:ol,datasets:[{{label:"Avg Price",data:ok.map(k=>+avg(bo[k].map(x=>x.sp)).toFixed(2)),backgroundColor:[C.gr,C.bl,C.am,C.re],borderRadius:5}}]}},options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{display:false}}}},scales:SC}}}})
}}

// CORRELATION
function pearson(x,y){{const n=x.length,mx=avg(x),my=avg(y);let nm=0,dx=0,dy=0;for(let i=0;i<n;i++){{const a=x[i]-mx,b=y[i]-my;nm+=a*b;dx+=a*a;dy+=b*b}};return dx&&dy?nm/Math.sqrt(dx*dy):0}}
function doCorr(){{
  const keys=["sp","pp","km","age","ow"],labs=["Selling_Price","Present_Price","Kms_Driven","Age","Owner"];
  let h='<table style="border-collapse:separate;border-spacing:3px;font-size:11px"><tr><th style="padding:4px 8px;color:var(--tm)"></th>';
  labs.forEach(l=>{{h+=`<th style="padding:4px 6px;color:var(--tm);text-align:center;font-size:10px">${{l.replace("_","<br>")}}</th>`}});
  h+="</tr>";
  keys.forEach((kx,i)=>{{
    h+=`<tr><th style="padding:4px 8px;text-align:right;color:var(--tm);font-size:10px">${{labs[i].replace("_","<br>")}}</th>`;
    keys.forEach((ky,j)=>{{
      const r=FD.length>1?pearson(FD.map(d=>d[kx]),FD.map(d=>d[ky])):i===j?1:0;
      const abs=Math.abs(r);
      const bg=r>0?`rgba(37,99,235,${{abs.toFixed(2)}})`:`rgba(239,68,68,${{abs.toFixed(2)}})`;
      const tc=abs>0.5?"#fff":"var(--tx)";
      h+=`<td style="background:${{bg}};color:${{tc}};padding:8px 10px;border-radius:4px;text-align:center;font-weight:${{abs>0.7?700:400}};min-width:60px">${{r.toFixed(2)}}</td>`
    }});h+="</tr>"
  }});
  document.getElementById("corr").innerHTML=h+"</table>"
}}

// DEPRECIATION
function doDepr(){{
  const ad=avg(FD.map(x=>x.depr)),adp=avg(FD.map(x=>x.dpct)),mxd=Math.max(...FD.map(x=>x.depr)),mnd=Math.min(...FD.map(x=>x.dpct));
  document.getElementById("dkg").innerHTML=`
    <div class="dkc"><div class="dkl">Avg Depreciation</div><div class="dkv">₹${{ad.toFixed(2)}}L</div><div class="dks">Present − Selling</div></div>
    <div class="dkc"><div class="dkl">Avg Depreciation %</div><div class="dkv">${{adp.toFixed(1)}}%</div><div class="dks">Value lost from present</div></div>
    <div class="dkc"><div class="dkl">Max Depreciation</div><div class="dkv">₹${{mxd.toFixed(2)}}L</div><div class="dks">Highest single-car loss</div></div>
    <div class="dkc"><div class="dkl">Best Retention</div><div class="dkv" style="color:var(--gr)">${{mnd.toFixed(1)}}%</div><div class="dks">Lowest depreciation %</div></div>`;
  const byF=grp(FD,"fu");
  const dsA=Object.entries(byF).map(([f,r])=>({{label:f,data:r.map(x=>({{x:x.age,y:x.dpct}})),backgroundColor:(FC[f]||C.cy)+"99",pointRadius:4}}));
  mk("c-da",{{type:"scatter",data:{{datasets:dsA}},options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{...LG,position:"bottom"}}}},scales:{{x:{{...SC.x,title:{{display:true,text:"Car Age (Years)",color:TC}}}},y:{{...SC.y,title:{{display:true,text:"Depreciation %",color:TC}}}}}}}}}});
  const dsK=Object.entries(byF).map(([f,r])=>({{label:f,data:r.map(x=>({{x:x.km,y:x.dpct}})),backgroundColor:(FC[f]||C.cy)+"99",pointRadius:4}}));
  mk("c-dkm",{{type:"scatter",data:{{datasets:dsK}},options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{...LG,position:"bottom"}}}},scales:{{x:{{...SC.x,title:{{display:true,text:"Km Driven",color:TC}}}},y:{{...SC.y,title:{{display:true,text:"Depreciation %",color:TC}}}}}}}}}});
  function dbar(id,key,colors){{const m=grp(FD,key,x=>x.dpct),lb=Object.keys(m),vl=lb.map(k=>+avg(m[k]).toFixed(2));mk(id,{{type:"bar",data:{{labels:lb,datasets:[{{label:"Avg Depr %",data:vl,backgroundColor:colors,borderRadius:5}}]}},options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:c=>`${{c.raw}}%`}}}}}},scales:{{...SC,y:{{...SC.y,title:{{display:true,text:"Depreciation %",color:TC}}}}}}}}}})}}
  dbar("c-df","fu",[C.bl,C.am,C.gr]);dbar("c-dtr","tr",[C.pu,C.cy]);dbar("c-dsl","se",[C.bl,C.gr]);
  const ao=["0–3 yrs","4–6 yrs","7–10 yrs","10+ yrs"],bag=grp(FD,"ag",x=>x.dpct),al=ao.filter(k=>bag[k]);
  mk("c-dag",{{type:"bar",data:{{labels:al,datasets:[{{label:"Avg Depr %",data:al.map(k=>+avg(bag[k]).toFixed(2)),backgroundColor:[C.gr,C.bl,C.am,C.re],borderRadius:5}}]}},options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:c=>`${{c.raw}}%`}}}}}},scales:{{...SC,y:{{...SC.y,title:{{display:true,text:"Depreciation %",color:TC}}}}}}}}}})
}}

// CAR INSIGHTS
function doCar(){{
  const cm={{}};FD.forEach(d=>{{cm[d.nm]=(cm[d.nm]||0)+1}});
  const tp=Object.entries(cm).sort((a,b)=>b[1]-a[1]).slice(0,10);
  hbar("c-tc",tp.map(x=>x[0]),tp.map(x=>x[1]),"Listings","Number of Listings",CAT);
  const pm=grp(FD,"nm",x=>x.sp);
  const tpr=Object.entries(pm).filter(([k,v])=>v.length>=2).map(([k,v])=>[k,+avg(v).toFixed(2)]).sort((a,b)=>b[1]-a[1]).slice(0,10);
  hbar("c-tp",tpr.map(x=>x[0]),tpr.map(x=>x[1]),"₹L","Avg Selling Price (₹L)",CAT);
  const dm=grp(FD,"nm",x=>x.dpct);
  const tr=Object.entries(dm).filter(([k,v])=>v.length>=2).map(([k,v])=>[k,+avg(v).toFixed(1)]).sort((a,b)=>a[1]-b[1]).slice(0,10);
  hbar("c-tret",tr.map(x=>x[0]),tr.map(x=>x[1]),"Depr %","Avg Depreciation % (lower = better)",[C.gr])
}}
function hbar(id,lb,dt,su,yl,colors){{
  const bgs=colors.length>1?lb.map((_,i)=>colors[i%colors.length]+"cc"):dt.map(()=>colors[0]+"cc");
  mk(id,{{type:"bar",data:{{labels:lb,datasets:[{{label:yl,data:dt,backgroundColor:bgs,borderRadius:4}}]}},options:{{responsive:true,maintainAspectRatio:false,indexAxis:"y",plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:c=>`${{c.raw}} ${{su}}`}}}}}},scales:{{x:{{...SC.x,title:{{display:true,text:yl,color:TC}}}},y:{{...SC.y,ticks:{{...SC.y.ticks,font:{{size:10}}}}}}}}}}}})
}}

// CAR SEARCH
document.getElementById("car-search").addEventListener("input",function(){{
  const q=this.value.trim().toLowerCase(),div=document.getElementById("car-detail");
  if(!q){{div.style.display="none";return}}
  const m=FD.filter(d=>d.nm.toLowerCase().includes(q));
  if(!m.length){{div.style.display="block";div.innerHTML="<p style='color:var(--tm);font-size:13px'>No matches in current filter.</p>";return}}
  const names=[...new Set(m.map(d=>d.nm))].slice(0,3);
  div.style.display="block";
  div.innerHTML=names.map(n=>{{
    const cars=m.filter(d=>d.nm===n);
    return `<div style="margin-bottom:14px"><div style="font-size:14px;font-weight:700;text-transform:capitalize;margin-bottom:6px">${{n}} <span style="font-size:11px;color:var(--tm);font-weight:400">${{cars.length}} listing${{cars.length>1?"s":""}}</span></div><div class="cdg"><div class="cdi"><div class="dl">Avg Sell Price</div><div class="dv" style="color:var(--gr)">${{fmt(avg(cars.map(x=>x.sp)))}}</div></div><div class="cdi"><div class="dl">Avg Present Price</div><div class="dv">${{fmt(avg(cars.map(x=>x.pp)))}}</div></div><div class="cdi"><div class="dl">Avg Kms</div><div class="dv">${{Math.round(avg(cars.map(x=>x.km))).toLocaleString("en-IN")}}</div></div><div class="cdi"><div class="dl">Avg Age</div><div class="dv">${{avg(cars.map(x=>x.age)).toFixed(1)}} yrs</div></div><div class="cdi"><div class="dl">Avg Depr %</div><div class="dv" style="color:var(--re)">${{avg(cars.map(x=>x.dpct)).toFixed(1)}}%</div></div><div class="cdi"><div class="dl">Fuel</div><div class="dv">${{[...new Set(cars.map(x=>x.fu))].join(" / ")}}</div></div></div></div>`
  }}).join("")
}});

// DATA QUALITY
function buildDQ(){{
  function qnt(a,p){{const s=[...a].sort((a,b)=>a-b);const i=p*(s.length-1),lo=Math.floor(i),hi=Math.ceil(i);return s[lo]+(s[hi]-s[lo])*(i-lo)}}
  const cols=["sp","pp","km","age","ow"],colN=["Selling_Price","Present_Price","Kms_Driven","Age","Owner"];
  const stats=["count","mean","std","min","25%","50%","75%","max"];
  const S={{}};
  cols.forEach(c=>{{const v=DATA.map(d=>d[c]).filter(x=>!isNaN(x));const n=v.length,m=avg(v),sd=Math.sqrt(v.reduce((a,x)=>a+(x-m)**2,0)/n);S[c]={{count:n,mean:m,std:sd,min:Math.min(...v),"25%":qnt(v,.25),"50%":qnt(v,.5),"75%":qnt(v,.75),max:Math.max(...v)}}}});
  let h=`<thead><tr><th>Stat</th>${{colN.map(c=>`<th>${{c}}</th>`).join("")}}</tr></thead><tbody>`;
  stats.forEach(s=>{{h+=`<tr><td><strong>${{s}}</strong></td>${{cols.map(c=>`<td>${{S[c][s].toFixed(3)}}</td>`).join("")}}</tr>`}});
  document.getElementById("sum-tbl").innerHTML=h+"</tbody>";
  const prices=DATA.map(d=>d.sp).sort((a,b)=>a-b);
  const q1=qnt(prices,.25),q3=qnt(prices,.75),iqr=q3-q1,lo=q1-1.5*iqr,hi=q3+1.5*iqr;
  const out=DATA.filter(d=>d.sp<lo||d.sp>hi);
  document.getElementById("outlier-sec").innerHTML=`<table class="dt"><tr><th>Metric</th><th>Value</th></tr><tr><td>Q1 (25%)</td><td>₹${{q1.toFixed(2)}}L</td></tr><tr><td>Q3 (75%)</td><td>₹${{q3.toFixed(2)}}L</td></tr><tr><td>IQR</td><td>₹${{iqr.toFixed(2)}}L</td></tr><tr><td>Lower Fence</td><td>₹${{lo.toFixed(2)}}L</td></tr><tr><td>Upper Fence</td><td>₹${{hi.toFixed(2)}}L</td></tr><tr><td>Outliers Found</td><td><span class="badge ba">${{out.length}}</span></td></tr><tr><td>Examples</td><td style="font-size:11px">${{out.slice(0,5).map(d=>`${{d.nm}} @ ₹${{d.sp}}L`).join(", ")}}</td></tr></table>`
}}

// TABS
document.querySelectorAll(".tb").forEach(btn=>{{btn.addEventListener("click",function(){{
  document.querySelectorAll(".tb").forEach(b=>b.classList.remove("active"));
  document.querySelectorAll(".page").forEach(p=>p.classList.remove("active"));
  this.classList.add("active");
  document.getElementById("page-"+this.dataset.tab).classList.add("active");
  setTimeout(()=>Object.values(CH).forEach(c=>c&&c.resize&&c.resize()),60)
}})}});

// FILTER LISTENERS
document.querySelectorAll("#sidebar input").forEach(el=>el.addEventListener("change",update));
document.getElementById("ym").addEventListener("input",function(){{const mx=+document.getElementById("yx").value;if(+this.value>mx)this.value=mx;document.getElementById("ymv").textContent=this.value;update()}});
document.getElementById("yx").addEventListener("input",function(){{const mn=+document.getElementById("ym").value;if(+this.value<mn)this.value=mn;document.getElementById("yxv").textContent=this.value;update()}});
document.getElementById("reset-btn").addEventListener("click",()=>{{
  document.querySelectorAll("#sidebar input[type=checkbox]").forEach(cb=>cb.checked=true);
  document.getElementById("ym").value={year_min};document.getElementById("yx").value={year_max};
  document.getElementById("ymv").textContent="{year_min}";document.getElementById("yxv").textContent="{year_max}";
  update()
}});

buildDQ();
update();
</script>
</body>
</html>'''

# ── Write ─────────────────────────────────────────────────────────────────
with open(OUT_PATH, "w", encoding="utf-8") as f:
    f.write(HTML)

print(f"✅ Dashboard generated: {OUT_PATH}")
print(f"   Records embedded: {TOTAL}")
print(f"   Unique cars: {len(set(r[0] for r in rows))}")
print(f"   Year range: {year_min}–{year_max}")
print(f"   Open index.html in your browser to view!")
