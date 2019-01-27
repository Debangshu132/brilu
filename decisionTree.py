def decision(input):
     if input=='JEE Mains':
         msg='Okay so JEE mains it is! I will give you some random questions from mains paper as practice untill you decide its time to do something else'
         listitems=['Deal','Go Back']
         return msg,listitems
     if input=='JEE Advanced':
         msg='Okay so JEE advanced it is! I will give you some random questions from the advanced paper as practice untill you decide its time to do something else'
         listitems=['Deal','Go Back']
         return msg,listitems 
     if input=='Go Back':
            msg='okay,Which exam would you like to take'
            listitems=['JEE Advanced','JEE Mains']   
            return msg, listitems
        
    
