"""
Diagnóstico rápido: invocar las tools exactamente como lo hace LangGraph.
"""
import os, sys
from dotenv import load_dotenv
load_dotenv()

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

TICKER = "AAPL"

print("=" * 60)
print("TEST 1: Technical Tool via .invoke()")
print("=" * 60)
from technical_agent import get_technical_indicators
result = get_technical_indicators.invoke({"ticker": TICKER})
print(result)
print()

print("=" * 60)
print("TEST 2: Risk Tool via .invoke()")
print("=" * 60)
from risk_agent import get_risk_metrics
result = get_risk_metrics.invoke({"ticker": TICKER})
print(result)
print()

print("=" * 60)
print("TEST 3: Fundamental Tool via .invoke()")
print("=" * 60)
from fundamental_agent import get_fundamental_and_insiders
result = get_fundamental_and_insiders.invoke({"ticker": TICKER})
print(result)
