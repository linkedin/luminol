#!/usr/bin/env python
# coding=utf-8
"""
© 2015 LinkedIn Corp. All rights reserved.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from luminol import exceptions
from luminol.anomaly_detector import AnomalyDetector
from luminol.modules.time_series import TimeSeries
# Needed for custom algorithms
from luminol.algorithms.anomaly_detector_algorithms import AnomalyDetectorAlgorithm


class TestAnomalyDetector(unittest.TestCase):

    def setUp(self):
        self.s1 = {0: 0, 1: 0, 2: 0, 3: 0, 4: 1, 5: 2, 6: 2, 7: 2, 8: 0}
        self.s2 = {0: 0, 1: 1, 2: 2, 3: 2, 4: 2, 5: 0, 6: 0, 7: 0, 8: 0}

        self.detector1 = AnomalyDetector(self.s1)
        self.detector2 = AnomalyDetector(self.s2)

    def test_custom_algorithm(self):
        """
        Test passing a custom algorithm class
        """
        detector = AnomalyDetector(self.s1, baseline_time_series=self.s2, algorithm_class=CustomAlgo,
                                   algorithm_params={'percent_threshold_upper': 20, 'percent_threshold_lower': -20})
        anomalies = detector.get_anomalies()
        self.assertTrue(anomalies is not None)
        self.assertTrue(len(anomalies) > 0)

    def test_diff_percent_threshold_algorithm(self):
        """
        Test "diff percent threshold" algorithm with a threshold of 20%
        """
        detector = AnomalyDetector(self.s1, baseline_time_series=self.s2, algorithm_name='diff_percent_threshold',
                                   algorithm_params={'percent_threshold_upper': 20, 'percent_threshold_lower': -20})
        anomalies = detector.get_anomalies()
        self.assertTrue(anomalies is not None)
        self.assertTrue(len(anomalies) > 0)
        self.assertRaises(exceptions.RequiredParametersNotPassed,
                          lambda: AnomalyDetector(self.s1, baseline_time_series=self.s2,
                                                  algorithm_name='diff_percent_threshold'))

    def test_sign_test_algorithm(self):
        """
        Test "sign test" algorithm with a threshold of 20%
        """
        bs = dict()
        bs.update((t, 1) for t in range(1, 100))
        ts = dict(bs)

        # test missing parameters
        self.assertRaises(exceptions.RequiredParametersNotPassed,
                          lambda: AnomalyDetector(self.s1, baseline_time_series=self.s2,
                                                  algorithm_name='sign_test'))
        # test over specified
        algorithm_params = {'percent_threshold_upper': 20,
                            'percent_threshold_lower': -20,
                            'scan_window': 24,
                            'confidence': 0.01}

        self.assertRaises(exceptions.RequiredParametersNotPassed,
                          lambda: AnomalyDetector(self.s1, baseline_time_series=self.s2,
                                                  algorithm_name='sign_test'))
        # Simple tests
        algorithm_params = {'percent_threshold_upper': 20,
                            'scan_window': 24}

        # first no anomalies
        detector = AnomalyDetector(ts, baseline_time_series=bs, algorithm_name='sign_test',
                                   algorithm_params=algorithm_params)
        anomalies = detector.get_anomalies()

        self.assertTrue(anomalies is not None)
        self.assertEqual(len(anomalies), 0)

        # Next one anomaly exactly equal to scan window
        ts.update((t, 1.200001) for t in range(10, 34))
        detector = AnomalyDetector(ts, baseline_time_series=bs, algorithm_name='sign_test',
                                   algorithm_params=algorithm_params)
        anomalies = detector.get_anomalies()

        self.assertTrue(anomalies is not None)
        self.assertEqual(len(anomalies), 1)
        anomaly = anomalies[0]
        s, e = anomaly.get_time_window()

        # note the anomaly is larger than scan window
        self.assertEqual(s, 4)
        self.assertEqual(e, 39)

        # score should be roughly 98.5
        self.assertGreater(anomaly.anomaly_score, 98)
        self.assertLess(anomaly.anomaly_score, 99)

        # anomaly below baseline
        algorithm_params = {'percent_threshold_lower': -20,
                            'scan_window': 24,
                            'confidence': 0.01}
        ts.update((t, 0.799999) for t in range(10, 34))

        detector = AnomalyDetector(ts, baseline_time_series=bs, algorithm_name='sign_test',
                                   algorithm_params=algorithm_params)
        anomalies = detector.get_anomalies()
        self.assertEqual(len(anomalies), 1)
        anomaly = anomalies[0]
        s, e = anomaly.get_time_window()
        self.assertEqual(s, 4)
        self.assertEqual(e, 39)

        # score should be roughly 98.5
        self.assertGreater(anomaly.anomaly_score, 98)
        self.assertLess(anomaly.anomaly_score, 99)

        # anomalies separated by big gap
        ts.update(bs)
        ts.update((t, 0.799999) for t in range(1, 25))
        ts.update((t, 0.799999) for t in range(60, 84))
        detector = AnomalyDetector(ts, baseline_time_series=bs, algorithm_name='sign_test',
                                   algorithm_params=algorithm_params)
        anomalies = detector.get_anomalies()
        self.assertEqual(len(anomalies), 2)
        anomaly = anomalies[0]
        s, e = anomaly.get_time_window()
        self.assertEqual(s, 1)
        self.assertEqual(e, 30)

        # score ~ 99.9
        self.assertGreater(anomaly.anomaly_score, 99)

        anomaly = anomalies[1]
        s, e = anomaly.get_time_window()
        self.assertEqual(s, 54)
        self.assertEqual(e, 89)

        # score should be roughly 98.5
        self.assertGreater(anomaly.anomaly_score, 98)
        self.assertLess(anomaly.anomaly_score, 99)

        # anomalies separated by small gap
        algorithm_params = {'percent_threshold_upper': 20,
                            'scan_window': 24}
        ts.update(bs)
        ts.update((t, 1.21) for t in range(1, 25))
        ts.update((t, 1.21) for t in range(30, 40))
        detector = AnomalyDetector(ts, baseline_time_series=bs, algorithm_name='sign_test',
                                   algorithm_params=algorithm_params)
        anomalies = detector.get_anomalies()

        # just one
        self.assertEqual(len(anomalies), 1)
        anomaly = anomalies[0]
        s, e = anomaly.get_time_window()
        self.assertEqual(s, 1)
        self.assertEqual(e, 40)

        # score ~ 99.9
        self.assertGreater(anomaly.anomaly_score, 99)

        # try noisy data
        ts.update(bs)
        ts.update((t, 1.21) for t in range(1, 25))
        ts.update((t, 1.19) for t in range(1, 25, 6))
        algorithm_params = {'percent_threshold_upper': 20,
                            'scan_window': 24,
                            'confidence': 0.01}

        detector = AnomalyDetector(ts, baseline_time_series=bs, algorithm_name='sign_test',
                                   algorithm_params=algorithm_params)
        anomalies = detector.get_anomalies()
        self.assertEqual(len(anomalies), 1)

        # now decrease sensitivity
        algorithm_params = {'percent_threshold_upper': 20,
                            'scan_window': 24,
                            'confidence': 0.0001}

        detector = AnomalyDetector(ts, baseline_time_series=bs, algorithm_name='sign_test',
                                   algorithm_params=algorithm_params)
        anomalies = detector.get_anomalies()
        self.assertEqual(len(anomalies), 0)

    def test_sign_test_algorithm_interface(self):
        """
        Test "sign test" algorithm with a threshold of 0%
        """
        bs = dict()
        bs.update((t, 1) for t in range(1, 30))

        # Simple tests
        algorithm_params = {'percent_threshold_upper': 0,
                            'offset': 2,
                            'scan_window': 24,
                            'confidence': 0.01}
        ts = dict(bs)
        # bigger than 10 percent but below bias
        ts.update((t, 3.1) for t in range(1, 21))

        # first no anomalies
        detector = AnomalyDetector(ts, baseline_time_series=bs, algorithm_name='sign_test',
                                   algorithm_params=algorithm_params)
        anomalies = detector.get_anomalies()

        self.assertTrue(anomalies is not None)
        self.assertEqual(len(anomalies), 1)

        # try lower bound
        algorithm_params = {'percent_threshold_lower': 0,
                            'offset': 2,
                            'scan_window': 24,
                            'confidence': 0.01}
        ts = dict(bs)
        # less than baseline plus bias
        ts.update((t, 2.9) for t in range(1, 25))

        # first no anomalies
        detector = AnomalyDetector(ts, baseline_time_series=bs, algorithm_name='sign_test',
                                   algorithm_params=algorithm_params)
        anomalies = detector.get_anomalies()

        self.assertTrue(anomalies is not None)
        self.assertEqual(len(anomalies), 1)

    def test_sign_test_algorithm_with_shift(self):
        """
        Test "sign test" algorithm with a threshold of 20%
        """
        bs = dict()
        bs.update((t, 1) for t in range(1, 100))

        # Simple tests
        algorithm_params = {'percent_threshold_upper': 10,
                            'offset': 1,
                            'scan_window': 24,
                            'confidence': 0.01}
        ts = dict(bs)
        # bigger than 10 percent but below bias
        ts.update((t, 1.2) for t in range(10, 34))

        # first no anomalies
        detector = AnomalyDetector(ts, baseline_time_series=bs, algorithm_name='sign_test',
                                   algorithm_params=algorithm_params)
        anomalies = detector.get_anomalies()

        self.assertTrue(anomalies is not None)
        self.assertEqual(len(anomalies), 0)

        # Next one anomaly exactly equal to scan window
        # uses bias
        ts.update((t, 2.100001) for t in range(10, 34))
        detector = AnomalyDetector(ts, baseline_time_series=bs, algorithm_name='sign_test',
                                   algorithm_params=algorithm_params)
        anomalies = detector.get_anomalies()

        self.assertTrue(anomalies is not None)
        self.assertEqual(len(anomalies), 1)
        anomaly = anomalies[0]
        s, e = anomaly.get_time_window()

        # note the anomaly is larger than scan window
        self.assertEqual(s, 4)
        self.assertEqual(e, 39)

        # score should be roughly 98.5
        self.assertGreater(anomaly.anomaly_score, 98)
        self.assertLess(anomaly.anomaly_score, 99)

        # anomaly below baseline but not below baseline with shift
        algorithm_params = {'percent_threshold_lower': -20,
                            'offset': -0.1,
                            'scan_window': 24}

        ts.update((t, 0.799999) for t in range(10, 34))
        # no anomalies
        detector = AnomalyDetector(ts, baseline_time_series=bs, algorithm_name='sign_test',
                                   algorithm_params=algorithm_params)
        anomalies = detector.get_anomalies()

        self.assertTrue(anomalies is not None)
        self.assertEqual(len(anomalies), 0)

        # lower the time series by 0.1
        ts.update((t, 0.699999) for t in range(10, 34))

        detector = AnomalyDetector(ts, baseline_time_series=bs, algorithm_name='sign_test',
                                   algorithm_params=algorithm_params)
        anomalies = detector.get_anomalies()
        self.assertEqual(len(anomalies), 1)
        anomaly = anomalies[0]
        s, e = anomaly.get_time_window()
        self.assertEqual(s, 4)
        self.assertEqual(e, 39)

        # score should be roughly 98.5
        self.assertGreater(anomaly.anomaly_score, 98)
        self.assertLess(anomaly.anomaly_score, 99)

    def test_absolute_threshold_algorithm(self):
        """
        Test "absolute threshold" algorithm with a upper and lower threshold of 0.2
        """
        detector = AnomalyDetector(self.s1, algorithm_name='absolute_threshold',
                                   algorithm_params={'absolute_threshold_value_upper': 0.2,
                                                     'absolute_threshold_value_lower': 0.2})
        anomalies = detector.get_anomalies()
        self.assertTrue(anomalies is not None)
        self.assertTrue(len(anomalies) > 0)
        self.assertRaises(exceptions.RequiredParametersNotPassed,
                          lambda: AnomalyDetector(self.s1, algorithm_name='absolute_threshold'))

    def test_threshold(self):
        """
        Test score threshold=0
        """
        detector = AnomalyDetector(self.s1, score_threshold=0)
        self.assertTrue(len(detector.get_anomalies()) == 1)
        self.assertTrue(detector.get_anomalies() is not None)

    def test_score_only(self):
        """
        Test that score_only parameter doesn't give anomalies
        """
        detector = AnomalyDetector(self.s1, score_only=True, algorithm_name='derivative_detector')
        detector2 = AnomalyDetector(self.s1, algorithm_name='derivative_detector')
        self.assertTrue(detector2.get_anomalies() is not None)
        self.assertTrue(len(detector.get_anomalies()) == 0)

    def test_get_all_scores(self):
        """
        Test if function get_all_scores works as expected.
        """
        self.assertTrue(isinstance(self.detector1.get_all_scores(), TimeSeries))
        self.assertEqual(len(self.detector1.get_all_scores()), len(self.detector1.time_series))

    def test_get_anomalies(self):
        """
        Test if anomaly is found as expected.
        """
        self.assertTrue(self.detector1.get_anomalies() is not None)

    def test_algorithm_DefaultDetector(self):
        """
        Test if optional parameter algorithm works as expected.
        """
        detector = AnomalyDetector(self.s1, algorithm_name='default_detector')
        self.assertEqual(detector.get_all_scores().timestamps, self.detector1.get_all_scores().timestamps)
        self.assertEqual(detector.get_all_scores().values, self.detector1.get_all_scores().values)

    def test_algorithm(self):
        """
        Test if exception AlgorithmNotFound is raised as expected.
        """
        self.assertRaises(exceptions.AlgorithmNotFound, lambda: AnomalyDetector(self.s1, algorithm_name='NotValidAlgorithm'))

    def test_algorithm_params(self):
        """
        Test if optional parameter algorithm_params works as expected.
        """
        self.assertRaises(ValueError, lambda: AnomalyDetector(self.s1, algorithm_name='exp_avg_detector', algorithm_params='0'))
        detector = AnomalyDetector(self.s1, algorithm_name="exp_avg_detector", algorithm_params={'smoothing_factor': 0.3})
        self.assertNotEqual(self.detector1.get_all_scores().values, detector.get_all_scores().values)

    def test_anomaly_threshold(self):
        """
        Test if score_percentile_threshold works as expected.
        """
        detector = AnomalyDetector(self.s1, score_percent_threshold=0.1, algorithm_name='exp_avg_detector')
        detector1 = AnomalyDetector(self.s1, score_percent_threshold=0.1, algorithm_name='derivative_detector')
        self.assertNotEqual(detector1.get_anomalies(), detector.get_anomalies())


class CustomAlgo(AnomalyDetectorAlgorithm):
    """
    Copy of DiffPercentThreshold Algorithm from algorithms/anomaly_detector_algorithms/diff_percent_threshold.py to test
    whether passing a AnomalyDetectorAlgorithm class works for AnomalyDetector module
    """
    def __init__(self, time_series, baseline_time_series, percent_threshold_upper=None, percent_threshold_lower=None):
        """
        :param time_series: current time series
        :param baseline_time_series: baseline time series
        :param percent_threshold_upper: If time_series is larger than baseline_time_series by this percent, then its
        an anomaly
        :param percent_threshold_lower: If time_series is smaller than baseline_time_series by this percent, then its
        an anomaly
        """
        super(CustomAlgo, self).__init__(self.__class__.__name__, time_series, baseline_time_series)
        self.percent_threshold_upper = percent_threshold_upper
        self.percent_threshold_lower = percent_threshold_lower
        # print "CustomAlgo being initiated"

    def _set_scores(self):
        """
        Compute anomaly scores for the time series
        This algorithm just takes the diff of threshold with current value as anomaly score
        """
        anom_scores = {}
        for i, (timestamp, value) in enumerate(self.time_series.items()):

            baseline_value = self.baseline_time_series[i]

            if baseline_value > 0:
                diff_percent = 100 * (value - baseline_value) / baseline_value
            elif value > 0:
                diff_percent = 100.0
            else:
                diff_percent = 0.0

            anom_scores[timestamp] = 0.0
            if self.percent_threshold_upper and diff_percent > 0 and diff_percent > self.percent_threshold_upper:
                anom_scores[timestamp] = diff_percent
            if self.percent_threshold_lower and diff_percent < 0 and diff_percent < self.percent_threshold_lower:
                anom_scores[timestamp] = -1 * diff_percent

        self.anom_scores = TimeSeries(self._denoise_scores(anom_scores))


if __name__ == '__main__':
    unittest.main()
