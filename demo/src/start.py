import csv
import datetime
import os
import sys
import time
import urllib

from flask import Flask, jsonify, render_template, request

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'src'))

from luminol import utils, anomaly_detector, correlator
from rca import RCA

app = Flask(__name__)

DATA_PATH = 'static/data/'
SCORE_FILE_PATH = 'static/'


@app.route('/')
def index():
  return render_template('index.html')


@app.route('/get_selection')
def get_selection():
  fs = list()
  for f in os.listdir(DATA_PATH):
    if f.endswith('.csv'):
      fs.append(f)
  return jsonify(selection=fs)


@app.route('/detect')
def luminoldetect():
  ts = urllib.unquote(request.args.get('ts_path')[1:])
  my_detector = anomaly_detector.AnomalyDetector(ts)
  score = my_detector.get_all_scores().values

  # Create a new csv file that contains both values and scores.
  anom_scores = list()
  for i, (timestamp, value) in enumerate(my_detector.time_series.iteritems()):
    t_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp / 1000))
    anom_scores.append([t_str, value, score[i]])
  write_csv(anom_scores, ts.split('/')[-1])

  anoms = my_detector.get_anomalies()
  result = list()
  for anom in anoms:
    entry = list()
    anom_dict = anom.__dict__
    for key in anom_dict:
      entry.append(anom_dict[key])
    result.append(entry)
  return jsonify(anom=result, anom_score=anom_scores)


@app.route('/correlate')
def luminolanalyze():
  ts = urllib.unquote(request.args.get('ts_paths'))
  ts = ts.split(",")
  matrix = ts.pop(0)
  matrices = list()
  for t in ts:
    matrices.append(t)
  myluminol = RCA(matrix, matrices)
  result = myluminol.output_by_name
  return jsonify(anom=result)


@app.route('/find_correlation_list')
def findCorrelationListPerAnomaly():
  ts = urllib.unquote(request.args.get('ts')[1:])
  all_ts = os.listdir(DATA_PATH)
  matrices = list()
  for t in all_ts:
    t = DATA_PATH + t
    if t.endswith('.csv') and t != ts:
      matrices.append(t)
  myluminol = RCA(ts, matrices)
  result = myluminol.output
  r = list()
  for t in result:
    l = result[t]
    data = list()
    for entry in l:
      data.append([entry[3]] + entry[2].values())
    data_sorted = sorted(data, key=lambda k: (-k[1], k[2], -k[3]))
    r.append([t, data_sorted])
  return jsonify(anom=r)


def write_csv(rows, name):
  with open(SCORE_FILE_PATH + name, 'w+') as fp:
    writer = csv.writer(fp)
    writer.writerows(rows)


def to_epoch(anom):
  r = list()
  for a in anom:
    cur = list()
    for t in a:
      cur.append(utils.to_epoch(t))
    r.append(cur)
  return r

if __name__ == "__main__":
  app.debug = True
  app.run(host='0.0.0.0')
