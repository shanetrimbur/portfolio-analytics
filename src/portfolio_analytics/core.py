from typing import Dict, List, Optional, Union
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
import yfinance as yf
from scipy.optimize import minimize
import plotly.graph_objects as go
from datetime import datetime
import jinja2
import subprocess
from dataclasses import dataclass

@dataclass
class FixedIncomeInstrument:
    """Fixed Income instrument details"""
    face_value: float
    coupon_rate: float
    years_to_maturity: float
    payment_frequency: int  # payments per year
    current_price: float
    credit_rating: str

class FixedIncomeCalculator:
    """Enhanced fixed income calculations"""
    
    def __init__(self, instrument: FixedIncomeInstrument):
        self.instrument = instrument
        
    def calculate_ytm(self) -> float:
        """Calculate Yield to Maturity using Newton's method"""
        def npv(yield_rate):
            total_npv = -self.instrument.current_price
            payments_per_year = self.instrument.payment_frequency
            coupon_payment = (self.instrument.face_value * 
                            self.instrument.coupon_rate / payments_per_year)
            
            for t in range(1, int(self.instrument.years_to_maturity * 
                                payments_per_year) + 1):
                total_npv += coupon_payment / (1 + yield_rate/payments_per_year)**t
            
            total_npv += self.instrument.face_value / \
                        (1 + yield_rate/payments_per_year)**(self.instrument.years_to_maturity * 
                                                           payments_per_year)
            return total_npv
            
        # Find YTM using Newton's method
        ytm = minimize(lambda x: npv(x)**2, x0=0.05, method='Nelder-Mead').x[0]
        return float(ytm)
    
    def calculate_duration(self) -> Dict[str, float]:
        """Calculate both Macaulay and Modified Duration"""
        ytm = self.calculate_ytm()
        payments_per_year = self.instrument.payment_frequency
        coupon_payment = (self.instrument.face_value * 
                         self.instrument.coupon_rate / payments_per_year)
        
        # Calculate Macaulay Duration
        total_pv = 0
        weighted_pvs = 0
        
        for t in range(1, int(self.instrument.years_to_maturity * 
                             payments_per_year) + 1):
            pv_factor = 1 / (1 + ytm/payments_per_year)**t
            pv = coupon_payment * pv_factor
            total_pv += pv
            weighted_pvs += t * pv / payments_per_year
            
        # Add face value contribution
        final_pv = self.instrument.face_value / \
                  (1 + ytm/payments_per_year)**(self.instrument.years_to_maturity * 
                                               payments_per_year)
        total_pv += final_pv
        weighted_pvs += self.instrument.years_to_maturity * final_pv
        
        macaulay_duration = weighted_pvs / total_pv
        modified_duration = macaulay_duration / (1 + ytm/payments_per_year)
        
        return {
            'macaulay_duration': float(macaulay_duration),
            'modified_duration': float(modified_duration)
        }
        
    def calculate_convexity(self) -> float:
        """Calculate convexity"""
        ytm = self.calculate_ytm()
        payments_per_year = self.instrument.payment_frequency
        coupon_payment = (self.instrument.face_value * 
                         self.instrument.coupon_rate / payments_per_year)
        
        total_convexity = 0
        for t in range(1, int(self.instrument.years_to_maturity * 
                             payments_per_year) + 1):
            t_years = t / payments_per_year
            pv_factor = 1 / (1 + ytm/payments_per_year)**t
            total_convexity += t_years * (t_years + 1) * coupon_payment * pv_factor
            
        # Add face value contribution
        final_t = self.instrument.years_to_maturity
        final_pv_factor = 1 / (1 + ytm/payments_per_year)**(final_t * payments_per_year)
        total_convexity += final_t * (final_t + 1) * self.instrument.face_value * final_pv_factor
        
        convexity = total_convexity / ((1 + ytm/payments_per_year)**2 * self.instrument.current_price)
        return float(convexity)

class MarketDataIntegration:
    """Enhanced market data integration with multiple providers"""
    
    def __init__(self):
        self.providers = {
            'yahoo': self._fetch_yahoo_data,
            'alpha_vantage': self._fetch_alpha_vantage_data,
            'bloomberg': self._fetch_bloomberg_data
        }
        
    async def fetch_market_data(
        self,
        ticker: str,
        start_date: str,
        end_date: str,
        provider: str = 'yahoo'
    ) -> pd.DataFrame:
        """Fetch market data from specified provider"""
        if provider not in self.providers:
            raise ValueError(f"Unsupported provider: {provider}")
            
        return await self.providers[provider](ticker, start_date, end_date)
        
    async def _fetch_yahoo_data(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch data from Yahoo Finance"""
        return yf.download(ticker, start=start_date, end=end_date)
        
    async def _fetch_alpha_vantage_data(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch data from Alpha Vantage"""
        # Implementation using Alpha Vantage API
        pass
        
    async def _fetch_bloomberg_data(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch data from Bloomberg"""
        # Implementation using Bloomberg API
        pass

class LatexReportGenerator:
    """Generate professional LaTeX reports with Quantex branding"""
    
    def __init__(self):
        self.template_loader = jinja2.FileSystemLoader(searchpath="./templates")
        self.template_env = jinja2.Environment(loader=self.template_loader)
        
    def generate_report(
        self,
        portfolio_data: Dict,
        analysis_results: Dict,
        report_type: str = 'full'
    ) -> str:
        """Generate LaTeX report"""
        template = self.template_env.get_template(f"{report_type}_report.tex")
        
        # Prepare report data
        report_data = {
            'company_name': 'Quantex',
            'report_date': datetime.now().strftime("%Y-%m-%d"),
            'portfolio_data': portfolio_data,
            'analysis_results': analysis_results,
            'logo_path': './assets/quantex_logo.png'
        }
        
        # Generate LaTeX content
        latex_content = template.render(**report_data)
        
        # Save to file
        report_filename = f"quantex_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        with open(f"{report_filename}.tex", 'w') as f:
            f.write(latex_content)
            
        # Compile to PDF
        subprocess.run(['pdflatex', f"{report_filename}.tex"])
        
        return f"{report_filename}.pdf"

# Example LaTeX template
LATEX_TEMPLATE = r"""
\documentclass{article}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{geometry}
\usepackage{xcolor}
\usepackage{fancyhdr}

\definecolor{quantexblue}{RGB}{0, 82, 164}

\geometry{margin=1in}
\pagestyle{fancy}

\begin{document}

\begin{center}
    \includegraphics[width=3cm]{ {{logo_path}} }
    \huge{\textcolor{quantexblue}{\textbf{Quantex}}}
    \\\vspace{0.5cm}
    \large{Portfolio Analysis Report}
    \\\vspace{0.25cm}
    \normalsize{ {{report_date}} }
\end{center}

\section*{Portfolio Overview}
\begin{tabular}{lr}
\toprule
Total Assets & \${{ '{:,.2f}'.format(portfolio_data.total_assets) }} \\
Number of Securities & {{ portfolio_data.num_securities }} \\
\bottomrule
\end{tabular}

\section*{Performance Metrics}
\begin{tabular}{lr}
\toprule
Metric & Value \\
\midrule
{% for metric, value in analysis_results.metrics.items() %}
{{ metric }} & {{ '{:.4f}'.format(value) }} \\
{% endfor %}
\bottomrule
\end{tabular}

\end{document}
"""

# Add to your FastAPI application
app = FastAPI(title="Quantex Analytics API")

@app.post("/generate-report")
async def generate_report(
    portfolio_data: Dict,
    analysis_results: Dict,
    report_type: str = 'full'
) -> Dict[str, str]:
    """Generate a professional report"""
    try:
        report_generator = LatexReportGenerator()
        pdf_path = report_generator.generate_report(
            portfolio_data,
            analysis_results,
            report_type
        )
        return {"report_path": pdf_path, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))