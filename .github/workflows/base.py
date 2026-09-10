"""
Contrato que qualquer fonte de dados de mercado precisa cumprir.
Isso é o que permite trocar "feed simulado" por "feed real da corretora"
sem tocar em nenhuma linha do resto do sistema.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Iterator


@dataclass(frozen=True)
class Tick:
    ticker: str
    price: float
    volume: int
    timestamp: datetime


class MarketDataFeed(ABC):
    @abstractmethod
    def stream_ticks(self) -> Iterator[Tick]:
        """
        Deve ser um generator infinito (ou até o mercado fechar) que
        produz um Tick por vez, na ordem em que chegam.
        """
        raise NotImplementedError
