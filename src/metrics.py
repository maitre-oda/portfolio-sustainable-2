"""Utility functions to compute key sustainable portfolio metrics."""

from __future__ import annotations

from typing import Tuple

import numpy as np
import pandas as pd


def annualized_return(returns: pd.Series | pd.DataFrame, periods_per_year: int = 252) -> float:
    """Compute the annualized arithmetic mean return.

    Parameters
    ----------
    returns : pandas Series or DataFrame
        Periodic returns expressed in decimal form.
    periods_per_year : int, optional
        Number of return observations in one year (default 252 for daily data).

    Returns
    -------
    float
        The annualized return.
    """

    if isinstance(returns, pd.DataFrame):
        mean_return = returns.mean().mean()
    else:
        mean_return = returns.mean()
    return float((1 + mean_return) ** periods_per_year - 1)


def annualized_volatility(returns: pd.Series | pd.DataFrame, periods_per_year: int = 252) -> float:
    """Compute the annualized volatility (standard deviation)."""

    if isinstance(returns, pd.DataFrame):
        volatility = returns.stack().std()
    else:
        volatility = returns.std()
    return float(volatility * np.sqrt(periods_per_year))


def conditional_value_at_risk(
    returns: pd.Series,
    alpha: float = 0.95,
) -> float:
    """Compute the Conditional Value at Risk (CVaR).

    The CVaR is defined on losses, so the sign of returns is inverted.
    """

    if returns.empty:
        raise ValueError("Returns series cannot be empty.")

    losses = -returns
    var_threshold = np.quantile(losses, alpha)
    tail_losses = losses[losses >= var_threshold]
    if tail_losses.empty:
        return float(var_threshold)
    return float(tail_losses.mean())


def max_drawdown(returns: pd.Series) -> Tuple[float, pd.Timestamp, pd.Timestamp]:
    """Compute the maximum drawdown of a return series.

    Returns
    -------
    tuple
        Maximum drawdown value (as a positive number) and the peak/trough dates.
    """

    cumulative = (1 + returns).cumprod()
    peak = cumulative.cummax()
    drawdowns = (cumulative - peak) / peak
    trough_idx = drawdowns.idxmin()
    peak_idx = cumulative.loc[:trough_idx].idxmax()
    max_dd = abs(drawdowns.min())
    return float(max_dd), peak_idx, trough_idx


__all__ = [
    "annualized_return",
    "annualized_volatility",
    "conditional_value_at_risk",
    "max_drawdown",
]
