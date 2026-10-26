"""Caller-supplied USD rates; no built-in model-price assumptions."""
from dataclasses import dataclass
import math
import os


@dataclass(frozen=True)
class TokenPrices:
    input_per_million: float
    output_per_million: float
    model: str | None = None

    def __post_init__(self):
        try:
            values = float(self.input_per_million), float(self.output_per_million)
        except (TypeError, ValueError):
            raise ValueError('Rates must be finite nonnegative numbers.') from None
        if any(not math.isfinite(value) or value < 0 for value in values):
            raise ValueError('Rates must be finite nonnegative numbers.')
        object.__setattr__(self, 'input_per_million', values[0])
        object.__setattr__(self, 'output_per_million', values[1])
        if self.model is not None and (not isinstance(self.model, str) or not self.model.strip()):
            raise ValueError('A rate model must be a nonempty string.')


def environment_prices():
    values = os.getenv('TRANSCRIPTION_PRICE_IN'), os.getenv('TRANSCRIPTION_PRICE_OUT')
    return TokenPrices(*values) if all(values) else None


def estimate_cost(tokens_in, tokens_out, *, prices=None, model=None):
    prices = environment_prices() if prices is None else prices
    if prices is None or (prices.model is not None and prices.model != model):
        return None
    return (tokens_in * prices.input_per_million + tokens_out * prices.output_per_million) / 1e6


def cost_text(tokens_in, tokens_out, *, prices=None, model=None):
    value = estimate_cost(tokens_in, tokens_out, prices=prices, model=model)
    return 'unknown (rates not configured for this model)' if value is None else f'{value:.4f} USD'
