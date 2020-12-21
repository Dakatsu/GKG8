#!/usr/bin/env python3

## Go Kubernetes Go! - Group 8
## Concordia University, 2020-12-20
## Code derived from the below tutorial:
##   https://opensource.com/article/19/2/deploy-influxdb-grafana-kubernetes
## Alterations made by group members.

import os
import sys
import tweepy
import urllib.request
import json
from datetime import datetime, timedelta
from influxdb import InfluxDBClient

<<<<<<< Updated upstream
# Quick variable to disable certain features for local testing purposes.
bIsLocalTest = False

=======
##Parse the environment vars from Config+Secret to the code.
>>>>>>> Stashed changes
def parseConfig():
    """Parse the environemnt variables and return them as a dictionary."""
    twitter_auth = ['TWITTER_API_KEY',
                    'TWITTER_API_SECRET',
                    'TWITTER_ACCESS_TOKEN',
                    'TWITTER_ACCESS_SECRET']

    twitter_vars = ['TWITTER_USER',
                    'TWITTER_QUERY']

    influx_auth = ['INFLUXDB_HOST',
                   'INFLUXDB_DATABASE',
                   'INFLUXDB_USERNAME',
                   'INFLUXDB_PASSWORD']

    weather_data = ['WEATHER_API_KEY',
                    'WEATHER_LOCATION']

    data = {}

    for i in twitter_auth, twitter_vars, influx_auth, weather_data:
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
    url = "https://api.openweathermap.org/data/2.5/weather?q=" + location_str + "&units=metric" + "&appid=" + api_key
    request = urllib.request.Request(url)
    r = urllib.request.urlopen(request).read()
    contents = json.loads(r.decode('utf-8'))
    value = contents['main']['temp']
    return value

def main():
    """Do the main."""
    time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    print("Script starting at " + str(time) + " UTC.")
    data = parseConfig()

    # Connect to InfluxDB
    client = initDBClient(data['INFLUXDB_HOST'],
                          data['INFLUXDB_DATABASE'],
                          data['INFLUXDB_USERNAME'],
                          data['INFLUXDB_PASSWORD'])

    createInfluxDB(client, data['INFLUXDB_DATABASE'])
    
    # Attempt to record Twitter stats.
    print("Attempting to retrieve Twitter stats.")
    try:
        twitter = twitterApi(data['TWITTER_API_KEY'],
                         data['TWITTER_API_SECRET'],
                         data['TWITTER_ACCESS_TOKEN'],
                         data['TWITTER_ACCESS_SECRET'])
                         
        # Get stats for our tracked Twitter user.
        userdata = getUser(twitter, data['TWITTER_USER'])
        
        json_body = []
        data_points = {
            "followers_count": userdata.followers_count,
            "friends_count": userdata.friends_count,
            "listed_count": userdata.listed_count,
            "favourites_count": userdata.favourites_count,
            "statuses_count": userdata.statuses_count
        }

        for key, value in data_points.items():
            json_body.append(createPoint(data['TWITTER_USER'],
                                         key,
                                         value,
                                         time))
                                         
        # Get stats for our tracked Twitter query.
        search_results_tweets = twitter.search(data['TWITTER_QUERY'], count=100, tweet_mode="extended")
        timeCutoff = datetime.utcnow() - timedelta(minutes = 5)
        tweet_count = 0
        tweet_length_sum = 0
        tweet_num_hashtags_sum = 0
        for tweet in search_results_tweets:
            if tweet.created_at > timeCutoff:
                tweet_count += 1
                tweet_length_sum += + len(tweet.full_text)
                if 'entities' in tweet._json and 'hashtags' in tweet._json['entities']:
                    tweet_num_hashtags_sum += len(tweet._json['entities']['hashtags'])
        tweet_length_avg = 0
        tweet_num_hashtags_avg = 0
        if tweet_count > 0:
            tweet_length_avg = tweet_length_sum / tweet_count
            tweet_num_hashtags_avg = tweet_num_hashtags_sum / tweet_count

        data_points = {
            "tweet_count": tweet_count,
            "tweet_length_avg": tweet_length_avg,
            "tweet_num_hashtags_avg": tweet_num_hashtags_avg
        }

        for key, value in data_points.items():
            json_body.append(createPoint(data['TWITTER_QUERY'],
                                         key,
                                         value,
                                         time))
        client.write_points(json_body)
        print("Successfully retrieved Twitter stats.")
    except Exception as err:
        print("Could not record Twitter Stats due to an exception: " + str(err))

    # Attempt to record weather stats.
    print("Attempting to retrieve OpenWeather stats.")
    try:
        json_body = []
        temp = getTemperatureIn(data['WEATHER_LOCATION'],data['WEATHER_API_KEY'])
        json_body.append(createPoint(data['WEATHER_LOCATION'],
                                 "temperature",
                                 float(temp),
                                 time))
        client.write_points(json_body)
        print("Successfully retrieved OpenWeather stats.")
    except Exception as err:
        print("Could not record OpenWeather Stats due to an exception: " + str(err))
    print("Scripted finished.")


if __name__ == "__main__":
    sys.exit(main())
