#Python libraries that we need to import for our bot
import random
from pymongo import MongoClient
from flask import Flask, request
from pymessenger.bot import Bot
import os
import wikipedia
from intelligence import BRAIN
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import euclidean_distances
from nltk.stem import PorterStemmer
app = Flask(__name__)
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
VERIFY_TOKEN = os.environ['VERIFY_TOKEN']
bot = Bot (ACCESS_TOKEN)
ps=PorterStemmer()
button=[{
  "type": "web_url",
  "url": "https://www.facebook.com/",
  "title": "Open Google",
}]
#We will receive messages that Facebook sends our bot at this endpoint
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook."""
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    #if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
       output = request.get_json()
       for event in output['entry']:
          messaging = event['messaging']
          for message in messaging:
            if message.get('message'):
                #Facebook Messenger ID for user so we know where to send response back to
                recipient_id = message['sender']['id']
                if message['message'].get('text'):
                    topic,mood,response = get_message(recipient_id,message['message'].get('text'))
                    send_message(recipient_id,topic,mood, response)
                #if user sends us a GIF, photo,video, or any other non-text item
                if message['message'].get('attachments'):
                    response_sent_nontext = 'sorry i cannot handle attachments now, but wait for an update'
                    send_message(recipient_id, response_sent_nontext)
    return "Message Processed"


def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'


#chooses a random message to send to the user
def get_message(recipient_id,query):
 
  try:  
    topic,mood,response=BRAIN(query)
    return(topic,mood,response)
  except:
    return 'dummy','dummy','I am sorry I dont know what to say'    
  
 
 

#uses PyMessenger to send response to user
def send_message(recipient_id, topic,mood,response):
    #sends user the text message provided via input response parameter
    if mood=='call':
          bot.send_button_message(recipient_id,'Not Satisfied with my responses? Call Our Representative! ',response)
          return 'success'  
    bot.send_text_message(recipient_id, response)
    return "success"


if __name__ == "__main__":
    app.run()
