import sys
import yfinance as yf
import pandas as pd

class YFinanceDataFetcher:
    def __init__(self, ticker):
        self.ticker = ticker
        # Initialize the yfinance Ticker object
        self.ticker_obj = yf.Ticker(ticker)
    
    def _get_latest_financial_data(self, df_type):
        """Helper to get the latest quarterly data from a financial DataFrame."""
        if df_type.empty:
            return {}
        
        # The first column of the yfinance DataFrame is the latest report.
        latest_data = df_type.iloc[:, 0].to_dict()
        return latest_data

    def get_quote(self):
        """Get current share price (uses the Ticker's info attribute)"""
        # .info fetches various general data, including price
        info = self.ticker_obj.info
        
        # Map yfinance key to the key expected by fetch_all_data
        price = info.get('currentPrice') or info.get('regularMarketPrice')
        return {'price': price if price is not None else 0}

    def get_income_statement(self, period="quarter"):
        """
        Get latest quarterly income statement.
        The 'period' argument is kept for signature consistency but forced to quarterly.
        """
        df = self.ticker_obj.quarterly_income_stmt
        latest_data = self._get_latest_financial_data(df)

        if not latest_data:
            return {}
            
        # yfinance often requires calculating Operating Expenses (OPEX)
        # by summing components like R&D and SG&A, as a single OPEX field is rare.
        rd = latest_data.get('Research And Development')
        sga = latest_data.get('Selling General And Administrative')
        
        # Map yfinance fields (row index names) to the original FMP keys
        return {
            'revenue': latest_data.get('Total Revenue'),
            'costOfRevenue': latest_data.get('Cost Of Revenue'),
            # Calculated OPEX
            'operatingExpenses': (rd if pd.notna(rd) else 0) + (sga if pd.notna(sga) else 0),
            'operatingIncome': latest_data.get('Operating Income'),
        }

    def get_balance_sheet(self, period="quarter"):
        """
        Get latest quarterly balance sheet.
        """
        df = self.ticker_obj.quarterly_balance_sheet
        latest_data = self._get_latest_financial_data(df)
        
        if not latest_data:
            return {}

        # Map yfinance fields (row index names) to the original FMP keys
        return {
            'cashAndCashEquivalents': latest_data.get('Cash And Cash Equivalents'),
            'totalDebt': latest_data.get('Total Debt'),
            # Note: Total Debt may be null; in complex scenarios, you might sum 
            # Short-term and Long-term debt from the DataFrame.
        }

    def get_shares_outstanding(self):
        """Get shares outstanding (uses the Ticker's info attribute)"""
        info = self.ticker_obj.info
        # Use 'sharesOutstanding' which is the closest match to the original FMP field
        return info.get('sharesOutstanding', 0)

    def fetch_all_data(self):
        """
        Fetch all financial data.
        The structure of this method is identical to your original code.
        """
        quote = self.get_quote()
        income = self.get_income_statement()
        balance = self.get_balance_sheet()
        shares = self.get_shares_outstanding()
        
        # This dictionary creation is UNCHANGED from your original code
        # It relies on the helper methods returning data with the expected keys.
        financial_data = {
            'Share Price': quote.get('price', 0),
            'Shares Outstanding': shares / 1000,  # in thousands
            'Revenue (Qtr)': income.get('revenue', 0) / 1000,  
            'COGS': income.get('costOfRevenue', 0) / 1000,  
            'OPEX': income.get('operatingExpenses', 0) / 1000,  
            'Operating Profit': income.get('operatingIncome', 0) / 1000,  
            'Cash': balance.get('cashAndCashEquivalents', 0) / 1000,  
            'Debt': balance.get('totalDebt', 0) / 1000, 
        }
        
        return financial_data

# --- Example Usage ---
if __name__ == "__main__":

    '''
    ticker = sys.argv[1] if len(sys.argv) > 1 else "MSFT"
    
    print(f"Fetching data for: {ticker}")
    
    fetcher = YFinanceDataFetcher(ticker)
    data = fetcher.fetch_all_data()
    
    # Pretty print the results
    import json
    print(json.dumps(data, indent=4))
    '''