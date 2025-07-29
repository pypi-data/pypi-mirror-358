import numpy as np
from numpy.linalg import solve, inv
import warnings
from .eblupSFH import eblupSFH
import patsy 

def mseSFH(formula, vardir, proxmat, method="REML", MAXITER=100, PRECISION=0.0001, data=None):
    result = {'est': None, 'mse': None}

    # Extract design matrix X and response y
    if data is not None:
        y, X = patsy.dmatrices(formula, data, return_type='matrix')
        y = np.asarray(y).flatten()
        X = np.asarray(X)
        vardir = data[vardir].values
    else:
        raise ValueError("Data argument is required for Python version.")

    if np.any(np.isnan(y)):
        raise ValueError("Argument formula contains NA values.")
    if np.any(np.isnan(vardir)):
        raise ValueError("Argument vardir contains NA values.")
    if np.any(np.isnan(proxmat)):
        raise ValueError("Argument proxmat contains NA values.")

    proxmat = np.asarray(proxmat)
    if proxmat.shape[0] != proxmat.shape[1]:
        raise ValueError("proxmat is not a square matrix.")

    m, p = X.shape

    # Call eblupSFH (assumed to be implemented)
    result['est'] = eblupSFH(formula, vardir, proxmat, method, MAXITER, PRECISION, data)
    if not result['est']['fit']['convergence']:
        warnings.warn("The fitting method does not converge.")
        return result

    A = result['est']['fit']['refvar']
    rho = result['est']['fit']['spatialcorr']

    I = np.eye(m)
    Xt = X.T
    proxmatt = proxmat.T
    # Gunakan solve untuk invers matriks
    Ci = solve((I - rho * proxmatt) @ (I - rho * proxmat), I)
    G = A * Ci
    V = G + np.diag(vardir)
    Vi = solve(V, I)
    XtVi = Xt @ Vi
    XtVi = Xt @ Vi
    Q = solve(XtVi @ X, np.eye(p))

    Ga = G - G @ Vi @ G
    Gb = G @ Vi @ X

    # Vektorisasi g1d dan g2d
    g1d = np.diag(Ga)
    Xa = X - Gb
    g2d = np.einsum('ij,jk,ik->i', Xa, Q, Xa)

    derRho = 2 * rho * proxmatt @ proxmat - proxmat - proxmatt
    Amat = -A * (Ci @ derRho @ Ci)
    P = Vi - Vi @ X @ Q @ X.T @ Vi
    PCi = P @ Ci
    PAmat = P @ Amat

    Idev = np.empty((2, 2))
    Idev[0, 0] = 0.5 * np.trace(PCi @ PCi)
    Idev[0, 1] = 0.5 * np.trace(PCi @ PAmat)
    Idev[1, 0] = Idev[0, 1]
    Idev[1, 1] = 0.5 * np.trace(PAmat @ PAmat)
    Idevi = np.linalg.inv(Idev)

    ViCi = Vi @ Ci
    ViAmat = Vi @ Amat

    l1 = ViCi - A * ViCi @ ViCi
    l2 = ViAmat - A * ViAmat @ ViCi

    # Vektorisasi g3d
    l1t = l1.T
    l2t = l2.T
    g3d = np.zeros(m)
    for i in range(m):
        L = np.vstack([l1t[i, :], l2t[i, :]])
        g3d[i] = np.trace(L @ V @ L.T @ Idevi)

    mse2d_aux = g1d + g2d + 2 * g3d

    psi = np.diag(vardir)
    D12aux = -Ci @ derRho @ Ci
    D22aux = 2 * A * Ci @ derRho @ Ci @ derRho @ Ci - 2 * A * Ci @ proxmatt @ proxmat @ Ci
    D = (psi @ Vi @ D12aux @ Vi @ psi) * (Idevi[0, 1] + Idevi[1, 0]) + psi @ Vi @ D22aux @ Vi @ psi * Idevi[1, 1]

    g4d = 0.5 * np.diag(D)

    mse2d = mse2d_aux - g4d

    if method == "ML":
        QXtVi = Q @ XtVi
        ViX = Vi @ X
        h1 = -np.trace(QXtVi @ Ci @ ViX)
        h2 = -np.trace(QXtVi @ Amat @ ViX)
        h = np.array([[h1], [h2]])
        bML = (Idevi @ h) / 2
        tbML = bML.T

        GVi = G @ Vi
        GViCi = GVi @ Ci
        GViAmat = GVi @ Amat
        ViCi = Vi @ Ci
        dg1_dA = Ci - 2 * GViCi + A * GViCi @ ViCi
        dg1_dp = Amat - 2 * GViAmat + A * GViAmat @ ViCi

        gradg1d = np.stack([np.diag(dg1_dA), np.diag(dg1_dp)], axis=1)
        bMLgradg1 = (tbML @ gradg1d.T).flatten()

        mse2d = mse2d - bMLgradg1

    result['mse'] = mse2d
    return result