#Python libraries that we need to import for our bot
import random
from pymongo import MongoClient
from flask import Flask, request
from pymessenger.bot import Bot
import os
import requests
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
      #for first time only check if this is the get started click or no
      checkPostback(output)
      for event in output['entry']:
          messaging = event['messaging']
          for message in messaging:
            if message.get('message'):
                #Facebook Messenger ID for user so we know where to send response back to
                recipient_id = message['sender']['id']
                if message['message'].get('text'):
                    typingon=pay({"recipient":{"id":recipient_id},"sender_action":"typing_on"})
                    print(typingon)
                    topic,mood,response = get_message(recipient_id,message['message'].get('text'))
                    #checkPostback(output)
                    checkQuickReply(message['message'].get('text'),recipient_id)
                    send_message(recipient_id,topic,mood, response)
                #if user sends us a GIF, photo,video, or any other non-text item
                if message['message'].get('attachments'):
                    response = 'sorry i cannot handle attachments now, but wait for an update'
                    send_message(recipient_id,'dummy','dummy', response)
    return "Message Processed"


def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'


#chooses a random message to send to the user
def get_message(recipient_id,query):
  if query=='Get Started':
     return 'dummy','dummy','Welcome'   
  try:  
    topic,mood,response=BRAIN(query)
    return(topic,mood,response)
  except:
    return 'dummy','dummy','I am sorry I dont know what to say'    
def getexamoptions(id):
    payload= {"recipient":{"id":id}, 
                "message":{"text": "Please choose an exam from below:",
                  "quick_replies":[{"content_type":"text","title":"JEE Advanced","payload":"JEE Advanced"},
                                   {"content_type":"text","title":"JEE Mains","payload":"JEE Mains"}]}}     
    pay(payload)
    return 'success'
  
def pay(payload):
  request_endpoint = "https://graph.facebook.com/v2.6/me/messages?access_token="+os.environ['ACCESS_TOKEN']
  #payload={"recipient":{"id":recipient_id},"sender_action":"typing_on"}
  response=requests.post(
    request_endpoint, params=bot.auth_args,
            json=payload )
  result = response.json()
  return result
def checkPostback(output):
    if output['entry'][0]['messaging'][0].get('postback'):
      id=  output['entry'][0]['messaging'][0]['sender']['id']    
      if output['entry'][0]['messaging'][0]['postback']['payload']=='Startyaar':
         welcome='Welcome! I am your friend brilu and I will help you with your exams!! :)'
         send_message(id,'a','a', welcome)   
         getexamoptions(id)
def checkQuickReply(text,id): 
      id=  output['entry'][0]['messaging'][0]['sender']['id']   
      if text=='JEE Mains':
         msg='Okay so JEE mains it is! I will give you some random questions from mains paper as practice untill you decide its time to do something else'
         send_message(id,'a','a', msg)   
      if text=='JEE Advanced':
         msg='Okay so JEE advanced it is! I will give you some random questions from the advanced paper as practice untill you decide its time to do something else'
         send_message(id,'a','a', msg)   
              
        
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
