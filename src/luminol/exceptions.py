class AlgorithmNotFound(Exception):
    """
    Raise when algorithm can not be found.
    """
    pass


class RequiredParametersNotPassed(Exception):
    """
    Raise when algorithm can not be properly initialized because some required
    parameters are not passed in init.
    """
    pass


class InvalidDataFormat(Exception):
    """
    Raise when data has invalid format.
    """
    pass


class NotEnoughDataPoints(Exception):
    """
    Raise when there are not enough data points.
    """
    pass
