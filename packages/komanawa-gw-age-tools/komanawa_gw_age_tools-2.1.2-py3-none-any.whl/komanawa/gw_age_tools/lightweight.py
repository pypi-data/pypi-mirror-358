"""
created matt_dumont 
on: 16/05/24
"""
import numpy as np
import pandas as pd


def lightweight_predict_future(source, out_years, ages, age_fractions, precision):
    """
    a lightweight version of predict_future_conc_bepm that does not check inputs and does not interpolate the source concentration and does not check the parmeters... use at your own warning

    :param source:
    :param out_years:
    :param ages:
    :param age_fractions:
    :param precision:
    :return:
    """
    out_conc = np.full_like(out_years, np.nan)
    for i, t in enumerate(out_years):
        out_conc[i] = (source.loc[(t - ages).round(precision)] * age_fractions).sum()
    receptor_conc = pd.Series(index=out_years, data=out_conc)
    return receptor_conc


def _lightweight_predict_future_int(source, out_years, ages, age_fractions):
    """
    a lightweight version of predict_future_conc_bepm that does not check inputs and does not interpolate the source concentration and does not check the parmeters... use at your own warning

    1/4 the speed of lightweight_predict_future
    :param source:
    :param out_years:
    :param ages:
    :param precision:
    :return:
    """
    out_conc = np.full(out_years.shape, np.nan)
    for i, t in enumerate(out_years):
        out_conc[i] = (source.loc[(t - ages)].values * age_fractions).sum()
    receptor_conc = pd.Series(index=out_years, data=out_conc)
    return receptor_conc


def lightweight_predict_future_int_np(source, out_years, ages, age_fractions, adder):
    """
    a lightweight version of predict_future_conc_bepm that does not check inputs and does not interpolate the source concentration and does not check the parmeters... use at your own warning, but 0.05x the runtime of lightweight_predict_future

    The inputs for this are different to the other functions, STRONGLY suggest testing with lightweight_predict_future first

    The inputs relative to lightweight_predict_future are:

    .. code-block:: python

        precision = 2
        age_step, ages, age_fractions = make_age_dist(....)
        source1 = pd.Series(index=np.arange(-ages.max(), 500, 10 ** -precision).round(precision), data=np.nan, dtype=float)
        outages = np.linspace(1, 400, 1000)
        lightweight_predict_future(source1, outages, ages, age_fractions, precision)

        source4.index = (np.round(source4.index * int(10 ** precision))).astype(int)
        outages4 = (np.round(deepcopy(outages) * int(10 ** precision))).astype(int)
        insource = deepcopy(source4).values
        adder = source4.index.min()*-1
        ages4 = (np.round(deepcopy(ages) * int(10 ** precision))).astype(int)
        lightweight_predict_future_int_np(insource, outages4, ages4, age_fractions, adder)

    :param source: np.ndarray, sorted by age
    :param out_years: np.ndarray of years to predict (integer (np.round(deepcopy(outages) * int(10 ** precision))).astype(int))
    :param ages: np.ndarray of ages (integer (np.round(deepcopy(ages) * int(10 ** precision))).astype(int)
    :param adder: integer, the minimum age in the source data (source4.index.min()*-1)
    :return:
    """
    useages = ages - adder
    out_conc = np.full(out_years.shape, np.nan)
    for i, t in enumerate(out_years):
        out_conc[i] = (source[(t - useages)] * age_fractions).sum()
    return out_conc


def _lightweight_v2_predict_future_np(source, out_years, ages, age_fractions, adder):
    """
    a lightweight version of predict_future_conc_bepm that does not check inputs and does not interpolate the source concentration and does not check the parmeters... use at your own warning

    slower than lightweight_predict_future_int_np
    :param source:
    :param out_years:
    :param ages:
    :param age_fractions:
    :param precision:
    :return:
    """
    useages = ages - adder
    temp = np.full((len(out_years), len(ages)), 0, dtype=int)
    temp[:] = out_years[:, np.newaxis]
    temp_ages = np.full((len(out_years), len(ages)), 0, dtype=int)
    temp_ages[:] = useages[np.newaxis, :]
    temp = temp - temp_ages
    temp_age_fractions = np.full((len(out_years), len(ages)), np.nan, dtype=float)
    temp_age_fractions[:] = age_fractions[np.newaxis, :]
    tempshape = temp.shape
    conc = source[temp.flatten()].reshape(tempshape)
    out_conc = (conc * age_fractions).sum(axis=1)
    return out_conc


def _lightweight_v2_predict_future(source, out_years, ages, age_fractions, precision):
    """
    a lightweight version of predict_future_conc_bepm that does not check inputs and does not interpolate the source concentration and does not check the parmeters... use at your own warning

    higher memory use and 2.5x slower than lightweight_predict_future
    :param source:
    :param out_years:
    :param ages:
    :param age_fractions:
    :param precision:
    :return:
    """
    temp = np.full((len(out_years), len(ages)), np.nan, dtype=float)
    temp[:] = out_years[:, np.newaxis]
    temp = np.repeat(np.array(out_years)[:, np.newaxis], len(ages), axis=1)
    ages = np.repeat(np.array(ages)[np.newaxis, :], len(out_years), axis=0)
    age_fractions = np.repeat(np.array(age_fractions)[np.newaxis, :], len(out_years), axis=0)
    temp = (temp - ages).round(precision)
    tempshape = temp.shape
    conc = source.loc[temp.flatten()].values.reshape(tempshape)
    out_conc = (conc * age_fractions).sum(axis=1)
    receptor_conc = pd.Series(index=out_years, data=out_conc)
    return receptor_conc


def _lightweight_v3_predict_future(source, out_years, ages, age_fractions, precision):
    """
    a lightweight version of predict_future_conc_bepm that does not check inputs and does not interpolate the source concentration and does not check the parmeters... use at your own warning

    higher memory use and 2x slower than lightweight_predict_future
    :param source:
    :param out_years:
    :param ages:
    :param age_fractions:
    :param precision:
    :return:
    """
    temp = np.full((len(out_years), len(ages)), np.nan, dtype=float)
    temp[:] = out_years[:, np.newaxis]
    temp_ages = np.full((len(out_years), len(ages)), np.nan, dtype=float)
    temp_ages[:] = ages[np.newaxis, :]
    temp = temp - temp_ages
    temp_age_fractions = np.full((len(out_years), len(ages)), np.nan, dtype=float)
    temp_age_fractions[:] = age_fractions[np.newaxis, :]
    temp = temp.round(precision)
    tempshape = temp.shape
    conc = source.loc[temp.flatten()].values.reshape(tempshape)
    out_conc = (conc * age_fractions).sum(axis=1)
    receptor_conc = pd.Series(index=out_years, data=out_conc)
    return receptor_conc
