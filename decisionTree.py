from pymongo import MongoClient
def fetchData():
    MONGODB_URI = "mongodb://Debangshu:Starrynight.1@ds163694.mlab.com:63694/brilu"
    client = MongoClient(MONGODB_URI, connectTimeoutMS=30000)
    db = client.get_database("brilu")
    col = db["usersInfo"]
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
def askQuestion(topic):
    question="who is the father of the nation"
    options=['gandhi','nehru','jayanta','netaji']
    right='gandhi'
    response=[]
    
    for option in options:
        if option==right:
            response.append({"type": "postback", "title": option,"payload": 'right'})
        if option!=right:    
           response.append({"type": "postback", "title": option,"payload": 'wrong'})
    return question,response

    
        
        
    
