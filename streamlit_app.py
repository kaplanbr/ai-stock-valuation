import streamlit as st
import pandas as pd
import os
import sys
import time

# Ensure the current directory is in the python path so imports work
sys.path.append(os.getcwd())

# Import your existing functions
try:
    from src.stock_valuation import value_stock
    from src.llm_valuation_summary import (
        load_valuation_excel, 
        generate_llm_investment_summary, 
        write_llm_result_to_excel
    )
except ImportError as e:
    st.error(f"Import Error: {e}. Make sure 'stock_valuation.py' and 'llm_valuation_summary.py' are correctly located in the 'src' directory.")
    st.stop()

# Page Config
st.set_page_config(page_title="AI Stock Valuation", layout="wide")

# --- Base CSS for padding etc. (colors handled via Styler) ---
st.markdown("""
<style>
    h3, h2, h1 { padding-top: 0.5rem; }
    .block-container { padding-top: 1.5rem; }
</style>
""", unsafe_allow_html=True)


# ---------- HELPER: styled table ----------
def styled_table(df: pd.DataFrame, numeric_cols=None):
    """
    Returns a pandas Styler with:
    - hidden index (no row numbers)
    - colored header and striped rows
    - left-aligned text columns, right-aligned numeric columns
    """
    if numeric_cols is None:
        numeric_cols = []

    # Ensure we don't mutate original
    df_disp = df.copy()

    # Format numeric columns with comma & 2 decimals
    for col in numeric_cols:
        if col in df_disp.columns:
            df_disp[col] = df_disp[col].apply(
                lambda x: f"{x:,.2f}" if isinstance(x, (int, float)) else x
            )

    # hide index (no row numbers)
    styler = df_disp.style.hide(axis="index")

    # Table styles (colors, borders, striping)
    styler = styler.set_table_styles([
        {
            "selector": "table",
            "props": [
                ("border-collapse", "collapse"),
                ("border", "1px solid #e5e7eb"),
                ("border-radius", "8px"),
                ("overflow", "hidden"),
                ("width", "100%")
            ],
        },
        {
            "selector": "th",
            "props": [
                ("background-color", "#f3f4f6"),
                ("color", "#111827"),
                ("font-weight", "600"),
                ("padding", "0.45rem 0.75rem"),
                ("border", "1px solid #e5e7eb"),
                ("text-align", "left"),
                ("font-size", "0.9rem"),
            ],
        },
        {
            "selector": "td",
            "props": [
                ("padding", "0.45rem 0.75rem"),
                ("border", "1px solid #e5e7eb"),
                ("font-size", "0.9rem"),
            ],
        },
        {
            "selector": "tbody tr:nth-child(odd)",
            "props": [("background-color", "#ffffff")],
        },
        {
            "selector": "tbody tr:nth-child(even)",
            "props": [("background-color", "#f9fafb")],
        },
    ])

    # Alignment: text columns left, numeric columns right
    all_cols = list(df_disp.columns)
    text_cols = [c for c in all_cols if c not in numeric_cols]

    if text_cols:
        styler = styler.set_properties(
            subset=text_cols,
            **{"text-align": "left", "white-space": "nowrap"}
        )
    if numeric_cols:
        styler = styler.set_properties(
            subset=numeric_cols,
            **{"text-align": "right"}
        )

    return styler


st.title("🤖 AI Stock Valuation")
st.markdown("Enter a ticker symbol to generate a valuation model and an AI-driven investment report.")

# --- INPUT SECTION ---
with st.form(key="input_form"):
    col1, col2 = st.columns([3, 1])
    with col1:
        ticker_input = st.text_input("Ticker Symbol", placeholder="e.g., AAPL, MSFT").upper()
    with col2:
        st.write("")
        st.write("")
        submit_btn = st.form_submit_button("Run Analysis", type="primary", use_container_width=True)

# Initialize session state
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
if "ticker" not in st.session_state:
    st.session_state.ticker = ""
if "ai_excel_path" not in st.session_state:
    st.session_state.ai_excel_path = ""
if "report_text" not in st.session_state:
    st.session_state.report_text = ""
if "predictions" not in st.session_state:
    st.session_state.predictions = {}

# --- MAIN LOGIC ---
if submit_btn and ticker_input:
    st.session_state.ticker = ticker_input
    
    status_container = st.status("Processing...", expanded=True)
    
    try:
        # 1. Fetch Data
        status_container.write(f"📊 Fetching financial data for {ticker_input}...")
        value_stock(ticker_input)
        
        base_excel_path = os.path.join("data", "valuations", f"{ticker_input}.xlsx")
        if not os.path.exists(base_excel_path):
            raise FileNotFoundError(f"Could not find generated file: {base_excel_path}")

        # 2. Generate LLM Summary
        status_container.write("🧠 Generating AI Investment Summary...")
        context = load_valuation_excel(base_excel_path)
        
        llm_text = generate_llm_investment_summary(
            context, 
            provider="gemini", 
            model="gemini-2.5-flash" 
        )

        # 3. Write to Excel
        status_container.write("💾 Saving results and calculating scenarios...")
        report_text, predictions, ai_excel_path = write_llm_result_to_excel(
            excel_path=base_excel_path, 
            ticker=ticker_input, 
            llm_text=llm_text
        )
        
        st.session_state.ai_excel_path = ai_excel_path
        st.session_state.report_text = report_text
        st.session_state.predictions = predictions
        st.session_state.analysis_done = True
        
        status_container.update(label="Analysis Complete!", state="complete", expanded=False)




    except Exception as e:
        status_container.update(label="Error Occurred", state="error")
        st.error(f"An error occurred: {str(e)}")
        st.session_state.analysis_done = False

# --- RESULTS DISPLAY ---
if st.session_state.analysis_done:

    # download button 
    if st.session_state.ai_excel_path and os.path.exists(st.session_state.ai_excel_path):
        _, col_dl, _ = st.columns([1, 2, 1])
        with col_dl:
            with open(st.session_state.ai_excel_path, "rb") as f:
                st.download_button(
                    label="📥 Download Valuation Excel",
                    data=f,
                    file_name=os.path.basename(st.session_state.ai_excel_path),
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )
    
    st.divider()


    # Load and prepare data for Fundamentals & Scenarios
    if os.path.exists(st.session_state.ai_excel_path):

        df = pd.read_excel(st.session_state.ai_excel_path, header=None)
        df = df.iloc[:38, :3]  # keep A–C, and limit rows if needed

        # find split index
        split_idx = 20
        start_keyword = "Expected Revenue CAGR"
        for i, row in df.iterrows():
            val = row.iloc[0]
            if isinstance(val, str) and start_keyword in val:
                split_idx = i
                break

        # ---------- Fundamentals ----------
        df_fund = df.iloc[:split_idx].copy()
        df_fund.columns = ["Metric", "Qtr Value (000s)", "Notes"]

        df_fund_display = df_fund[["Metric", "Qtr Value (000s)"]].copy()
        df_fund_display = df_fund_display.dropna(how="all")
        df_fund_display = df_fund_display[df_fund_display["Metric"].notna()]
        df_fund_display = df_fund_display[
            df_fund_display["Metric"].astype(str).str.strip() != ""
        ]

        # ---------- Scenarios ----------
        df_scenarios = df.iloc[split_idx:].copy()
        df_scenarios.columns = ["Metric", "Mid Scenario", "Good Scenario"]

        df_scenarios = df_scenarios.dropna(how="all")
        df_scenarios = df_scenarios[df_scenarios["Metric"].notna()]
        df_scenarios = df_scenarios[
            df_scenarios["Metric"].astype(str).str.strip() != ""
        ]
        print(df_scenarios)
        print(df_fund_display)
        # ---- Fundamentals değerlerini çek ----
        def get_fund(metric):
            try:
                val = df_fund_display.loc[
                    df_fund_display["Metric"] == metric, "Qtr Value (000s)"
                ].iloc[0]
                return float(val)
            except IndexError:
                return None

        share_price   = get_fund("Share Price")
        shares_out    = get_fund("Shares Outstanding")
        revenue_qtr   = get_fund("Revenue (Qtr)")
        cogs          = get_fund("COGS")
        opex          = get_fund("OPEX")
        op_profit     = get_fund("Operating Profit")
        cash          = get_fund("Cash")
        debt          = get_fund("Debt")

        # ---- Python ile temel türevler ----
        market_cap       = share_price * shares_out if share_price and shares_out else None
        gross_profit     = revenue_qtr - cogs if revenue_qtr is not None and cogs is not None else None
        gross_margin     = (gross_profit / revenue_qtr) if revenue_qtr else None
        ebitda_ps        = op_profit / shares_out if op_profit is not None and shares_out else None
        operating_margin = (op_profit / revenue_qtr) if revenue_qtr else None
        net_cash         = (cash - debt) if cash is not None and debt is not None else None

        # Fundamentals tablosunu override et
        fund_overrides = {
            "Market Cap (auto)": market_cap,
            "Gross Profit": gross_profit,
            "Gross Margin": gross_margin,
            "Operating Margin": operating_margin,
            "Net Cash (auto)": net_cash,
            "EBITDA PS": ebitda_ps,
        }
        for metric, val in fund_overrides.items():
            if val is not None:
                mask = df_fund_display["Metric"] == metric
                if mask.any():
                    df_fund_display.loc[mask, "Qtr Value (000s)"] = val

        # ---- Scenarios değerlerini çek ----
        def get_scen(metric, col):
            try:
                val = df_scenarios.loc[df_scenarios["Metric"] == metric, col].iloc[0]
                return float(val)
            except IndexError:
                return None

        cagr_mid   = get_scen("Expected Revenue CAGR (5y)", "Mid Scenario")
        cagr_good  = get_scen("Expected Revenue CAGR (5y)", "Good Scenario")

        op_margin_mid   = get_scen("E Operated Margin", "Mid Scenario")
        op_margin_good  = get_scen("E Operated Margin", "Good Scenario")

        dil_mid   = get_scen("Expected Dilution (5y)", "Mid Scenario")
        dil_good  = get_scen("Expected Dilution (5y)", "Good Scenario")

        tax_mid   = get_scen("Tax rate", "Mid Scenario") or 0.21
        tax_good  = get_scen("Tax rate", "Good Scenario") or tax_mid

        mult_mid  = get_scen("Long Term Earning Multiple", "Mid Scenario") or 25
        mult_good = get_scen("Long Term Earning Multiple", "Good Scenario") or mult_mid


        # ---- senaryo bazlı hesaplama fonksiyonu ----
        def compute_scenario_targets(cagr, op_margin, tax_rate, dilution, multiple):
            if revenue_qtr is None or shares_out is None or cagr is None or op_margin is None:
                return None, None, None

            revenue_year0 = revenue_qtr * 4  # Q'dan yıla
            rev_5y = revenue_year0 * (1 + cagr) ** 5
            ebit_5y = rev_5y * op_margin
            earning_5y = ebit_5y * (1 - tax_rate)

            # basit P/E tarzı değerleme
            equity_5y = earning_5y * multiple

            shares_5y = shares_out * (1 + (dilution or 0.0))
            price_5y = equity_5y / shares_5y if shares_5y else None

            price_5y_disc = price_5y*((1.05 ** 5))  # 5% iskonto ile bugüne indirgeme

            return rev_5y, ebit_5y, earning_5y, shares_5y, price_5y, price_5y_disc

        e_rev_mid, e_ebit_mid, earning_mid,shares_mid, price_mid, price_mid_disc = compute_scenario_targets(
            cagr_mid, op_margin_mid, tax_mid, dil_mid, mult_mid
        )
        e_rev_good, e_ebit_good,earning_good,shares_good, price_good, price_good_disc = compute_scenario_targets(
            cagr_good, op_margin_good, tax_good, dil_good, mult_good
        )

        # EPS hesapla
        eps_mid = earning_mid / shares_mid  
        eps_good = earning_good / shares_good   

        # Scenarios tablosunda ilgili satırları override et
        scen_override_rows = {
            "E Revenue": (e_rev_mid, e_rev_good),
            "E EBITDA": (e_ebit_mid, e_ebit_good),
            "Earning": (earning_mid, earning_good),
            "E Shares Outstanding": (shares_mid, shares_good),
            "Expected EPS": (eps_mid, eps_good),
            "Predicted Share Price (5 yr)": (price_mid, price_good),
            "Predicted Share Price": (price_mid_disc, price_good_disc),
        }
        scen_metric_series = df_scenarios["Metric"].astype(str)
        for metric, (mid_val, good_val) in scen_override_rows.items():
            mask = scen_metric_series.str.contains(metric, na=False)
            if mask.any():
                if mid_val is not None:
                    df_scenarios.loc[mask, "Mid Scenario"] = mid_val
                if good_val is not None:
                    df_scenarios.loc[mask, "Good Scenario"] = good_val

        # ---- Valuation Targets prediction ----
        if share_price is not None and price_mid_disc is not None and price_good_disc is not None:
            st.session_state.predictions = {
                "ticker": st.session_state.ticker,
                "current_price": f"{share_price:.2f}",
                "lower_prediction": f"{price_mid_disc:.2f}",
                "upper_prediction": f"{price_good_disc:.2f}",
            }

        # 1. Top Level Metrics (Python hesaplarından)
        st.subheader("🎯 Valuation Targets")

        def show_metrics(preds):
            m1, m2, m3 = st.columns(3)
            m1.metric(
                "Current Price", preds.get("current_price", "N/A")
            )
            m2.metric("Mid Target", preds.get("lower_prediction", "N/A"))
            m3.metric("Upper Target", preds.get("upper_prediction", "N/A"))

        show_metrics(st.session_state.predictions)
        st.write("")


        # Fundamentals (25%) | Scenarios (25%) | AI Summary (50%)
        col_fund, col_scen, col_text = st.columns([1, 1, 2])


        with col_fund:
            st.subheader("📊 Fundamentals")
            st.markdown(
                styled_table(df_fund_display, numeric_cols=["Qtr Value (000s)"]).to_html(),
                unsafe_allow_html=True
            )

        with col_scen:
            st.subheader("📈 Scenarios")
            st.markdown(
                styled_table(
                    df_scenarios,
                    numeric_cols=["Mid Scenario", "Good Scenario"],
                ).to_html(),
                unsafe_allow_html=True
            )

        with col_text:
            st.subheader("📝 AI Analysis")
            st.info(st.session_state.report_text)

    else:
        st.warning("Data file missing.")

elif not submit_btn and not st.session_state.analysis_done:
    st.info("👈 Enter a ticker above to start.")
