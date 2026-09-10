"""
Configuração central do robô.
Tudo que muda entre paper/real, ou entre ambientes, vem de env vars —
nunca hardcoded, pra não vazar credenciais no repo.
"""
import os
from dataclasses import dataclass, field
from typing import List


@dataclass
class Config:
    # Modo de operação: "paper" (simulado) ou "live" (dinheiro real)
    mode: str = os.getenv("TRADING_MODE", "paper")

    # Ativos monitorados (B3, sem sufixo .SA se usar provedor local)
    tickers: List[str] = field(default_factory=lambda: os.getenv(
        "TICKERS", "PETR4,VALE3,ITUB4,BBDC4,WEGE3"
    ).split(","))

    # Horário de pregão B3 (horário de Brasília)
    market_open: str = os.getenv("MARKET_OPEN", "10:00")
    market_close: str = os.getenv("MARKET_CLOSE", "17:00")
    timezone: str = "America/Sao_Paulo"

    # Capital inicial (paper trading) ou limite de alocação (live)
    initial_capital: float = float(os.getenv("INITIAL_CAPITAL", "10000.0"))

    # --- Risk Gate ---
    max_position_pct: float = float(os.getenv("MAX_POSITION_PCT", "0.10"))  # 10% do capital por ativo
    max_daily_loss_pct: float = float(os.getenv("MAX_DAILY_LOSS_PCT", "0.03"))  # circuit breaker: -3% no dia
    max_open_positions: int = int(os.getenv("MAX_OPEN_POSITIONS", "5"))

    # --- Estratégia (exemplo: cruzamento de médias móveis) ---
    sma_fast: int = int(os.getenv("SMA_FAST", "9"))
    sma_slow: int = int(os.getenv("SMA_SLOW", "21"))

    # --- Persistência ---
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///trading_bot.db")

    # --- Broker (só usado em modo "live") ---
    broker_api_key: str = os.getenv("BROKER_API_KEY", "")
    broker_api_secret: str = os.getenv("BROKER_API_SECRET", "")

    def is_live(self) -> bool:
        return self.mode == "live"


config = Config()
