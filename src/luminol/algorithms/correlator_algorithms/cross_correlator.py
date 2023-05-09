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
from luminol.algorithms.correlator_algorithms import CorrelatorAlgorithm
from luminol.modules.correlation_result import CorrelationResult
from luminol.constants import (DEFAULT_SHIFT_IMPACT,
                               DEFAULT_ALLOWED_SHIFT_SECONDS)


class CrossCorrelator(CorrelatorAlgorithm):

    """
    Method 1: CrossCorrelation algorithm.
    Ideas come from Paul Bourke(http://paulbourke.net/miscellaneous/correlate/).
    """
    def __init__(self, time_series_a, time_series_b, max_shift_seconds=None, shift_impact=None):
        """
        Initializer
        :param TimeSeries time_series_a: TimeSeries a.
        :param TimeSeries time_series_b: TimeSeries b.
        :param int max_shift_seconds: allowed maximal shift seconds.
        :param time_period: if given, correlate the data inside the time period only.
        """
        super(CrossCorrelator, self).__init__(self.__class__.__name__, time_series_a, time_series_b)
        self.shift_impact = shift_impact or DEFAULT_SHIFT_IMPACT
        if max_shift_seconds is not None:
            self.max_shift_seconds = max_shift_seconds
        else:
            self.max_shift_seconds = DEFAULT_ALLOWED_SHIFT_SECONDS

    def _detect_correlation(self):
        """
        Detect correlation by computing correlation coefficients for all allowed shift steps,
        then take the maximum.
        """
        correlations = []
        shifted_correlations = []
        self.time_series_a.normalize()
        self.time_series_b.normalize()
        a, b = self.time_series_a.align(self.time_series_b)
        a_values, b_values = a.values, b.values
        a_avg, b_avg = a.average(), b.average()
        a_stdev, b_stdev = a.stdev(), b.stdev()
        n = len(a)
        denom = a_stdev * b_stdev * n
        # Find the maximal shift steps according to the maximal shift seconds.
        allowed_shift_step = self._find_allowed_shift(a.timestamps)
        if allowed_shift_step:
            shift_upper_bound = allowed_shift_step
            shift_lower_bound = -allowed_shift_step
        else:
            shift_upper_bound = 1
            shift_lower_bound = 0
        for delay in range(shift_lower_bound, shift_upper_bound):
            delay_in_seconds = a.timestamps[abs(delay)] - a.timestamps[0]
            if delay < 0:
                delay_in_seconds = -delay_in_seconds
            s = 0
            for i in range(n):
                j = i + delay
                if j < 0 or j >= n:
                    continue
                else:
                    s += ((a_values[i] - a_avg) * (b_values[j] - b_avg))
            r = s / denom if denom != 0 else s
            correlations.append([delay_in_seconds, r])
            # Take shift into account to create a "shifted correlation coefficient".
            if self.max_shift_seconds:
                shifted_correlations.append(r * (1 + float(delay_in_seconds) / self.max_shift_seconds * self.shift_impact))
            else:
                shifted_correlations.append(r)
        max_correlation = list(max(correlations, key=lambda k: k[1]))
        max_shifted_correlation = max(shifted_correlations)
        max_correlation.append(max_shifted_correlation)
        self.correlation_result = CorrelationResult(*max_correlation)

    def _find_allowed_shift(self, timestamps):
        """
        Find the maximum allowed shift steps based on max_shift_seconds.
        param list timestamps: timestamps of a time series.
        """
        init_ts = timestamps[0]
        residual_timestamps = [ts - init_ts for ts in timestamps]
        n = len(residual_timestamps)
        return self._find_first_bigger(residual_timestamps, self.max_shift_seconds, 0, n)

    def _find_first_bigger(self, timestamps, target, lower_bound, upper_bound):
        """
        Find the first element in timestamps whose value is bigger than target.
        param list values: list of timestamps(epoch number).
        param target: target value.
        param lower_bound: lower bound for binary search.
        param upper_bound: upper bound for binary search.
        """
        while lower_bound < upper_bound:
            pos = lower_bound + (upper_bound - lower_bound) / 2
            pos = int(pos)
            if timestamps[pos] > target:
                upper_bound = pos
            else:
                lower_bound = pos + 1
        return pos
