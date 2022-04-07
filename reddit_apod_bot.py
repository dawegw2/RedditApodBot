# NASA APOD Reddit Bot
# working with the praw reddit api to access reddit data and post on reddit
import praw
import requests
from  threading import Timer 

keys = []
run = False

def post():
    global run

    with open('keys.txt', 'r') as f:
        for line in f:
            keys.append(line.strip())

    #create an instance of reddit
    reddit = praw.Reddit(client_id = keys[0],
                        client_secret = keys[1],
                        username = "daily-apod-bot",
                        password = keys[2],
                        user_agent = "APOD reddit bot v1")

    #NASA api key and url
    nasa_api_key = keys[3]
    url = f"https://api.nasa.gov/planetary/apod?api_key={nasa_api_key}"

    response = requests.get(url)
    data = response.json()

    # picture information
    apod_date = data['date']
    apod_title = data['title']
    apod_explanation = data['explanation']

    # some APOD can be images and videos. this tests for which one to post and avoids the keyError
    try:
        apod_url = data['hdurl']
    except KeyError:
        apod_url = data['url']

    # some data recieved from the api doesn't always contain the credit for the picture
    try:
        apod_copyright = data['copyright']
        credit = "Credit: " + apod_copyright
    except KeyError:
        credit = ""

    # posting on a subreddit - https://www.reddit.com/r/daily_apod/
    title = f"({apod_date}) " + f"Nasa's Astronomy Picture of the Day: {apod_title} {credit}"
    s = reddit.subreddit("daily_apod") # get the subreddit(s) to post to
    s.submit(title=title, url=apod_url) # post to the reddit

    # commenting the explanation of the image
    for submission in s.stream.submissions():
        submission_title = submission.title.lower()

        if apod_date in submission_title:

            explanation = "Explanation: " + "\r\r\n" + apod_explanation
            comment = submission.reply(explanation) # comment the explanation for the apod
            comment.mod.distinguish(sticky=True)

            break
    
    print(apod_date + ' posted ' + apod_url + ' to r/daily_apod')
    
    if run:
        Timer(120, post).start()

post()

