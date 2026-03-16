"""
Configuración del Módulo de Fundamentales.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any

@dataclass
class ScoringWeights:
    """Pesos para el cálculo del puntaje final (0.0 - 1.0)."""
    piotroski: float = 0.15
    altman: float = 0.10
    beneish: float = 0.05  # Penaliza si hay riesgo, bonifica poco
    magic_formula: float = 0.20
    growth_momentum: float = 0.30
    analyst_upside: float = 0.20

@dataclass
class FundamentalsConfig:
    """Configuración principal del módulo."""
    
    # Rutas relativas al archivo de configuración
    data_path: Path = field(
        default_factory=lambda: Path(__file__).parent / "data"
    )
    
    # Pesos para el puntaje final
    weights: ScoringWeights = field(default_factory=ScoringWeights)
    
    # Umbrales
    min_market_cap: float = 1_000_000_000  # 1B para evitar small caps muy volátiles
    min_volume: float = 100_000             # Liquidez mínima diaria promedio
    
    # Directorio para guardar reportes
    reports_path: Path = field(
        default_factory=lambda: Path(__file__).parent / "reports"
    )

    def __post_init__(self):
        if isinstance(self.data_path, str):
            self.data_path = Path(self.data_path)
        if isinstance(self.reports_path, str):
            self.reports_path = Path(self.reports_path)
            
        # Asegurar creación de directorios
        self.data_path.mkdir(parents=True, exist_ok=True)
        self.reports_path.mkdir(parents=True, exist_ok=True)
