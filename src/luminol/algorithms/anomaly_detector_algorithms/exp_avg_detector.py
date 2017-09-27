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
import numpy

from luminol import utils
from luminol.algorithms.anomaly_detector_algorithms import AnomalyDetectorAlgorithm
from luminol.modules.time_series import TimeSeries
from luminol.constants import (DEFAULT_EMA_SMOOTHING_FACTOR,
                               DEFAULT_EMA_WINDOW_SIZE_PCT)


class ExpAvgDetector(AnomalyDetectorAlgorithm):

    """
    Exponential Moving Average.
    This method uses a data point's deviation from the exponential moving average of a lagging window
    to determine its anomaly score.
    """
    def __init__(self, time_series, baseline_time_series=None, smoothing_factor=0, use_lag_window=False, lag_window_size=None):
        """
        Initializer
        :param TimeSeries time_series: a TimeSeries object.
        :param TimeSeries baseline_time_series: baseline TimeSeries.
        :param float smoothing_factor: smoothing factor for computing exponential moving average.
        :param int lag_window_size: lagging window size.
        """
        super(ExpAvgDetector, self).__init__(self.__class__.__name__, time_series, baseline_time_series)
        self.use_lag_window = use_lag_window
        self.smoothing_factor = smoothing_factor if smoothing_factor > 0 else DEFAULT_EMA_SMOOTHING_FACTOR
        self.lag_window_size = lag_window_size if lag_window_size else int(self.time_series_length * DEFAULT_EMA_WINDOW_SIZE_PCT)
        self.time_series_items = self.time_series.items()

    def _compute_anom_score(self, lag_window_points, point):
        """
        Compute anomaly score for a single data point.
        Anomaly score for a single data point(t,v) equals: abs(v - ema(lagging window)).
        :param list lag_window_points: values in the lagging window.
        :param float point: data point value.
        :return float: the anomaly score.
        """
        ema = utils.compute_ema(self.smoothing_factor, lag_window_points)[-1]
        return abs(point - ema)

    def _compute_anom_data_using_window(self):
        """
        Compute anomaly scores using a lagging window.
        """
        anom_scores = {}
        values = self.time_series.values
        stdev = numpy.std(values)
        for i, (timestamp, value) in enumerate(self.time_series_items):
            if i < self.lag_window_size:
                anom_score = self._compute_anom_score(values[:i + 1], value)
            else:
                anom_score = self._compute_anom_score(values[i - self.lag_window_size: i + 1], value)
            if stdev:
                anom_scores[timestamp] = anom_score / stdev
            else:
                anom_scores[timestamp] = anom_score
        self.anom_scores = TimeSeries(self._denoise_scores(anom_scores))

    def _compute_anom_data_decay_all(self):
        """
        Compute anomaly scores using a lagging window covering all the data points before.
        """
        anom_scores = {}
        values = self.time_series.values
        ema = utils.compute_ema(self.smoothing_factor, values)
        stdev = numpy.std(values)
        for i, (timestamp, value) in enumerate(self.time_series_items):
            anom_score = abs((value - ema[i]) / stdev) if stdev else value - ema[i]
            anom_scores[timestamp] = anom_score
        self.anom_scores = TimeSeries(self._denoise_scores(anom_scores))

    def _set_scores(self):
        """
        Compute anomaly scores for the time series.
        Currently uses a lagging window covering all the data points before.
        """
        if self.use_lag_window:
            self._compute_anom_data_using_window()
        self._compute_anom_data_decay_all()
