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

app = Flask(__name__)
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
VERIFY_TOKEN = os.environ['VERIFY_TOKEN']
bot = Bot (ACCESS_TOKEN)

RID=''
#We will receive messages that Facebook sends our bot at this endpoint
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    global RID
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook."""
        token_sent = request.args.get("hub.verify_token")
        print('bot started yeay0')
        return verify_fb_token(token_sent)
    #if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
      # get whatever message a user sent the bot
      print('bot started yeay2')
      output = request.get_json()
      print('bot started yeay3')  
      #for first time only check if this is the get started click or no
      checkReferral(output) 
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
                      secretcode= message['message']['quick_reply']['payload']
                      if secretcode=='hint':
                            hint=getUserInformation(recipient_id,'lasthint')
                            sendLastOptionsQuickReply(recipient_id,hint)
                            return "Message Processed"
                      if secretcode=='right':
                          
                        currtopic=getUserInformation(recipient_id,"currenttopic")
                       
                        updateUsersInformation(recipient_id,insidequestion=False,totalquestionasked=int(getUserInformation(recipient_id,'totalquestionasked'))+1)
                        updateUsersInformation(recipient_id,totalquestionright=int(getUserInformation(recipient_id,'totalquestionright'))+1)
                        updateUsersInformation(recipient_id,**{str(currtopic)+'total':int(getUserInformation(recipient_id,str(str(currtopic)+'total')))+1})
                        updateUsersInformation(recipient_id,**{str(currtopic)+'right':int(getUserInformation(recipient_id,str(str(currtopic)+'right')))+1})
                        noofconsecutiveright=getUserInformation(recipient_id,'noofconsecutiveright')
                        updateUsersInformation(recipient_id,noofconsecutivewrong=0)
                        updateUsersInformation(recipient_id,noofconsecutiveright=noofconsecutiveright+1)
                        reply=decisionRightWrong('right', noofconsecutiveright)
                        
                        if getUserInformation(recipient_id,'currenttopic')=='aptitude':
                            quickreply(recipient_id,['Another One','Go Back','Results','I am Bored!'], reply)
                        else:
                            quickreply(recipient_id,['Another One','Go Back','Results','I am Bored!'], reply+'\n'+getUserInformation(recipient_id,'lastsolution'))
                        
                        return "Message Processed"
                      if secretcode=='wrong':
                        
                        updateUsersInformation(recipient_id,insidequestion=False,totalquestionasked=int(getUserInformation(recipient_id,'totalquestionasked'))+1)
                        rightAns=getUserInformation(recipient_id,'lastRightAnswer')
                        
                        noofconsecutivewrong=getUserInformation(recipient_id,'noofconsecutivewrong')
                        updateUsersInformation(recipient_id,noofconsecutiveright=0)
                        updateUsersInformation(recipient_id,noofconsecutivewrong=noofconsecutivewrong+1)
                        
                        
                        
                        currtopic=getUserInformation(recipient_id,"currenttopic")
                        #currtotal=str(currtopic)+'total'
                        updateUsersInformation(recipient_id,**{str(currtopic)+'total':int(getUserInformation(recipient_id,str(str(currtopic)+'total')))+1})
                        
                        
                        reply=decisionRightWrong('wrong', noofconsecutivewrong)
                        #send_message(recipient_id, "dummy","dummy",reply+ ' ,the right answer is: '+'\n'+rightAns)
                        quickreply(recipient_id,['Try Another','Go Back','Results','I am Bored!'],reply+ ' ,the right answer is: '+'\n'+rightAns+'\n'+getUserInformation(recipient_id,'lastsolution'))
                        
                        return "Message Processed"
                    
                    topic,mood,response = get_message(recipient_id,message['message'].get('text'))
                    #checkPostback(output)
                    isQuickReply=checkQuickReply(message['message'].get('text'),recipient_id)
                    
                    isQuickReplyHint=checkQuickReply(response,recipient_id)
                    isCalculator=checkCalculator(recipient_id,message['message'].get('text'))
                    if isQuickReply==False and isQuickReplyHint==False and isCalculator==False :
                        quickreply(recipient_id,['I am good', 'I am Bored!'],response)
                        #sendLastOptionsQuickReply(recipient_id,'kya be')
                        return "Message Processed"
                #if user sends us a GIF, photo,video, or any other non-text item
                if message['message'].get('attachments'):
                    response = ['(y)',':)',":D"]
                    sendVideo(recipient_id,'http://clips.vorwaerts-gmbh.de/big_buck_bunny.mp4')
                    quickreply(recipient_id,['Lets test', 'I am Bored!'],random.choice(response))
                
    return "Message Processed"


def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error
    print('bot started yeay1')
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'


#chooses a random message to send to the user
def get_message(recipient_id,query):
      
  try:  
    punctuation=[',','.','!','?']
    for i in punctuation:
        query=query.replace(i,"")
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
    global consumer_id     
    id=  output['entry'][0]['messaging'][0]['sender']['id']  
    consumer_id=id
    a=requests.get("https://graph.facebook.com/"+id+"?fields=first_name,last_name,profile_pic&access_token="+ACCESS_TOKEN)
    data=a.json()
    name=data['first_name']
    if output['entry'][0]['messaging'][0]['postback']['payload']=='Startyaar':
       if output['entry'][0]['messaging'][0]['postback'].get('referral'):
         fulladdress=str(output['entry'][0]['messaging'][0]['postback']['referral']['ref'])
         if fulladdress=='clinic':   
          welcome='Hey '+name+',how are you doing today?'
          quickreply(id,['Amazing :D ','Good :) ', 'Not Good :/','Bad :('],welcome)   
          time.sleep(1)
              
        
       else:
          welcome='Hey '+name+',how are you doing today?'
          quickreply(id,['Amazing :D ','Good :) ', 'Not Good :/','Bad :('],welcome)   
          time.sleep(1)
            
def checkReferral(output):
     print('bot started2')
     if output['entry'][0]['messaging'][0].get('referral'):
      id=  output['entry'][0]['messaging'][0]['sender']['id']  
      consumer_id=id
      a=requests.get("https://graph.facebook.com/"+id+"?fields=first_name,last_name,profile_pic&access_token="+ACCESS_TOKEN)
      data=a.json()
      name=data['first_name']
      fulladdress=str(output['entry'][0]['messaging'][0]['referral']['ref'])
      if fulladdress=='clinic':
         print('bot started3')
         welcome='Hey '+name+',how are you doing today?'
         quickreply(id,['Amazing :D ','Good :) ', 'Not Good :/','Bad :('],welcome)   
         time.sleep(1)
             
      
      return True                  
            
            
            
            
            
            
     
         
      
def checkCalculator(id,text):
   try:
     text=text.lower()
     text=text.replace('+','%2B')
     text=text.replace("what is","")
     text=text.replace("calculate","")
     text=text.replace("evaluate","")   
     resultOfCalculation=requests.get("http://api.mathjs.org/v4/?expr="+str(text)) 
     if str(resultOfCalculation)=="<Response [200]>":   
      if getUserInformation(id,'insidequestion')==True: 
         p=sendLastOptionsQuickReply(id,resultOfCalculation.text)
         return True
      else:
         quickreply(id,['Lets test', 'I am Bored!'],resultOfCalculation.text)   
         return True
     else:
        return False
    
   
   except:
    return False
    
def checkQuickReply(text,id): 
          
          
          if text=='Good :) ':
                send_message(id,'a','a', 'I am glad :) ')
                quickreply(id,['Yes (y)','No'],'Do you feel healthy?') 
                return True 
          if text=='Not Good :/':
                send_message(id,'a','a', 'ooh :( ')
                quickreply(id,['Yes (y)','No'],'Do you feel healthy?') 
                return True 
          if text=='Bad :(':
                send_message(id,'a','a', 'Ooh.Sorry to hear that')
                quickreply(id,['Yes (y)','No'],'Do you feel healthy?') 
                return True   
          if text=='Amazing :D ':
                send_message(id,'a','a', 'Awesome :D.')
                quickreply(id,['Yes (y)','No'],'Do you feel healthy?') 
                return True 
          if text=='Yes':
                send_message(id,'a','a', 'Great :D.')
                quickreply(id,['Yup','No Never'],'Have you ever heard the quote-"we are what we eat"?') 
                return True 
          if text=='No':
                send_message(id,'a','a', 'Ok!')
                quickreply(id,['Yup','No Never'],'Have you ever heard the quote-"we are what we eat"?') 
                return True
          if text=='Yup':
                send_message(id,'a','a', 'Cool,hope you follow it! B)')
                send_message(id,'a','a', 'Alright!')
                quickreply(id,['Pretty well :)','Not so well :) '],'How well did you sleep? 😴') 
                return True 
          if text=='No Never':
                send_message(id,'a','a', 'Well its a popular saying: \n Anyways it means its important to be eating good to be feeling good')
                send_message(id,'a','a', 'Alright!')
                quickreply(id,['Pretty well','Not so well'],'How well did you sleep? 😴') 
                return True  
          if text=='Pretty well':
                
                send_message(id,'a','a', 'Great!')
                quickreply(id,['I surely do!','Nope I am busy'],'Do you get time to work out? 💪') 
                return True 
          if text=='Not so well':
                send_message(id,'a','a', 'Ooh,I see')
                quickreply(id,['I surely do!','Nope I am busy'],'Do you get time to work out? 💪')  
                return True  
          if text=='I surely do!':
                
                send_message(id,'a','a', 'Good for you!')
                quickreply(id,['Yes please 🥗','No Thanks'],'Are you ready for a fun healthy diet?🥗 \n You would see the real results,its not difficult but needs only slight disciplpine,anyways I am here to help.You ready for a good change?') 
                return True 
          if text=='Nope I am busy':
                send_message(id,'a','a', 'Ooh,I see')
                quickreply(id,['Yes please 🥗','No Thanks'],'Are you ready for a fun healthy diet?🥗 \n You would see the real results,its not difficult but needs only slight disciplpine,anyways I am here to help.You ready for a good change?')  
                return True   
          if text=='Yes please 🥗':
                
                send_message(id,'a','a', 'Please schedule a time wih us here, and lets meet and discuss')
                return True 
          if text=='No Thanks':
                send_message(id,'a','a', 'Cool,Please let us know if we can help!')
                return True   
              
        
          else:
            return False    

        
#uses PyMessenger to send response to user
def send_message(recipient_id, topic,mood,response):
    #sends user the text message provided via input response parameter
    if mood=='call':
          bot.send_button_message(recipient_id,'Not Satisfied with my responses? Call Our Representative! ',response)
          return 'success'  
    bot.send_text_message(recipient_id, response)
    return "success"



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

    
    
    
    
    
    
    
    
def shareme(message):
    shareit={
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
    return shareit
def sendSuperTopic(id):
    response=   {
     "recipient":{"id":id},
     "message":{
      "quick_replies": [
      {
        "content_type":"text",
        "title":"I am Bored!",
        "payload":'I am Bored!'
      }],   
      "attachment":{
        "type":"template",
          "payload":{
           "template_type":"generic",
             "elements":[
                 
                 {
                 "title":"Job Preparation",
                   "image_url":"http://www.dvc.edu/enrollment/career-employment/images/Jobs.jpg",
                      "subtitle":"practice problems that makes you ready for interview I have aptitude,verbal ability and logical reasoning",
                       
                           "buttons":[
                             {"type":"postback",
  "title":"Start now",
  "payload":"jobPrep"},shareme('he helps practice interview questions,you should try it')] },
                 
                 
                 
                 
                  {
                 "title":"Internship interview",
                   "image_url":"http://www.dvc.edu/enrollment/career-employment/images/Jobs.jpg",
                      "subtitle":"solve questions and get interview with top companies!!",
                       "buttons":[{"type":"postback","title":"Start now",
                                   "payload":"InternPrep"},shareme('Let us practice interview questions!')] },
                 
                 
                 
                  {
                 "title":"Basic Science",
                   "image_url":"http://2.bp.blogspot.com/_Q_ZJiaCqn38/TFIu3dkYfxI/AAAAAAAAACo/63Vuzi-IG4A/s1600/SCIENCE.png",
                     "subtitle":"Practice basic science problems and improve your concepts",
                        
                           "buttons":[
                             {"type":"postback",
  "title":"Start now",
  "payload":"Basic Science"},shareme('Lets practice basic science questions,you should try it')] }
             ]}}}}
    r=pay(response)
    return r
  
def sendResult(id, gif,message):
    url = search_gif(gif)
    share=shareme(message)
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
        AR=int(getUserInformation(id,'aptituderight'))
        AT=int(getUserInformation(id,'aptitudetotal'))
        VR=int(getUserInformation(id,'verbalabilityright'))
        VT=int(getUserInformation(id,'verbalabilitytotal'))
        GR=int(getUserInformation(id,'generalknowledgeright'))
        GT=int(getUserInformation(id,'generalknowledgetotal'))
        PR=int(getUserInformation(id,'physicsright'))
        PT=int(getUserInformation(id,'physicstotal'))
        CR=int(getUserInformation(id,'chemistryright'))
        CT=int(getUserInformation(id,'chemistrytotal'))
        BR=int(getUserInformation(id,'biologyright'))
        BT=int(getUserInformation(id,'biologytotal'))
        MR=int(getUserInformation(id,'mathright'))
        MT=int(getUserInformation(id,'mathtotal'))
        W=T-R 
        AW=AT-AR 
        VW=VT-VR
        GW=GT-GR 
        PW=PT-PR
        BW=BT-BR 
        CW=CT-CR 
        MW=MT-MR 
        
        return render_template('chart.html',R=R, W=W,PR=PR, PW=PW,CR=CR, CW=CW,MR=MR, MW=MW,BR=BR, BW=BW,AR=AR,AW=AW,GW=GW,GR=GR,VW=VW,VR=VR)
    


if __name__ == "__main__":
    app.run()
