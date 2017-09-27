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
from luminol.algorithms.anomaly_detector_algorithms.exp_avg_detector import ExpAvgDetector
from luminol.algorithms.anomaly_detector_algorithms.derivative_detector import DerivativeDetector
from luminol.algorithms.anomaly_detector_algorithms import AnomalyDetectorAlgorithm
from luminol.modules.time_series import TimeSeries
from luminol.constants import (DEFAULT_DETECTOR_EMA_WEIGHT,
                               DEFAULT_DETECTOR_EMA_SIGNIFICANT)


class DefaultDetector(AnomalyDetectorAlgorithm):

    """
    Default detector.
    Not configurable.
    """
    def __init__(self, time_series, baseline_time_series=None):
        """
        Initializer
        :param TimeSeries time_series: a TimeSeries object.
        :param TimeSeries baseline_time_series: baseline TimeSeries.
        """
        self.exp_avg_detector = ExpAvgDetector(time_series, baseline_time_series)
        self.derivative_detector = DerivativeDetector(time_series, baseline_time_series)

    def _set_scores(self):
        """
        Set anomaly scores using a weighted sum.
        """
        anom_scores_ema = self.exp_avg_detector.run()
        anom_scores_deri = self.derivative_detector.run()
        anom_scores = {}
        for timestamp in anom_scores_ema.timestamps:
            # Compute a weighted anomaly score.
            anom_scores[timestamp] = max(anom_scores_ema[timestamp],
                                         anom_scores_ema[timestamp] * DEFAULT_DETECTOR_EMA_WEIGHT + anom_scores_deri[timestamp] * (1 - DEFAULT_DETECTOR_EMA_WEIGHT))
            # If ema score is significant enough, take the bigger one of the weighted score and deri score.
            if anom_scores_ema[timestamp] > DEFAULT_DETECTOR_EMA_SIGNIFICANT:
                anom_scores[timestamp] = max(anom_scores[timestamp], anom_scores_deri[timestamp])
        self.anom_scores = TimeSeries(self._denoise_scores(anom_scores))
