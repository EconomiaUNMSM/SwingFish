"""
Motor principal de análisis fundamental.
Orquesta la descarga de datos, ejecución de modelos y cálculo de puntajes.
"""

import pandas as pd
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional
import time
from pathlib import Path

from .config import FundamentalsConfig
from .models import ScoredAsset, FundamentalResult
from .scrapers.wikipedia import WikipediaScraper
from .scrapers.yfinance_data import YFinanceScraper
from .core.piotroski import PiotroskiAnalyzer
from .core.altman import AltmanAnalyzer
from .core.beneish import BeneishAnalyzer
from .core.magic_formula import MagicFormulaAnalyzer
from .core.momentum_growth import GrowthMomentumAnalyzer

logger = logging.getLogger(__name__)

class FundamentalsEngine:
    """Orquestador del análisis fundamental."""
    
    def __init__(self, config: FundamentalsConfig = None):
        self.config = config or FundamentalsConfig()
        self.scraper = YFinanceScraper(retries=3, delay=1.0)
        
        # Analizadores
        self.piotroski = PiotroskiAnalyzer()
        self.altman = AltmanAnalyzer()
        self.beneish = BeneishAnalyzer()
        self.magic = MagicFormulaAnalyzer()
        self.growth = GrowthMomentumAnalyzer()

    def analyze_ticker(self, ticker: str) -> Optional[ScoredAsset]:
        """
        Analiza un solo ticker completo.
        """
        logger.info(f"Procesando {ticker}...")
        try:
            # 1. Descarga de datos
            fin, bs, cf, hist, info = self.scraper.fetch_full_data(ticker)
            
            if fin.empty and bs.empty:
                logger.warning(f"{ticker}: Sin datos financieros suficientes.")
                return None
            
            # Filtros básicos (Market Cap, Volumen)
            mcap = info.get("marketCap", 0)
            avg_vol = info.get("averageVolume", 0)
            
            if mcap < self.config.min_market_cap:
                logger.info(f"{ticker}: Market Cap {mcap} < {self.config.min_market_cap}. Descartado.")
                return None
                
            # 2. Ejecución de Modelos
            p_res = self.piotroski.analyze(ticker, fin, bs, cf)
            a_res = self.altman.analyze(ticker, fin, bs, info)
            b_res = self.beneish.analyze(ticker, fin, bs, cf)
            m_res = self.magic.analyze(ticker, fin, bs, info)
            g_res = self.growth.analyze(ticker, fin, hist)
            
            # 2.5 Detección de Ventana Post-Earnings
            earnings_transitional = False
            try:
                earnings_dates = info.get("earningsDate") or info.get("earningsDates")
                if earnings_dates:
                    import datetime
                    now = pd.Timestamp.now()
                    # earningsDate puede ser timestamp o lista
                    if isinstance(earnings_dates, (list, tuple)):
                        for ed in earnings_dates:
                            ed_ts = pd.Timestamp(ed)
                            days_since = (now - ed_ts).days
                            if 0 <= days_since <= 30:
                                earnings_transitional = True
                                logger.info(f"{ticker}: En ventana post-earnings ({days_since} días desde reporte). Datos pueden ser transitorios.")
                                break
                    else:
                        ed_ts = pd.Timestamp(earnings_dates)
                        days_since = (now - ed_ts).days
                        if 0 <= days_since <= 30:
                            earnings_transitional = True
                            logger.info(f"{ticker}: En ventana post-earnings ({days_since} días desde reporte).")
            except Exception as e:
                logger.debug(f"{ticker}: No se pudo verificar earnings date: {e}")
            
            # 3. Datos de Analistas
            upside = self.scraper.get_analyst_upside(info, hist["Close"].iloc[-1] if not hist.empty else 0)
            
            # Normalizar Upside score (0-10)
            # > 20% upside = 10 pts
            # > 10% upside = 5 pts
            # < 0% upside = 0 pts
            upside_score = min(upside / 2.0, 10.0) if upside > 0 else 0
            analyst_res = FundamentalResult(
                score=upside_score,
                max_score=10.0,
                details={"upside_pct": upside, "target_mean": info.get("targetMeanPrice")},
                interpretation="Bullish" if upside > 10 else "Neutral"
            )

            # 4. Scoring Final Ponderado con Rebalanceo Dinámico
            w = self.config.weights
            
            # Definimos sub-scores con sus pesos y validez
            sub_scores = {
                "piotroski":       {"result": p_res, "weight": w.piotroski},
                "altman":          {"result": a_res, "weight": w.altman},
                "beneish":         {"result": b_res, "weight": w.beneish},
                "magic_formula":   {"result": m_res, "weight": w.magic_formula},
                "growth_momentum": {"result": g_res, "weight": w.growth_momentum},
                "analyst_upside":  {"result": analyst_res, "weight": w.analyst_upside},
            }
            
            # Separar analizadores válidos de los que fallaron
            valid_scores = {}
            failed_analyzers = []
            
            for name, entry in sub_scores.items():
                res = entry["result"]
                if res.interpretation == "Unknown" or res.max_score == 0:
                    failed_analyzers.append(name)
                    logger.warning(f"{ticker}: Analizador '{name}' falló o retornó datos vacíos. Excluido del scoring.")
                else:
                    normalized = (res.score / res.max_score) * 10
                    valid_scores[name] = {"score": normalized, "weight": entry["weight"]}
            
            # Rebalancear pesos: redistribuir proporcionalmente entre los válidos
            if valid_scores:
                total_valid_weight = sum(v["weight"] for v in valid_scores.values())
                
                if total_valid_weight > 0:
                    # Escalar los pesos para que sumen 1.0
                    rebalance_factor = 1.0 / total_valid_weight
                    
                    final_score = sum(
                        v["score"] * v["weight"] * rebalance_factor 
                        for v in valid_scores.values()
                    ) * 10  # Escalar a 0-100
                else:
                    final_score = 0.0
            else:
                # Todos fallaron — no hay datos suficientes
                final_score = 0.0
                logger.error(f"{ticker}: TODOS los analizadores fallaron. Score = 0.")
            
            # Penalización por datos incompletos
            # Si más de la mitad de los analizadores fallaron, el score es poco confiable
            data_confidence = len(valid_scores) / len(sub_scores)
            
            # Recomendación con protección de confianza
            rec = "HOLD"
            if data_confidence < 0.5:
                # Datos insuficientes: no emitir recomendación de compra/venta
                rec = "HOLD"
                logger.warning(f"{ticker}: Confianza de datos baja ({data_confidence:.0%}). Forzando HOLD.")
            else:
                if final_score >= 80: rec = "STRONG_BUY"
                elif final_score >= 65: rec = "BUY"
                elif final_score <= 30: rec = "SELL"
            
            # Risk Flags
            flags = []
            if b_res.interpretation == "Bearish": flags.append("ACCOUNTING_RISK")
            if a_res.interpretation == "Bearish": flags.append("BANKRUPTCY_RISK")
            if upside < -10: flags.append("OVERVALUED_ANALYST")
            if failed_analyzers: flags.append(f"INCOMPLETE_DATA({','.join(failed_analyzers)})")
            if data_confidence < 0.5: flags.append("LOW_CONFIDENCE")
            if earnings_transitional: flags.append("DATA_TRANSITIONAL")
            
            return ScoredAsset(
                ticker=ticker,
                price=hist["Close"].iloc[-1] if not hist.empty else 0,
                market_cap=mcap,
                sector=info.get("sector", "Unknown"),
                industry=info.get("industry", "Unknown"),
                piotroski_result=p_res,
                altman_result=a_res,
                beneish_result=b_res,
                magic_result=m_res,
                growth_momentum_result=g_res,
                analyst_result=analyst_res,
                final_score=final_score,
                recommendation=rec,
                risk_flags=flags
            )

        except Exception as e:
            logger.error(f"Error analizando {ticker}: {e}")
            return None

    def run_market_scan(self, tickers: List[str] = None, max_workers: int = 1) -> pd.DataFrame:
        """
        Ejecuta el escáner sobre una lista de tickers.
        Si tickers es None, usa S&P 500.
        """
        if not tickers:
            logger.info("Obteniendo tickers del S&P 500 desde Wikipedia...")
            tickers = WikipediaScraper.get_sp500_tickers()
            is_custom = False
        else:
            is_custom = True
            
        logger.info(f"Iniciando análisis de {len(tickers)} activos...")
        
        results = []
        # Ejecución secuencial recomendada para evitar Ban de IP (max_workers=1)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self.analyze_ticker, t): t for t in tickers}
            
            completed = 0
            for future in as_completed(futures):
                try:
                    res = future.result()
                    completed += 1
                    
                    if res:
                        results.append(res.to_dict())
                        print(f"[{completed}/{len(tickers)}] {res.ticker}: Score {res.final_score:.1f} ({res.recommendation})")
                    else:
                        print(f"[{completed}/{len(tickers)}] - Skipped/Error")
                        
                except ConnectionError as e:
                    if "RATE_LIMIT_HIT" in str(e):
                        logger.critical("EJECUCIÓN ABORTADA POR BLOQUEO DE IP. GUARDANDO RESULTADOS PARCIALES.")
                        executor.shutdown(wait=False, cancel_futures=True)
                        break
                except Exception as e:
                    logger.error(f"Error inesperado en hilo: {e}")

        df = pd.DataFrame(results)
        if not df.empty:
            df = df.sort_values(by="final_score", ascending=False)
            
            # Guardar reporte
            now = pd.Timestamp.now()
            timestamp = now.strftime("%Y%m%d_%H%M%S")
            filename = self.config.reports_path / f"fundamentals_scan_{timestamp}.csv"
            df.to_csv(filename, index=False)
            logger.info(f"Reporte guardado localmente en {filename}")
            
            # Solo guardamos el CSV localmente para la v1.0, quitamos PostgreSQL.
            
        return df
