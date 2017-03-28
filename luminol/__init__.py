from luminol import exceptions


class Luminol(object):

    def __init__(self, anomalies, correlations):
        """
        :param list anomalies: a list of `Anomaly` objects.
            `Anomaly` is defined in luminol.modules.anomaly.
        :param dict correlations: a dict represents correlated
            metrics(`TimeSeries` object) to each anomaly.
            each key-value pair looks like this:
            `Anomaly` --> [metric1, metric2, metric3 ...].
        """
        self.anomalies = anomalies
        self.correlations = correlations
        self._analyze_root_causes()

    # TODO(yaguo): Replace this with valid root cause analysis.
    def _analyze_root_causes(self):
        """
        Conduct root cause analysis.
        The first metric of the list is taken as the root cause right now.
        """
        causes = {}
        for a in self.anomalies:
            try:
                causes[a] = self.correlations[a][0]
            except IndexError:
                raise exceptions.InvalidDataFormat('luminol.luminol: dict correlations contains empty list.')
        self.causes = causes

    def get_root_causes(self):
        """
        Get root causes.
        :return dict: a dict represents root causes for each anomaly.
        """
        return getattr(self, 'causes', None)
