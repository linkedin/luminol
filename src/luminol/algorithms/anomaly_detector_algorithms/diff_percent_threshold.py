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

from luminol import exceptions
from luminol.algorithms.anomaly_detector_algorithms import AnomalyDetectorAlgorithm
from luminol.modules.time_series import TimeSeries


class DiffPercentThreshold(AnomalyDetectorAlgorithm):
    """
    In this algorithm, anomalies are those data points that are above a percentage threshold as compared to the baseline.
    This algorithm assumes that time_series and baseline_time_series are perfectly aligned, meaning that:
     a) every timestamp that exists in time_series also exists in baseline_time_series
     b) lengths of both time series are same
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
        super(DiffPercentThreshold, self).__init__(self.__class__.__name__, time_series, baseline_time_series)
        self.percent_threshold_upper = percent_threshold_upper
        self.percent_threshold_lower = percent_threshold_lower
        if not self.percent_threshold_upper and not self.percent_threshold_lower:
            raise exceptions.RequiredParametersNotPassed('luminol.algorithms.anomaly_detector_algorithms.diff_percent_threshold: \
                    Either percent_threshold_upper or percent_threshold_lower needed')

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
