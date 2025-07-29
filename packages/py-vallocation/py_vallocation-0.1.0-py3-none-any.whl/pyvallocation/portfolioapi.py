"""High-level portfolio optimization API."""

import logging
from dataclasses import dataclass
from typing import Callable, List, Optional, Sequence, Union

import numpy as np

from . import probabilities
from .optimization import MeanCVaR, MeanVariance, RobustBayes, build_G_h_A_b
from .optional import HAS_PANDAS, pd
from .probabilities import generate_uniform_probabilities
from .utils.functions import portfolio_cvar

logger = logging.getLogger(__name__)


@dataclass
class AssetsDistribution:
    """
    Representation of an asset return distribution for portfolio optimization.

    This data class stores either the parametric statistics (mean vector and covariance matrix)
    of asset returns, or a scenario-based representation with return realizations and associated
    probabilities. It is used as a foundational input for various portfolio optimization methods
    (e.g., mean-variance, CVaR).

    Args:
        mu (np.ndarray or 'pd.Series', optional):
            Mean vector of asset returns (length N). If provided, `cov` must also be provided.
        cov (np.ndarray or 'pd.DataFrame', optional):
            Covariance matrix of asset returns (N x N). If provided, `mu` must also be provided.
        scenarios (np.ndarray or 'pd.DataFrame', optional):
            Matrix of scenario returns, with shape (T, N), where T is the number of scenarios
            and N is the number of assets. If provided, `probabilities` must also be provided.
        probabilities (np.ndarray or 'pd.Series', optional):
            Vector of scenario probabilities (length T). Should sum to 1. Used with `scenarios`.

    Attributes:
        mu (np.ndarray or None):
            Mean vector of asset returns. Converted to np.ndarray if originally pd.Series.
        cov (np.ndarray or None):
            Covariance matrix of asset returns. Converted to np.ndarray if originally pd.DataFrame.
        scenarios (np.ndarray or None):
            Scenario matrix (T x N). Converted to np.ndarray if originally pd.DataFrame.
        probabilities (np.ndarray or None):
            Scenario probabilities vector (length T). Converted to np.ndarray if originally pd.Series.
        N (int):
            Number of assets.
        T (int, optional):
            Number of scenarios, if using scenario-based input.

    Raises:
        ValueError: If neither (mu, cov) nor (scenarios, probabilities) are both provided.

    Example:
        >>> # Using mean and covariance
        >>> dist = AssetsDistribution(mu=np.array([0.01, 0.02]), cov=np.eye(2))
        >>> # Using scenarios and probabilities
        >>> scenarios = np.array([[0.01, 0.03], [0.02, 0.01]])
        >>> probs = np.array([0.6, 0.4])
        >>> dist = AssetsDistribution(scenarios=scenarios, probabilities=probs)
    """

    mu: Optional[Union[np.ndarray, "pd.Series"]] = None
    cov: Optional[Union[np.ndarray, "pd.DataFrame"]] = None
    scenarios: Optional[Union[np.ndarray, "pd.DataFrame"]] = None
    probabilities: Optional[Union[np.ndarray, "pd.Series"]] = None

    def __post_init__(self):
        if HAS_PANDAS:
            if isinstance(self.mu, pd.Series):
                self._pd_mu = self.mu.copy()
            if isinstance(self.cov, pd.DataFrame):
                self._pd_cov = self.cov.copy()
            if isinstance(self.scenarios, pd.DataFrame):
                self._pd_scenarios = self.scenarios.copy()
            if isinstance(self.probabilities, pd.Series):
                self._pd_probabilities = self.probabilities.copy()
        if self.mu is not None and self.cov is not None:
            if HAS_PANDAS and isinstance(self.mu, pd.Series):
                self.mu = self.mu.values
            if HAS_PANDAS and isinstance(self.cov, pd.DataFrame):
                self.cov = self.cov.values if hasattr(self.cov, "values") else self.cov
            self.N = self.mu.shape[0]
        elif self.scenarios is not None:
            if HAS_PANDAS and isinstance(self.scenarios, pd.DataFrame):
                self.scenarios = self.scenarios.values
            if self.probabilities is None:
                self.probabilities = generate_uniform_probabilities(len(self.scenarios))
            elif HAS_PANDAS and isinstance(self.probabilities, pd.Series):
                self.probabilities = self.probabilities.values
            self.T, self.N = self.scenarios.shape
        else:
            raise ValueError(
                "Either (mu, cov) or (scenarios, probabilities) must be provided."
            )


class PortfolioWrapper(AssetsDistribution):
    """
    Portfolio optimization wrapper supporting mean-variance and CVaR optimization.

    This class extends `AssetsDistribution` and provides methods for constructing and solving portfolio optimization
    problems under both mean-variance (Markowitz) and Conditional Value-at-Risk (CVaR) risk measures. It supports
    both parametric (mean/covariance) and scenario-based inputs, flexible risk and return constraints,
    and efficient frontier calculation.

    Args:
        assets_distribution (AssetsDistribution):
            The asset return distribution, specified via means/covariances or scenarios/probabilities.
        num_portfolios (int, optional):
            Number of points to calculate on the efficient frontier. Defaults to 10.
        n_sim_scenarios (int, optional):
            Number of simulated scenarios to generate if needed. Defaults to 10000.
        dist (str or Callable, optional):
            Distribution to use for scenario simulation if scenarios are not provided.
            Defaults to 'Normal'. Can be a callable.
        alpha (float, optional):
            Confidence level for CVaR calculations (e.g., 0.05 for 95% CVaR). Defaults to 0.05.
        verbose (bool, optional):
            If True, enables logging and detailed warnings. Defaults to False.

    Attributes:
        N (int):
            Number of assets.
        T (int or None):
            Number of scenarios (if scenario-based).
        mu (np.ndarray):
            Asset means.
        cov (np.ndarray):
            Asset covariance matrix.
        scenarios (np.ndarray):
            Scenario return matrix.
        probabilities (np.ndarray):
            Probabilities for each scenario.
        num_portfolios (int):
            Number of points on the efficient frontier.
        n_sim_scenarios (int):
            Number of simulated scenarios (if needed).
        dist (str or Callable):
            Distribution for scenario simulation.
        alpha (float):
            CVaR confidence level.
        G, h, A, b (np.ndarray or None):
            Constraint matrices and vectors.
        optimizer (object or None):
            The instantiated optimizer (MeanVariance or MeanCVaR).
        efficient_frontier (np.ndarray or None):
            Cached efficient frontier weights.
        risk_measure (str or None):
            Currently selected risk measure ("Variance" or "CVaR").

    Methods:
        validate_data():
            Validates the provided asset data for internal consistency.
        set_constraints(params: dict = None):
            Sets linear constraints for the optimization problem.
        initialize_optimizer(risk_measure: str = 'Variance'):
            Initializes the optimizer for the selected risk measure.
        set_efficient_frontier():
            Computes and caches the efficient frontier portfolios.
        get_portfolios_risk_constraint(maxrisk):
            Returns portfolio(s) with maximal return for a given risk constraint.
        get_portfolios_return_constraint(lowerret):
            Returns portfolio(s) with minimal risk for a given return constraint.
        get_minrisk_portfolio():
            Returns the minimum risk portfolio from the efficient frontier.

    Example:
        >>> assets_dist = AssetsDistribution(mu=mu, cov=cov)
        >>> wrapper = PortfolioWrapper(assets_dist)
        >>> wrapper.initialize_optimizer(risk_measure='CVaR')
        >>> wrapper.set_efficient_frontier()
        >>> min_risk_weights = wrapper.get_minrisk_portfolio()

    Raises:
        ValueError: If provided data is incomplete or inconsistent.
        KeyError: If an invalid risk measure is specified.
    """

    def __init__(
        self,
        assets_distribution: AssetsDistribution,
        num_portfolios: int = 10,
        n_sim_scenarios: int = 10000,
        dist: Union[str, Callable] = "Normal",
        alpha: float = 0.05,
        rho: float = 0.0,
        gamma: float = 3.0,
        gamma_grid: Sequence[float] | int | None = None,
        risk_budgets: Sequence[float] | None = None,
        verbose: bool = False,
    ):
        super().__init__(
            mu=assets_distribution.mu,
            cov=assets_distribution.cov,
            scenarios=assets_distribution.scenarios,
            probabilities=assets_distribution.probabilities,
        )
        self.verbose = verbose
        if self.verbose:
            logger.info(f"Initializing PortfolioWrapper with {self.N} assets.")
        self.validate_data()
        self.G = self.h = self.A = self.b = None
        self.num_portfolios = num_portfolios
        self.optimizer = None
        self.efficient_frontier = None
        self._frontier_returns = None
        self._frontier_param = None
        self.T = getattr(self, "T", None)
        self.n_sim_scenarios = n_sim_scenarios
        self.dist = dist
        self.alpha = alpha
        self.rho = rho
        self.gamma = gamma
        self.gamma_grid = gamma_grid
        self.risk_budgets = risk_budgets
        self.risk_measure = None
        # pandas detection
        if HAS_PANDAS:
            if hasattr(assets_distribution, "_pd_mu"):
                self._pandas = True
                self._asset_index = assets_distribution._pd_mu.index
            elif hasattr(assets_distribution, "_pd_cov"):
                self._pandas = True
                self._asset_index = assets_distribution._pd_cov.columns
            elif hasattr(assets_distribution, "_pd_scenarios"):
                self._pandas = True
                self._asset_index = assets_distribution._pd_scenarios.columns
            else:
                self._pandas = False
        else:
            self._pandas = False

    def validate_data(self):
        """Validate that provided distribution information is consistent."""

        if self.mu is not None and self.cov is not None:
            if len(self.mu) != len(self.cov):
                raise ValueError("Dimensions of mu and cov must match.")
        elif self.scenarios is not None and self.probabilities is not None:
            if len(self.scenarios) != len(self.probabilities):
                raise ValueError("Number of scenarios and probabilities must match.")
        if self.verbose:
            logger.info("Data validation passed.")

    def set_constraints(self, params: Optional[dict] = None):
        """Build linear constraints for the optimisation problem."""

        params = params or {}
        self.G, self.h, self.A, self.b = build_G_h_A_b(self.N, **params)
        if self.verbose:
            logger.info("Constraints set.")

    def _compute_mv_moments(self):
        """Calculate mean and covariance from scenario data."""

        self.mu = self.scenarios.T @ self.probabilities
        self.cov = np.cov(self.scenarios.T, aweights=self.probabilities)
        if self.verbose:
            logger.info("Computed mean and covariance from scenarios.")

    def _simulate_scenarios(self) -> None:
        """Simulate return scenarios based on the configured distribution."""
        if callable(self.dist):
            self.scenarios = self.dist(self.mu, self.cov, self.n_sim_scenarios)
        elif self.dist == "Normal":
            self.scenarios = np.random.multivariate_normal(
                self.mu, self.cov, self.n_sim_scenarios
            )
        else:
            raise ValueError("Specified distribution not available or must be callable")
        self.probabilities = probabilities.generate_uniform_probabilities(
            self.n_sim_scenarios
        )
        if self.verbose:
            logger.info(
                f"Simulated {self.n_sim_scenarios} scenarios using distribution {self.dist}."
            )

    def initialize_optimizer(
        self,
        risk_measure: str = "Variance",
        *,
        tcost_lambda: Union[float, Sequence[float]] = 0.0,
        prev_weights: Optional[np.ndarray] = None,
    ):
        self.risk_measure = risk_measure
        if self.G is None or self.h is None:
            logger.warning("No custom constraints specified, using default ones")
            self.set_constraints()
        if risk_measure == "Variance":
            if self.mu is None or self.cov is None:
                logger.warning("Computing mean and covariance from scenarios")
                self._compute_mv_moments()
            self.optimizer = MeanVariance(
                self.mu,
                self.cov,
                self.G,
                self.h,
                self.A,
                self.b,
                tcost_lambda=tcost_lambda,
                prev_weights=prev_weights,
            )
        elif risk_measure == "CVaR":
            if self.scenarios is None or self.probabilities is None:
                logger.warning(
                    f"Computing scenarios from mu and cov, using distribution: {self.dist}"
                )
                self._simulate_scenarios()
            self.optimizer = MeanCVaR(
                self.scenarios,
                self.G,
                self.h,
                self.A,
                self.b,
                p=self.probabilities,
                alpha=self.alpha,
                tcost_lambda=tcost_lambda,
                prev_weights=prev_weights,
            )
        elif risk_measure == "RobustBayes":
            if self.mu is None or self.cov is None:
                logger.warning("Computing mean and covariance from scenarios")
                self._compute_mv_moments()
            self.optimizer = RobustBayes(
                self.mu,
                self.cov,
                rho=self.rho,
                gamma=self.gamma,
                G=self.G,
                h=self.h,
                A=self.A,
                b=self.b,
            )
        else:
            raise KeyError('risk_measure must be "Variance", "CVaR", or "RobustBayes"')
        if self.verbose:
            logger.info(f"Initialized optimizer with risk measure: {risk_measure}")

    def set_efficient_frontier(self):
        if self.optimizer is None:
            logger.warning(
                "Setting default optimizer, call initialize_optimizer to customize it"
            )
            self.initialize_optimizer()
        self.efficient_frontier = self.optimizer.efficient_frontier(self.num_portfolios)
        if getattr(self, "_pandas", False):
            import pandas as _pd

            self.efficient_frontier = _pd.DataFrame(
                self.efficient_frontier,
                index=self._asset_index,
                columns=range(self.efficient_frontier.shape[1]),
            )
        if self.verbose:
            logger.info("Efficient frontier set.")

    def _efficient_frontier(self) -> np.ndarray:
        """Return the cached efficient frontier, computing it if necessary."""

        if self.efficient_frontier is None:
            self.set_efficient_frontier()
        return self.efficient_frontier

    def set_robust_frontier_gamma(self, gamma_grid="auto"):
        if gamma_grid == "auto":
            gamma_grid = RobustBayes.gamma_grid(n=self.num_portfolios)
        W, ret = RobustBayes.frontier_by_gamma(
            self.mu,
            self.cov,
            self.rho,
            gamma_grid,
            self.G,
            self.h,
            self.A,
            self.b,
        )
        self.efficient_frontier = W
        self._frontier_returns = ret
        self._frontier_param = gamma_grid

    def set_robust_frontier_risk(self, risk_vec):
        W, ret = RobustBayes.frontier_by_risk(
            self.mu,
            self.cov,
            self.rho,
            self.gamma,
            risk_vec,
            self.G,
            self.h,
            self.A,
            self.b,
        )
        self.efficient_frontier = W
        self._frontier_returns = ret
        self._frontier_param = risk_vec

    def get_portfolios_risk_constraint(
        self, maxrisk: Union[float, np.ndarray]
    ) -> List[np.ndarray]:
        """
        Returns portfolio(s) with maximum return subject to risk constraint(s) using the efficient frontier.
        """
        ef = self._efficient_frontier()
        if self.risk_measure == "CVaR":
            cvar = portfolio_cvar(
                ef, self.scenarios, self.probabilities.reshape(-1, 1), self.alpha
            )
            result = self._search_risk(maxrisk, cvar, ef)
            if getattr(self, "_pandas", False):
                import pandas as _pd

                result = [_pd.Series(r, index=self._asset_index) for r in result]
            return result
        elif self.risk_measure in {"Variance", "RobustBayes"}:
            vol = np.sqrt(np.sum(ef.T @ self.cov * ef.T, axis=1))
            result = self._search_risk(maxrisk, vol, ef)
            if getattr(self, "_pandas", False):
                import pandas as _pd

                result = [_pd.Series(r, index=self._asset_index) for r in result]
            return result
        else:
            raise KeyError('risk_measure must be "Variance", "CVaR", or "RobustBayes"')

    def get_portfolios_return_constraint(
        self, lowerret: Union[float, np.ndarray]
    ) -> List[np.ndarray]:
        """
        Returns portfolio(s) with minimum risk subject to return constraint(s) using the efficient frontier.
        """
        ef = self._efficient_frontier()
        if (
            isinstance(lowerret, float)
            or (hasattr(lowerret, "__len__") and len(lowerret) < 2)
        ) and self.efficient_frontier is None:
            result = self.optimizer.efficient_portfolio(lowerret)
            if getattr(self, "_pandas", False):
                import pandas as _pd

                result = _pd.Series(result, index=self._asset_index)
            return result
        else:
            returns = (
                self.mu @ ef
                if self.mu is not None
                else self.scenarios.T @ self.probabilities
            )
            result = self._search_returns(lowerret, returns, ef)
            if getattr(self, "_pandas", False):
                import pandas as _pd

                result = [_pd.Series(r, index=self._asset_index) for r in result]
            return result

    @staticmethod
    def _search_risk(maxrisk, risk, ef) -> List[np.ndarray]:
        """Select portfolios whose risk is below ``maxrisk``."""

        return PortfolioWrapper._select_by_threshold(
            maxrisk, risk, ef, lambda v, t: v <= t
        )

    @staticmethod
    def _search_returns(lowerret, returns, ef) -> List[np.ndarray]:
        """Select portfolios achieving at least ``lowerret``."""

        return PortfolioWrapper._select_by_threshold(
            lowerret, returns, ef, lambda v, t: t >= v
        )

    @staticmethod
    def _select_by_threshold(thresholds, values, ef, cmp) -> List[np.ndarray]:
        """Return columns from ``ef`` meeting ``cmp(values, threshold)``."""

        import pandas as _pd

        thresh_arr = np.atleast_1d(thresholds)
        indices = np.array([max(np.sum(cmp(values, t)) - 1, 0) for t in thresh_arr])
        data = ef.values if isinstance(ef, _pd.DataFrame) else ef
        return [data[:, idx] for idx in indices]

    def get_minrisk_portfolio(self) -> np.ndarray:
        """
        Returns the minimum risk portfolio from the efficient frontier or optimizer.
        """
        if self.optimizer is None:
            self.initialize_optimizer()
        if self.efficient_frontier is None:
            self.set_efficient_frontier()
        result = (
            self.efficient_frontier.iloc[:, 0]
            if getattr(self, "_pandas", False)
            else self.efficient_frontier[:, 0]
        )
        return result
