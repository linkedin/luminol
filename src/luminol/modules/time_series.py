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


class TimeSeries(object):

    def __init__(self, series):
        self.timestamps = []
        self.values = []

        # Clean the time series by removing null values.
        for ts in sorted(series):
            if series[ts] is not None:
                self.timestamps.append(int(ts))
                self.values.append(float(series[ts]))

    @property
    def start(self):
        """
        Return the earliest timestamp in the time series.
        """
        return min(self.timestamps) if self.timestamps else None

    @property
    def end(self):
        """
        Return the latest timestamp in the time series.
        """
        return max(self.timestamps) if self.timestamps else None

    @property
    def timestamps_ms(self):
        """
        Return list of timestamp values in order by milliseconds since epoch.
        """
        return [ts * 1000 for ts in self.timestamps]

    def __repr__(self):
        return 'TimeSeries<start={0}, end={1}>'.format(repr(self.start), repr(self.end))

    def __str__(self):
        """
        :return string: Return string representation of time series
        """
        string_rep = ''
        for item in self.iteritems():
            string_rep += str(item)
        return string_rep

    def __nonzero__(self):
        return len(self.timestamps) > 0

    def __getitem__(self, key):
        if key in self.timestamps:
            pos = self.timestamps.index(key)
            return self.values[pos]
        else:
            raise ValueError('Timestamp does not exist in TimeSeries object')

    def __setitem__(self, key, val):
        if key in self.timestamps:
            pos = self.timestamps.index(key)
            if val is None:
                del self.timestamps[pos]
                del self.values[pos]
            else:
                self.values[pos] = val
        else:
            self.timestamps = sorted(self.timestamps + [key])
            pos = self.timestamps.index(key)
            self.values.insert(pos, val)

    def __delitem__(self, key):
        if key in self.timestamps:
            pos = self.timestamps.index(key)
            del self.timestamps[pos]
            del self.values[pos]

    def __contains__(self, item):
        return item in self.timestamps

    def __iter__(self):
        for key in self.timestamps:
            yield key

    def __len__(self):
        return len(self.timestamps)

    def __eq__(self, other):
        if len(self.timestamps) != len(other.timestamps):
            return False

        for pos, ts in enumerate(self.timestamps):
            if ts != other.timestamps[pos] or self.values[pos] != other.values[pos]:
                return False
        else:
            return True

    def __add__(self, other):
        return self._generic_binary_op(other, self._get_value_type(other).__add__)

    def __sub__(self, other):
        return self._generic_binary_op(other, self._get_value_type(other).__sub__)

    def __mul__(self, other):
        return self._generic_binary_op(other, self._get_value_type(other).__mul__)

    def __div__(self, other):
        return self._generic_binary_op(other, self._get_value_type(other).__div__)

    __radd__ = __add__
    __rmul__ = __mul__

    def __rsub__(self, other):
        return self._generic_binary_op(other, self._get_value_type(other).__rsub__)

    def __rdiv__(self, other):
        return self._generic_binary_op(other, self._get_value_type(other).__rdiv__)

    def items(self):
        return [(ts, self.values[pos]) for pos, ts in enumerate(self.timestamps)]

    def iterkeys(self):
        for key in self.timestamps:
            yield key

    def itervalues(self):
        for value in self.values:
            yield value

    def iteritems(self):
        for item in self.items():
            yield item

    def iteritems_silent(self):
        for item in self.items():
            yield item
        yield None

    def _generic_binary_op(self, other, op):
        """
        Perform the method operation specified in the op parameter on the values
        within the instance's time series values and either another time series
        or a constant number value.

        :param other: Time series of values or a constant number to use in calculations with instance's time series.
        :param func op: The method to perform the calculation between the values.
        :return: :class:`TimeSeries` object.
        """
        output = {}
        if isinstance(other, TimeSeries):
            for key, value in self.items():
                if key in other:
                    try:
                        result = op(value, other[key])
                        if result is NotImplemented:
                            other_type = type(other[key])
                            other_op = vars(other_type).get(op.__name__)
                            if other_op:
                                output[key] = other_op(other_type(value), other[key])
                        else:
                            output[key] = result
                    except ZeroDivisionError:
                        continue
        else:
            for key, value in self.items():
                try:
                    result = op(value, other)
                    if result is NotImplemented:
                        other_type = type(other)
                        other_op = vars(other_type).get(op.__name__)
                        if other_op:
                            output[key] = other_op(other_type(value), other)
                    else:
                        output[key] = result
                except ZeroDivisionError:
                    continue

        if output:
            return TimeSeries(output)
        else:
            raise ValueError('TimeSeries data was empty or invalid.')

    def _get_value_type(self, other):
        """
        Get the object type of the value within the values portion of the time series.

        :return: `type` of object
        """
        if self.values:
            return type(self.values[0])
        elif isinstance(other, TimeSeries) and other.values:
            return type(other.values[0])
        else:
            raise ValueError('Cannot perform arithmetic on empty time series.')

    def align(self, other):
        """
        Align two time series so that len(self) == len(other) and self.timstamps == other.timestamps.

        :return: :tuple:(`TimeSeries` object(the aligned self), `TimeSeries` object(the aligned other))
        """
        if isinstance(other, TimeSeries):
            aligned, other_aligned = {}, {}
            i, other_i = self.iteritems_silent(), other.iteritems_silent()
            item, other_item = next(i), next(other_i)

            while item and other_item:
                # Unpack timestamps and values.
                timestamp, value = item
                other_timestamp, other_value = other_item
                if timestamp == other_timestamp:
                    aligned[timestamp] = value
                    other_aligned[other_timestamp] = other_value
                    item = next(i)
                    other_item = next(other_i)
                elif timestamp < other_timestamp:
                    aligned[timestamp] = value
                    other_aligned[timestamp] = other_value
                    item = next(i)
                else:
                    aligned[other_timestamp] = value
                    other_aligned[other_timestamp] = other_value
                    other_item = next(other_i)
            # Align remaining items.
            while item:
                timestamp, value = item
                aligned[timestamp] = value
                other_aligned[timestamp] = other.values[-1]
                item = next(i)
            while other_item:
                other_timestamp, other_value = other_item
                aligned[other_timestamp] = self.values[-1]
                other_aligned[other_timestamp] = other_value
                other_item = next(other_i)
            return TimeSeries(aligned), TimeSeries(other_aligned)

    def smooth(self, smoothing_factor):
        """
        return a new time series which is a exponential smoothed version of the original data series.
        soomth forward once, backward once, and then take the average.

        :param float smoothing_factor: smoothing factor
        :return: :class:`TimeSeries` object.
        """
        forward_smooth = {}
        backward_smooth = {}
        output = {}

        if self:
            pre = self.values[0]
            next = self.values[-1]
            for key, value in self.items():
                forward_smooth[key] = smoothing_factor * pre + (1 - smoothing_factor) * value
                pre = forward_smooth[key]
            for key, value in reversed(self.items()):
                backward_smooth[key] = smoothing_factor * next + (1 - smoothing_factor) * value
                next = backward_smooth[key]
            for key in forward_smooth.keys():
                output[key] = (forward_smooth[key] + backward_smooth[key]) / 2

        return TimeSeries(output)

    def add_offset(self, offset):
        """
        Return a new time series with all timestamps incremented by some offset.

        :param int offset: The number of seconds to offset the time series.
        :return: `None`
        """
        self.timestamps = [ts + offset for ts in self.timestamps]

    def normalize(self):
        """
        Return a new time series with all values normalized between 0 and 1.

        :return: `None`
        """
        maximum = self.max()
        if maximum:
            minimum = self.min()
            self.values = [((value - minimum) / (maximum - minimum)) for value in self.values]

    def crop(self, start_timestamp, end_timestamp):
        """
        Return a new TimeSeries object contains all the timstamps and values within
        the specified range.

        :param int start_timestamp: the start timestamp value
        :param int end_timestamp: the end timestamp value
        :return: :class:`TimeSeries` object.
        """
        output = {}
        for key, value in self.items():
            if key >= start_timestamp and key <= end_timestamp:
                output[key] = value

        if output:
            return TimeSeries(output)
        else:
            raise ValueError('TimeSeries data was empty or invalid.')

    def average(self, default=None):
        """
        Calculate the average value over the time series.

        :param default: Value to return as a default should the calculation not be possible.
        :return: Float representing the average value or `None`.
        """
        return numpy.asscalar(numpy.average(self.values)) if self.values else default

    def median(self, default=None):
        """
        Calculate the median value over the time series.

        :param default: Value to return as a default should the calculation not be possible.
        :return: Float representing the median value or `None`.
        """
        return numpy.asscalar(numpy.median(self.values)) if self.values else default

    def max(self, default=None):
        """
        Calculate the maximum value over the time series.

        :param default: Value to return as a default should the calculation not be possible.
        :return: Float representing the maximum value or `None`.
        """
        return numpy.asscalar(numpy.max(self.values)) if self.values else default

    def min(self, default=None):
        """
        Calculate the minimum value over the time series.

        :param default: Value to return as a default should the calculation not be possible.
        :return: Float representing the maximum value or `None`.
        """
        return numpy.asscalar(numpy.min(self.values)) if self.values else default

    def percentile(self, n, default=None):
        """
        Calculate the Nth Percentile value over the time series.

        :param int n: Integer value of the percentile to calculate.
        :param default: Value to return as a default should the calculation not be possible.
        :return: Float representing the Nth percentile value or `None`.
        """
        return numpy.asscalar(numpy.percentile(self.values, n)) if self.values else default

    def stdev(self, default=None):
        """
        Calculate the standard deviation of the time series.

        :param default: Value to return as a default should the calculation not be possible.
        :return: Float representing the standard deviation value or `None`.
        """
        return numpy.asscalar(numpy.std(self.values)) if self.values else default

    def sum(self, default=None):
        """
        Calculate the sum of all the values in the times series.

        :param default: Value to return as a default should the calculation not be possible.
        :return: Float representing the sum or `None`.
        """
        return numpy.asscalar(numpy.sum(self.values)) if self.values else default
