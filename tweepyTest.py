import tweepy
import json
import urllib.request

consumer_key = "4b2LTskX9vEUrxDL5xXIEngYK"
consumer_secret = "Fax5Lid8OkbxVymNPqRbRtTaFOPNxXX5thFTC1VLDgXC8HCFQ6"
access_token = "1104535698433077250-QA2uxhGZ46RdQX43Bi3pNPUYqYpIvV"
access_token_secret = "zc6YU0ERb9w82oR0L1ngYm1Vhfh2OH9qiKDqjxN2qzbuk"
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

API = tweepy.API(auth)

# Method to get the latest posts on a user's timeline.
# Gets the user via their screen name, then we can extract their user ID to get information on them.
# Example: NPR
def searchUser():
    print("Please enter a screen name to search:")
    screenName = input()
    user = API.get_user(screenName)
    userID = user.id

    print("Stats for the user " + user.screen_name + " (user ID: " + str(userID) + "):")
    print("  Followers: " + str(user.followers_count))
    print("  Friends: " + str(user.friends_count))
    # I do not know what these three actually mean; they're taken from the twitterGraph app.
    print("  Listed: " + str(user.listed_count))
    print("  Favourites: " + str(user.favourites_count))
    print("  Statuses: " + str(user.statuses_count))

    print("Here are the tweets from " + user.screen_name + " (user ID: " + str(userID) + ").")
    public_tweets = API.user_timeline(user.id, tweet_mode="extended")
    for tweet in public_tweets:
        print("  " + tweet.full_text)

    print("Tweet collection is finished.")

# Search query test: http://docs.tweepy.org/en/latest/api.html#API.search
# Line 83 of models.py on GitHub defines what is in a Tweet (status):
#   https://github.com/tweepy/tweepy/blob/17700c6bf266ac695bde9d08deb62fe7770c98df/tweepy/models.py
# There are some things that are manually defined (e.g. author, created_at), but most items
#   come directly from the JSON file. What comes from the JSON file will be identical.
def searchQuery():
    print("Enter a query to search.")
    query = input()
    print("Here are tweets for the search query \"" +  query + "\":")
    # Use 'tweet_mode'="extended"' to use newer API calls.
    # Note: text becomes full_text under this scheme.
    # search_results_tweets = API.search(query, count=5, tweet_mode="extended")
    search_results_tweets = API.search(query, count=5)
    for tweet in search_results_tweets:
        #print("  " + tweet.full_text)
        print("  " + tweet.text)
        print("    Created: " + str(tweet.created_at))
        # Can also use just "id" for an integer.
        print("    Tweet ID: " + tweet.id_str)
        # print("    URL: " + tweet.entities.urls.expanded_url)
        print("    User Name: " + tweet.author.screen_name)
        # How to print the JSON file.
        # print(json.dumps(tweet._json, sort_keys=True, indent=4))

def getTemperatureIn(location_str):
    API_key = "8a3c4c852d112b89543a1174dc283e66"
    units_str = "&units=metric"
    API_str = "&appid=" + API_key
    url = "https://api.openweathermap.org/data/2.5/weather?q=" + location_str + units_str + API_str
    request = urllib.request.Request(url)
    r = urllib.request.urlopen(request).read()
    contents = json.loads(r.decode('utf-8'))
    print("Current Temperature in " + location_str + ": " + str(contents['main']['temp']))

#searchQuery()
getTemperatureIn("Montreal,QC,CA")
getTemperatureIn("Tampa,FL,USA")
