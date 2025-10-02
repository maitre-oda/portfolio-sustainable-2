"""Streamlit interface for the Portfolio Sustainable optimisation engine."""

from __future__ import annotations

import pathlib

import numpy as np

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from src.metrics import (
    annualized_return,
    annualized_volatility,
    conditional_value_at_risk,
    max_drawdown,
)
from src.optimization import OptimizationError, optimize_portfolio

DATA_DIR = pathlib.Path(__file__).resolve().parents[1] / "data" / "processed"


@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.Series]:
    """Load processed returns and carbon intensity data.

    The notebooks produce ``returns.csv`` and ``carbon_intensity.csv``. When these
    files are not available, the function creates a synthetic dataset so that the
    application remains usable in a fresh clone.
    """

    returns_path = DATA_DIR / "returns.csv"
    carbon_path = DATA_DIR / "carbon_intensity.csv"

    if returns_path.exists() and carbon_path.exists():
        returns = pd.read_csv(returns_path, index_col=0, parse_dates=True)
        carbon_intensity = pd.read_csv(carbon_path, index_col=0)
        if carbon_intensity.shape[1] != 1:
            raise ValueError("carbon_intensity.csv must contain a single column")
        carbon_intensity = carbon_intensity.iloc[:, 0]
    else:
        st.warning("Processed data not found. Using synthetic demo data.")
        assets = ["AAA", "BBB", "CCC", "DDD"]
        dates = pd.date_range("2020-01-01", periods=252, freq="B")
        rng = np.random.default_rng(42)
        base_returns = rng.normal(loc=0.0005, scale=0.01, size=(len(dates), len(assets)))
        returns = pd.DataFrame(base_returns, index=dates, columns=assets)
        carbon_intensity = pd.Series([100, 150, 90, 200], index=assets)

    return returns, carbon_intensity


st.set_page_config(page_title="Portfolio Sustainable", layout="wide")
st.title("Portfolio Sustainable")
st.markdown(
    """
    Ajustez les contraintes ci-dessous puis lancez l'optimisation pour obtenir un
    portefeuille durable aligné avec vos objectifs de rendement, de risque et
    d'empreinte carbone.
    """
)

returns, carbon_intensity = load_data()

max_carbon = st.slider("Intensité carbone maximale (tCO₂e / M€)", 50.0, 300.0, 150.0, step=5.0)
max_cvar = st.slider("CVaR maximal (95%)", 0.0, 0.5, 0.2, step=0.01)
turnover_limit = st.slider("Turnover maximal", 0.0, 1.0, 0.3, step=0.05)

previous_weights = pd.Series(1 / len(returns.columns), index=returns.columns)

if st.button("Optimiser le portefeuille"):
    try:
        weights = optimize_portfolio(
            returns=returns,
            carbon_intensity=carbon_intensity,
            max_carbon=max_carbon,
            max_cvar=max_cvar,
            turnover_limit=turnover_limit,
            previous_weights=previous_weights,
        )
    except OptimizationError as exc:  # pragma: no cover - handled via UI
        st.error(f"Optimisation impossible: {exc}")
    else:
        st.success("Optimisation réalisée avec succès !")
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(weights.index, weights.values)
        ax.set_ylabel("Poids")
        ax.set_title("Allocation optimisée")
        st.pyplot(fig)

        portfolio_returns = returns @ weights
        metrics = {
            "Rendement annualisé": annualized_return(portfolio_returns),
            "Volatilité annualisée": annualized_volatility(portfolio_returns),
            "CVaR 95%": conditional_value_at_risk(portfolio_returns, alpha=0.95),
            "Drawdown maximal": max_drawdown(portfolio_returns)[0],
            "Intensité carbone": float(carbon_intensity @ weights),
        }
        st.dataframe(pd.DataFrame.from_dict(metrics, orient="index", columns=["Valeur"]))
else:
    st.info("Choisissez vos contraintes puis cliquez sur le bouton pour optimiser.")
