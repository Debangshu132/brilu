from pymongo import MongoClient
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import euclidean_distances
import random
from nltk.stem import PorterStemmer
ps=PorterStemmer()
dummy=''

def fetchData():
    MONGODB_URI = "mongodb://Debangshu:Starrynight.1@ds163694.mlab.com:63694/brilu"
    client = MongoClient(MONGODB_URI, connectTimeoutMS=30000)
    db = client.get_database("brilu")
    col = db["Knowledgebase"]
    cursor = col.find()
    # p.pprint(cursor[0])
    document = cursor[0]
    #p.pprint(document.keys())
    #p.pprint(document["chitchat"])
    return(document)





def findBest(query,document,topic):
   for mood in  document[topic].keys():
    for question in document[topic][mood]:
        if(stem(query)==stem(question)):
            return(topic,mood,random.choice(document[topic][mood]))
   return ('not','not','not')
def answerBest(topic,mood,document):
    if topic=='chitchat':
      return(topic,mood,random.choice(document[topic][mood]))
    if topic=='comments':
      return(topic+'ans',mood,random.choice(document[topic+'ans'][mood]))



def findBestQuery(query,document,que):

   questionarr = []
   intentarr=[]
   answerarr=[]
   for topics in document.keys():
    if topics==que:
        for questionlist in document[topics].keys():
         for question in document[topics][questionlist]:
               questionarr.append(question)
               intentarr.append(questionlist)
               #print(questionlist)

   query = stem(query)
   for i in range(0, len(questionarr)):
       questionarr[i] = stem(questionarr[i])
   questionarr.append(query)
   #print(questionarr)
   vectorizer = CountVectorizer()
   ques = vectorizer.fit_transform(questionarr).todense()
   match = []
   for f in range(0, len(ques) - 2):
       p = euclidean_distances(ques[len(ques) - 1], ques[f])
       match.append(p[0][0])
   m = match.index(min(match))
   #print(match)
   if match == [] or min(match) > 1.5:
      return 'sorry i dont know how to reply'
   probableQuestion=questionarr[m]
   #print('probable question=',intentarr[m])
   #print('query=',query)
   return (que,intentarr[m],probableQuestion)


def findBestAnswer(probableQuestion,document):
    myanswers=[]
    for answer in document['questionans'][probableQuestion]:
        #print(answer)
        myanswers.append(answer)
    return(random.choice(myanswers))
def tryToHandleByQuickReply(probableQuestion,document):
     if document['quickreplymapping'].get(probableQuestion):
           return True,probableQuestion
     return False,"dummy"


def stem(mystring):
  mystring=mystring.lower()
  mystring=mystring.split()
  my=''
  for word in range(0,len(mystring)):
    my=my+ ps.stem(mystring[word])+' '
  return my

def BRAIN(query):
    document = fetchData()
    topic,mood,question=findBest(query,document,'chitchat')
    if mood !='not':
        return (answerBest(topic,mood,document))
    topic, mood,question=findBest(query,document,'comments')
    if mood !='not':
        return (answerBest(topic,mood,document))
    topic,mood,question = findBestQuery(query,document,'question')

    if mood =='callrepresentative':
        return ('question', 'call', document['journeys']['callrepresentativeans']['button'])
    isquickreply,answer=tryToHandleByQuickReply(mood,document)
    if isquickreply==True:
         return ("dummy", "dummy",answer)
    answer = findBestAnswer(mood, document)
    return (topic, mood,answer)






