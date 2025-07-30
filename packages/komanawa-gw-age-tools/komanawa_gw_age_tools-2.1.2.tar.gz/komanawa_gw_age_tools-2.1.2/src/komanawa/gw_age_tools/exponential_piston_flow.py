"""
created matt_dumont 
on: 10/07/23
"""
import numpy as np
import pandas as pd


def exponential_piston_flow(t, tm, f):
    """
    produce an exponential piston flow model pdf

    :param t: time steps to calculate pdf for (yrs)
    :param tm: mean residence time (yrs)
    :param f: fraction of the total source that is in the fast flow component
    :return:
    """
    t = np.atleast_1d(t)
    out = np.zeros_like(t)
    idx = t >= tm * (1 - f)
    out[idx] = (f * tm) ** -1. * np.e ** (-(t[idx] / f / tm) + (1 / f) - 1)
    return out


def binary_exp_piston_flow(t, mrt_p1, mrt_p2, frac_p1, f_p1, f_p2):
    """
    produce a binary exponential piston flow model pdf

    :param t: time steps to calculate pdf for (yrs)
    :param mrt_p1: mean residence time of the first piston flow component (yrs)
    :param mrt_p2: mean residence time of the second piston flow component (yrs)
    :param frac_p1: fraction of the total source that is in the first piston flow component
    :param f_p1: fraction of the first piston flow component that is in the fast flow component
    :param f_p2: fraction of the second piston flow component that is in the fast flow component
    :return: pdf of the binary exponential piston flow model
    """
    frac_p2 = 1 - frac_p1
    out = (frac_p1 * exponential_piston_flow(t, mrt_p1, f_p1)
           + frac_p2 * exponential_piston_flow(t, mrt_p2, f_p2))
    return out


def exponential_piston_flow_cdf(t, tm, f):
    """
    produce a cdf for an exponential piston flow model

    :param t: time steps to calculate cdf for (yrs)
    :param tm: mean residence time (yrs)
    :param f: fraction of the total source that is in the fast flow component
    :return:
    """
    t = np.atleast_1d(t).astype(float)
    tm = float(tm)
    f = float(f)
    out = np.zeros_like(t)
    idx = t >= tm * (1 - f)
    out[idx] = 1 - np.e ** (-(t[idx] / f / tm) + (1 / f) - 1)
    return out


def binary_exp_piston_flow_cdf(t, mrt_p1, mrt_p2, frac_p1, f_p1, f_p2):
    """
    produce a cdf for a binary exponential piston flow model

    :param t: time steps to calculate cdf for (yrs)
    :param mrt_p1: mean residence time of the first piston flow model (yrs)
    :param mrt_p2: mean residence time of the second piston flow model (yrs)
    :param frac_p1: fraction of the total source that is in the first piston flow model
    :param f_p1: fraction of the first piston flow model that is in the fast flow component
    :param f_p2: fraction of the second piston flow model that is in the fast flow component
    :return: cdf of the binary exponential piston flow model
    """
    frac_p1 = float(frac_p1)
    frac_p2 = 1 - frac_p1
    out = (frac_p1 * exponential_piston_flow_cdf(t, mrt_p1, f_p1)
           + frac_p2 * exponential_piston_flow_cdf(t, mrt_p2, f_p2))
    return out

def check_age_inputs(mrt, mrt_p1, mrt_p2, frac_p1, precision, f_p1, f_p2):
    """
    convenience function to check BEPM age inputs

    :param mrt: mean residence time of the source (yrs) either mrt or mrt_p2 can be None
    :param mrt_p1: mean residence time of the first piston flow component (yrs)
    :param mrt_p2: mean residence time of the second piston flow component (yrs)
    :param frac_p1: fraction of the total source that is in the first piston flow component
    :param precision: precision of the age distribution (decimal places)
    :param f_p1: fraction of the first piston flow component that is in the fast flow component
    :param f_p2: fraction of the second piston flow component that is in the fast flow component
    :return:
    """
    if frac_p1 == 1:
        mrt_p2 = np.nan
        if mrt is None and mrt_p1 is not None:
            mrt = mrt_p1
        elif mrt is not None and mrt_p1 is None:
            mrt_p1 = mrt
        elif mrt is None and mrt_p1 is None:
            raise ValueError('one of mrt or mrt_p1 must be passed')
        else:
            assert mrt == mrt_p1, 'if frac_p1 == 1 then mrt must equal mrt_p1'
    else:
        assert mrt_p1 is not None
        if mrt is None and mrt_p2 is None:
            raise ValueError('one of mrt or mrt_p2 must be passed')
        elif mrt is not None and mrt_p2 is None:
            mrt_p2 = (mrt - (mrt_p1 * frac_p1)) / (1 - frac_p1)
        elif mrt is None and mrt_p2 is not None:
            mrt = (mrt_p1 * frac_p1) + (mrt_p2 * (1 - frac_p1))
        else:
            mrt_test = (mrt_p1 * frac_p1) + (mrt_p2 * (1 - frac_p1))
            assert np.isclose(mrt, mrt_test), 'both mrt and mrt_p2 are passed and they are not consistent with each other'

    assert isinstance(precision, int), 'precision must be an integer'
    assert pd.api.types.is_number(mrt_p1), 'mrt_p1 must be a number'
    assert pd.api.types.is_number(frac_p1), 'frac_p1 must be a number'
    assert pd.api.types.is_number(f_p1), 'f_p1 must be a number'
    assert pd.api.types.is_number(f_p2), 'f_p2 must be a number, set a dummy value if using only one piston'
    assert pd.api.types.is_number(mrt) or mrt is None, 'mrt must be a number'
    assert pd.api.types.is_number(mrt_p2) or mrt_p2 is None, 'mrt_p2 must be a number'
    if any([mrtv < 0 for mrtv in [mrt_p1, mrt_p2, mrt]]):
        raise ValueError(f'all mean residence times must be positive. Got:{mrt=}, {mrt_p1=}, {mrt_p2=}')
    return mrt, mrt_p2


def make_age_dist(mrt, mrt_p1, mrt_p2, frac_p1, precision, f_p1, f_p2, start=np.nan):
    """
    make an age distribution for the binary exponential piston flow model

    :param mrt: mean residence time of the source (yrs) either mrt or mrt_p2 can be None
    :param mrt_p1: mean residence time of the first piston flow component (yrs)
    :param mrt_p2: mean residence time of the second piston flow component (yrs)
    :param frac_p1: fraction of the total source that is in the first piston flow component
    :param precision: precision of the age distribution (decimal places)
    :param f_p1: fraction of the first piston flow component that is in the fast flow component
    :param f_p2: fraction of the second piston flow component that is in the fast flow component
    :param start: start age for the age distribution (yrs) default is np.nan which will use the maximum of the mrt_p1*5 and mrt_p2*5
    :return: a tuple

             * age_step: the step size of the age distribution (yrs)
             * ages: the ages of the age distribution (yrs)
             * age_fractions: the fractions of the age distribution (decimal)

    """
    check_age_inputs(mrt, mrt_p1, mrt_p2, frac_p1, precision, f_p1, f_p2)
    age_step = round(10 ** -precision, precision)
    ages = np.arange(0, np.nanmax([mrt_p1*5, mrt_p2*5, start]), age_step).round(precision)
    age_cdf = binary_exp_piston_flow_cdf(ages, mrt_p1, mrt_p2, frac_p1, f_p1, f_p2)
    age_fractions = np.diff(age_cdf, prepend=0)
    age_fractions = age_fractions / age_fractions.sum()
    return age_step, ages, age_fractions
