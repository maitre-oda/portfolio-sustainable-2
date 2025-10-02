"""Portfolio optimisation routines for sustainable investing use-cases."""

from __future__ import annotations

from typing import Dict, Optional

import cvxpy as cp
import numpy as np
import pandas as pd


class OptimizationError(RuntimeError):
    """Raised when the optimizer cannot find a feasible solution."""


def optimize_portfolio(
    returns: pd.DataFrame,
    carbon_intensity: pd.Series,
    expected_returns: Optional[pd.Series] = None,
    max_carbon: Optional[float] = None,
    max_cvar: Optional[float] = None,
    bounds: Optional[Dict[str, tuple[float, float]]] = None,
    turnover_limit: Optional[float] = None,
    previous_weights: Optional[pd.Series] = None,
    sector_map: Optional[pd.Series] = None,
    sector_limits: Optional[Dict[str, float]] = None,
    cvar_alpha: float = 0.95,
) -> pd.Series:
    """Optimise portfolio weights subject to sustainability constraints.

    Parameters
    ----------
    returns
        Historical return matrix indexed by date with columns representing assets.
    carbon_intensity
        Series of carbon intensities aligned with the columns of ``returns``.
    expected_returns
        Optional vector of expected returns. Defaults to the historical mean returns.
    max_carbon
        Upper bound on the weighted average carbon intensity.
    max_cvar
        Upper bound on the portfolio Conditional Value at Risk.
    bounds
        Dictionary mapping assets to (lower, upper) bounds. Defaults to (0, 1).
    turnover_limit
        Maximum allowable portfolio turnover relative to ``previous_weights``.
    previous_weights
        Previous allocation used in the turnover constraint.
    sector_map
        Series mapping asset tickers to sector names for optional limits.
    sector_limits
        Dictionary mapping sector names to maximum weights.
    cvar_alpha
        Tail probability for the CVaR constraint.

    Returns
    -------
    pandas.Series
        Optimal weights indexed by asset name.
    """

    if returns.empty:
        raise ValueError("Return matrix must not be empty.")

    assets = list(returns.columns)
    n_assets = len(assets)

    if expected_returns is None:
        expected_returns = returns.mean()
    expected_returns = expected_returns.reindex(assets)

    carbon_intensity = carbon_intensity.reindex(assets)
    if carbon_intensity.isnull().any():
        raise ValueError("Carbon intensity must be provided for all assets.")

    weights = cp.Variable(n_assets)

    # Objective: maximise expected return subject to convex constraints
    objective = cp.Maximize(expected_returns.values @ weights)

    constraints = [cp.sum(weights) == 1]

    # Bounds per asset
    for idx, asset in enumerate(assets):
        lb, ub = (0.0, 1.0)
        if bounds and asset in bounds:
            lb, ub = bounds[asset]
        constraints += [weights[idx] >= lb, weights[idx] <= ub]

    # Carbon intensity constraint
    if max_carbon is not None:
        constraints.append(carbon_intensity.values @ weights <= max_carbon)

    # CVaR constraint using auxiliary variables
    if max_cvar is not None:
        scenario_returns = returns.values
        n_scenarios = scenario_returns.shape[0]
        z = cp.Variable()  # VaR auxiliary variable
        u = cp.Variable(n_scenarios)
        losses = -scenario_returns @ weights
        constraints += [
            u >= 0,
            u >= losses - z,
            z + 1 / ((1 - cvar_alpha) * n_scenarios) * cp.sum(u) <= max_cvar,
        ]

    # Turnover constraint
    if turnover_limit is not None:
        if previous_weights is None:
            previous_weights = pd.Series(np.zeros(n_assets), index=assets)
        else:
            previous_weights = previous_weights.reindex(assets).fillna(0)
        constraints.append(cp.norm1(weights - previous_weights.values) <= turnover_limit)

    # Sector limits
    if sector_limits:
        if sector_map is None:
            raise ValueError("sector_map must be provided when sector_limits are used.")
        sector_map = sector_map.reindex(assets)
        for sector, limit in sector_limits.items():
            mask = [asset for asset, sec in sector_map.items() if sec == sector]
            if mask:
                idxs = [assets.index(asset) for asset in mask]
                constraints.append(cp.sum(weights[idxs]) <= limit)

    problem = cp.Problem(objective, constraints)
    problem.solve(solver=cp.SCS, verbose=False)

    if problem.status not in {cp.OPTIMAL, cp.OPTIMAL_INACCURATE}:
        raise OptimizationError(f"Optimisation failed: {problem.status}")

    solution = pd.Series(weights.value, index=assets)
    solution.name = "weight"
    return solution


__all__ = ["optimize_portfolio", "OptimizationError"]
