import numpy as np
import pandas as pd
import patsy
from .eblupFH import eblupFH

def mseFH(formula, vardir_col, method="REML", MAXITER=100, PRECISION=1e-4, B=0, data=None):
    result = {"est": None, "mse": None}

    if data is None:
        raise ValueError("Data must be provided as a pandas DataFrame.")

    # Build design matrix X and response y
    y_df, X_df = patsy.dmatrices(formula, data, return_type='dataframe', NA_action='drop')
    y = y_df.values.flatten()
    X = X_df.values
    vardir = data.loc[y_df.index, vardir_col].values

    if np.any(np.isnan(y)):
        raise ValueError(f"Argument formula={formula} contains NA values.")
    if np.any(np.isnan(vardir)):
        raise ValueError(f"Argument vardir={vardir_col} contains NA values.")

    # Call eblupFH
    result["est"] = eblupFH(formula, vardir_col, method, MAXITER, PRECISION, B, data)
    fit = result["est"]["fit"]
    if not fit["convergence"]:
        print("Warning: The fitting method does not converge.")
        return result

    A = fit["refVar"]
    m, p = X.shape

    Vi = 1.0 / (A + vardir)
    Bd = vardir / (A + vardir)
    SumAD2 = np.sum(Vi ** 2)
    XtVi = (Vi[:, None] * X).T
    Q = np.linalg.inv(XtVi @ X)

    # Vectorized computation
    g1d = vardir * (1 - Bd)
    XQ = X @ Q
    g2d = (Bd ** 2) * np.einsum('ij,ij->i', XQ, X)
    if method == "REML":
        VarA = 2 / SumAD2
        g3d = (Bd ** 2) * VarA / (A + vardir)
        mse2d = g1d + g2d + 2 * g3d
    elif method == "ML":
        VarA = 2 / SumAD2
        b = -np.trace(Q @ ((Vi ** 2)[:, None] * X).T @ X) / SumAD2
        g3d = (Bd ** 2) * VarA / (A + vardir)
        mse2d = g1d + g2d + 2 * g3d - b * (Bd ** 2)
    else:  # FH
        SumAD = np.sum(Vi)
        VarA = 2 * m / (SumAD ** 2)
        b = 2 * (m * SumAD2 - SumAD ** 2) / (SumAD ** 3)
        g3d = (Bd ** 2) * VarA / (A + vardir)
        mse2d = g1d + g2d + 2 * g3d - b * (Bd ** 2)

    result["mse"] = mse2d
    return result