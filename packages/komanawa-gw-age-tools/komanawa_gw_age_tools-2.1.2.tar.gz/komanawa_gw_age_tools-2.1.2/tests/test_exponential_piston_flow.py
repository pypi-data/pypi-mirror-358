"""
created matt_dumont 
on: 17/07/23
"""
import unittest
import numpy as np
import pandas as pd
from komanawa.gw_age_tools import binary_exp_piston_flow, binary_exp_piston_flow_cdf, predict_historical_source_conc, \
    predict_source_future_past_conc_bepm, predict_future_conc_bepm, check_age_inputs, make_age_dist
from komanawa.gw_age_tools.lightweight import lightweight_predict_future_int_np, lightweight_predict_future
from copy import deepcopy
from pathlib import Path

plot_tests = False


class TestExponentialPistonFlow(unittest.TestCase):

    def test_binary_piston_flow(self):
        """

        :return:
        """

        tm1 = 1
        tm2 = 15
        f_p1 = 0.75
        f_p2 = 0.8
        frac_p1 = 0.5
        step = 0.5
        t = np.arange(0.1, 6., step)
        out = binary_exp_piston_flow(t, tm1, tm2, frac_p1, f_p1, f_p2)
        out2 = binary_exp_piston_flow_cdf(t, tm1, tm2, frac_p1, f_p1, f_p2)
        expect_1 = [0.0, 0.41805939018203736, 0.2146388476917839, 0.11019925881439102, 0.05657818598001161,
                    0.029048209245947743, 0.05623473509739689, 0.04729158417881503, 0.04194829909552831,
                    0.03848392479037335, 0.036013641488773174, 0.03408196667833277]
        expect_2 = [0.0, 0.18645545736347197, 0.33902086423116207, 0.4173505558892067, 0.4575663605149913,
                    0.4782138430655392, 0.4929639677524792, 0.5186425191311791, 0.5408469466440985, 0.5608995631058383,
                    0.5794942903978542, 0.5970018106077799]
        self.assertTrue(np.allclose(out, expect_1))
        self.assertTrue(np.allclose(out2, expect_2))
        step = 0.00001
        t = np.arange(0.1, 6., step)
        out = binary_exp_piston_flow(t, tm1, tm2, frac_p1, f_p1, f_p2)
        out2 = binary_exp_piston_flow_cdf(t, tm1, tm2, frac_p1, f_p1, f_p2)

        # test approximate integration of pdf vs cdf
        self.assertTrue(np.allclose((out * step).cumsum(), out2))

    def test_get_source_initial_conc_bepm(self, plot=plot_tests):
        mrt = 20
        mrt_p1 = 10
        frac_p1 = 0.7
        f_p1 = 0.8
        f_p2 = 0.75
        init_conc = 10
        prev_slope = 0.5
        max_conc = 20
        min_conc = 1.
        mrt_p2 = (mrt - (mrt_p1 * frac_p1)) / (1 - frac_p1)
        precision = 2

        source_conc = predict_historical_source_conc(init_conc=init_conc,
                                                     mrt=mrt, mrt_p1=mrt_p1, mrt_p2=mrt_p2,
                                                     frac_p1=frac_p1, f_p1=f_p1,
                                                     f_p2=f_p2, prev_slope=prev_slope, max_conc=max_conc,
                                                     min_conc=min_conc, start_age=np.nan, precision=precision)

        test_data_path = Path(__file__).parent.joinpath('test_data', 'test_get_source_initial_conc_bepm.hdf')
        write_test_data = False
        if write_test_data:
            test_data_path.unlink(missing_ok=True)
            source_conc.to_hdf(test_data_path, 'source_conc')
        true_source_conc = pd.read_hdf(test_data_path, 'source_conc')
        self.assertIsInstance(true_source_conc, pd.Series)
        pd.testing.assert_series_equal(source_conc, true_source_conc, check_names=False)

        if plot:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots()
            temp = pd.Series(index=source_conc.index)
            temp[:] = init_conc + (prev_slope * source_conc.index[:])
            temp[temp < min_conc] = np.nan

            ax.plot(temp.index, temp.values, label='receptor concentration (input)', color='orange')
            ax.plot(source_conc.index, source_conc.values, label='source concentration (predicted)', color='b')
            ax.axvline(0, color='k', linestyle='--', label='initial time')
            ax.set_xlabel('time (years)')
            ax.set_xlim(-100, 10)
            ax.set_ylabel('concentration')
            ax.set_title('predict_historical_source_conc')
            ax.legend()
            fig.tight_layout()
            fig.savefig(Path(__file__).parents[1].joinpath('figures', 'predict_historical_source_conc.png'))
            plt.show()

    def test_predict_source_future_past_conc_bepm(self, plot=plot_tests):
        mrt = 20
        mrt_p1 = 10
        frac_p1 = 0.7
        f_p1 = 0.8
        f_p2 = 0.75
        initial_conc = 10
        prev_slope = 0.5
        max_conc = 20
        min_conc = 1.
        age_range = (-20, 50)
        fut_slope = -0.1
        total_source_conc, receptor_conc = predict_source_future_past_conc_bepm(initial_conc, mrt, mrt_p1, frac_p1,
                                                                                f_p1,
                                                                                f_p2,
                                                                                prev_slope, fut_slope, age_range,
                                                                                max_conc, min_conc, max_fut_conc=20,
                                                                                min_fut_conc=1)
        test_data_path = Path(__file__).parent.joinpath('test_data', 'test_predict_source_future_past_conc_bepm.hdf')

        write_test_data = False
        if write_test_data:
            test_data_path.unlink(missing_ok=True)
            total_source_conc.to_hdf(test_data_path, 'total_source_conc')
            receptor_conc.to_hdf(test_data_path, 'receptor_conc')
        true_total_source_conc = pd.read_hdf(test_data_path, 'total_source_conc')
        self.assertIsInstance(true_total_source_conc, pd.Series)
        true_receptor_conc = pd.read_hdf(test_data_path, 'receptor_conc')
        self.assertIsInstance(true_receptor_conc, pd.Series)
        pd.testing.assert_series_equal(total_source_conc, true_total_source_conc, check_names=False)
        pd.testing.assert_series_equal(receptor_conc, true_receptor_conc, check_names=False)

        if plot:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots()
            ax.plot(total_source_conc.index, total_source_conc.values, label='source_conc', color='b')
            ax.plot(receptor_conc.index, receptor_conc.values, label='receptor_conc', color='r')
            ax.axvline(0, color='k', ls='--', label='initial time')
            ax.set_xlabel('time (years)')
            ax.set_ylabel('concentration')
            ax.set_title('predict_source_future_past_conc_bepm')
            ax.set_xlim(age_range)
            ax.legend()
            fig.tight_layout()
            fig.savefig(Path(__file__).parents[1].joinpath('figures', 'predict_source_future_past_conc_bepm.png'))
            plt.show()

    def test_predict_future_conc_bepm(self, plot=plot_tests):
        input_series = pd.Series(index=[-35, 0., 20, 27, 35, 40, 50, 100, 200],
                                 data=[1, 1, 3, 5, 15, 21, 18, 2.4, 2.4])
        mrt = 20
        mrt_p1 = 5
        frac_p1 = 0.2
        f_p1 = 0.8
        f_p2 = 0.75
        data = predict_future_conc_bepm(once_and_future_source_conc=input_series,
                                        predict_start=20,
                                        predict_stop=200,
                                        mrt_p1=mrt_p1, frac_p1=frac_p1, f_p1=f_p1, f_p2=f_p2, mrt=mrt, mrt_p2=None,
                                        fill_value=1,
                                        fill_threshold=0.05,
                                        pred_step=0.5)
        write_test_data = False
        test_path = Path(__file__).parent.joinpath('test_data', 'test_predict_future_conc_bepm.hdf')
        if write_test_data:
            test_path.unlink(missing_ok=True)
            data.to_hdf(test_path, 'data')
        true_data = pd.read_hdf(test_path, 'data')
        self.assertIsInstance(true_data, pd.Series)
        pd.testing.assert_series_equal(data, true_data, check_names=False)
        self.assertTrue(np.allclose(data.values, true_data.values))

        if plot:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots()
            ax.plot(input_series.index, input_series.values, label='Source Concentration (input)')
            ax.plot(data.index, data.values, label='Receptor Concentration')
            ax.set_xlabel('time (years)')
            ax.set_ylabel('concentration')
            ax.set_title('predict_future_conc_bepm')
            ax.legend()
            fig.savefig(Path(__file__).parents[1].joinpath('figures', 'predict_future_conc_bepm.png'))
            plt.show()

        # test with missing source concentration
        with self.assertRaises(ValueError):
            data = predict_future_conc_bepm(once_and_future_source_conc=input_series,
                                            predict_start=0,
                                            predict_stop=200,
                                            mrt_p1=mrt_p1, frac_p1=frac_p1, f_p1=f_p1, f_p2=f_p2, mrt=mrt, mrt_p2=None,
                                            fill_value=1,
                                            fill_threshold=0.05,
                                            pred_step=0.5)

    def test_lightweight_int_np_vs_lightweight(self):
        precision = 2
        mrt, mrt_p1 = 31.5, 31.5
        frac_p1 = 1
        mrt_p2 = None
        f_p1 = 0.65619
        f_p2 = 0.65619  # dummy
        mrt, mrt_p2 = check_age_inputs(mrt, mrt_p1, mrt_p2, frac_p1, precision, f_p1, f_p2)
        age_step, ages, age_fractions = make_age_dist(mrt, mrt_p1, mrt_p2, frac_p1, precision, f_p1, f_p2)
        source1 = pd.Series(index=np.arange(-ages.max(), 500, 10 ** -precision).round(precision), data=np.nan,
                            dtype=float)
        source1.iloc[0] = 1
        source1.iloc[-1] = 10
        source1 = source1.interpolate(method='index')
        source1 = source1.sort_index()
        source4 = deepcopy(source1)
        source4.index = (np.round(source4.index * int(10 ** precision))).astype(int)
        ages4 = (np.round(deepcopy(ages) * int(10 ** precision))).astype(int)

        outages = np.linspace(1, 400, 1000)
        outages4 = (np.round(deepcopy(outages) * int(10 ** precision))).astype(int)
        adder = source4.index.min() * -1
        source5 = deepcopy(source4).values

        v1 = lightweight_predict_future(source1, outages, ages, age_fractions, precision)
        v5 = lightweight_predict_future_int_np(source5, outages4, ages4, age_fractions, adder)
        self.assertTrue(np.allclose(v1.values, v5))


if __name__ == '__main__':
    unittest.main()
