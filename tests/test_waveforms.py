"""Check waveform structure; these are not physiological validation tests."""

import importlib
import unittest

import numpy as np
from functions import waveforms


class WaveformTests(unittest.TestCase):
    def test_import_does_not_generate_demo_arrays(self):
        module = importlib.reload(waveforms)
        self.assertFalse(
            any(isinstance(value, np.ndarray) for value in vars(module).values())
        )

    def test_conventional_phase_amplitude_and_period(self):
        time, signal = waveforms.conventional(40, 0.2, 0, 30, 0.01)
        self.assertEqual(len(time), 3000)
        np.testing.assert_array_equal(signal[:20], -np.ones(20))
        np.testing.assert_array_equal(signal[20:40], np.ones(20))
        np.testing.assert_array_equal(signal[40:2500], np.zeros(2460))
        np.testing.assert_array_equal(signal[2500:2540], signal[:40])

    def test_truncated_final_pulse_has_matching_time_axis(self):
        time, signal = waveforms.conventional(40, 0.2, 0, 0.25, 0.01)
        self.assertEqual(time.shape, signal.shape)
        self.assertTrue(np.isfinite(signal).all())

    def test_passive_recharge_decays_after_negative_phase(self):
        time, signal = waveforms.conventional_passive(40, 0.2, 0, 30, 0.01, tau=0.5)
        self.assertEqual(time.shape, signal.shape)
        self.assertTrue(np.isfinite(signal).all())
        np.testing.assert_array_equal(signal[:20], -np.ones(20))
        self.assertTrue(np.all(np.diff(signal[20:60]) <= 0))
        self.assertAlmostEqual(signal[59], 0)


if __name__ == "__main__":
    unittest.main()
