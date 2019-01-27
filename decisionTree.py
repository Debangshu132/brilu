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
     if input=='Go Back':
            msg=['okay going back,Which exam would you like to take']
            listitems=listOfExams()   
            return msg, listitems
     if input=='Okay Sure':
            msg=['okay,Lets start']
            listitems=[]
            return msg,listitems    
        
    
