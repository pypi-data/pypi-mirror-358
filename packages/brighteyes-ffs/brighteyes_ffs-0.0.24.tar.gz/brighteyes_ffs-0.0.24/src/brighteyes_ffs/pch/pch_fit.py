import numpy as np
from scipy.optimize import differential_evolution
from .simulate_pch import simulate_pch_1c_mc_ntimes

def fit_pch(hist, fitparamStart, fixedparam, fit_info, psf, lowerBounds, upperBounds, weights=1):
    #fitresult = least_squares(fitfun_pch, fitparamStart, args=(fixedparam, fit_info, hist, psf, weights), bounds=(lowerBounds, upperBounds), xtol=1e-12)
    bounds = list(zip(lowerBounds, upperBounds))
    fitresult = differential_evolution(fitfun_pch, bounds, args=(param, fit_info, hist, psf, weights))
    return fitresult


def fitfun_pch(fitparam, fixedparam, fit_info, hist, psf, weights=1):
    """
    fcs free diffusion fit function
    
    Parameters
    ----------
    fitparamStart : 1D np.array
        List with starting values for the fit parameters:
        order: [N, tauD, SP, offset, A, B]
        E.g. if only N and tauD are fitted, this becomes a two
        element vector [1, 1e-3].
    fixedparam : 1D np.array
        List with values for the fixed parameters:
        order: [N, tauD, SP, offset, 1e6*A, B]
        same principle as fitparamStart.
    fit_info : 1D np.array
        np.array boolean vector with always 6 elements
        1 for a fitted parameter, 0 for a fixed parameter
        E.g. to fit N and tau D this becomes [1, 1, 0, 0, 0, 0]
        order: [N, tauD, SP, offset, 1e6*A, B].
    tau : 1D np.array
        Vector with tau values.
    yexp : 1D np.array
        Vector with experimental autocorrelation.
    weights : 1D np.array, optional
        Vector with weights. The default is 1.

    Returns
    -------
    res : 1D np.array
        Residuals.

    """
    
    all_param = np.float64(np.zeros(6))
    all_param[fit_info==1] = fitparam
    all_param[fit_info==0] = fixedparam
    
    concentration = all_param[0]
    brightness = all_param[1]
    n_samples = int(all_param[2])
    n_hist_max = int(all_param[3])
    max_bin = int(all_param[4])
    err = all_param[5]

    # calculate theoretical autocorrelation function    
    pch_theo, _, _, _, _ = simulate_pch_1c_mc_ntimes(psf, concentration, brightness, n_samples, n_hist_max, max_bin, err)
    
    # calculate residuals
    res = hist - pch_theo
    
    # calculate weighted residuals
    res *= weights
    
    return np.sum(res**2)