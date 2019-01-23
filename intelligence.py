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

document=fetchData()
mydict = document['question']
def findBestChitchat(query,document):
    for question in document["chitchat"]["Greetings"]:
        if(stem(query)==stem(question)):
            return('chitchat','Greetings',query)
    for question in document["chitchat"]["partings"]:
        if(stem(query)==stem(question)):
            return('chitchat','partings',query)
    for question in document["chitchat"]["laughter"]:
        if(stem(query)==stem(question)):
            return('chitchat','laughter',query)
    for question in document["chitchat"]["crying"]:
        if(stem(query)==stem(question)):
            return('chitchat','crying',query)
    return('notChitchat','notChitchat','notChitchat')

def answerBestChitchat(mood):
    return('chitchat',mood,random.choice(document["chitchat"][mood]))
def findBestComment(query,document):
    for question in document["comments"]["praisecomment"]:
        if stem(query)==stem(question):
            return('comments','praisecomment',question)
    for question in document["comments"]["Grateful"]:
        if stem(query)==stem(question):
            return('comments','Grateful',question)
    for question in document["comments"]["negativecomment"]:
        if stem(query)==stem(question):
            return('comments','negativecomment',question)
    return ('notComment','notComment','notComment')
def answerBestComment(mood):
    return ('chitchat', mood, random.choice(document["commentsans"][mood]))

def findBestQuestion(query):

   questionarr = []
   intentarr=[]
   answerarr=[]
   for topics in document.keys():
    if topics=='question':
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
   print('probable question=',intentarr[m])
   #print('query=',query)
   return (intentarr[m])
def findBestAnswer(probableQuestion):
    myanswers=[]
    for answer in document['questionans'][probableQuestion]:
        #print(answer)
        myanswers.append(answer)
    return(random.choice(myanswers))

def stem(mystring):
  mystring=mystring.lower()
  mystring=mystring.split()
  my=''
  for word in range(0,len(mystring)):
    my=my+ ps.stem(mystring[word])+' '
  return my

def BRAIN(query):
    topic,mood,question=findBestChitchat(query,document)
    print(topic,mood,question)
    if mood !='notChitchat':
        return (answerBestChitchat(mood))
    topic, mood,question=findBestComment(query,document)
    if mood !='notComment':
        return (answerBestComment(mood))
    pq = findBestQuestion(query)
    print(pq)
    answer=findBestAnswer(pq)
    return('question','enquiry',answer)



