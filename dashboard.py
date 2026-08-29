import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import warnings
warnings.filterwarnings("ignore")

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Car Market Analysis | Car Dekho",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS Theme ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html,body,[class*="css"]{font-family:'Inter',-apple-system,sans-serif!important;background-color:#0f1117!important;color:#f1f5f9!important}
.stApp{background:linear-gradient(135deg,#0f1117 0%,#0d1117 50%,#111827 100%)!important}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#13161f 0%,#0f1117 100%)!important;border-right:1px solid #2a2d3e!important}
h1,h2,h3,h4,h5,h6{color:#f1f5f9!important}
[data-testid="metric-container"]{background:linear-gradient(135deg,#1e2130,#252840)!important;border:1px solid #2a2d3e!important;border-radius:14px!important;padding:1.2rem 1.4rem!important;box-shadow:0 4px 20px rgba(0,0,0,.4)!important;transition:transform .2s,box-shadow .2s!important}
[data-testid="metric-container"]:hover{transform:translateY(-2px)!important;box-shadow:0 8px 32px rgba(59,130,246,.2)!important}
[data-testid="stMetricLabel"]{color:#94a3b8!important;font-size:.78rem!important;font-weight:500!important;text-transform:uppercase!important;letter-spacing:.06em!important}
[data-testid="stMetricValue"]{color:#f1f5f9!important;font-size:1.6rem!important;font-weight:700!important}
.stTabs [data-baseweb="tab-list"]{background:#1a1d27!important;border-radius:12px!important;padding:4px!important;gap:4px!important;border:1px solid #2a2d3e!important}
.stTabs [data-baseweb="tab"]{background:transparent!important;color:#94a3b8!important;border-radius:8px!important;font-weight:500!important;font-size:.85rem!important;padding:.45rem 1rem!important;border:none!important}
.stTabs [aria-selected="true"]{background:#3b82f6!important;color:#fff!important;box-shadow:0 2px 12px rgba(59,130,246,.4)!important}
.stButton>button{background:linear-gradient(135deg,#3b82f6,#6366f1)!important;color:#fff!important;border:none!important;border-radius:8px!important;font-weight:600!important;box-shadow:0 2px 12px rgba(59,130,246,.3)!important;padding:.5rem 1.2rem!important}
hr{border-color:#2a2d3e!important}
.insight-card{background:linear-gradient(135deg,#1e2130,#1a2040);border:1px solid #2a3060;border-left:4px solid #3b82f6;border-radius:10px;padding:1rem 1.2rem;margin:.4rem 0;font-size:.88rem;color:#cbd5e1;line-height:1.6}
.insight-card strong{color:#60a5fa}
.section-header{font-size:1rem;font-weight:600;color:#94a3b8;text-transform:uppercase;letter-spacing:.08em;margin:1.2rem 0 .5rem 0;padding-bottom:.4rem;border-bottom:1px solid #2a2d3e}
.page-title{font-size:1.9rem;font-weight:800;color:#f1f5f9;margin-bottom:.2rem}
.page-subtitle{font-size:.9rem;color:#64748b;margin-bottom:1.5rem}
::-webkit-scrollbar{width:6px;height:6px}
::-webkit-scrollbar-track{background:#1a1d27}
::-webkit-scrollbar-thumb{background:#3b82f6;border-radius:3px}
</style>
""", unsafe_allow_html=True)

# ─── Plotly Theme ───────────────────────────────────────────────────────────────
PT = dict(
    paper_bgcolor="#1e2130", plot_bgcolor="#1e2130",
    font=dict(family="Inter, sans-serif", color="#94a3b8", size=12),
    title_font=dict(size=14, color="#e2e8f0", family="Inter, sans-serif"),
    margin=dict(l=40, r=20, t=50, b=40),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)", font=dict(color="#94a3b8")),
    colorway=["#3b82f6","#10b981","#f59e0b","#8b5cf6","#ef4444","#06b6d4","#f97316"],
)
CM = {"Petrol":"#3b82f6","Diesel":"#f59e0b","CNG":"#10b981","Dealer":"#6366f1","Individual":"#f97316","Manual":"#06b6d4","Automatic":"#8b5cf6"}


def th(fig, x="", y=""):
    fig.update_layout(**PT)
    fig.update_xaxes(title_text=x, gridcolor="#2a2d3e", zerolinecolor="#2a2d3e", tickfont=dict(color="#64748b"))
    fig.update_yaxes(title_text=y, gridcolor="#2a2d3e", zerolinecolor="#2a2d3e", tickfont=dict(color="#64748b"))
    return fig


# ─── Data Loading ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "car_dekho_data.csv")
    d = pd.read_csv(p)
    d["Age"] = 2020 - d["Year"]
    d["Depreciation"] = d["Present_Price"] - d["Selling_Price"]
    d["Depreciation_Pct"] = (d["Depreciation"] / d["Present_Price"]) * 100
    d["Age_Group"] = pd.cut(d["Age"], [0,3,6,10,15,25],
        labels=["0-3 yrs","4-6 yrs","7-10 yrs","11-15 yrs","16+ yrs"], right=True)
    d["Mileage_Group"] = pd.cut(d["Kms_Driven"], [0,20000,50000,100000,200000,600000],
        labels=["<20K km","20-50K km","50-100K km","100-200K km","200K+ km"], right=True)
    return d


RAW = load_data()

# ─── Sidebar Filters ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="text-align:center;margin-bottom:1rem"><span style="font-size:2.2rem">🚗</span><br>'
                '<span style="font-weight:800;font-size:1.1rem;color:#f1f5f9">Car Dekho</span><br>'
                '<span style="font-size:.75rem;color:#64748b">Market Analysis Dashboard</span></div>',
                unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div class="section-header">🔍 Filters</div>', unsafe_allow_html=True)

    fuels = sorted(RAW["Fuel_Type"].unique())
    sel_fuel = st.multiselect("Fuel Type", fuels, default=fuels, key="fuel")
    sellers = sorted(RAW["Seller_Type"].unique())
    sel_seller = st.multiselect("Seller Type", sellers, default=sellers, key="seller")
    trans_opts = sorted(RAW["Transmission"].unique())
    sel_trans = st.multiselect("Transmission", trans_opts, default=trans_opts, key="trans")
    ymin, ymax = int(RAW["Year"].min()), int(RAW["Year"].max())
    sel_year = st.slider("Manufacturing Year", ymin, ymax, (ymin, ymax), key="year")
    amin, amax = int(RAW["Age"].min()), int(RAW["Age"].max())
    sel_age = st.slider("Car Age (years)", amin, amax, (amin, amax), key="age")
    owners = sorted(RAW["Owner"].unique())
    sel_own = st.multiselect("Previous Owners", owners, default=owners,
                              format_func=lambda x: f"{x} owners" if x != 1 else "1 owner", key="own")
    st.markdown("---")
    if st.button("↺ Reset Filters", use_container_width=True):
        st.rerun()
    st.markdown("---")
    st.markdown('<div style="font-size:.72rem;color:#475569;text-align:center">Dataset: Car Dekho · 301 records<br>Car Age = 2020 − Year</div>',
                unsafe_allow_html=True)

# ─── Apply Filters ──────────────────────────────────────────────────────────────
df = RAW.copy()
if sel_fuel:    df = df[df["Fuel_Type"].isin(sel_fuel)]
if sel_seller:  df = df[df["Seller_Type"].isin(sel_seller)]
if sel_trans:   df = df[df["Transmission"].isin(sel_trans)]
df = df[(df["Year"] >= sel_year[0]) & (df["Year"] <= sel_year[1])]
df = df[(df["Age"]  >= sel_age[0])  & (df["Age"]  <= sel_age[1])]
if sel_own:     df = df[df["Owner"].isin(sel_own)]
EMPTY = len(df) == 0

# ─── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Overview", "💰 Price Analysis", "📈 Market Trends",
    "📉 Depreciation", "🔍 Car Insights", "🧪 Data Quality",
])

# ══════════════════════════════════════════════════════════════════════════════
#  TAB 1 – OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="page-title">Market Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">High-level summary of the used-car market based on current filters</div>', unsafe_allow_html=True)

    if EMPTY:
        st.warning("⚠️ No records match the current filters. Please adjust your filters.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🚘 Total Cars",        f"{len(df):,}")
        c2.metric("💰 Avg Selling Price",  f"₹{df['Selling_Price'].mean():.2f}L")
        c3.metric("📉 Min Selling Price",  f"₹{df['Selling_Price'].min():.2f}L")
        c4.metric("📈 Max Selling Price",  f"₹{df['Selling_Price'].max():.2f}L")
        c5, c6, c7, c8 = st.columns(4)
        c5.metric("🏭 Avg Present Price",  f"₹{df['Present_Price'].mean():.2f}L")
        c6.metric("🛣️ Avg Kms Driven",    f"{df['Kms_Driven'].mean():,.0f} km")
        c7.metric("📅 Avg Car Age",        f"{df['Age'].mean():.1f} yrs")
        c8.metric("⚙️ Unique Models",      f"{df['Car_Name'].nunique()}")
        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            fig = px.histogram(df, x="Selling_Price", nbins=30,
                               color_discrete_sequence=["#3b82f6"],
                               title="Selling Price Distribution",
                               labels={"Selling_Price":"Selling Price (₹ Lakhs)"})
            fig.update_traces(marker_line_color="#1e2130", marker_line_width=0.5)
            st.plotly_chart(th(fig, "Selling Price (₹ Lakhs)", "Count"), use_container_width=True)

        with col2:
            fc = df["Fuel_Type"].value_counts().reset_index()
            fc.columns = ["Fuel_Type","Count"]
            fig2 = px.pie(fc, names="Fuel_Type", values="Count", hole=0.55,
                          color="Fuel_Type", color_discrete_map=CM, title="Fleet by Fuel Type")
            fig2.update_traces(textfont=dict(color="#e2e8f0"), textinfo="percent+label")
            st.plotly_chart(th(fig2), use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            sc = df["Seller_Type"].value_counts().reset_index()
            sc.columns = ["Seller_Type","Count"]
            fig3 = px.pie(sc, names="Seller_Type", values="Count", hole=0.55,
                          color="Seller_Type", color_discrete_map=CM, title="Fleet by Seller Type")
            fig3.update_traces(textfont=dict(color="#e2e8f0"), textinfo="percent+label")
            st.plotly_chart(th(fig3), use_container_width=True)

        with col4:
            tc = df["Transmission"].value_counts().reset_index()
            tc.columns = ["Transmission","Count"]
            fig4 = px.pie(tc, names="Transmission", values="Count", hole=0.55,
                          color="Transmission", color_discrete_map=CM, title="Fleet by Transmission")
            fig4.update_traces(textfont=dict(color="#e2e8f0"), textinfo="percent+label")
            st.plotly_chart(th(fig4), use_container_width=True)

        st.markdown("---")
        st.markdown("**🔑 Key Market Insights**")
        auto_d   = df[df["Transmission"]=="Automatic"]
        man_d    = df[df["Transmission"]=="Manual"]
        dealer_d = df[df["Seller_Type"]=="Dealer"]
        ind_d    = df[df["Seller_Type"]=="Individual"]
        auto_avg   = auto_d["Selling_Price"].mean()   if len(auto_d)>0   else 0
        man_avg    = man_d["Selling_Price"].mean()    if len(man_d)>0    else 0
        dealer_avg = dealer_d["Selling_Price"].mean() if len(dealer_d)>0 else 0
        ind_avg    = ind_d["Selling_Price"].mean()    if len(ind_d)>0    else 0
        top_fuel     = df.groupby("Fuel_Type")["Selling_Price"].mean().idxmax() if len(df)>0 else "-"
        top_fuel_avg = df.groupby("Fuel_Type")["Selling_Price"].mean().max()    if len(df)>0 else 0
        corr_pp  = df["Selling_Price"].corr(df["Present_Price"]) if len(df)>1 else 0
        corr_kms = df["Selling_Price"].corr(df["Kms_Driven"])    if len(df)>1 else 0

        i1, i2 = st.columns(2)
        with i1:
            if len(auto_d)>0 and len(man_d)>0:
                st.markdown(f'<div class="insight-card">⚙️ <strong>Automatic</strong> cars average <strong>₹{auto_avg:.2f}L</strong> vs <strong>₹{man_avg:.2f}L</strong> for <strong>Manual</strong> cars.</div>', unsafe_allow_html=True)
            if len(dealer_d)>0 and len(ind_d)>0:
                st.markdown(f'<div class="insight-card">🏪 <strong>Dealer</strong> listings average <strong>₹{dealer_avg:.2f}L</strong> vs <strong>₹{ind_avg:.2f}L</strong> for <strong>Individual</strong> sellers.</div>', unsafe_allow_html=True)
        with i2:
            if len(df)>0:
                st.markdown(f'<div class="insight-card">⛽ <strong>{top_fuel}</strong> cars have the highest avg resale price at <strong>₹{top_fuel_avg:.2f}L</strong>.</div>', unsafe_allow_html=True)
            if len(df)>1:
                st.markdown(f'<div class="insight-card">📊 <strong>Present Price</strong> has the strongest correlation with Selling Price (r = <strong>{corr_pp:.2f}</strong>), followed by Kms Driven (r = <strong>{corr_kms:.2f}</strong>).</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  TAB 2 – PRICE ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="page-title">Price Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Factors influencing used-car selling prices</div>', unsafe_allow_html=True)

    if EMPTY:
        st.warning("⚠️ No records match the current filters.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            fig = px.box(df, y="Selling_Price", color_discrete_sequence=["#3b82f6"],
                         title="Selling Price – Box Plot", points="outliers")
            st.plotly_chart(th(fig, "", "Selling Price (₹ Lakhs)"), use_container_width=True)
        with col2:
            fig2 = px.scatter(df, x="Present_Price", y="Selling_Price",
                              color="Fuel_Type", color_discrete_map=CM,
                              hover_data=["Car_Name","Year","Transmission"],
                              title="Selling Price vs Present Price", trendline="ols")
            st.plotly_chart(th(fig2, "Present Price (₹ Lakhs)", "Selling Price (₹ Lakhs)"), use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            fig3 = px.scatter(df, x="Age", y="Selling_Price",
                              color="Fuel_Type", color_discrete_map=CM,
                              hover_data=["Car_Name","Kms_Driven"],
                              title="Selling Price vs Car Age", trendline="ols")
            st.plotly_chart(th(fig3, "Car Age (years)", "Selling Price (₹ Lakhs)"), use_container_width=True)
        with col4:
            fig4 = px.scatter(df, x="Kms_Driven", y="Selling_Price",
                              color="Transmission", color_discrete_map=CM,
                              hover_data=["Car_Name","Age"],
                              title="Selling Price vs Kilometers Driven", trendline="ols")
            st.plotly_chart(th(fig4, "Kilometers Driven", "Selling Price (₹ Lakhs)"), use_container_width=True)

        col5, col6, col7 = st.columns(3)
        for col_w, grp_col in zip([col5, col6, col7], ["Fuel_Type","Transmission","Seller_Type"]):
            with col_w:
                gdf = df.groupby(grp_col)["Selling_Price"].mean().reset_index().sort_values("Selling_Price")
                fg = px.bar(gdf, x="Selling_Price", y=grp_col, orientation="h",
                            color=grp_col, color_discrete_map=CM,
                            title=f"Avg Price by {grp_col.replace('_',' ')}", text="Selling_Price")
                fg.update_traces(texttemplate="₹%{text:.2f}L", textposition="outside")
                st.plotly_chart(th(fg, "Avg Selling Price (₹ Lakhs)", ""), use_container_width=True)

        st.markdown("---")
        col8, col9 = st.columns(2)
        with col8:
            fig8 = px.box(df, x="Fuel_Type", y="Selling_Price", color="Fuel_Type",
                          color_discrete_map=CM, title="Price Distribution by Fuel Type", points="outliers")
            st.plotly_chart(th(fig8, "Fuel Type", "Selling Price (₹ Lakhs)"), use_container_width=True)
        with col9:
            fig9 = px.box(df, x="Seller_Type", y="Selling_Price", color="Seller_Type",
                          color_discrete_map=CM, title="Price Distribution by Seller Type", points="outliers")
            st.plotly_chart(th(fig9, "Seller Type", "Selling Price (₹ Lakhs)"), use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
#  TAB 3 – MARKET TRENDS
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="page-title">Market Trends</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Trends across manufacturing years, mileage, age cohorts, and ownership history</div>', unsafe_allow_html=True)

    if EMPTY:
        st.warning("⚠️ No records match the current filters.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            yc = df.groupby("Year").size().reset_index(name="Count")
            f1 = px.bar(yc, x="Year", y="Count", color_discrete_sequence=["#3b82f6"],
                        title="Cars Listed by Manufacturing Year", text="Count")
            f1.update_traces(textposition="outside")
            st.plotly_chart(th(f1, "Manufacturing Year", "Number of Cars"), use_container_width=True)
        with col2:
            yp = df.groupby("Year")["Selling_Price"].mean().reset_index()
            f2 = px.line(yp, x="Year", y="Selling_Price", markers=True,
                         color_discrete_sequence=["#10b981"],
                         title="Avg Selling Price by Manufacturing Year")
            f2.update_traces(line_width=2.5, marker_size=8)
            st.plotly_chart(th(f2, "Manufacturing Year", "Avg Selling Price (₹ Lakhs)"), use_container_width=True)

        st.markdown("---")
        col3, col4 = st.columns(2)
        with col3:
            ag = df.groupby("Age_Group", observed=True)["Selling_Price"].mean().reset_index()
            f3 = px.bar(ag, x="Age_Group", y="Selling_Price",
                        color="Age_Group", color_discrete_sequence=px.colors.sequential.Blues_r,
                        title="Avg Selling Price by Age Group", text="Selling_Price")
            f3.update_traces(texttemplate="₹%{text:.2f}L", textposition="outside", showlegend=False)
            st.plotly_chart(th(f3, "Age Group", "Avg Selling Price (₹ Lakhs)"), use_container_width=True)
        with col4:
            f4 = px.scatter(df, x="Age", y="Selling_Price", color="Transmission",
                            color_discrete_map=CM, hover_data=["Car_Name","Kms_Driven"],
                            title="Selling Price vs Age (with Trend)", trendline="ols")
            st.plotly_chart(th(f4, "Car Age (years)", "Selling Price (₹ Lakhs)"), use_container_width=True)

        st.markdown("---")
        col5, col6 = st.columns(2)
        with col5:
            mg = df.groupby("Mileage_Group", observed=True)["Selling_Price"].mean().reset_index()
            f5 = px.bar(mg, x="Mileage_Group", y="Selling_Price",
                        color="Mileage_Group", color_discrete_sequence=px.colors.sequential.Purples_r,
                        title="Avg Selling Price by Mileage Group", text="Selling_Price")
            f5.update_traces(texttemplate="₹%{text:.2f}L", textposition="outside", showlegend=False)
            st.plotly_chart(th(f5, "Mileage Group", "Avg Selling Price (₹ Lakhs)"), use_container_width=True)
        with col6:
            mc = df.groupby("Mileage_Group", observed=True).size().reset_index(name="Count")
            f6 = px.pie(mc, names="Mileage_Group", values="Count", hole=0.55,
                        title="Fleet Composition by Mileage")
            f6.update_traces(textfont=dict(color="#e2e8f0"), textinfo="percent+label")
            st.plotly_chart(th(f6), use_container_width=True)

        st.markdown("---")
        col7, col8 = st.columns(2)
        with col7:
            oc = df.groupby("Owner").size().reset_index(name="Count")
            oc["Label"] = oc["Owner"].apply(lambda x: f"{x} Owners" if x != 1 else "1 Owner")
            f7 = px.bar(oc, x="Label", y="Count", color_discrete_sequence=["#6366f1"],
                        title="Cars by Previous Owners", text="Count")
            f7.update_traces(textposition="outside")
            st.plotly_chart(th(f7, "Previous Owners", "Count"), use_container_width=True)
        with col8:
            op = df.groupby("Owner")["Selling_Price"].mean().reset_index()
            op["Label"] = op["Owner"].apply(lambda x: f"{x} Owners" if x != 1 else "1 Owner")
            f8 = px.line(op, x="Label", y="Selling_Price", markers=True,
                         color_discrete_sequence=["#f59e0b"],
                         title="Avg Selling Price by Previous Owners")
            f8.update_traces(line_width=2.5, marker_size=10)
            st.plotly_chart(th(f8, "Previous Owners", "Avg Selling Price (₹ Lakhs)"), use_container_width=True)

        st.markdown("---")
        col9, col10 = st.columns(2)
        with col9:
            ft = df.groupby(["Fuel_Type","Transmission"]).size().reset_index(name="Count")
            f9 = px.bar(ft, x="Fuel_Type", y="Count", color="Transmission", barmode="group",
                        color_discrete_map=CM, title="Fuel Type x Transmission Composition")
            st.plotly_chart(th(f9, "Fuel Type", "Count"), use_container_width=True)
        with col10:
            sf = df.groupby(["Seller_Type","Fuel_Type"]).size().reset_index(name="Count")
            f10 = px.bar(sf, x="Seller_Type", y="Count", color="Fuel_Type", barmode="stack",
                         color_discrete_map=CM, title="Seller Type x Fuel Type Composition")
            st.plotly_chart(th(f10, "Seller Type", "Count"), use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
#  TAB 4 – DEPRECIATION
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="page-title">Depreciation Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">How much value does a car lose relative to its showroom price?</div>', unsafe_allow_html=True)
    st.markdown('<div class="insight-card">Depreciation = Present Price − Selling Price &nbsp;|&nbsp; Depreciation % = (Depreciation / Present Price) × 100</div>', unsafe_allow_html=True)

    if EMPTY:
        st.warning("⚠️ No records match the current filters.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("📉 Avg Depreciation",   f"₹{df['Depreciation'].mean():.2f}L")
        c2.metric("📊 Avg Depreciation %", f"{df['Depreciation_Pct'].mean():.1f}%")
        c3.metric("⬇️ Min Depreciation",   f"₹{df['Depreciation'].min():.2f}L")
        c4.metric("⬆️ Max Depreciation",   f"₹{df['Depreciation'].max():.2f}L")
        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            f1 = px.scatter(df, x="Age", y="Depreciation_Pct", color="Fuel_Type",
                            color_discrete_map=CM, hover_data=["Car_Name","Selling_Price","Present_Price"],
                            title="Depreciation % vs Car Age", trendline="ols")
            st.plotly_chart(th(f1, "Car Age (years)", "Depreciation (%)"), use_container_width=True)
        with col2:
            f2 = px.scatter(df, x="Kms_Driven", y="Depreciation_Pct", color="Transmission",
                            color_discrete_map=CM, hover_data=["Car_Name","Age"],
                            title="Depreciation % vs Kilometers Driven", trendline="ols")
            st.plotly_chart(th(f2, "Kilometers Driven", "Depreciation (%)"), use_container_width=True)

        col3, col4, col5 = st.columns(3)
        for col_w, grp_col in zip([col3, col4, col5], ["Fuel_Type","Transmission","Seller_Type"]):
            with col_w:
                gdf = df.groupby(grp_col)["Depreciation_Pct"].mean().reset_index().sort_values("Depreciation_Pct")
                fg = px.bar(gdf, x="Depreciation_Pct", y=grp_col, orientation="h",
                            color=grp_col, color_discrete_map=CM,
                            title=f"Avg Dep% by {grp_col.replace('_',' ')}", text="Depreciation_Pct")
                fg.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
                st.plotly_chart(th(fg, "Avg Depreciation (%)", ""), use_container_width=True)

        st.markdown("---")
        col6, col7 = st.columns(2)
        with col6:
            ad = df.groupby("Age_Group", observed=True)["Depreciation_Pct"].mean().reset_index()
            f6 = px.line(ad, x="Age_Group", y="Depreciation_Pct", markers=True,
                         color_discrete_sequence=["#ef4444"],
                         title="Avg Depreciation % by Age Group")
            f6.update_traces(line_width=2.5, marker_size=10)
            st.plotly_chart(th(f6, "Age Group", "Avg Depreciation (%)"), use_container_width=True)
        with col7:
            f7 = px.histogram(df, x="Depreciation_Pct", nbins=25,
                              color_discrete_sequence=["#ef4444"],
                              title="Distribution of Depreciation %")
            f7.update_traces(marker_line_color="#1e2130", marker_line_width=0.5)
            st.plotly_chart(th(f7, "Depreciation (%)", "Count"), use_container_width=True)

        hdep = df.groupby("Fuel_Type")["Depreciation_Pct"].mean()
        hf, lf = hdep.idxmax(), hdep.idxmin()
        st.markdown("**💡 Depreciation Insights**")
        i1, i2 = st.columns(2)
        with i1:
            st.markdown(f'<div class="insight-card">⛽ <strong>{hf}</strong> cars depreciate most on average (<strong>{hdep[hf]:.1f}%</strong>).</div>', unsafe_allow_html=True)
        with i2:
            st.markdown(f'<div class="insight-card">💡 <strong>{lf}</strong> cars retain value best — avg depreciation of only <strong>{hdep[lf]:.1f}%</strong>.</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  TAB 5 – CAR INSIGHTS
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="page-title">Car Insights</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Popular models, top earners, and individual car deep-dive</div>', unsafe_allow_html=True)

    if EMPTY:
        st.warning("⚠️ No records match the current filters.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            t10c = df["Car_Name"].value_counts().head(10).reset_index()
            t10c.columns = ["Car_Name","Count"]
            t10c = t10c.sort_values("Count")
            f1 = px.bar(t10c, x="Count", y="Car_Name", orientation="h",
                        color="Count", color_continuous_scale="Blues",
                        title="Top 10 Most Listed Cars", text="Count")
            f1.update_traces(textposition="outside")
            f1.update_coloraxes(showscale=False)
            st.plotly_chart(th(f1, "Listings", ""), use_container_width=True)

        with col2:
            t10p = df.groupby("Car_Name")["Selling_Price"].agg(["mean","count"]).reset_index()
            t10p.columns = ["Car_Name","Avg_Price","Count"]
            t10p = t10p[t10p["Count"]>=2].sort_values("Avg_Price", ascending=False).head(10).sort_values("Avg_Price")
            f2 = px.bar(t10p, x="Avg_Price", y="Car_Name", orientation="h",
                        color="Avg_Price", color_continuous_scale="Greens",
                        title="Top Cars by Avg Selling Price (≥2 listings)", text="Avg_Price")
            f2.update_traces(texttemplate="₹%{text:.2f}L", textposition="outside")
            f2.update_coloraxes(showscale=False)
            st.plotly_chart(th(f2, "Avg Selling Price (₹ Lakhs)", ""), use_container_width=True)

        st.markdown("---")
        col3, col4 = st.columns(2)
        dep_car = df.groupby("Car_Name")["Depreciation_Pct"].agg(["mean","count"]).reset_index()
        dep_car.columns = ["Car_Name","Avg_Dep","Count"]
        dep_car = dep_car[dep_car["Count"]>=2]

        with col3:
            td = dep_car.sort_values("Avg_Dep", ascending=False).head(10).sort_values("Avg_Dep")
            f3 = px.bar(td, x="Avg_Dep", y="Car_Name", orientation="h",
                        color="Avg_Dep", color_continuous_scale="Reds",
                        title="Top Cars – Highest Avg Depreciation % (≥2 listings)", text="Avg_Dep")
            f3.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            f3.update_coloraxes(showscale=False)
            st.plotly_chart(th(f3, "Avg Depreciation (%)", ""), use_container_width=True)

        with col4:
            ld = dep_car.sort_values("Avg_Dep").head(10).sort_values("Avg_Dep")
            f4 = px.bar(ld, x="Avg_Dep", y="Car_Name", orientation="h",
                        color="Avg_Dep", color_continuous_scale="Greens",
                        title="Top Cars – Lowest Avg Depreciation % (≥2 listings)", text="Avg_Dep")
            f4.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            f4.update_coloraxes(showscale=False)
            st.plotly_chart(th(f4, "Avg Depreciation (%)", ""), use_container_width=True)

        st.markdown("---")
        st.markdown("**🔎 Individual Car Deep-Dive**")
        avail = sorted(df["Car_Name"].unique())
        sel_car = st.selectbox("Select a Car Model", avail, key="car_sel")
        car_df = df[df["Car_Name"]==sel_car]
        if len(car_df)>0:
            m1,m2,m3,m4,m5 = st.columns(5)
            m1.metric("Listings",           f"{len(car_df)}")
            m2.metric("Avg Selling Price",  f"₹{car_df['Selling_Price'].mean():.2f}L")
            m3.metric("Avg Present Price",  f"₹{car_df['Present_Price'].mean():.2f}L")
            m4.metric("Avg Depreciation %", f"{car_df['Depreciation_Pct'].mean():.1f}%")
            m5.metric("Avg Kms Driven",     f"{car_df['Kms_Driven'].mean():,.0f}")
            ca, cb = st.columns(2)
            with ca:
                fc = px.scatter(car_df, x="Age", y="Selling_Price", color="Fuel_Type",
                                color_discrete_map=CM, hover_data=["Year","Kms_Driven","Transmission","Seller_Type"],
                                title=f"{sel_car.title()} – Price vs Age")
                st.plotly_chart(th(fc, "Car Age (years)", "Selling Price (₹ Lakhs)"), use_container_width=True)
            with cb:
                fc2 = px.scatter(car_df, x="Kms_Driven", y="Selling_Price", color="Transmission",
                                 color_discrete_map=CM, hover_data=["Year","Age","Fuel_Type"],
                                 title=f"{sel_car.title()} – Price vs Kms Driven")
                st.plotly_chart(th(fc2, "Kilometers Driven", "Selling Price (₹ Lakhs)"), use_container_width=True)
            with st.expander(f"📋 View all {sel_car.title()} listings"):
                disp = ["Car_Name","Year","Selling_Price","Present_Price","Kms_Driven",
                        "Fuel_Type","Seller_Type","Transmission","Owner","Age","Depreciation_Pct"]
                st.dataframe(car_df[disp].rename(columns={
                    "Car_Name":"Model","Selling_Price":"Selling (₹L)","Present_Price":"Present (₹L)",
                    "Kms_Driven":"Kms","Depreciation_Pct":"Dep%"}).reset_index(drop=True),
                    use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
#  TAB 6 – DATA QUALITY
# ══════════════════════════════════════════════════════════════════════════════
with tab6:
    st.markdown('<div class="page-title">Data Quality Report</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Dataset completeness, structure, distributions, and outlier detection</div>', unsafe_allow_html=True)

    fdf = RAW.copy()
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("📋 Total Records",   f"{len(fdf):,}")
    c2.metric("🗂️ Columns",         f"{fdf.shape[1]}")
    c3.metric("❌ Missing Values",  f"{fdf.isnull().sum().sum()}")
    c4.metric("🔁 Duplicate Rows",  f"{fdf.duplicated().sum()}")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        uv = fdf.nunique().reset_index()
        uv.columns = ["Column","Unique Values"]
        fu = px.bar(uv, x="Unique Values", y="Column", orientation="h",
                    color_discrete_sequence=["#3b82f6"],
                    title="Unique Values per Column", text="Unique Values")
        fu.update_traces(textposition="outside")
        st.plotly_chart(th(fu, "Count", ""), use_container_width=True)
    with col2:
        mv = fdf.isnull().sum().reset_index()
        mv.columns = ["Column","Missing"]
        fm = px.bar(mv, x="Missing", y="Column", orientation="h",
                    color_discrete_sequence=["#ef4444"],
                    title="Missing Values per Column", text="Missing")
        fm.update_traces(textposition="outside")
        st.plotly_chart(th(fm, "Count", ""), use_container_width=True)

    st.markdown("---")
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("**📐 Column Data Types**")
        dt = fdf.dtypes.reset_index()
        dt.columns = ["Column","Type"]
        dt["Type"] = dt["Type"].astype(str)
        st.dataframe(dt, use_container_width=True)
    with col4:
        st.markdown("**📊 Numerical Summary Statistics**")
        nc = ["Selling_Price","Present_Price","Kms_Driven","Age"]
        desc = fdf[nc].describe().T.round(2)
        desc.index.name = "Column"
        st.dataframe(desc, use_container_width=True)

    st.markdown("---")
    st.markdown("**🚨 Outlier Detection (IQR Method)**")
    nf = ["Selling_Price","Present_Price","Kms_Driven"]
    rows = []
    for cn in nf:
        Q1 = fdf[cn].quantile(0.25); Q3 = fdf[cn].quantile(0.75); IQR = Q3-Q1
        lo = Q1-1.5*IQR; hi = Q3+1.5*IQR
        n_out = ((fdf[cn]<lo)|(fdf[cn]>hi)).sum()
        rows.append({"Feature":cn,"Q1":round(Q1,2),"Q3":round(Q3,2),"IQR":round(IQR,2),
                     "Lower Bound":round(lo,2),"Upper Bound":round(hi,2),"Outliers":n_out})
    st.dataframe(pd.DataFrame(rows), use_container_width=True)

    obc1, obc2, obc3 = st.columns(3)
    for col_w, feat in zip([obc1,obc2,obc3], nf):
        with col_w:
            fb = px.box(fdf, y=feat, color_discrete_sequence=["#3b82f6"],
                        title=f"{feat} – Outlier View", points="outliers")
            st.plotly_chart(th(fb, "", feat), use_container_width=True)

    st.markdown("---")
    st.markdown("**🔗 Correlation Heatmap**")
    num_df = fdf[["Selling_Price","Present_Price","Kms_Driven","Age","Owner"]].corr().round(2)
    fh = go.Figure(data=go.Heatmap(
        z=num_df.values, x=num_df.columns.tolist(), y=num_df.index.tolist(),
        colorscale="RdBu", zmin=-1, zmax=1,
        text=num_df.values.round(2), texttemplate="%{text}",
        textfont=dict(size=12, color="white"),
        colorbar=dict(title="r", tickfont=dict(color="#94a3b8"), title_font=dict(color="#94a3b8")),
    ))
    fh.update_layout(title="Correlation Matrix – Numerical Features", **PT,
                     xaxis=dict(tickfont=dict(color="#94a3b8")),
                     yaxis=dict(tickfont=dict(color="#94a3b8")))
    st.plotly_chart(fh, use_container_width=True)

    st.markdown("**📌 Strongest Correlations with Selling Price**")
    cs = num_df["Selling_Price"].drop("Selling_Price").sort_values(key=abs, ascending=False)
    for feat, val in cs.items():
        direction = "positively" if val > 0 else "negatively"
        strength = "very strongly" if abs(val)>0.8 else ("strongly" if abs(val)>0.5 else ("moderately" if abs(val)>0.3 else "weakly"))
        st.markdown(f'<div class="insight-card">📊 <strong>{feat}</strong> is {strength} {direction} correlated with Selling Price (r = <strong>{val:.2f}</strong>).</div>', unsafe_allow_html=True)

# ─── Footer ──────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown('<div style="text-align:center;color:#475569;font-size:.78rem;padding:.5rem 0">🚗 Car Market Analysis Dashboard &nbsp;·&nbsp; Car Dekho Dataset &nbsp;·&nbsp; Built with Streamlit & Plotly &nbsp;·&nbsp; Data Analyst Portfolio Project</div>', unsafe_allow_html=True)
