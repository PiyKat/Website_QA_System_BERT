# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 11:54:50 2019

@author: piyush.kathuria
"""

from Ranker import DocumentRanker,PassageRanker

from inference import bertQAModel
import time
import spacy
from queryProcess import queryProcess

class WebsiteQA:
    
    def __init__(self, query, folderPath):
        self.query = query
        self.path = folderPath
        
    def process(self):
        start = time.time()
        queryObj = queryProcess(self.query)
        docRanker = DocumentRanker(queryObj, self.path)
        topDocuments = docRanker.returnTopDocumentsData()
        print([documents[0] for documents in topDocuments])
        passageRanker = PassageRanker(queryObj, topDocuments)
        passageRanking = passageRanker.returnTopPassages(5)
        #print([])
        bertQA = bertQAModel()
        answerTuple = []
        for docName,levScore,passage in passageRanking : 
            print(docName)
            print(levScore)
            paraText = " ".join(passage)
            answer,bertScore = bertQA.predict(paraText, queryObj)
            print(bertScore)
            finalScore = bertScore + levScore
            answerTuple.append((answer, finalScore))
            #answerTuple.append(bertQA.predict(paraText, self.query))
            
        print("ANSWERS : ")
        sortedAnswers = sorted(answerTuple, key = lambda x: x[1], reverse = True)
        for item in sortedAnswers:
            print(item)
        
        end = time.time()
    
        print("TIME TAKEN : ")
        print(end - start)
        
        answerList = []
        for idx , el in enumerate(sortedAnswers[:6]):
            if el[0].strip() not in ["","[SEP]","[CLS]"]:
                answerList.append({"answer" : el[0], "confidence" : str(el[1])})
            
        
        resultDict = {"question" : self.query, "data": answerList }
        print(resultDict)
        
        return resultDict
            
        
        
        

if __name__ == "__main__":
    
    path = r".\invest_corpus"
    #query = "What was the annualized total return of the S&P 500 between August 1, 1992 and July 31, 2007"
    #query = "who is current CEO?"
    #query = "what is volatility?"
    #query = "Give me an example of cos?"
    #query = "what is black scholes model?"
    #query = "what is moral hazard?"
    #query = "What are mortgage backed securities?"
    #query = "What is Alpha risk?"
    #query = "What is margin call definition?"
    #query = "Give me an example of cost of risk."
    #query = "How does a leveraged loan work?"
    #query = "What was Moody’s role in the 2008 financial crisis?"
    #query = "How do I calculate volatility?"
    #query = "What was the annualized total return of the S&P 500 between August 1, 1992 and July 31, 2007?"
    #query = "Give me an example of a leveraged loan."
    #query = "What is an example of value at risk?"
    #query = "Give me a real world example of volatility?"
    
    
    #query = "What is arbitrage?"
    #query = "What are the two common types of mbss"
    #query = "What is black scholes?"
    #query = "What is covariance?"
    #query = "What is fundamental analysis?"
    #query = "What does modern portfolio theory say?"
    #query = "give me examples of pooled investment vehicle?"
    #query = "give me an example of portable alpha strategy"
    #query = "give me examples of unsystematic risks"
    #query = "Why did LTCM loose money?"
    #query = "who created the internal revenue service?"
    #query = "when was the internal revenue serives created?"
    #query = "who created the government sponsored enterprise?"
    query = "who created global investment performance standard?"
    
    #Collateralized Debt Obligations
    #quer
    obj = WebsiteQA(query, path)
    obj.process()
    