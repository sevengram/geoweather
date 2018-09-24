from unittest.mock import MagicMock
from unittest.mock import patch

from requests.models import Response


def test_weather_cached(client):
  response = client.get('/weather', query_string={'query': 'Shanghai'})
  assert response.status_code == 200
  assert response.json == {
    'query': 'Shanghai',
    'formatted_address': 'Shanghai, China',
    'longitude': 121.47,
    'latitude': 31.23,
    '7timer_url': 'http://www.7timer.info/bin/astro.php?lang=en&lat=31.23&lon=121.47'
  }


def test_weather_non_cached(client):
  mock_response = Response()
  mock_response.json = MagicMock(return_value={
    'results': [
      {
        'formatted_address': '\u4e2d\u56fd\u5317\u4eac',
        'geometry': {
          'location': {
            'lng': 116.41,
            'lat': 39.91
          }
        }
      }
    ],
    'status': 'OK'})
  with patch('requests.get', return_value=mock_response):
    response = client.get('/weather', query_string={'query': '\u5317\u4eac'})
    assert response.status_code == 200
    assert response.json == {
      'query': '\u5317\u4eac',
      'formatted_address': '\u4e2d\u56fd\u5317\u4eac',
      'longitude': 116.41,
      'latitude': 39.91,
      '7timer_url': 'http://www.7timer.info/bin/astro.php?lang=zh-CN&lat=39.91&lon=116.41'
    }


def test_weather_no_geocode(client):
  mock_response = Response()
  mock_response.json = MagicMock(return_value={
    'results': [],
    'status': 'ZERO_RESULTS'})
  with patch('requests.get', return_value=mock_response):
    response = client.get('/weather', query_string={'query': 'Beijing'})
    assert response.status_code == 200
    assert response.json == {
      'query': 'Beijing',
      'formatted_address': '',
      'longitude': None,
      'latitude': None,
      '7timer_url': ''
    }
