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

__all__ = ['cross_correlator']


class CorrelatorAlgorithm(object):

    """
    Base class for Correlator algorithm.
    """
    def __init__(self, class_name, time_series_a, time_series_b):
        """
        Initializer
        :param class_name: name of extended class.
        :param TimeSeries time_series_a: TimeSeries a.
        :param TimeSeries time_series_b: TimeSeries b.
        """
        self.class_name = class_name
        self.time_series_a = time_series_a
        self.time_series_b = time_series_b

    # Need to be extended.
    def _detect_correlation(self):
        """
        Detect correlation.
        """
        raise NotImplementedError

    def get_correlation_result(self):
        """
        Get correlation result.
        :return CorrelationResult: a CorrelationResult object represents the correlation result.
        """
        return self.correlation_result

    def run(self):
        """
        Execute algorithm.
        :return CorrelationResult: a CorrelationResult object represents the correlation result.
        """
        self._detect_correlation()
        return self.correlation_result
