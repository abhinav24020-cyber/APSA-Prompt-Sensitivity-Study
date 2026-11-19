"""Linear mixed-effects model for D_out prediction (Gaussian GLMM, identity link).

Model specification (methodology section 12.3):
  D_out ~ beta0 + beta1*d_lex + beta2*d_sem + beta3*Type + beta4*Task
         + beta5*Model [+ (Type x Model)] + u_prompt + epsilon
with a random intercept u_prompt per original prompt, fitted by REML (statsmodels MixedLM).
"""

import warnings


class GLMMRegressor:
    """Fit and summarise the mixed model for output divergence."""

    def __init__(self, outcome: str = "d_out_sem", interaction: bool = False) -> None:
        self.outcome = outcome
        self.interaction = interaction
        self._fit = None
        self.formula = None

    def fit(self, data) -> None:
        import statsmodels.formula.api as smf

        terms = "d_in_char + d_in_sem + C(operator) + C(task_category) + C(model)"
        if self.interaction:
            terms += " + C(operator):C(model)"
        self.formula = f"{self.outcome} ~ {terms}"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            import numpy as np

            data = data.reset_index(drop=True)
            self._fit = None
            # lbfgs can converge to a degenerate boundary solution; prefer Powell / Nelder-Mead.
            for method in ("powell", "nm", "lbfgs"):
                fit = smf.mixedlm(self.formula, data, groups=data["prompt_id"].to_numpy()).fit(
                    method=method, reml=True
                )
                if fit.converged and np.isfinite(fit.bse).all() and fit.bse.max() < 10:
                    self._fit, self.optimizer = fit, method
                    break
            if self._fit is None:
                raise RuntimeError("Mixed model did not reach a non-degenerate solution")

    def summary(self) -> dict:
        if self._fit is None:
            raise RuntimeError("Call fit() first")
        f = self._fit
        ci = f.conf_int()
        return {
            "formula": self.formula + " + (1 | prompt_id)",
            "converged": bool(f.converged),
            "optimizer": self.optimizer,
            "random_intercept_variance": float(f.cov_re.iloc[0, 0]),
            "residual_variance": float(f.scale),
            "coefficients": {
                name: {
                    "estimate": float(f.fe_params[name]),
                    "ci_low": float(ci.loc[name, 0]),
                    "ci_high": float(ci.loc[name, 1]),
                    "p_value": float(f.pvalues[name]),
                }
                for name in f.fe_params.index
            },
        }
