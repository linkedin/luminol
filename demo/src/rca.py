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

from collections import defaultdict
import os
import sys

from luminol import utils, exceptions
from luminol.anomaly_detector import AnomalyDetector
from luminol.correlator import Correlator
from luminol.modules.correlation_result import CorrelationResult
from luminol.modules.time_series import TimeSeries


class RCA(object):
  def __init__(self, metrix, related_metrices):
    """
    Initializer
    :param metrix: a TimeSeries, a dictionary or a path to a csv file(str)
    :param list related_metrixes: a list of time series.
    """
    self.metrix = self._load(metrix)
    self.anomaly_detector = AnomalyDetector(metrix)
    self.related_metrices = related_metrices
    self.anomalies = self.anomaly_detector.get_anomalies()
    self._analyze()

  def _load(self, metrix):
    """
    Load time series.
    :param timeseries: a TimeSeries, a dictionary or a path to a csv file(str).
    :return TimeSeries: a TimeSeries object.
    """
    if isinstance(metrix, TimeSeries):
      return metrix
    if isinstance(metrix, dict):
      return TimeSeries(metrix)
    return TimeSeries(utils.read_csv(metrix))

  def _analyze(self):
    """
    Analyzes if a matrix has anomalies.
    If any anomaly is found, determine if the matrix correlates with any other matrixes.
    To be implemented.
    """
    output = defaultdict(list)
    output_by_name = defaultdict(list)
    scores = self.anomaly_detector.get_all_scores()

    if self.anomalies:
      for anomaly in self.anomalies:
        metrix_scores = scores
        start_t, end_t = anomaly.get_time_window()
        t = anomaly.exact_timestamp

        # Compute extended start timestamp and extended end timestamp.
        room = (end_t - start_t) / 2
        if not room:
          room = 30
        extended_start_t = start_t - room
        extended_end_t = end_t + room
        metrix_scores_cropped = metrix_scores.crop(extended_start_t, extended_end_t)

        # Adjust the two timestamps if not enough data points are included.
        while len(metrix_scores_cropped) < 2:
          extended_start_t = extended_start_t - room
          extended_end_t = extended_end_t + room
          metrix_scores_cropped = metrix_scores.crop(extended_start_t, extended_end_t)

        # Correlate with other metrics
        for entry in self.related_metrices:
          try:
            entry_correlation_result = Correlator(self.metrix, entry, time_period=(extended_start_t, extended_end_t),
                                                  use_anomaly_score=True).get_correlation_result()
            record = extended_start_t, extended_end_t, entry_correlation_result.__dict__, entry
            record_by_name = extended_start_t, extended_end_t, entry_correlation_result.__dict__
            output[t].append(record)
            output_by_name[entry].append(record_by_name)
          except exceptions.NotEnoughDataPoints:
            pass

    self.output = output
    self.output_by_name = output_by_name
