from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import euclidean_distances

def singlechat():
  questions = open("Knowledge/questions.txt", "r+")
  answers = open("Knowledge/answers.txt", "r+")
  questionarr=questions.read().split("\n")
  query=input("How may I help you:")
  questionarr.append(query)
  answerarr=answers.read().split("\n")
  vectorizer=CountVectorizer()
  ques=vectorizer.fit_transform(questionarr).todense()
  match=[]
  for f in range(0,len(ques)-2):
    p=euclidean_distances(ques[len(ques)-1],ques[f])
    match.append(p[0][0])
  m=match.index(min(match))
  print(answerarr[m])
  return(answerarr[m])
while(1):
    reply=singlechat()
    if reply=='stop':
        break

