"""Generalized Linear Mixed-Effects Model (GLMM) for D_out prediction.

Model specification:
  D_out ~ beta0 + beta1*d_lex + beta2*d_sem + beta3*Type + beta4*Task
         + beta5*Model + (Type x Model) + u_prompt + epsilon
"""


class GLMMRegressor:
    """Fit and summarise the GLMM for output divergence."""

    def fit(self, data) -> None:
        # TODO: implement using statsmodels MixedLM or pymer4
        raise NotImplementedError

    def summary(self) -> dict:
        raise NotImplementedError
