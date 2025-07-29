import numpy as np
import pandas as pd
from scipy.stats import norm
import patsy

def eblupSFH(formula, vardir, proxmat, method="REML", MAXITER=100, PRECISION=1e-4, data=None):
    result = {
        "eblup": None,
        "fit": {
            "method": method,
            "convergence": True,
            "iterations": 0,
            "estcoef": None,
            "refvar": None,
            "spatialcorr": None,
            "goodness": None
        }
    }

    if method not in ["REML", "ML"]:
        raise ValueError(f'method="{method}" must be "REML" or "ML".')

    # Formula parsing
    if data is not None:
        formula = formula.replace("as.factor", "C")
        y, X = patsy.dmatrices(formula, data, return_type='dataframe')
        vardir = data[vardir].to_numpy() if isinstance(vardir, str) else np.asarray(vardir)
    else:
        raise ValueError("Data argument is required for formula parsing.")

    proxmat = np.asarray(proxmat)
    m = len(y)
    p = X.shape[1]
    X_np = X.to_numpy()
    y_np = y.to_numpy().reshape(-1, 1)
    proxmat_T = proxmat.T
    I = np.eye(m)

    # Initial values
    sigma2_u_stim_S = [np.median(vardir)]
    rho_stim_S = [0.5]
    k = 0
    diff_S = PRECISION + 1

    while diff_S > PRECISION and k < MAXITER:
        k += 1
        sigma2_u = sigma2_u_stim_S[-1]
        rho = rho_stim_S[-1]

        # Precompute (I - rho * proxmat) and its transpose
        I_rhoP = I - rho * proxmat
        I_rhoPT = I - rho * proxmat_T

        # Derivative of covariance matrix V
        try:
            A = np.linalg.inv(I_rhoPT @ I_rhoP)
        except np.linalg.LinAlgError:
            result["fit"]["convergence"] = False
            return result
        derSigma = A
        derRho = 2 * rho * proxmat_T @ proxmat - proxmat - proxmat_T
        derVRho = -sigma2_u * (derSigma @ derRho @ derSigma)

        V = sigma2_u * derSigma + I * vardir
        try:
            Vi = np.linalg.inv(V)
        except np.linalg.LinAlgError:
            result["fit"]["convergence"] = False
            return result
        XtVi = X_np.T @ Vi
        Q = np.linalg.inv(XtVi @ X_np)
        P = Vi - XtVi.T @ Q @ XtVi
        b_s = Q @ XtVi @ y_np

        PD = P @ derSigma
        PR = P @ derVRho
        Pdir = P @ y_np

        if method == "REML":
            s1 = -0.5 * np.trace(PD) + 0.5 * (y_np.T @ PD @ Pdir)
            s2 = -0.5 * np.trace(PR) + 0.5 * (y_np.T @ PR @ Pdir)
            I11 = 0.5 * np.trace(PD @ PD)
            I12 = 0.5 * np.trace(PD @ PR)
            I22 = 0.5 * np.trace(PR @ PR)
        else:  # ML
            ViD = Vi @ derSigma
            ViR = Vi @ derVRho
            s1 = -0.5 * np.trace(ViD) + 0.5 * (y_np.T @ PD @ Pdir)
            s2 = -0.5 * np.trace(ViR) + 0.5 * (y_np.T @ PR @ Pdir)
            I11 = 0.5 * np.trace(ViD @ ViD)
            I12 = 0.5 * np.trace(ViD @ ViR)
            I22 = 0.5 * np.trace(ViR @ ViR)

        s1 = float(np.asarray(s1).item())
        s2 = float(np.asarray(s2).item())
        s = np.array([[s1], [s2]])
        Idev = np.array([[I11, I12], [I12, I22]])

        par_stim = np.array([[sigma2_u], [rho]])
        try:
            stime_fin = par_stim + np.linalg.solve(Idev, s)
        except np.linalg.LinAlgError:
            result["fit"]["convergence"] = False
            return result

        # Restricting the spatial correlation to (-0.999, 0.999)
        stime_fin[1, 0] = np.clip(stime_fin[1, 0], -0.999, 0.999)
        sigma2_u_stim_S.append(stime_fin[0, 0])
        rho_stim_S.append(stime_fin[1, 0])
        diff_S = np.max(np.abs(stime_fin - par_stim) / np.abs(par_stim))

    # Final values
    rho = rho_stim_S[-1]
    if rho == -0.999:
        rho = -1
    elif rho == 0.999:
        rho = 1
    sigma2u = max(sigma2_u_stim_S[-1], 0)

    result["fit"]["iterations"] = k
    if k >= MAXITER and diff_S >= PRECISION:
        result["fit"]["convergence"] = False
        return result

    result["fit"]["refvar"] = sigma2u
    result["fit"]["spatialcorr"] = rho

    # Coefficient estimation
    I_rhoP = I - rho * proxmat
    I_rhoPT = I - rho * proxmat_T
    try:
        A = np.linalg.inv(I_rhoPT @ I_rhoP)
    except np.linalg.LinAlgError:
        result["fit"]["convergence"] = False
        return result
    G = sigma2u * A
    V = G + I * vardir
    try:
        Vi = np.linalg.inv(V)
    except np.linalg.LinAlgError:
        result["fit"]["convergence"] = False
        return result
    XtVi = X_np.T @ Vi
    Q = np.linalg.inv(XtVi @ X_np)
    Bstim = Q @ XtVi @ y_np

    std_errorbeta = np.sqrt(np.diag(Q))
    tvalue = Bstim.flatten() / std_errorbeta
    pvalue = 2 * norm.sf(np.abs(tvalue))
    coef = pd.DataFrame({
        "beta": Bstim.flatten(),
        "std.error": std_errorbeta,
        "tvalue": tvalue,
        "pvalue": pvalue
    })

    # Goodness of fit
    Xbeta = X_np @ Bstim
    resid = y_np.flatten() - Xbeta.flatten()
    loglike = (-0.5) * (m * np.log(2 * np.pi) +
                        np.linalg.slogdet(V)[1] +
                        resid.T @ Vi @ resid)
    AIC = -2 * loglike + 2 * (p + 2)
    BIC = -2 * loglike + (p + 2) * np.log(m)
    goodness = {"loglike": float(loglike), "AIC": float(AIC), "BIC": float(BIC)}

    # EBLUP
    res = y_np.flatten() - (X_np @ Bstim).flatten()
    thetaSpat = X_np @ Bstim + G @ Vi @ res

    result["fit"]["estcoef"] = coef
    result["fit"]["goodness"] = goodness
    result["eblup"] = np.diag(thetaSpat)

    return result