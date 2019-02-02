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
    return ['physics','biology','chemistry','math']
def decision(input):
     if input=='JEE Mains':
         msg=['Okay so JEE mains it is! I will continue giving you some random questions from mains paper ',' Untill you decide its enough','JEE Mains']
         listitems=['Okay Sure','Go Back']
         return msg,listitems
     if input=='biology':
         msg=['Okay so biology it is! I will continue giving you some random questions from biology ',' Untill you decide its enough','biology']
         listitems=['Okay Sure','Go Back']
         return msg,listitems
     if input=='math':
         msg=['Okay so math it is! I will continue giving you some random questions from math ',' Untill you decide its enough','math']
         listitems=['Okay Sure','Go Back']
         return msg,listitems 
     if input=='chemistry':
         msg=['Okay so chemistry it is! I continue giving you some random questions from chemistry ',' Untill you decide its enough','chemistry']
         listitems=['Okay Sure','Go Back']
         return msg,listitems 
     if input=='physics':
         msg=['Okay so physics it is! I will continue giving you some random questions from physics ',' Untill you decide its enough','physics']
         listitems=['Okay Sure','Go Back']
         return msg,listitems 
     if input=='Lets test':
           msg=['okay lets test your knowledge! ','Choose a topic from below','biology']
           listitems=listOfExams()
           return msg,listitems  
     if input=='Go Back':
            msg=['Going back,which topic would you like to practice']
            listitems=listOfExams()   
            return msg, listitems
     if input=='Okay Sure':
            msg=['okay,Lets start']
            listitems=['Go Back']
            return msg,listitems
     if input=='Try Another':
            msg=['okay,Lets start again']
            listitems=['Go Back']
            return msg,listitems   
     if input=='Another One':
            msg=['okay,Lets start again']
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
        
     if input=='I am Bored!':  
            msg=['I am Bored!']
            listitems=['Go Back','Lets test','Continue','Tell me a joke']
            return msg,listitems
def decisionRightWrong(rightwrong,numberofrightwrong):
    if rightwrong=='right':
        if numberofrightwrong==0:
            Arr=['Thats right! :)','Yup, thats right','You got it right!','Your answer is correct :)']
            return random.choice(Arr)
        if numberofrightwrong==1:
             Arr=['Right again!','Yay! again right! :D','Absolutely right again!','You got it right again! :D']
             return random.choice(Arr)
        if numberofrightwrong>=2:
            Arr=['You are on fire :D , Thats right!','Guess what :D , THATS RIGHT....AGAIN',
                 'Wow I am so proud of you,Right AGAIN!! :D','You are a genius!,RIGHT AGAIN :D']
            return random.choice(Arr)
        
    if rightwrong=='wrong':
        if numberofrightwrong==0:
            Arr=['Thats wrong !','Its wrong ','That answer is wrong','Sorry but its incorrect']
            return random.choice(Arr)
        if numberofrightwrong==1:
            Arr=['OOPS! wrong again!','Its wrong again!!','You got it wrong again','thats incorrect again :)']
            return random.choice(Arr)
        if numberofrightwrong>=2:
            Arr=['Well this is embarrasing. You should try harder may be :)','Think hard!! this is not good','Sorry to say but WRONG AGAIN!!!!' ]
            return random.choice(Arr) 
    
    
    
    
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

    
        
        
    
