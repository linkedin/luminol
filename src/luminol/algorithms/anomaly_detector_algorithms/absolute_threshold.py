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


class AbsoluteThreshold(AnomalyDetectorAlgorithm):
    """
    Anomalies are those data points that are above a pre-specified threshold value.
    This algorithm does not take baseline time series.
    """
    def __init__(self, time_series, absolute_threshold_value_upper=None,
                 absolute_threshold_value_lower=None, baseline_time_series=None):
        """
        Initialize algorithm, check all required args are present

        :param time_series: The current time series dict to run anomaly detection on
        :param absolute_threshold_value_upper: Time series values above this are considered anomalies
        :param absolute_threshold_value_lower: Time series values below this are considered anomalies
        :param baseline_time_series: A no-op for now
        :return:
        """
        super(AbsoluteThreshold, self).__init__(self.__class__.__name__, time_series, baseline_time_series)
        self.absolute_threshold_value_upper = absolute_threshold_value_upper
        self.absolute_threshold_value_lower = absolute_threshold_value_lower
        if not self.absolute_threshold_value_lower and not self.absolute_threshold_value_upper:
            raise exceptions.RequiredParametersNotPassed('luminol.algorithms.anomaly_detector_algorithms.absolute_threshold: '
                                                         'Either absolute_threshold_value_upper or '
                                                         'absolute_threshold_value_lower needed')

    def _set_scores(self):
        """
        Compute anomaly scores for the time series
        This algorithm just takes the diff of threshold with current value as anomaly score
        """
        anom_scores = {}
        for timestamp, value in self.time_series.items():
            anom_scores[timestamp] = 0.0
            if self.absolute_threshold_value_upper and value > self.absolute_threshold_value_upper:
                anom_scores[timestamp] = value - self.absolute_threshold_value_upper
            if self.absolute_threshold_value_lower and value < self.absolute_threshold_value_lower:
                anom_scores[timestamp] = self.absolute_threshold_value_lower - value
        self.anom_scores = TimeSeries(self._denoise_scores(anom_scores))
