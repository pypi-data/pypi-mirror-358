import numpy as np
import pandas as pd
from .eblupBHF import eblupBHF  
from statsmodels.formula.api import ols
from statsmodels.regression.mixed_linear_model import MixedLM
import patsy

def pbmseBHF(formula, dom, selectdom, meanxpop, popnsize, B=200, method="REML", data=None):
    result = {'est': None, 'mse': None}

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

    if intercept and p == meanxpop.shape[1]:
        meanxpopaux = np.column_stack((meanxpop[:, 0], np.ones(meanxpop.shape[0]), meanxpop[:, 1:]))
    else:
        meanxpopaux = meanxpop

    result['est'] = eblupBHF(formula, dom, selectdom, meanxpop, popnsize, method=method, data=data)
    if not isinstance(result['est']['eblup'], pd.DataFrame):
        print("The fitting method does not converge.")
        return result

    betaest = np.array(result['est']['fit']['fixed']).reshape(-1, 1)
    sigmae2est = result['est']['fit']['errorvar']
    sigmau2est = result['est']['fit']['refvar']

    I = len(selectdom)
    n = len(ys)

    # Save meanxpop and popnsize domains in the same order as selected domains
    meanxpopsel = np.zeros((I, meanxpop.shape[1]))
    popnsizesel = np.zeros((I, popnsize.shape[1]))
    selectdomfinded = []

    for i in range(I):
        idom1 = np.where(selectdom[i] == meanxpop[:, 0])[0]
        idom2 = np.where(selectdom[i] == popnsize[:, 0])[0]
        if len(idom1) != 0 and len(idom2) != 0:
            meanxpopsel[i, :] = meanxpop[idom1[0], :]
            popnsizesel[i, :] = popnsize[idom2[0], :]
            selectdomfinded.append(selectdom[i])

    meanxpop = meanxpopsel[:, 1:]
    popnsize = popnsizesel[:, 1:]

    if intercept and p == meanxpop.shape[1] + 1:
        meanxpop = np.column_stack((np.ones(meanxpop.shape[0]), meanxpop))

    udom = np.unique(dom)
    D = len(udom)
    nd = np.zeros(D, dtype=int)
    SampSizeselectdom = np.zeros(I, dtype=int)
    musd_B = [None] * D
    mud_B = [None] * I

    for d in range(D):
        rowsd = (dom == udom[d])
        musd_B[d] = X.values[rowsd, :] @ betaest
        nd[d] = np.sum(rowsd)

    for i in range(I):
        mud_B[i] = np.sum(meanxpop[i, :] * betaest[:, 0])
        d = selectdom[i]
        posd = np.where(udom == d)[0]
        if len(posd) > 0:
            SampSizeselectdom[i] = nd[posd[0]]

    Ni = popnsize
    rd = Ni.flatten() - SampSizeselectdom

    meanxpop_df = pd.DataFrame(np.column_stack((selectdom, meanxpop)))
    popnsize_df = pd.DataFrame(np.column_stack((selectdom, popnsize)))

    MSE_B = np.zeros(I)
    truemean_B = np.zeros(I)

    print(f"\nBootstrap procedure with B = {B} iterations starts.")
    b = 1
    
    while b <= B:
        ys_B = np.zeros(n)
        ud_B = np.zeros(D)
        esdmean_B = np.zeros(D)
        for d in range(D):
            esd_B = np.random.normal(0, np.sqrt(sigmae2est), nd[d])
            ud_B[d] = np.random.normal(0, np.sqrt(sigmau2est))
            rowsd = (dom == udom[d])
            ys_B[rowsd] = musd_B[d].flatten() + ud_B[d] + esd_B
            esdmean_B[d] = np.mean(esd_B)

        for i in range(I):
            erdmean_B = np.random.normal(0, np.sqrt(sigmae2est / rd[i])) if rd[i] > 0 else 0
            posd = np.where(udom == selectdom[i])[0]
            if len(posd) != 0:
                edmean_B = esdmean_B[posd[0]] * nd[posd[0]] / Ni[i] + erdmean_B * rd[i] / Ni[i]
                truemean_B[i] = mud_B[i] + ud_B[posd[0]] + edmean_B
            else:
                truemean_B[i] = mud_B[i] + np.random.normal(0, np.sqrt(sigmau2est)) + erdmean_B


        bootstrap_data = data.copy()
        response_var = y.columns[0]  # nama kolom response dari patsy.dmatrices di atas
        bootstrap_data.loc[mask, response_var] = ys_B  # mask dari atas, agar urutan sama
        
        mean_EB = eblupBHF(formula, dom, selectdom, meanxpopsel, popnsizesel, method, bootstrap_data)

        if not isinstance(mean_EB['eblup'], pd.DataFrame):
            continue

        print(f"b = {b}")
        print("asoy", mean_EB)
        MSE_B += (mean_EB['eblup']['eblup'].values.flatten() - truemean_B) ** 2
        b += 1
    
    MSEEB_B = MSE_B / B
    result['mse'] = pd.DataFrame({'domain': selectdom, 'mse': MSEEB_B})
    return result

