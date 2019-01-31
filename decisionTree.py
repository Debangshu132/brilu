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
    return(userInfo)
def updateUsersInformation(ID, **kwargs):
    MONGODB_URI = "mongodb://Debangshu:Starrynight.1@ds163694.mlab.com:63694/brilu"
    client = MongoClient(MONGODB_URI, connectTimeoutMS=30000)
    db = client.get_database("brilu")
    for key in kwargs:
        db.userInfo.update({"_id" : "5c4e064ffb6fc05326ad8c57"}, {"$set":{str(ID)+"."+str(key): kwargs[key]}},upsert=True);
    return(0)


def listOfExams():
    return ['physics','biology','chemistry']
def decision(input):
     if input=='JEE Mains':
         msg=['Okay so JEE mains it is! I will give you some random questions from mains paper ',' untill you decide its enough','JEE Mains']
         listitems=['Okay Sure','Go Back']
         return msg,listitems
     if input=='biology':
         msg=['Okay so biology it is! I will give you some random questions from biology ',' untill you decide its enough','biology']
         listitems=['Okay Sure','Go Back']
         return msg,listitems 
     if input=='chemistry':
         msg=['Okay so chemistry it is! I will give you some random questions from biology ',' untill you decide its enough','chemistry']
         listitems=['Okay Sure','Go Back']
         return msg,listitems 
     if input=='physics':
         msg=['Okay so physics it is! I will give you some random questions from physics ',' untill you decide its enough','physics']
         listitems=['Okay Sure','Go Back']
         return msg,listitems 
     if input=='Lets test':
           msg=['okay lets test your knowledge! ','choose a topic from below','biology']
           listitems=['JEE Mains','physics','biology']
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
        
     if input=='Results':
            msg=['Results','Okay let me check your results!!']
            listitems=['Details','Go Back','Continue']
            return msg,listitems      
     if input=='Continue':
            msg=['okay,Lets start']
            listitems=['Go Back']
            return msg,listitems
        
     if input=='Inspire me':  
            msg=['Inspire me']
            listitems=['Go Back','Lets test']
            return msg,listitems
def handleResults(total,right):
    percent=(right*100.0/total)
    if percent<=50:
        return 'nice'
    if percent<=80 and percent>50:
        return 'fantastic'
    if percent<=100 and percent>80:
        return 'awesome'
    
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
    questionanswer=fetchQuestionanswer(topic)
    question= questionanswer['question']
    options=questionanswer['options']
    right=questionanswer['right']
    exceeded=False
    for option in options:
        if len(option)>19:
            exceeded=True
    return question,options,right,exceeded
def fetchQuestionanswer(topic):
    MONGODB_URI = "mongodb://Debangshu:Starrynight.1@ds163694.mlab.com:63694/brilu"
    client = MongoClient(MONGODB_URI, connectTimeoutMS=30000)
    db = client.get_database("brilu")
    col = db["questionAnswers"]
    cursor = col.find()
    questionAnswers = cursor[0]
    return(random.choice(questionAnswers[topic]))

    
        
        
    
