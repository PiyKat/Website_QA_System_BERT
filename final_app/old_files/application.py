# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 11:54:50 2019

@author: piyush.kathuria
"""

from Ranker import DocumentRanker,PassageRanker

from inference import bertQAModel
import time
import spacy


class WebsiteQA:
    
    def __init__(self, query, folderPath):
        self.query = query
        self.path = folderPath
        
    def process(self):
        start = time.time()
        
        docRanker = DocumentRanker(self.query, self.path)
        topDocuments = docRanker.returnTopDocumentsData()
        #print(topDocuments[5])
        passageRanker = PassageRanker(self.query, topDocuments)
        passageRanking = passageRanker.returnTopPassages()
       
        bertQA = bertQAModel()
        answerTuple = []
        for passage,_ in passageRanking : 
            
            paraText = " ".join(passage)
            answerTuple.append(bertQA.predict(paraText, self.query))
            
        print("ANSWERS : ")
        sortedAnswers = sorted(answerTuple, key = lambda x: x[1], reverse = True)
        for item in sortedAnswers:
            print(item)
        
        end = time.time()
    
        print("TIME TAKEN : ")
        print(end - start)
        
        answerList = []
        for idx , el in enumerate(sortedAnswers[:6]):
            answerList.append({"answer" : el[0], "confidence" : str(el[1])})
            
        
        resultDict = {"question" : self.query, "data": answerList }
        print(resultDict)
        
        return resultDict
            
        
        
        

if __name__ == "__main__":
    
    path = r".\invest-data"
    #query = "What was the annualized total return of the S&P 500 between August 1, 1992 and July 31, 2007"
    #query = "who is current CEO?"
    #query = "what is volatility?"
    #query = "Give me an example of cos?"
    #query = "what is black scholes model?"
    query = "what is shareholder equity?"
    #query = "What is an alpha risk?"
    #query = "How do I calculate volatility?"

    
    obj = WebsiteQA(query, path)
    obj.process()
    