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

"""
API for Anomaly Detector Module
This module detects anomalies in a single time series.
"""

from luminol import exceptions, utils
from luminol.algorithms.anomaly_detector_algorithms.all import anomaly_detector_algorithms
from luminol.modules.anomaly import Anomaly
from luminol.modules.time_series import TimeSeries
from luminol.constants import (ANOMALY_DETECTOR_ALGORITHM, ANOMALY_THRESHOLD,
                               ANOMALY_DETECTOR_REFINE_ALGORITHM,
                               DEFAULT_SCORE_PERCENT_THRESHOLD)


class AnomalyDetector(object):

    def __init__(self, time_series, baseline_time_series=None, score_only=False, score_threshold=None,
                 score_percent_threshold=None, algorithm_name=None, algorithm_params=None, refine_algorithm_name=None,
                 refine_algorithm_params=None, algorithm_class=None):
        """
        Initializer
        :param time_series: a TimeSeries, a dictionary or a path to a csv file(str).
        :param baseline_time_series: a TimeSeries, a dictionary or a path to a csv file(str).
        :param bool score_only: if asserted, only anomaly scores are computed.
        :param float score_percent_threshold: percent threshold on anomaly score above which is considered an anomaly.
        :param str algorithm_name: name of the algorithm to use(file name).
        :param dict algorithm_params: additional params for the specific algorithm.
        :param str refine_algorithm_name: name of the refine algorithm to use(file name).
        :param dict refine_algorithm_params: additional params for the specific refine algorithm.
        :param AnomalyDetectorAlgorithm algorithm_class: A AnomalyDetectorAlgorithm class that when passed to luminol will
            be used to assign anomaly scores. This is useful when luminol user wants to use a custom algorithm.
        """

        self.time_series = self._load(time_series)
        self.baseline_time_series = self._load(baseline_time_series)
        self.score_percent_threshold = score_percent_threshold or DEFAULT_SCORE_PERCENT_THRESHOLD

        # Prepare algorithms.
        algorithm_name = algorithm_name or ANOMALY_DETECTOR_ALGORITHM
        self.algorithm = algorithm_class or self._get_algorithm(algorithm_name)
        self.threshold = score_threshold or ANOMALY_THRESHOLD.get(algorithm_name)
        self.refine_algorithm = self._get_algorithm(refine_algorithm_name or ANOMALY_DETECTOR_REFINE_ALGORITHM)

        # Prepare parameters.
        self.algorithm_params = {'time_series': self.time_series, 'baseline_time_series': self.baseline_time_series}
        algorithm_params = algorithm_params or {}
        self.algorithm_params.update(algorithm_params)
        self.refine_algorithm_params = refine_algorithm_params or {}

        # Detect anomalies.
        self._detect(score_only)

    def _load(self, time_series):
        """
        Load time series.
        :param time_series: a TimeSeries, a dictionary or a path to a csv file(str).
        :return TimeSeries: a TimeSeries object.
        """
        if not time_series:
            return None
        if isinstance(time_series, TimeSeries):
            return time_series
        if isinstance(time_series, dict):
            return TimeSeries(time_series)
        return TimeSeries(utils.read_csv(time_series))

    def _get_algorithm(self, algorithm_name):
        """
        Get the specific algorithm.
        :param str algorithm_name: name of the algorithm to use(file name).
        :return: algorithm object.
        """
        try:
            algorithm = anomaly_detector_algorithms[algorithm_name]
            return algorithm
        except KeyError:
            raise exceptions.AlgorithmNotFound('luminol.AnomalyDetector: ' + str(algorithm_name) + ' not found.')

    def _detect(self, score_only):
        """
        Detect anomaly periods.
        :param bool score_only: if true, only anomaly scores are computed.
        """
        try:
            algorithm = self.algorithm(**self.algorithm_params)
            self.anom_scores = algorithm.run()
        except exceptions.NotEnoughDataPoints:
            algorithm = anomaly_detector_algorithms['default_detector'](self.time_series)
            self.threshold = self.threshold or ANOMALY_THRESHOLD['default_detector']
            self.anom_scores = algorithm.run()
        if not score_only:
            self._detect_anomalies()

    def _detect_anomalies(self):
        """
        Detect anomalies using a threshold on anomaly scores.
        """
        anom_scores = self.anom_scores
        max_anom_score = anom_scores.max()
        anomalies = []

        if max_anom_score:
            threshold = self.threshold or max_anom_score * self.score_percent_threshold
            # Find all the anomaly intervals.
            intervals = []
            start, end = None, None
            for timestamp, value in anom_scores.iteritems():
                if value > threshold:
                    end = timestamp
                    if not start:
                        start = timestamp
                elif start and end is not None:
                    intervals.append([start, end])
                    start = None
                    end = None
            if start is not None:
                intervals.append([start, end])

            # Locate the exact anomaly point within each anomaly interval.
            for interval_start, interval_end in intervals:
                interval_series = anom_scores.crop(interval_start, interval_end)

                self.refine_algorithm_params['time_series'] = interval_series
                refine_algorithm = self.refine_algorithm(**self.refine_algorithm_params)
                scores = refine_algorithm.run()
                max_refine_score = scores.max()

                # Get the timestamp of the maximal score.
                max_refine_timestamp = scores.timestamps[scores.values.index(max_refine_score)]
                anomaly = Anomaly(interval_start, interval_end, interval_series.max(), max_refine_timestamp)
                anomalies.append(anomaly)

        self.anomalies = anomalies

    def get_anomalies(self):
        """
        Get anomalies.
        :return list: a list of Anomaly objects.
        """
        return getattr(self, 'anomalies', [])

    def get_all_scores(self):
        """
        Get anomaly scores.
        :return: a TimeSeries object represents anomaly scores.
        """
        return getattr(self, 'anom_scores', None)
