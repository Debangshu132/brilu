def decision(payload):
    if payload==Startyaar:
     return (examOptions)
def examOptions():
     payload= {"recipient":{"id":id}, 
                "message":{"text": "Please choose an exam from below:",
                  "quick_replies":[{"content_type":"text","title":"JEE Advanced","payload":"JEE Advanced"},
                                   {"content_type":"text","title":"JEE Mains","payload":"JEE Mains"}]}}     
     return payload    
