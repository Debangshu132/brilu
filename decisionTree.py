from pymongo import MongoClient
import random
def fetchData():
    MONGODB_URI = "mongodb://Debangshu:Starrynight.1@ds163694.mlab.com:63694/brilu"
    client = MongoClient(MONGODB_URI, connectTimeoutMS=30000)
    db = client.get_database("brilu")
    col = db["questionAnswers"]
    cursor = col.find()
    # p.pprint(cursor[0])
    userInfo = cursor[0]
    #p.pprint(document.keys())
    #p.pprint(document["chitchat"])
    return(userInfo)


def listOfExams():
    return ['JEE Advanced','JEE Mains','GATE']
def decision(input):
     if input=='JEE Mains':
         msg=['Okay so JEE mains it is! I will give you some random questions from mains paper ',' untill you decide its enough']
         listitems=['Okay Sure','Go Back']
         return msg,listitems
     if input=='JEE Advanced':
         msg=['Okay so JEE advanced it is! I will give you some random questions from the advanced paper',' untill you decide its enough']
         listitems=['Okay Sure','Go Back']
         return msg,listitems 
     if input=='GATE':
         msg=['Okay so GATE it is! I will give you some random questions from the GATEpaper',' untill you decide its enough']
         listitems=['Okay Sure','Go Back']
         return msg,listitems 
     if input=='Lets test':
           msg=['okay lets test you buddy','choose an exam from below']
           listitems=['JEE Advanced','JEE Mains','GATE']
           return msg,listitems  
     if input=='Go Back':
            msg=['Going back,Which exam would you like to take']
            listitems=listOfExams()   
            return msg, listitems
     if input=='Okay Sure':
            msg=['okay,Lets start']
            listitems=['Go Back']
            return msg,listitems
     if input=='Try Another':
            msg=['okay,Lets start']
            listitems=['Go Back']
            return msg,listitems   
     if input=='Another One':
            msg=['okay,Lets start']
            listitems=['Go Back']
            return msg,listitems     
       
"""def resultOfQuickreply(message):        
     if  message['message'].get('quick_reply'):
                      if message['message']['quick_reply']['payload']=='right':
                        return('Thats right',['Another one','Go Back'],True)
                      if message['message']['quick_reply']['payload']=='wrong':
                        return ('sorry thats wrong!',['Try again','Go Back'],True)
     else:
        return 'sorry thats wrong!',['Try again','Go Back'],False"""
                         
def askQuestion(topic):
    question="Who is the father of the nation?"
    options=['  A  ','  B  ','  C  ','  D  ']
    right='gandhi'
    questionanswer=fetchQuestionanswer('physics')
    question= questionanswer['question']
    options=questionanswer['options']
    right=questionanswer['right']
    return question,options,right
def fetchQuestionanswer(topic):
    MONGODB_URI = "mongodb://Debangshu:Starrynight.1@ds163694.mlab.com:63694/brilu"
    client = MongoClient(MONGODB_URI, connectTimeoutMS=30000)
    db = client.get_database("brilu")
    col = db["questionAnswers"]
    cursor = col.find()
    questionAnswers = cursor[0]
    return(random.choice(questionAnswers[topic]))

    
        
        
    
