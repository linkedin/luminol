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
Anomaly Object
"""


class Anomaly(object):

    def __init__(self, start_timestamp, end_timestamp, anomaly_score, exact_timestamp):
        """
        Construct an anomaly object.
        :param:start_timestamp: start time of the anomaly period.
        :param:end_timestamp: end time of the anomaly period.
        :param:anomly_score: the score of the anomaly.
        :param:exact_timestamp: the timestamp within the period where the anomaly likely happened.
        """
        self.start_timestamp = start_timestamp
        self.end_timestamp = end_timestamp
        self.anomaly_score = anomaly_score
        self.exact_timestamp = exact_timestamp

    def get_time_window(self):
        """
        Get the anomaly period.
        :return tuple: a tuple representation of the anomaly period.
        """
        return self.start_timestamp, self.end_timestamp

    def __str__(self):
        """
        return string representation of the anomaly
        :return: string
        """
        return "Anomaly from {0} to {1} with score {2}".format(self.start_timestamp, self.end_timestamp, self.anomaly_score)
