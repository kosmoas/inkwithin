import requests, datetime, random, json
with open(r'C:\Quotes.txt', 'r') as file:
      word = file.readlines()
class quote():
    def __init__(self):
        pass
    def random_quote(self):
        rquote = random.choice(word)
        return rquote
