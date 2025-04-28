import  praw, requests, os, asyncpraw, asyncio
from dotenv import load_dotenv
load_dotenv()
async def use():
    usernamee = os.getenv('REDDITUSERNAME')
    passwordd = os.getenv('REDDITPASSWORD')
    clientID = os.getenv('REDDITCLIENTID')
    clientSecret = os.getenv('REDDITSECRET')
    hope=asyncpraw.Reddit(
    client_id = clientID,
    password = passwordd,
    username = usernamee,
    client_secret = clientSecret,
        user_agent = 'Hopescraper'
    )
    subreddit = await hope.subreddit('hopeposting', fetch=True)
    ids = []
    async for submission in subreddit.hot():
       x= f'https://www.reddit.com/r/hopeposting/comments/{submission}'
       print(x)
       ids.append(x)
    print(ids)
    await hope.close()
    return ids
async def randomm():
    usernamee = os.getenv('REDDITUSERNAME')
    passwordd = os.getenv('REDDITPASSWORD')
    clientID = os.getenv('REDDITCLIENTID')
    clientSecret = os.getenv('REDDITSECRET')
    hope=asyncpraw.Reddit(
    client_id = clientID,
    password = passwordd,
    username = usernamee,
    client_secret = clientSecret,
        user_agent = 'Hopescraper'
    )
    subreddit = await hope.subreddit('hopeposting', fetch=True)
    ids = []
    random = ''
    async def sett():
        random = await hope.subreddit('hopeposting').random()
    await hope.close()
    return ids
