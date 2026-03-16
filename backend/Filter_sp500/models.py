"""
Modelos de datos para el análisis fundamental.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
import pandas as pd

@dataclass
class FundamentalResult:
    """Resultado de un sub-módulo de análisis (ej: Piotroski)."""
    score: float
    max_score: float
    details: Dict[str, Any]
    interpretation: str  # "Bullish", "Bearish", "Neutral", "Risk"

@dataclass
class ScoredAsset:
    """Activo con todos sus puntajes calculados."""
    ticker: str
    price: float
    market_cap: float
    sector: str = "Unknown"
    industry: str = "Unknown"
    
    # Resultados individuales
    piotroski_result: Optional[FundamentalResult] = None
    altman_result: Optional[FundamentalResult] = None
    beneish_result: Optional[FundamentalResult] = None
    magic_result: Optional[FundamentalResult] = None
    growth_momentum_result: Optional[FundamentalResult] = None
    analyst_result: Optional[FundamentalResult] = None
    
    # Puntaje Final (0 - 100)
    final_score: float = 0.0
    recommendation: str = "HOLD" # STRONG_BUY, BUY, HOLD, SELL, AVOID
    
    # Flags de riesgo
    risk_flags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para exportatación con claves compatibles con el Frontend."""
        return {
            "Ticker": self.ticker,
            "Price": self.price,
            "Market_Cap": self.market_cap,
            "Sector": self.sector,
            "Final_Score": self.final_score,
            "Recommendation": self.recommendation,
            "Piotroski_Score": self.piotroski_result.score if self.piotroski_result else "N/A",
            "Altman_Score": self.altman_result.details.get("z_score") if self.altman_result else "N/A",
            "Beneish_Score": self.beneish_result.details.get("m_score") if self.beneish_result else "N/A",
            "Magic_Rank": self.magic_result.score if self.magic_result else "N/A",
            "Growth_Score": self.growth_momentum_result.score if self.growth_momentum_result else "N/A",
            "Upside_Pct": self.analyst_result.details.get("upside_pct") if self.analyst_result else 0.0,
            "Risk_Flags": ", ".join(self.risk_flags) if self.risk_flags else "N/A"
        }
