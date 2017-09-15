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
from copy import copy
import math

from luminol import exceptions
from luminol.algorithms.anomaly_detector_algorithms import AnomalyDetectorAlgorithm
from luminol.modules.time_series import TimeSeries
from luminol.constants import (DEFAULT_BITMAP_PRECISION,
                               DEFAULT_BITMAP_CHUNK_SIZE,
                               DEFAULT_BITMAP_LAGGING_WINDOW_SIZE_PCT,
                               DEFAULT_BITMAP_LEADING_WINDOW_SIZE_PCT,
                               DEFAULT_BITMAP_MINIMAL_POINTS_IN_WINDOWS,
                               DEFAULT_BITMAP_MAXIMAL_POINTS_IN_WINDOWS)


class BitmapDetector(AnomalyDetectorAlgorithm):

    """
    Bitmap Algorithm.
    This method breaks time series into chunks and uses the frequency of similar chunks
    to determine anomaly scores.
    The ideas are from this paper:
    Assumption-Free Anomaly Detection in Time Series(http://alumni.cs.ucr.edu/~ratana/SSDBM05.pdf).
    """
    def __init__(self, time_series, baseline_time_series=None, precision=None,
                 lag_window_size=None, future_window_size=None, chunk_size=None):
        """
        Initializer
        :param TimeSeries time_series: a TimeSeries object.
        :param TimeSeries baseline_time_series: baseline TimeSeries.
        :param int precision: how many sections to categorize values.
        :param int lag_window_size: lagging window size.
        :param int future_window_size: future window size.
        :param int chunk_size: chunk size.
        """
        super(BitmapDetector, self).__init__(self.__class__.__name__, time_series, baseline_time_series)
        self.precision = precision if precision and precision > 0 else DEFAULT_BITMAP_PRECISION
        self.chunk_size = chunk_size if chunk_size and chunk_size > 0 else DEFAULT_BITMAP_CHUNK_SIZE
        if lag_window_size:
            self.lag_window_size = lag_window_size
        else:
            self.lag_window_size = int(self.time_series_length * DEFAULT_BITMAP_LAGGING_WINDOW_SIZE_PCT)
        if future_window_size:
            self.future_window_size = future_window_size
        else:
            self.future_window_size = int(self.time_series_length * DEFAULT_BITMAP_LEADING_WINDOW_SIZE_PCT)
        self._sanity_check()

    def _sanity_check(self):
        """
        Check if there are enough data points.
        """
        windows = self.lag_window_size + self.future_window_size
        if (not self.lag_window_size or not self.future_window_size or self.time_series_length < windows or windows < DEFAULT_BITMAP_MINIMAL_POINTS_IN_WINDOWS):
            raise exceptions.NotEnoughDataPoints

        # If window size is too big, too many data points will be assigned a score of 0 in the first lag window
        # and the last future window.
        if self.lag_window_size > DEFAULT_BITMAP_MAXIMAL_POINTS_IN_WINDOWS:
            self.lag_window_size = DEFAULT_BITMAP_MAXIMAL_POINTS_IN_WINDOWS
        if self.future_window_size > DEFAULT_BITMAP_MAXIMAL_POINTS_IN_WINDOWS:
            self.future_window_size = DEFAULT_BITMAP_MAXIMAL_POINTS_IN_WINDOWS

    def _generate_SAX_single(self, sections, value):
        """
        Generate SAX representation(Symbolic Aggregate approXimation) for a single data point.
        Read more about it here: Assumption-Free Anomaly Detection in Time Series(http://alumni.cs.ucr.edu/~ratana/SSDBM05.pdf).
        :param dict sections: value sections.
        :param float value: value to be categorized.
        :return str: a SAX representation.
        """
        sax = 0
        for section_number in sections.keys():
            section_lower_bound = sections[section_number]
            if value >= section_lower_bound:
                sax = section_number
            else:
                break
        return str(sax)

    def _generate_SAX(self):
        """
        Generate SAX representation for all values of the time series.
        """
        sections = {}
        self.value_min = self.time_series.min()
        self.value_max = self.time_series.max()
        # Break the whole value range into different sections.
        section_height = (self.value_max - self.value_min) / self.precision
        for section_number in range(self.precision):
            sections[section_number] = self.value_min + section_number * section_height
        # Generate SAX representation.
        self.sax = ''.join(self._generate_SAX_single(sections, value) for value in self.time_series.values)

    def _construct_SAX_chunk_dict(self, sax):
        """
        Form a chunk frequency dictionary from a SAX representation.
        :param str sax: a SAX representation.
        :return dict: frequency dictionary for chunks in the SAX representation.
        """
        frequency = defaultdict(int)
        chunk_size = self.chunk_size
        length = len(sax)
        for i in range(length):
            if i + chunk_size <= length:
                chunk = sax[i: i + chunk_size]
                frequency[chunk] += 1
        return frequency

    def _construct_all_SAX_chunk_dict(self):
        """
        Construct the chunk dicts for lagging window and future window at each index.
         e.g: Suppose we have a SAX sequence as '1234567890', both window sizes are 3, and the chunk size is 2.
         The first index that has a lagging window is 3. For index equals 3, the lagging window has sequence '123',
         the chunk to leave lagging window(lw_leave_chunk) is '12', and the chunk to enter lagging window(lw_enter_chunk) is '34'.
         Therefore, given chunk dicts at i, to compute chunk dicts at i+1, simply decrement the count for lw_leave_chunk,
         and increment the count for lw_enter_chunk from chunk dicts at i. Same method applies to future window as well.
        """
        lag_dicts = {}
        fut_dicts = {}
        length = self.time_series_length
        lws = self.lag_window_size
        fws = self.future_window_size
        chunk_size = self.chunk_size

        for i in range(length):
            # If i is too small or too big, there will be no chunk dicts.
            if i < lws or i > length - fws:
                lag_dicts[i] = None

            else:
                # Just enter valid range.
                if lag_dicts[i - 1] is None:
                    lag_dict = self._construct_SAX_chunk_dict(self.sax[i - lws: i])
                    lag_dicts[i] = lag_dict
                    lw_leave_chunk = self.sax[0:chunk_size]
                    lw_enter_chunk = self.sax[i - chunk_size + 1: i + 1]

                    fut_dict = self._construct_SAX_chunk_dict(self.sax[i: i + fws])
                    fut_dicts[i] = fut_dict
                    fw_leave_chunk = self.sax[i: i + chunk_size]
                    fw_enter_chunk = self.sax[i + fws + 1 - chunk_size: i + fws + 1]

                else:
                    # Update dicts according to leave_chunks and enter_chunks.
                    lag_dict = copy(lag_dicts[i - 1])
                    lag_dict[lw_leave_chunk] -= 1
                    lag_dict[lw_enter_chunk] += 1
                    lag_dicts[i] = lag_dict

                    fut_dict = copy(fut_dicts[i - 1])
                    fut_dict[fw_leave_chunk] -= 1
                    fut_dict[fw_enter_chunk] += 1
                    fut_dicts[i] = fut_dict

                    # Updata leave_chunks and enter_chunks.
                    lw_leave_chunk = self.sax[i - lws: i - lws + chunk_size]
                    lw_enter_chunk = self.sax[i - chunk_size + 1: i + 1]
                    fw_leave_chunk = self.sax[i: i + chunk_size]
                    fw_enter_chunk = self.sax[i + fws + 1 - chunk_size: i + fws + 1]

        self.lag_dicts = lag_dicts
        self.fut_dicts = fut_dicts

    def _compute_anom_score_between_two_windows(self, i):
        """
        Compute distance difference between two windows' chunk frequencies,
        which is then marked as the anomaly score of the data point on the window boundary in the middle.
        :param int i: index of the data point between two windows.
        :return float: the anomaly score.
        """
        lag_window_chunk_dict = self.lag_dicts[i]
        future_window_chunk_dict = self.fut_dicts[i]
        score = 0
        for chunk in lag_window_chunk_dict:
            if chunk in future_window_chunk_dict:
                score += math.pow(future_window_chunk_dict[chunk] - lag_window_chunk_dict[chunk], 2)
            else:
                score += math.pow(lag_window_chunk_dict[chunk], 2)
        for chunk in future_window_chunk_dict:
            if chunk not in lag_window_chunk_dict:
                score += math.pow(future_window_chunk_dict[chunk], 2)
        return score

    def _set_scores(self):
        """
        Compute anomaly scores for the time series by sliding both lagging window and future window.
        """
        anom_scores = {}
        self._generate_SAX()
        self._construct_all_SAX_chunk_dict()
        length = self.time_series_length
        lws = self.lag_window_size
        fws = self.future_window_size

        for i, timestamp in enumerate(self.time_series.timestamps):
            if i < lws or i > length - fws:
                anom_scores[timestamp] = 0
            else:
                anom_scores[timestamp] = self._compute_anom_score_between_two_windows(i)
        self.anom_scores = TimeSeries(self._denoise_scores(anom_scores))
