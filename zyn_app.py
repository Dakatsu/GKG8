#!/usr/bin/env python3

import os
import sys
import tweepy
import json
from datetime import datetime
#from influxdb import InfluxDBClient

##Parse the environment vars from Config+Secret to the code.
def parseConfig():
    """Parse the environemnt variables and return them as a dictionary."""
    twitter_auth = ['4b2LTskX9vEUrxDL5xXIEngYK',
                    'Fax5Lid8OkbxVymNPqRbRtTaFOPNxXX5thFTC1VLDgXC8HCFQ6',
                    '1104535698433077250-QA2uxhGZ46RdQX43Bi3pNPUYqYpIvV',
                    'zc6YU0ERb9w82oR0L1ngYm1Vhfh2OH9qiKDqjxN2qzbuk']

    twitter_user = ['BenJone20134571']

    influx_auth = ['INFLUXDB_HOST',
                   'INFLUXDB_DATABASE',
                   'INFLUXDB_USERNAME',
                   'INFLUXDB_PASSWORD']

    weather_data = ['WEATHER_API_KEY',
                    'WEATHER_LOCATION']

    data = {}

    for i in twitter_auth, twitter_user, influx_auth, weather_data:
        for k in i:
            data[k] = os.environ[k]

    return(data)


def twitterApi(api_key, api_secret, access_token, access_secret):
    """Authenticate and create a Twitter session."""

    auth = tweepy.OAuthHandler(api_key, api_secret)
    auth.set_access_token(access_token, access_secret)

    return tweepy.API(auth)

##==========================================================
def getUser(twitter_api, user):
    """Query the Twitter API for the user's stats."""
    return twitter_api.get_user(user)

'''
def getNumber(twitter_api):

    return twitter_api.


def getLog(twitter_api):
    twitter_log = [twitter_api.,
                   'INFLUXDB_DATABASE',
                   'INFLUXDB_USERNAME',
                   'INFLUXDB_PASSWORD']

'''

def createPoint(username, measurement, value, time):
    """Create a datapoint."""
    json_body = {
        "measurement": measurement,
        "tags": {
            "user": username
        },
        "time": time,
        "fields": {
            "value": value
        }
    }

    return json_body
##==========================================================

##=======------==============------=========------==========
def auth():
    return os.environ.get("BEARER_TOKEN")

def create_url():
    return "https://api.twitter.com/2/tweets/sample/stream"

def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers

def connect_to_endpoint(url, headers):
    response = requests.request("GET", url, headers=headers, stream=True)
    print(response.status_code)
    for response_line in response.iter_lines():
        if response_line:
            json_response = json.loads(response_line)
            print(json.dumps(json_response, indent=4, sort_keys=True))
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
##=======------==============------=========------==========
def main():
    """Do the main."""
    '''
    data = parseConfig()
    time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    twitter = twitterApi(data['TWITTER_API_KEY'],
                         data['TWITTER_API_SECRET'],
                         data['TWITTER_ACCESS_TOKEN'],
                         data['TWITTER_ACCESS_SECRET'])

    userdata = getUser(twitter, data['TWITTER_USER'])

    client = initDBClient(data['INFLUXDB_HOST'],
                          data['INFLUXDB_DATABASE'],
                          data['INFLUXDB_USERNAME'],
                          data['INFLUXDB_PASSWORD'])

    # createInfluxDB(client, data['INFLUXDB_DATABASE'])

    json_body = []

    # TODO: Make this a secret variable in the environment.
    # weather_api_key = "8a3c4c852d112b89543a1174dc283e66"
    # current_temp = getTemperatureIn(data['WEATHER_LOCATION'],data['WEATHER_API_KEY'])

    data_points = {
        "followers_count": userdata.followers_count,
        "friends_count": userdata.friends_count,
        "listed_count": userdata.listed_count,
        ##TEST
        ##"favourites_count": userdata.favourites_count,
        "favourites_count": current_temp,
        "statuses_count": userdata.statuses_count
    }

    for key, value in data_points.items():
        json_body.append(createPoint(data['TWITTER_USER'],
                                     key,
                                     value,
                                     time))

    json_body.append(createPoint(data['WEATHER_LOCATION'],
                                 "current_temp",
                                 int(current_temp),
                                 time))

    client.write_points(json_body)
    '''
    bearer_token = auth()
    url = create_url()
    headers = create_headers(bearer_token)
    timeout = 0
    while True:
        connect_to_endpoint(url, headers)
        timeout += 1

##@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
def createInfluxDB(client, db_name):
    """Create the database if it doesn't exist."""
    dbs = client.get_list_database()
    if not any(db['name'] == db_name for db in dbs):
        client.create_database(db_name)
    client.switch_database(db_name)


def initDBClient(host, db, user, password):
    """Create an InfluxDB client connection."""

    client = InfluxDBClient(host, 8086, user, password, db)

    return(client)
def getTemperatureIn(location_str, api_key):
    units_str = "&units=metric"
    API_str = "&appid=" + api_key
    url = "https://api.openweathermap.org/data/2.5/weather?q=" + location_str + units_str + API_str
    request = urllib.request.Request(url)
    r = urllib.request.urlopen(request).read()
    contents = json.loads(r.decode('utf-8'))
    return contents['main']['temp']
##@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

if __name__ == "__main__":
    sys.exit(main())
