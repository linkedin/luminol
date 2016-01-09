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
Utilities for luminol
"""
import csv
import datetime
import math
import time

from luminol import constants, exceptions


def compute_ema(smoothing_factor, points):
  """
  Compute exponential moving average of a list of points.
  :param float smoothing_factor: the smoothing factor.
  :param list points: the data points.
  :return list: all ema in a list.
  """
  ema = []
  # The initial point has a ema equal to itself.
  if(len(points) > 0):
    ema.append(points[0])
  for i in range(1, len(points)):
    ema.append(smoothing_factor * points[i] + (1 - smoothing_factor) * ema[i - 1])
  return ema


def read_csv(csv_name):
  """
  Read data from a csv file into a dictionary.
  :param str csv_name: path to a csv file.
  :return dict: a dictionary represents the data in file.
  """
  data = {}
  if not isinstance(csv_name, (str, unicode)):
    raise exceptions.InvalidDataFormat('luminol.utils: csv_name has to be a string!')
  with open(csv_name, 'r') as csv_data:
    reader = csv.reader(csv_data, delimiter=',', quotechar='|')
    for row in reader:
      try:
        key = to_epoch(row[0])
        value = float(row[1])
        data[key] = value
      except ValueError:
        pass
  return data


def to_epoch(t_str):
  """
  Covert a timestamp string to an epoch number.
  :param str t_str: a timestamp string.
  :return int: epoch number of the timestamp.
  """
  try:
    t = float(t_str)
    return t
  except:
    for format in constants.TIMESTAMP_STR_FORMATS:
      try:
        t = datetime.datetime.strptime(t_str, format)
        return float(time.mktime(t.utctimetuple()) * 1000.0 + t.microsecond / 1000.0)
      except:
        pass
  raise exceptions.InvalidDataFormat


def qbinom(p, n):
  """
  quantile function for binomial with
  probability of success 0.5
  returns smallest k such that Prob(X <= k) >= p
  compare to R qbinom
  :param n: number
  :param p: quantile level
  :return: k su
  """
  if p > 0.5:
    return n - qbinom(1 - p, n)
  elif p == 0.5:
    return n / 2

  two_nth = 0.5 ** n
  q = two_nth
  k = n
  fact = 1
  while q < 1 - p and k > 0:
    fact *= float(k) / (n - k + 1)
    q += fact * two_nth
    k -= 1

  return k


def pbinom(k, n):
  """
  Compute cdf for binomial with prob = 0.5
  uses normal approx for n > 10 (err < 0.0025)
  compare to R pbinom
  :param k:
  :param n:
  :return:
  """
  if k == n:
    return 1.0
  elif k < n / 2:
    return 1.0 - pbinom(n - k, n)
  elif n > 10:
    # use normal approximation
    con_adj = 0 if n % 2 else 0.5
    return 0.5 * (1 + math.erf((k + con_adj - n * 0.5) / (math.sqrt(n * 0.5))))

  # compute exactly
  two_nth = 0.5 ** n
  prob = 1.0 - two_nth
  fact = n
  j = n - 1
  while j > k:
    prob -= fact * two_nth
    fact *= float(j) / (n - j + 1)
    j -= 1

  return prob
