#Importing the desired libraries
from pymongo import MongoClient
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import euclidean_distances
import random
from nltk.stem import PorterStemmer
ps=PorterStemmer()
dummy=''

#Fetching the data from the MongoDB database
def fetchData():
    MONGODB_URI = "mongodb://Debangshu:Starrynight.1@ds163694.mlab.com:63694/brilu"
    client = MongoClient(MONGODB_URI, connectTimeoutMS=30000)
    db = client.get_database("brilu")
    col = db["Knowledgebase"]
    cursor = col.find()
    document = cursor[0]
    return(document)

document=fetchData()
mydict = document['question']

#Functions to check if the query is a chitchat like hi ,hello,bye e.t.c or a comment
def findBest(query,document,topic):
   for mood in  document[topic].keys():
    for question in document[topic][mood]:
        if(stem(query)==stem(question)):
            return(topic,mood,random.choice(document[topic][mood]))
   return ('not','not','not')
def answerBest(topic,mood):
    if topic=='chitchat':
      return(topic,mood,random.choice(document[topic][mood]))
    if topic=='comments':
      return(topic+'ans',mood,random.choice(document[topic+'ans'][mood]))

#If it is not then it searches if the query is a question or not and returns the best matching question

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
#returns the best answer to the question asked
def findBestAnswer(probableQuestion):
    myanswers=[]
    for answer in document['questionans'][probableQuestion]:
        #print(answer)
        myanswers.append(answer)
    return(random.choice(myanswers))

#helper function for stemming of the words
def stem(mystring):
  mystring=mystring.lower()
  mystring=mystring.split()
  my=''
  for word in range(0,len(mystring)):
    my=my+ ps.stem(mystring[word])+' '
  return my

#Main function which calls other finctions and executes the commands one by one.This is the boss

def BRAIN(query):
    topic,mood,question=findBest(query,document,'chitchat')
    if mood !='not':
        return (answerBest(topic,mood))
    topic, mood,question=findBest(query,document,'comments')
    if mood !='not':
        return (answerBest(topic,mood))
    pq = findBestQuestion(query)
    answer=findBestAnswer(pq)
    return('question','enquiry',answer)




