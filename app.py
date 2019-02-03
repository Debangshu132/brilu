#Python libraries that we need to import for our bot
import random
from pymongo import MongoClient
from flask import Flask, request,render_template
from pymessenger.bot import Bot
import os
import requests

import json
from decisionTree import decision,listOfExams,askQuestion,handleResults,decisionRightWrong
from intelligence import BRAIN
import time
#from sklearn.feature_extraction.text import CountVectorizer
#from sklearn.metrics.pairwise import euclidean_distances
#from nltk.stem import PorterStemmer
app = Flask(__name__)
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
VERIFY_TOKEN = os.environ['VERIFY_TOKEN']
bot = Bot (ACCESS_TOKEN)
#ps=PorterStemmer()
listOfExams=listOfExams()
RID=''
#We will receive messages that Facebook sends our bot at this endpoint
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    global RID
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
                RID=recipient_id 
                if message['message'].get('text'):
                    typingon=pay({"recipient":{"id":recipient_id},"sender_action":"typing_on"})
                    if  message['message'].get('quick_reply'):
                      if message['message']['quick_reply']['payload']=='right':
                        
                        currtopic=getUserInformation(recipient_id,"currenttopic")
                        #currtotal=str(currtopic)+'total'
                        #currright=str(currtopic)+'right'
                        updateUsersInformation(recipient_id,totalquestionasked=int(getUserInformation(recipient_id,'totalquestionasked'))+1)
                        updateUsersInformation(recipient_id,totalquestionright=int(getUserInformation(recipient_id,'totalquestionright'))+1)
                        updateUsersInformation(recipient_id,**{str(currtopic)+'total':int(getUserInformation(recipient_id,str(str(currtopic)+'total')))+1})
                        updateUsersInformation(recipient_id,**{str(currtopic)+'right':int(getUserInformation(recipient_id,str(str(currtopic)+'right')))+1})
                        noofconsecutiveright=getUserInformation(recipient_id,'noofconsecutiveright')
                        updateUsersInformation(recipient_id,noofconsecutivewrong=0)
                        updateUsersInformation(recipient_id,noofconsecutiveright=noofconsecutiveright+1)
                        reply=decisionRightWrong('right', noofconsecutiveright)
                        quickreply(recipient_id,['Another One','Go Back','Results','I am Bored!'],reply)
                        
                        return "Message Processed"
                      if message['message']['quick_reply']['payload']=='wrong':
                        
                        updateUsersInformation(recipient_id,totalquestionasked=int(getUserInformation(recipient_id,'totalquestionasked'))+1)
                        rightAns=getUserInformation(recipient_id,'lastRightAnswer')
                        
                        noofconsecutivewrong=getUserInformation(recipient_id,'noofconsecutivewrong')
                        updateUsersInformation(recipient_id,noofconsecutiveright=0)
                        updateUsersInformation(recipient_id,noofconsecutivewrong=noofconsecutivewrong+1)
                        
                        
                        
                        currtopic=getUserInformation(recipient_id,"currenttopic")
                        #currtotal=str(currtopic)+'total'
                        updateUsersInformation(recipient_id,**{str(currtopic)+'total':int(getUserInformation(recipient_id,str(str(currtopic)+'total')))+1})
                        
                        
                        reply=decisionRightWrong('wrong', noofconsecutivewrong)
                        quickreply(recipient_id,['Try Another','Go Back','Results','I am Bored!'],reply+ ' ,the right answer is: '+'\n'+rightAns)
                        
                        return "Message Processed"
                   
                    topic,mood,response = get_message(recipient_id,message['message'].get('text'))
                    #checkPostback(output)
                    isQuickReply=checkQuickReply(message['message'].get('text'),recipient_id)
                    if isQuickReply==False:
                        #send_message(recipient_id,topic,mood, response)
                        quickreply(recipient_id,['Lets test', 'I am Bored!'],response)
                #if user sends us a GIF, photo,video, or any other non-text item
                if message['message'].get('attachments'):
                    response = 'sorry i cannot handle attachments now, but wait for an update'
                    quickreply(recipient_id,['Lets test', 'I am Bored!'],response)
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
      a=requests.get("https://graph.facebook.com/"+id+"?fields=first_name,last_name,profile_pic&access_token="+ACCESS_TOKEN)
      data=a.json()
      name=data['first_name']
      if output['entry'][0]['messaging'][0]['postback']['payload']=='Startyaar':
         welcome='Welcome! '+name+' I am an AI-powered teacher bot,I will challenge your knowledge and help you learn while having fun! Get ready for a revolution in education :D'
         initializeUser(id)
         send_message(id,'a','a', welcome)
         pay({"recipient":{"id":id},"sender_action":"typing_on"})
         exam='Choose any topic to start practising problems!'   
         time.sleep(1)   
         quickreply(id,listOfExams,exam)
      if output['entry'][0]['messaging'][0]['postback']['payload']=='right':
          quickreply(id,['Lets test','I am Bored!'],'Thats right!!')
      if output['entry'][0]['messaging'][0]['postback']['payload']=='wrong':
          quickreply(id,['Try again','I am Bored!'],'Sorry thats wrong!')      
    
def checkQuickReply(text,id): 
         try: 
           msges,listofitems=decision(text)
           if msges[0]=='okay,Lets start':
                sendQuestion(id)
                updateUsersInformation(id,noofconsecutivewrong=0,noofconsecutiveright=0)
                return True  
           if msges[0]=='okay,Lets start again':
                sendQuestion(id)
                return True  
           if msges[0]==  'I am Bored!':
                 send_gif_message(id,'study quotes')
                 quickreply(id,listofitems,'lets study now!')
                 return True  
           if msges[0]=='Going back,Which exam would you like to take':
               updateUsersInformation(id,noofconsecutivewrong=0,noofconsecutiveright=0)
           if msges[0]=="Results":
               send_message(id,'a','a', msges[1])
               total=int(getUserInformation(id,'totalquestionasked')) 
               right=int(getUserInformation(id,'totalquestionright'))
               result="You got "+str(right)+' out of '+str(total)+' correct!'
               send_gif_message(id, handleResults(total,right))
               print(sendResult(id,handleResults(total,right),result)) 
               #quickreply(id,listofitems,result)
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
def sendResult(id, gif,message):
    url = search_gif(gif)
    share={
  "type": "element_share",
  "share_contents": { 
    "attachment": {
      "type": "template",
      "payload": {
        "template_type": "generic",
        "elements": [
          {
            "title": "I was just answering Brilu's questions!!",
            "subtitle": "He says: " + message,
            #"image_url": "<IMAGE_URL_TO_DISPLAY>",
            "default_action": {
              "type": "web_url",
              "url": "https://www.messenger.com/t/teacherchatbot"
            },
            "buttons": [
              {
                "type": "web_url",
                "url": "https://www.messenger.com/t/teacherchatbot", 
                "title": "Chat now"
              }]}]}}}}
    response=   {
     "recipient":{
           "id":id
                      },
     "message":{
      "quick_replies": [
      {
        "content_type":"text",
        "title":"Go Back",
        
        "payload":"Go Back"
      },
      {
        "content_type":"text",
        "title":"Continue",
        "payload":"Continue"
      },
        {
        "content_type":"text",
        "title":"I am Bored!",
        "payload":'I am Bored!'
      }
    ],   
      "attachment":{
        "type":"template",
          "payload":{
           "template_type":"generic",
             "elements":[
                 {
                 "title":"Here is your result!",
                   #"image_url":https://images.pexels.com/photos/1642883/pexels-photo-1642883.jpeg?cs=srgb&dl=adults-affection-couple-1642883.jpg&fm=jpg,
                     "subtitle":message,
                        "default_action": {
                            "type":"web_url",
                            "url":"http://brilu.herokuapp.com/result/"+str(id),
                            "webview_height_ratio": "tall"  
                              },
                           "buttons":[
                             {
                "type":"web_url",
                "url":"http://brilu.herokuapp.com/result/"+str(id),
                "title":"See Details!",
                "webview_height_ratio": "tall"  
              },share ] }]}}}}
    
    r=pay(response)
    return r
@app.route("/result/<id>", methods=['GET', 'POST'])
def result(id):
        global RID
        R=int(getUserInformation(id,'totalquestionright'))
        T=int(getUserInformation(id,'totalquestionasked'))
        PR=int(getUserInformation(id,'physicsright'))
        PT=int(getUserInformation(id,'physicstotal'))
        CR=int(getUserInformation(id,'chemistryright'))
        CT=int(getUserInformation(id,'chemistrytotal'))
        BR=int(getUserInformation(id,'biologyright'))
        BT=int(getUserInformation(id,'biologytotal'))
        MR=int(getUserInformation(id,'mathright'))
        MT=int(getUserInformation(id,'mathtotal'))
        W=T-R 
        PW=PT-PR
        BW=BT-BR 
        CW=CT-CR 
        MW=MT-MR 
        
        return render_template('chart.html',R=R, W=W,PR=PR, PW=PW,CR=CR, CW=CW,MR=MR, MW=MW,BR=BR, BW=BW)
def initializeUser(id):
    a=requests.get("https://graph.facebook.com/"+id+"?fields=first_name,last_name,profile_pic&access_token="+ACCESS_TOKEN)
    data=a.json()
    name=data['first_name']
    updateUsersInformation(id,lastQuestion="",
                                totalquestionasked=0,
                           totalquestionright=0,
                           currenttopic="",name=name,
                               noofconsecutivewrong=0,
                           noofconsecutiveright=0,
                           lastRightAnswer= "",
        physicstotal= 0,
        physicsright= 0,
        aptitudetotal= 0,
        aptituderight= 0,                   
        chemistrytotal= 0,
        chemistryright= 0,
        biologytotal= 0,
        biologyright= 0,
        mathtotal= 0,
        mathright= 0
                          )
    

if __name__ == "__main__":
    app.run()
