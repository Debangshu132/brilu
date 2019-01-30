#Python libraries that we need to import for our bot
import random
from pymongo import MongoClient
from flask import Flask, request,render_template
from pymessenger.bot import Bot
import os
import requests

import json
from decisionTree import decision,listOfExams,askQuestion,handleResults
from intelligence import BRAIN
import time
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import euclidean_distances
from nltk.stem import PorterStemmer
app = Flask(__name__)
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
VERIFY_TOKEN = os.environ['VERIFY_TOKEN']
bot = Bot (ACCESS_TOKEN)
ps=PorterStemmer()
listOfExams=listOfExams()
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
                    if  message['message'].get('quick_reply'):
                      if message['message']['quick_reply']['payload']=='right':
                        
                        quickreply(recipient_id,['Another One','Go Back','Results'],'Thats right :D')
                        updateUsersInformation(recipient_id,totalquestionasked=int(getUserInformation(recipient_id,'totalquestionasked'))+1)
                        updateUsersInformation(recipient_id,totalquestionright=int(getUserInformation(recipient_id,'totalquestionright'))+1)
                        
                        return "Message Processed"
                      if message['message']['quick_reply']['payload']=='wrong':
                        
                        updateUsersInformation(recipient_id,totalquestionasked=int(getUserInformation(recipient_id,'totalquestionasked'))+1)
                        rightAns=getUserInformation(recipient_id,'lastRightAnswer')
                        quickreply(recipient_id,['Try Another','Go Back','Results'],'sorry Thats wrong! :) ,the right answer is: '+'\n'+rightAns)
                        
                        return "Message Processed"
                   
                    topic,mood,response = get_message(recipient_id,message['message'].get('text'))
                    #checkPostback(output)
                    isQuickReply=checkQuickReply(message['message'].get('text'),recipient_id)
                    if isQuickReply==False:
                        #send_message(recipient_id,topic,mood, response)
                        quickreply(recipient_id,['Lets test','Inspire me'],response)
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
    return 'dummy','dummy','I am sorry I didnot quite get what you are saying'    
def quickreply(id,listofitems,text):
    payload = {"recipient": {"id": id}, "message": {"text":text,"quick_replies": []}}
    for item in listofitems:
        payload['message']['quick_replies'].append({"content_type":"text","title":str(item),"payload":str(item)})   
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
         updateUsersInformation(id,lastQuestion="",totalquestionasked=0,totalquestionright=0,currenttopic="")
         send_message(id,'a','a', welcome)
         pay({"recipient":{"id":id},"sender_action":"typing_on"})
         exam='Choose any topic to start practising probems!'   
         time.sleep(1)   
         quickreply(id,listOfExams,exam)
      if output['entry'][0]['messaging'][0]['postback']['payload']=='right':
          quickreply(id,['Lets test','Inspire me'],'Thats right!!')
      if output['entry'][0]['messaging'][0]['postback']['payload']=='wrong':
          quickreply(id,['Try again','Inspire me'],'Sorry thats wrong!')      
    
def checkQuickReply(text,id): 
         try: 
           msges,listofitems=decision(text)
           if msges[0]=='okay,Lets start':
                sendQuestion(id)
                return True  
           if msges[0]==  'Inspire me':
                 send_gif_message(id,'study quotes')
                 quickreply(id,listofitems,'lets study now!')
                 return True  
           if msges[0]=="Results":
               send_message(id,'a','a', msges[1])
               total=int(getUserInformation(id,'totalquestionasked')) 
               right=int(getUserInformation(id,'totalquestionright'))
               result="I have asked you "+str(total)+' questions until now, out of which you got '+str(right)+' correct!'
               send_gif_message(id, handleResults(total,right))
               sendResult(id) 
               quickreply(id,listofitems,result)
               return True 
           for msg in range(0,len(msges)-2):
              send_message(id,'a','a', msges[msg])
              time.sleep(1)
           updateUsersInformation(id, currenttopic=str(msges[len(msges)-1])) 
           quickreply(id,listofitems,msges[len(msges)-2]) 
           return True
         except:
            return False    
def sendQuestion(id):
    question,options,right,exceeded=askQuestion(getUserInformation(id,'currenttopic'))
    updateUsersInformation(id,lastQuestion=question,lastRightAnswer=right)
    if exceeded==False:
      payload = {"recipient": {"id": id}, "message": {"text":question,"quick_replies": []}}
      for item in options:
        if item==right:
           payload['message']['quick_replies'].append({"content_type":"text","title":str(item),"payload":'right'})
           
        else:
           payload['message']['quick_replies'].append({"content_type":"text","title":str(item),"payload":'wrong'})  
      pay(payload)
      return 'success'
    if exceeded==True:
         shortOptions=['A','B','C','D']
         questionAns=question+'\n'+"A)"+options[0]+"\n"+"B)"+options[1]+"\n"+"C)"+options[2]+"\n"+"D)"+options[3]+"\n"
         payload = {"recipient": {"id": id}, "message": {"text":questionAns,"quick_replies": []}}
         for itemindex in range(0,4):
            if options[itemindex]==right:
              payload['message']['quick_replies'].append({"content_type":"text","title":shortOptions[itemindex],"payload":'right'})
              
            else:
              payload['message']['quick_replies'].append({"content_type":"text","title":shortOptions[itemindex],"payload":'wrong'})
         pay(payload)
         return 'success'  
        
#uses PyMessenger to send response to user
def send_message(recipient_id, topic,mood,response):
    #sends user the text message provided via input response parameter
    if mood=='call':
          bot.send_button_message(recipient_id,'Not Satisfied with my responses? Call Our Representative! ',response)
          return 'success'  
    bot.send_text_message(recipient_id, response)
    return "success"

def updateUsersInformation(ID, **kwargs):
    MONGODB_URI = "mongodb://Debangshu:Starrynight.1@ds163694.mlab.com:63694/brilu"
    client = MongoClient(MONGODB_URI, connectTimeoutMS=30000)
    db = client.get_database("brilu")
    for key in kwargs:
        db.userInfo.update({"_id" : "5c4e064ffb6fc05326ad8c57"}, {"$set":{str(ID)+"."+str(key): kwargs[key]}},upsert=True);
    return(0)
def getUserInformation(id,property):
    MONGODB_URI = "mongodb://Debangshu:Starrynight.1@ds163694.mlab.com:63694/brilu"
    client = MongoClient(MONGODB_URI, connectTimeoutMS=30000)
    db = client.get_database("brilu")
    col = db["userInfo"]
    cursor = col.find()
    userInfo = cursor[0]
    return(userInfo[id][property])
def search_gif(text):
    #get a GIF that is similar to text sent
    payload = {'s': text, 'api_key': '8uWKU7YtJ4bIzYcAnjRVov8poEHCCj8l'}
    r = requests.get('http://api.giphy.com/v1/gifs/translate', params=payload)
    r = r.json()
    url = r['data']['images']['original']['url']
    return url
def send_gif_message(recipient_id, message):
    gif_url = search_gif(message)
    data = json.dumps({"recipient": {"id": recipient_id},"message": {"attachment": {"type": "image","payload": {"url": gif_url}}}})
    params = {"access_token": ACCESS_TOKEN }
    headers = {"Content-Type": "application/json"}
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
def sendResult(id):
    response= [
                {
             "type":"web_url",
            "url":"ttp://brilu.herokuapp.com/result",
            "title":"See result",
            "webview_height_ratio": "compact"
                }
            ]
        
    bot.send_button_message(id,'Get detailed result',response)
    return 'ok'
@app.route("/result", methods=['GET', 'POST'])
def result():
    
        return render_template('chart.html')

if __name__ == "__main__":
    app.run()
