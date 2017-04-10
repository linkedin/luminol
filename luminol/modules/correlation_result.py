class CorrelationResult(object):

    def __init__(self, shift, coefficient, shifted_coefficient):
        """
        Construct a CorrelationResult object.
        :param int shift: the amount of shift where the coefficient is obtained.
        :param float coefficient: the correlation coefficient.
        :param float shifted_coefficient: the correlation coefficient with shift
            taken into account.
        """
        self.shift = shift
        self.coefficient = coefficient
        self.shifted_coefficient = shifted_coefficient
