#!/usr/bin/env python3

import os
import sys
import tweepy
import urllib.request
import json
from datetime import datetime
from influxdb import InfluxDBClient

# Quick variable to disable certain features for local testing purposes.
bIsLocalTest = True

def parseConfig(bUseLocalVariables):
    """Parse the environemnt variables and return them as a dictionary."""
    data = {}
    if bUseLocalVariables:
        data['TWITTER_API_KEY'] = "4b2LTskX9vEUrxDL5xXIEngYK"
        data['TWITTER_API_SECRET'] = "Fax5Lid8OkbxVymNPqRbRtTaFOPNxXX5thFTC1VLDgXC8HCFQ6"
        data['TWITTER_ACCESS_TOKEN'] = "1104535698433077250-QA2uxhGZ46RdQX43Bi3pNPUYqYpIvV"
        data['TWITTER_ACCESS_SECRET'] = "zc6YU0ERb9w82oR0L1ngYm1Vhfh2OH9qiKDqjxN2qzbuk"
        data['TWITTER_USER'] = "NPR"
        data['WEATHER_API_KEY'] = "8a3c4c852d112b89543a1174dc283e66"
        data['WEATHER_LOCATION'] = "Montreal,QC,CA"
    else:
        twitter_auth = ['TWITTER_API_KEY',
                        'TWITTER_API_SECRET',
                        'TWITTER_ACCESS_TOKEN',
                        'TWITTER_ACCESS_SECRET']

        twitter_user = ['TWITTER_USER']

        influx_auth = ['INFLUXDB_HOST',
                       'INFLUXDB_DATABASE',
                       'INFLUXDB_USERNAME',
                       'INFLUXDB_PASSWORD']

        weather_data = ['WEATHER_API_KEY',
                        'WEATHER_LOCATION']


        for i in twitter_auth, twitter_user, influx_auth:
            for k in i:
                if k not in os.environ:
                    raise Exception('{} not found in environment'.format(k))
                else:
                    data[k] = os.environ[k]

    return(data)


def twitterApi(api_key, api_secret, access_token, access_secret):
    """Authenticate and create a Twitter session."""

    auth = tweepy.OAuthHandler(api_key, api_secret)
    auth.set_access_token(access_token, access_secret)

    return tweepy.API(auth)


def getUser(twitter_api, user):
    """Query the Twitter API for the user's stats."""
    return twitter_api.get_user(user)


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

def getTemperatureIn(location_str, api_key):
    units_str = "&units=metric"
    API_str = "&appid=" + api_key
    url = "https://api.openweathermap.org/data/2.5/weather?q=" + location_str + units_str + API_str
    request = urllib.request.Request(url)
    r = urllib.request.urlopen(request).read()
    contents = json.loads(r.decode('utf-8'))
    return contents['main']['temp']

def main():
    """Do the main."""
    if bIsLocalTest:
        print("Starting local test.")
    data = parseConfig(bIsLocalTest)
    time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    twitter = twitterApi(data['TWITTER_API_KEY'],
                         data['TWITTER_API_SECRET'],
                         data['TWITTER_ACCESS_TOKEN'],
                         data['TWITTER_ACCESS_SECRET'])

    userdata = getUser(twitter, data['TWITTER_USER'])

    if not bIsLocalTest:
        client = initDBClient(data['INFLUXDB_HOST'],
                              data['INFLUXDB_DATABASE'],
                              data['INFLUXDB_USERNAME'],
                              data['INFLUXDB_PASSWORD'])
        createInfluxDB(client, data['INFLUXDB_DATABASE'])

    json_body = []

    if bIsLocalTest:
        print("Getting temperature from " + data['WEATHER_LOCATION'] + ".")
    current_temp = getTemperatureIn(data['WEATHER_LOCATION'],data['WEATHER_API_KEY'])

    data_points = {
        "followers_count": userdata.followers_count,
        "friends_count": userdata.friends_count,
        "listed_count": userdata.listed_count,
        ##TEST
        ##"favourites_count": userdata.favourites_count,
        "favourites_count": current_temp,
        "statuses_count": userdata.statuses_count
    }

    if bIsLocalTest:
        print("Creating JSON file.")

    for key, value in data_points.items():
        json_body.append(createPoint(data['TWITTER_USER'],
                                     key,
                                     value,
                                     time))

    json_body.append(createPoint(data['WEATHER_LOCATION'],
                                 "current_temp",
                                 int(current_temp),
                                 time))

    if not bIsLocalTest:
        client.write_points(json_body)
    else:
        print("FINISHED: ",json_body)


if __name__ == "__main__":
    sys.exit(main())
