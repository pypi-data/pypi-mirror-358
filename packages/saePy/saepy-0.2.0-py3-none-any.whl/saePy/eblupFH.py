import numpy as np
from scipy.stats import norm
from numpy.linalg import inv, solve
import pandas as pd
import patsy
import logging

def _get_design_matrix(formula, data):
    """Generate response vector y and design matrix X from formula and data."""
    formula = formula.replace("as.factor", "C")
    y, X = patsy.dmatrices(formula, data, return_type='dataframe')
    return y.values.flatten(), X.values

def _get_vardir(data, vardir_col):
    """Extract variance directory column as numpy array."""
    if vardir_col not in data.columns:
        raise ValueError(f"vardir_col '{vardir_col}' not found in data columns.")
    vardir = data[vardir_col].to_numpy()
    if vardir is None:
        raise ValueError("vardir must be provided.")
    return np.asarray(vardir)

def _fit_beta(X, y, Vi):
    """Estimate beta and its covariance matrix."""
    XtVi = (Vi[:, None] * X)
    Q = inv(X.T @ XtVi)
    beta = Q @ (XtVi.T @ y)
    return beta, Q

def _goodness_of_fit(y, y_hat, A_est, vardir, p):
    """Calculate loglike, AIC, BIC."""
    m = len(y)
    loglike = (-0.5) * np.sum(np.log(2 * np.pi * (A_est + vardir)) + ((y - y_hat) ** 2) / (A_est + vardir))
    aic = -2 * loglike + 2 * (p + 1)
    bic = -2 * loglike + np.log(m) * (p + 1)
    return {"loglike": loglike, "AIC": aic, "BIC": bic}

def eblupFH(formula, vardir_col, method="REML", MAXITER=100, PRECISION=1e-4, B=0, data=None):
    """
    Estimate EBLUP using FH model.
    Parameters:
        formula (str): Regression formula.
        vardir_col (str): Column name for variance.
        method (str): 'REML', 'ML', or 'FH'.
        MAXITER (int): Maximum iteration.
        PRECISION (float): Convergence threshold.
        data (pd.DataFrame): Input data.
    Returns:
        dict: Results.
    """
    if method not in ["REML", "ML", "FH"]:
        raise ValueError(f"method='{method}' must be 'REML', 'ML', or 'FH'.")

    y, X = _get_design_matrix(formula, data)
    vardir = _get_vardir(data, vardir_col)
    m, p = len(y), X.shape[1]

    A_est = [0, np.mean(vardir)]
    k = 0
    diff = PRECISION + 1
    result = {"fit": {}}

    while diff > PRECISION and k < MAXITER:
        k += 1
        Vi = 1 / (A_est[k] + vardir)
        if method == "ML":
            XtVi = X.T * Vi
            Q = inv(XtVi @ X)
            P = np.diag(Vi) - XtVi.T @ Q @ XtVi
            Py = P @ y
            s = -0.5 * np.sum(Vi) + 0.5 * (Py.T @ Py)
            I = 0.5 * np.sum(Vi ** 2)
        elif method == "REML":
            XtVi = X.T * Vi
            Q = inv(XtVi @ X)
            P = np.diag(Vi) - XtVi.T @ Q @ XtVi
            Py = P @ y
            s = -0.5 * np.sum(np.diag(P)) + 0.5 * (Py.T @ Py)
            I = 0.5 * np.sum(np.diag(P @ P))
        elif method == "FH":
            XtVi = X.T * Vi
            Q = inv(XtVi @ X)
            beta_aux = Q @ (XtVi @ y)
            residuals_aux = y - X @ beta_aux
            s = np.sum((residuals_aux ** 2) * Vi) - (m - p)
            I = np.sum(Vi)
        else:
            raise ValueError("Unknown method.")

        A_est.append(A_est[k] + s / I)
        diff = abs((A_est[k + 1] - A_est[k]) / A_est[k])

    A_final = max(A_est[k + 1], 0)
    result["fit"]["itteration"] = k
    result["fit"]["convergence"] = not (k == MAXITER and diff > PRECISION)
    result["fit"]["method"] = method
    result["fit"]["refVar"] = A_final

    # Estimate beta and statistics
    Vi = 1 / (A_final + vardir)
    beta, Q = _fit_beta(X, y, Vi)
    std_err_beta = np.sqrt(np.diag(Q))
    t_stat = beta / std_err_beta
    p_values = 2 * (1 - norm.cdf(np.abs(t_stat)))

    # Goodness of fit
    y_hat = X @ beta
    residuals = y - y_hat
    goodness_of_fit = _goodness_of_fit(y, y_hat, A_final, vardir, p)

    # EBLUP
    eblup = y_hat + A_final * Vi * residuals

    # Output coefficients as pandas DataFrame
    coef = pd.DataFrame({
        "Estimate": beta,
        "Std.Error": std_err_beta,
        "t.value": t_stat,
        "p.value": p_values
    })

    result["fit"]["coefficients"] = coef
    result["EBLUP"] = eblup
    result["fit"]["goodness"] = goodness_of_fit
    min2loglike = -2 * goodness_of_fit["loglike"]
    kic = min2loglike + 2 * (p + 1)
    result["fit"]["goodness"]["KIC"] = kic
    
    if B >= 1:
        sigma2d = vardir
        lambdahat = A_final
        betahat = beta.reshape(-1, 1)
        D = X.shape[0]
        B1hatast = 0
        B3ast = 0
        B5ast = 0
        sumlogf_ythetahatastb = 0
        sumlogf_yastbthetahatastb = 0

        Xbetahat = X @ betahat
        b = 0
        n_success = 0
        while b < B:
            uastb = np.sqrt(lambdahat) * np.random.randn(D, 1)
            eastb = np.sqrt(sigma2d).reshape(-1, 1) * np.random.randn(D, 1)
            yastb = Xbetahat + uastb + eastb
            # Buat DataFrame baru untuk bootstrap
            data_b = data.copy()
            data_b["y"] = yastb.flatten()
            data_b[vardir_col] = sigma2d
            try:
                resultb = eblupFH(formula, vardir_col, method=method, MAXITER=MAXITER, PRECISION=PRECISION, data=data_b, B=0)
            except Exception as e:
                logging.warning(f"Bootstrap b={b+1}: {method} error: {e}")
                continue
            if not resultb["fit"]["convergence"]:
                logging.warning(f"Bootstrap b={b+1}: {method} iteration does not converge.")
                continue
            betahatastb = resultb["fit"]["coefficients"]["Estimate"].to_numpy().reshape(-1, 1)
            lambdahatastb = resultb["fit"]["refVar"]

            Xbetahathatastb2 = (X @ (betahat - betahatastb)) ** 2
            yastbXbetahatastb2 = (yastb - X @ betahatastb) ** 2

            lambdahatastbsigma2d = lambdahatastb + sigma2d
            lambdahatsigma2d = lambdahat + sigma2d

            B1ast = np.sum((lambdahatsigma2d + Xbetahathatastb2.flatten() - yastbXbetahatastb2.flatten()) / lambdahatastbsigma2d)
            B1hatast += B1ast

            # AICb1, AICb2
            logf = (-0.5) * np.sum(
                np.log(2 * np.pi * lambdahatastbsigma2d) +
                ((yastb - X @ betahatastb).flatten() ** 2) / lambdahatastbsigma2d
            )
            sumlogf_ythetahatastb += logf
            sumlogf_yastbthetahatastb += resultb["fit"]["goodness"]["loglike"]

            # KICc, KICb1, KICb2
            B3ast += np.sum((lambdahatastbsigma2d + Xbetahathatastb2.flatten()) / lambdahatsigma2d)
            B5ast += np.sum(np.log(lambdahatastbsigma2d) + yastbXbetahatastb2.flatten() / lambdahatastbsigma2d)

            b += 1
            n_success += 1

        if n_success > 0:
            B2ast = np.sum(np.log(lambdahatsigma2d)) + B3ast / n_success - B5ast / n_success
            AICc = min2loglike + B1hatast / n_success
            AICb1 = float(min2loglike - 2 / n_success * (sumlogf_ythetahatastb - sumlogf_yastbthetahatastb))
            AICb2 = float(min2loglike - 4 / n_success * (sumlogf_ythetahatastb - result["fit"]["goodness"]["loglike"] * n_success))
            KICc = AICc + B2ast
            KICb1 = AICb1 + B2ast
            KICb2 = AICb2 + B2ast
            result["fit"]["goodness"].update(dict(
                KIC=kic, AICc=AICc, AICb1=AICb1, AICb2=AICb2,
                KICc=KICc, KICb1=KICb1, KICb2=KICb2, nBootstrap=n_success
            ))
        else:
            result["fit"]["goodness"].update(dict(KIC=kic, nBootstrap=0))

    return result