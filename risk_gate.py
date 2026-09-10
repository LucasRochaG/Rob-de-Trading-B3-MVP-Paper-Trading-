"""
Risk Gate: TODO sinal passa por aqui antes de virar ordem.
Este é o componente que mais precisa de rigor e testes antes de operar
com dinheiro real — bugs aqui custam dinheiro de verdade.

Regras implementadas:
1. Limite de posição por ativo (% do capital)
2. Limite de posições abertas simultâneas
3. Circuit breaker de perda diária (para tudo se bater o limite)
4. Sanity check de preço (evita agir sobre tick corrompido/absurdo)
"""
from dataclasses import dataclass

from engine.strategy.base import Signal, Side


@dataclass
class Order:
    ticker: str
    side: Side
    quantity: int
    reason: str


class RiskGate:
    def __init__(self, initial_capital: float, max_position_pct: float,
                 max_daily_loss_pct: float, max_open_positions: int):
        self.initial_capital = initial_capital
        self.max_position_pct = max_position_pct
        self.max_daily_loss_pct = max_daily_loss_pct
        self.max_open_positions = max_open_positions
        self.trading_halted = False  # circuit breaker ligado = True

    def check_daily_loss(self, current_equity: float) -> bool:
        """Retorna False (e trava o sistema) se o circuit breaker disparar."""
        loss_pct = (self.initial_capital - current_equity) / self.initial_capital
        if loss_pct >= self.max_daily_loss_pct:
            self.trading_halted = True
            return False
        return True

    def _sanity_check_price(self, price: float) -> bool:
        # Preço zerado, negativo ou absurdamente alto = tick corrompido
        return 0 < price < 100_000

    def approve_order(self, signal: Signal, price: float, current_equity: float,
                       open_positions: dict[str, int], cash: float) -> Order | None:
        if self.trading_halted:
            return None

        if not self._sanity_check_price(price):
            return None

        if signal.side == Side.BUY:
            if len(open_positions) >= self.max_open_positions and signal.ticker not in open_positions:
                return None  # já no limite de diversificação

            max_position_value = current_equity * self.max_position_pct
            quantity = int(max_position_value // price)
            if quantity < 1 or quantity * price > cash:
                return None  # sem caixa suficiente ou lote mínimo não atingido

            return Order(signal.ticker, Side.BUY, quantity, signal.reason)

        elif signal.side == Side.SELL:
            held_qty = open_positions.get(signal.ticker, 0)
            if held_qty <= 0:
                return None  # não vende o que não tem (sem short-selling neste MVP)
            return Order(signal.ticker, Side.SELL, held_qty, signal.reason)

        return None
