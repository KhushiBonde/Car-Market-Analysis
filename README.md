# 🚗 Car Market Analysis Dashboard — Car Dekho

A professional, interactive **used-car market analysis dashboard** built with **Streamlit** and **Plotly**. This project explores pricing patterns, depreciation trends, market composition, and model-level insights from the Car Dekho used-car dataset.

---

## 📋 Project Overview

### Problem Statement

The used-car market lacks transparency around fair pricing. Buyers and sellers need data-driven insights to understand how factors like car age, fuel type, transmission, mileage, and ownership history affect resale value.

### Objectives

- Analyze pricing patterns across fuel types, transmission, and seller types
- Quantify depreciation as a function of age, mileage, and category
- Identify the best and worst value-retaining car models
- Provide an interactive, filterable dashboard for exploration
- Deliver a professional portfolio-ready data analysis project

---

## 📊 Dataset

| Property | Value |
|---|---|
| **Source** | [Car Dekho](https://www.cardekho.com/) |
| **Records** | 301 |
| **Features** | 9 |
| **File** | `car_dekho_data.csv` |

### Columns

| Column | Type | Description |
|---|---|---|
| `Car_Name` | string | Car model name |
| `Year` | int | Manufacturing year |
| `Selling_Price` | float | Resale/selling price (₹ Lakhs) |
| `Present_Price` | float | Current showroom price (₹ Lakhs) |
| `Kms_Driven` | int | Total kilometers driven |
| `Fuel_Type` | category | Petrol / Diesel / CNG |
| `Seller_Type` | category | Dealer / Individual |
| `Transmission` | category | Manual / Automatic |
| `Owner` | int | Number of previous owners (0, 1, 2, 3) |

---

## ✨ Features

The Streamlit dashboard has **6 interactive tabs**:

1. **📊 Overview** — KPIs, price distribution, fleet composition (fuel, seller, transmission), and key market insights
2. **💰 Price Analysis** — Selling price vs present price, age, kms driven; average price by category; box plots with outlier detection
3. **📈 Market Trends** — Year-on-year trends, age group analysis, mileage group analysis, ownership history impact, cross-category composition
4. **📉 Depreciation** — Depreciation % vs age and mileage, category breakdowns, age group trends, distribution analysis
5. **🔍 Car Insights** — Top 10 most listed cars, top cars by price, highest/lowest depreciation models, individual car deep-dive with full listing view
6. **🧪 Data Quality** — Record counts, missing values, duplicates, column types, summary statistics, IQR outlier detection, correlation heatmap

### Interactive Filters (Sidebar)

- Fuel Type (multi-select)
- Seller Type (multi-select)
- Transmission (multi-select)
- Manufacturing Year (range slider)
- Car Age (range slider)
- Previous Owners (multi-select)
- Reset All Filters button

All charts and KPIs update dynamically. Empty-data states show a clear warning.

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| **Python 3.12** | Core language |
| **Streamlit** | Web dashboard framework |
| **Plotly** | Interactive visualizations |
| **Pandas** | Data manipulation |
| **NumPy** | Numerical operations |
| **Statsmodels** | OLS trendlines in scatter plots |

---

## 📁 Project Structure

```
Car-Market-Analysis/
├── dashboard.py           # Main Streamlit application (entry point)
├── car_dekho_data.csv     # Dataset (301 records)
├── Car_Dekho.ipynb        # Jupyter analysis notebook
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
├── .gitignore             # Git exclusions
├── .streamlit/
│   └── config.toml        # Streamlit theme & server config
├── build_dashboard.py     # Utility: generates index.html
├── gen_dashboard.py       # Utility: generates dashboard.py
└── index.html             # Static HTML dashboard (standalone)
```

---

## 🚀 Installation & Setup

### Prerequisites

- Python 3.10 or higher
- pip

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Locally

```bash
streamlit run dashboard.py
```

The dashboard will open at **http://localhost:8501**.

---

## ☁️ Deployment (Streamlit Community Cloud)

1. Push this project to a **GitHub repository**
2. Go to [share.streamlit.io](https://share.streamlit.io/)
3. Connect your GitHub account
4. Select the repository and set:
   - **Main file path:** `dashboard.py`
   - **Python version:** 3.10+
5. Click **Deploy**

### Required Files for Deployment

- `dashboard.py`
- `car_dekho_data.csv`
- `requirements.txt`
- `.streamlit/config.toml`

---

## 🔍 Key Analysis & Insights

- **Present Price** has the strongest positive correlation with Selling Price — the best single predictor of resale value
- **Diesel** cars command the highest average resale price
- **Automatic** transmission cars have a higher average selling price than Manual
- **Dealer** listings are priced higher on average than Individual sellers
- **CNG** cars retain value best (lowest depreciation %)
- **Newer cars (0–3 years)** fetch the highest resale prices
- **Higher mileage** generally correlates with lower resale value
- The dataset is clean with **zero missing values** and only **2 near-duplicate rows**

---

## 📓 Notebook

`Car_Dekho.ipynb` contains the exploratory data analysis (EDA) performed on the dataset. It covers data loading, cleaning, statistical summaries, and visualization of key patterns.

---

## 🔮 Future Improvements

- Add a machine learning price prediction model (e.g., Random Forest, XGBoost)
- Include more car features (engine size, mileage per liter, brand)
- Add time-series analysis with a larger dataset
- Implement user-uploadable CSV for custom analysis
- Add export functionality for filtered data

---

## 📄 License

This project is for educational and portfolio purposes.

---

*Built with ❤️ using Streamlit & Plotly*
