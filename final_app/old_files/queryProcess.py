# -*- coding: utf-8 -*-
"""
Created on Fri Dec  6 14:31:28 2019

@author: piyush.kathuria
"""

import spacy


class queryProcess():
    
    def __init__(self,query):
        self.query = query
        
    
    def queryNLPObj(self):
        '''
        Convert query string to lower and return a list of tokens from query string
        '''
        nlp = spacy.load("en_core_web_sm",disable = ['ner', 'parser', 'textcat'])
        doc = nlp(self.query.lower())
        queryList = [tokens for tokens in doc]
        print(queryList)
        return queryList
    
    def returnDRQuery(self):
        '''
        Steps for processing query before DocumentRanker
        '''
        queryList = self.queryNLPObj()
        queryList = self.removePunct(queryList)
        return self.returnQList(queryList)
    
    def returnPRQuery(self):
        '''
        Steps for processing query for PassageRanker
        '''
        queryList = self.queryNLPObj()
        queryList = self.removeArticles(queryList)
        queryList = self.removePunct(queryList)
        print("GENERATING NOUNLIST : ")
        nounList = self.getNouns(queryList)
        return self.returnQList(queryList),nounList
    
    def returnInferenceQuery(self):
        '''
        Steps for processing query for Inference
        '''
        queryList = self.queryNLPObj()
        queryList = self.removeArticles(queryList)
        queryList = self.removePunct(queryList)
        return self.returnQString(queryList)
    
    def returnQList(self,queryList):
        '''
        return query tokens after processing
        '''
        return [tokens.text for tokens in queryList]
    
    def returnQString(self,queryList):
        '''
        return query string after processing
        '''
        return " ".join([tokens.text for tokens in queryList])
    
    def getNouns(self,queryList):
        '''
        Return the nouns and adjectives inside a query string
        '''
        nounList = []
        
        for tokens in queryList:
            
            if tokens.pos_ == "NOUN" or tokens.pos_ == "PROPN" or tokens.pos_ == "ADJ":
                print(tokens.text)
                print(tokens.pos_)
                nounList.append(tokens.text)
            
        print("noun list : ", nounList)        
        return nounList
    
    def removePunct(self,queryList):
        '''
        Remove punctuations from our query
        '''
        queryList = [tokens for tokens in queryList if not tokens.is_punct]
        return queryList
        
    def removeArticles(self,queryList):
        '''
        Remove articles from query
        '''
        queryList = [tokens for tokens in queryList if tokens.text not in ["a","an","the"]]
        return queryList
    
if __name__ == "__main__":
    
    queryObj = queryProcess("What is hello ????")
    x = queryObj.returnInferenceQuery()
    print(type(x))