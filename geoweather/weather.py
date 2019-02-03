import time
import urllib.parse
from collections import OrderedDict

import requests
from flask import Blueprint, request, jsonify, current_app

from geoweather import db

bp = Blueprint('weather', __name__)


@bp.route('/weather')
def weather():
  query = request.args.get('query')
  language = request.args.get('lang', 'zh-CN' if is_chinese(query) else 'en')
  config = current_app.config

  db_client = db.get_db()
  query_result = db_client.execute(
      'SELECT formatted_address, longitude, latitude FROM geocodes WHERE query = ?',
      (query,)
  ).fetchone()
  if query_result is None:
    response = requests.get('https://maps.googleapis.com/maps/api/geocode/json',
                            params={
                              'address': query,
                              'key': config['GEOCODING_API_KEY'],
                              'language': language})
    json_response = response.json()
    if json_response['status'] == 'OK':
      result = json_response['results'][0]
      formatted_address = result['formatted_address']
      longitude = result['geometry']['location']['lng']
      latitude = result['geometry']['location']['lat']
      db_client.execute(
          'INSERT INTO geocodes (query, formatted_address, longitude, latitude) VALUES (?, ?, ?, ?)',
          (query, formatted_address, longitude, latitude)
      )
      db_client.commit()
    else:
      return jsonify({
        'query': query,
        'formatted_address': '',
        'longitude': None,
        'latitude': None,
        '7timer_url': ''
      })
  else:
    formatted_address, longitude, latitude = query_result
  return jsonify({
    'query': query,
    'formatted_address': formatted_address,
    'longitude': longitude,
    'latitude': latitude,
    '7timer_url': build_url('http://www.7timer.info/bin/astro.php', {
      'lon': longitude,
      'lat': latitude,
      'lang': language,
      'time': int(time.time())
    })})


def build_url(base_url, params):
  return base_url + '?' + urllib.parse.urlencode(OrderedDict(
      sorted(params.items(), key=lambda t: t[0]))) if params else base_url


def is_chinese(s):
  return any('\u4e00' <= c <= '\u9fff' for c in s)
