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
"""
Correlation object
"""


class CorrelationResult(object):

    def __init__(self, shift, coefficient, shifted_coefficient):
        """
        Construct a CorrelationResult object.
        :param int shift: the amount of shift where the coefficient is obtained.
        :param float coefficient: the correlation coefficient.
        :param float shifted_coefficient: the correlation coefficient with shift taken into account.
        """
        self.shift = shift
        self.coefficient = coefficient
        self.shifted_coefficient = shifted_coefficient
