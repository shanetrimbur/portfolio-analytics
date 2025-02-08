// src/portfolio_analytics/sec_data.py

import requests
import pandas as pd
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time

class SECDataAnalyzer:
    def __init__(self):
        self.base_url = "https://www.sec.gov/Archives/"
        self.edgar_url = "https://www.sec.gov/cgi-bin/browse-edgar"
        # Important: SEC requires a user-agent header with your email
        self.headers = {
            'User-Agent': 'Your Name yourname@email.com',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'www.sec.gov'
        }

    def get_company_filings(self, ticker, filing_type="10-K", limit=10):
        """
        Get recent SEC filings for a company
        
        Args:
            ticker (str): Company ticker symbol
            filing_type (str): Type of filing (10-K, 10-Q, 8-K, etc.)
            limit (int): Number of filings to retrieve
        """
        params = {
            'CIK': ticker,
            'type': filing_type,
            'owner': 'exclude',
            'count': limit,
            'action': 'getcompany',
            'output': 'json'
        }
        
        # Respect SEC's rate limit (10 requests/second)
        time.sleep(0.1)
        response = requests.get(self.edgar_url, params=params, headers=self.headers)
        
        if response.status_code != 200:
            raise Exception(f"Failed to fetch filings: {response.status_code}")
            
        return response.json()

    def extract_financial_data(self, filing_url):
        """
        Extract key financial metrics from a filing
        """
        # Respect SEC's rate limit
        time.sleep(0.1)
        response = requests.get(filing_url, headers=self.headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract key financial tables
        financial_data = {
            'income_statement': self._parse_income_statement(soup),
            'balance_sheet': self._parse_balance_sheet(soup),
            'cash_flow': self._parse_cash_flow(soup)
        }
        
        return financial_data

    def _parse_income_statement(self, soup):
        """Parse income statement data from filing"""
        metrics = {
            'revenue': self._find_metric(soup, ['revenue', 'sales']),
            'operating_income': self._find_metric(soup, ['operating income', 'income from operations']),
            'net_income': self._find_metric(soup, ['net income', 'net earnings']),
            'eps': self._find_metric(soup, ['earnings per share', 'eps'])
        }
        return metrics

    def _parse_balance_sheet(self, soup):
        """Parse balance sheet data from filing"""
        metrics = {
            'total_assets': self._find_metric(soup, ['total assets']),
            'total_liabilities': self._find_metric(soup, ['total liabilities']),
            'stockholders_equity': self._find_metric(soup, ['stockholders equity', 'shareholders equity']),
            'cash': self._find_metric(soup, ['cash and cash equivalents'])
        }
        return metrics

    def _parse_cash_flow(self, soup):
        """Parse cash flow data from filing"""
        metrics = {
            'operating_cash_flow': self._find_metric(soup, ['cash from operations']),
            'investing_cash_flow': self._find_metric(soup, ['cash from investing']),
            'financing_cash_flow': self._find_metric(soup, ['cash from financing'])
        }
        return metrics

    def _find_metric(self, soup, keywords):
        """Helper method to find specific metrics in the filing"""
        for keyword in keywords:
            elements = soup.find_all(string=lambda text: keyword.lower() in text.lower() if text else False)
            if elements:
                # Find nearest number
                for element in elements:
                    parent = element.parent
                    numbers = parent.find_all(string=lambda text: any(char.isdigit() for char in text) if text else False)
                    if numbers:
                        return self._clean_number(numbers[0])
        return None

    def _clean_number(self, text):
        """Clean and convert text number to float"""
        try:
            # Remove common text artifacts and convert to float
            cleaned = ''.join(filter(lambda x: x.isdigit() or x in '.-', text))
            return float(cleaned)
        except:
            return None

    def calculate_financial_ratios(self, financial_data):
        """Calculate key financial ratios from filing data"""
        try:
            income = financial_data['income_statement']
            balance = financial_data['balance_sheet']
            
            ratios = {
                'return_on_equity': income['net_income'] / balance['stockholders_equity'] if balance['stockholders_equity'] else None,
                'return_on_assets': income['net_income'] / balance['total_assets'] if balance['total_assets'] else None,
                'debt_to_equity': (balance['total_liabilities'] / balance['stockholders_equity']) if balance['stockholders_equity'] else None,
                'current_ratio': balance['total_assets'] / balance['total_liabilities'] if balance['total_liabilities'] else None
            }
            
            return ratios
        except Exception as e:
            print(f"Error calculating ratios: {e}")
            return {}

# Example usage:
"""
analyzer = SECDataAnalyzer()

# Get recent 10-K filings for Apple
filings = analyzer.get_company_filings('AAPL', '10-K')

# Get financial data from the most recent filing
latest_filing = filings[0]
financial_data = analyzer.extract_financial_data(latest_filing['url'])

# Calculate financial ratios
ratios = analyzer.calculate_financial_ratios(financial_data)
"""