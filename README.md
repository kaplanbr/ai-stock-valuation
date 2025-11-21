## Try Live App

You can use the live version here:

**https://ai-stock-valuation.streamlit.app/**

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

### 3. AI Valuation Summary
- Uses the latest quarterly earnings context  
- Generates a readable investment summary  


### 4. Streamlit Web Application
- Displays fundamentals + AI summary  
- Allows downloading the generated valuation Excel

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
