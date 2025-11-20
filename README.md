# Stock Valuation App

This project provides a complete automated stock valuation pipeline including:

- Financial data retrieval from the latest income statement and balance sheet  
- Intrinsic value estimation using a single-stage DCF model  
- Scenario calculations guided by AI-suggested assumptions  
- Excel-based valuation model for verification and deeper analysis  
- AI-generated valuation summary  
- Streamlit web interface to run valuations interactively

---

## Features

### 1. Financial Data Retrieval
Supports:
- Yahoo Finance

### 2. Excel-Based Valuation Model
- Populates fundamentals, scenarios, and fair-value predictions  
- Saves outputs to: `data/valuations/`

### 3. AI Valuation Summary
- Uses the latest quarterly earnings context  
- Generates a readable investment summary  
- Optionally writes results back to the valuation workbook

### 4. Streamlit Web Application
- Clean UI  
- Displays fundamentals + AI summary  
- Allows downloading the generated Excel valuation

---

## Project Structure

```
stock_val/
  data/
    format.xlsx
    valuations/
  src/
    fin_data_yf.py
    llm_valuation_summary.py
    stock_valuation.py
    __init__.py
  streamlit_app.py
  requirements.txt
  README.md
```

---

## Run Streamlit App

```
streamlit run streamlit_app.py
```
