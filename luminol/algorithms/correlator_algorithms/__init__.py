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
        :return CorrelationResult: a CorrelationResult object represents the
            correlation result.
        """
        return self.correlation_result

    def run(self):
        """
        Execute algorithm.
        :return CorrelationResult: a CorrelationResult object represents the
            correlation result.
        """
        self._detect_correlation()
        return self.correlation_result
