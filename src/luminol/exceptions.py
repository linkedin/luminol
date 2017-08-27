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
Exception Classes
"""


class AlgorithmNotFound(Exception):

    """
    Raise when algorithm can not be found.
    """
    pass


class RequiredParametersNotPassed(Exception):

    """
    Raise when algorithm can not be properly initialized because some required parameters are not passed in init.
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
