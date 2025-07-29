import numpy as np
import pandas as pd
import warnings
from statsmodels.regression.mixed_linear_model import MixedLM
import patsy
import logging

def eblupBHF(formula, dom, selectdom, meanxpop, popnsize, method="REML", data=None):
    result = {"eblup": None, "fit": None}

    if data is not None:
        formuladataall = data.copy()
        y, X = patsy.dmatrices(formula, data, return_type='dataframe')
        mask = ~(y.isnull().any(axis=1) | X.isnull().any(axis=1))
        y = y[mask]
        X = X[mask]
        formuladata = data.loc[mask]
        dom_vals = data.loc[mask, dom].values
    else:
        raise ValueError("Data must be provided in Python version.")

    if isinstance(dom_vals.dtype, pd.CategoricalDtype):
        dom_vals = dom_vals.astype(str)

    if len(formuladataall) != len(data[dom]):
        raise ValueError(f"Arguments formula [rows={len(formuladataall)}] and dom [rows={len(data[dom])}] must be the same length.")

    
    ys = y.values.flatten()
    intercept = 'Intercept' in X.columns or 'const' in X.columns
    p = X.shape[1]
    

    # Number of domains for which EBLUPs are required
    if selectdom is None:
        selectdom = np.unique(dom_vals)
    else:
        if isinstance(selectdom, pd.Series) and selectdom.dtype.name == 'category':
            selectdom = selectdom.astype(str)
        selectdom = np.unique(selectdom)
    I = len(selectdom)
    n = len(ys)

    # Save meanxpop and popnsize domains in the same order as selected domains
    meanxpopsel = np.zeros((I, meanxpop.shape[1]))
    popnsizesel = np.zeros((I, popnsize.shape[1]))
    noselectdom_meanxpop = []
    noselectdom_popnsize = []
    selectdomfinded = []

    for i in range(I):
        idom1 = np.where(selectdom[i] == meanxpop[:, 0])[0]
        idom2 = np.where(selectdom[i] == popnsize[:, 0])[0]
        if len(idom1) != 0 and len(idom2) != 0:
            meanxpopsel[i, :] = meanxpop[idom1[0], :]
            popnsizesel[i, :] = popnsize[idom2[0], :]
            selectdomfinded.append(selectdom[i])
        else:
            if len(idom1) == 0:
                noselectdom_meanxpop.append(selectdom[i])
            if len(idom2) == 0:
                noselectdom_popnsize.append(selectdom[i])

    # warning message
    if len(noselectdom_meanxpop) > 0 or len(noselectdom_popnsize) > 0:
        text = "The following domain codes (selectdom) are not defined in population domain codes."
        if len(noselectdom_meanxpop) > 0:
            text += "\n    - meanxpop[:,0]: " + " ".join(map(str, sorted(noselectdom_meanxpop)))
        if len(noselectdom_popnsize) > 0:
            text += "\n    - popnsize[:,0]: " + " ".join(map(str, sorted(noselectdom_popnsize)))
        warnings.warn(text)

    meanxpop = meanxpopsel[:, 1:]
    popnsize = popnsizesel[:, 1:]

    if intercept and p == meanxpop.shape[1] + 1:
        meanxpop = np.hstack([np.ones((meanxpop.shape[0], 1)), meanxpop])

    # Fit the nested-error model to sample data by REML/ML
    exog = X.values
    groups = dom_vals
    if method == "REML":
        reml = True
    elif method == "ML":
        reml = False
    else:
        raise ValueError(f'Argument method="{method}" must be "REML" or "ML".')

    with warnings.catch_warnings(record=True) as wlog:
        warnings.simplefilter("always")
        try:
            model = MixedLM(ys, exog, groups=groups)
            fit_EB = model.fit(reml=reml)
        except Exception as e:
            logging.error("MixedLM function within eblupBHF: %s", str(e))
            return result
        for warn in wlog:
            logging.warning("MixedLM warning: %s: %s", warn.category.__name__, str(warn.message))

    betaest = fit_EB.fe_params.reshape(-1, 1)
    upred = fit_EB.random_effects
    upred_str = {str(k): float(np.array(v).flatten()[0]) for k, v in fit_EB.random_effects.items()}

    Resultsfit = {
        "summary": fit_EB.summary(),
        "fixed": fit_EB.fe_params,
        "random": upred_str,
        "errorvar": fit_EB.scale,
        "refvar": fit_EB.cov_re[0, 0] if hasattr(fit_EB, 'cov_re') else None,
        "loglike": fit_EB.llf,
        "residuals": fit_EB.resid
    }

    eblup = np.zeros(I)
    meanXsd = np.zeros((1, p))
    text = []
    SampSizeselectdom = np.zeros(I, dtype=int)
    for i in range(I):
        d = selectdom[i]
        if d not in selectdomfinded:
            eblup[i] = np.nan
        else:
            rowsd = (dom_vals == d)
            if np.any(rowsd):
                Xsd = exog[rowsd, :]
                fd = np.sum(rowsd) / popnsize[i]
                for k in range(p):
                    meanXsd[0, k] = np.mean(Xsd[:, k])
                eblup[i] = (
                    fd * np.mean(ys[rowsd]) +
                    np.dot(meanxpop[i, :] - fd * meanXsd[0, :], betaest.flatten()) +
                    (1 - fd) * upred[d].iloc[0].item()
                ).item()
                SampSizeselectdom[i] = np.sum(rowsd)
            else:
                eblup[i] = np.dot(meanxpop[i, :], betaest.flatten())
                text.append(str(d))

    if len(text) > 0:
        warnings.warn(
            "The following selected domains (selectdom) have zero sample size. \n"
            "  The EBLUPs of these domains are the synthetic regression estimators.\n"
            "   Domains: " + " ".join(text)
        )

    result["eblup"] = pd.DataFrame({
        "domain": selectdom,
        "eblup": eblup,
        "sampsize": SampSizeselectdom
    })
    result["fit"] = Resultsfit
    return result
