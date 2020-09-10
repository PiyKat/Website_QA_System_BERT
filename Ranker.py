# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 11:57:11 2019

@author: piyush.kathuria
"""

#from gensim.summarization.bm25 import get_bm25_weights
#from gensim.summarization import bm25
import gensim.summarization.bm25 
import gensim
import os
import numpy as np
import pickle
import spacy


class DocumentRanker():
    
    def __init__(self, query, folderPath):
        
        self.documentFolderPath = folderPath
        print("folderPath  : ", folderPath)
        self.query = query
        self.folderDocumentContent = self.loadDocuments()  # Store the content of all the files in dictionary
        self.bm25Model = self.createBM25Model()
        
        
    def loadDocuments(self):
        '''
        Load documents from the invest_data folder into a dictionary
        '''
        documentTuple = []
        nounList = self.getNouns()
        
        for root, dirs, files in os.walk(self.documentFolderPath):
    
            for file in files:
                if file.endswith('txt'):
                    with open(os.path.abspath(os.path.join(root, file)), 'r' , encoding="utf8" ) as f:
                        content = f.read()
                        content = content.lower()
                        #if all(nouns in content for nouns in nounList):
                            
                        documentTuple.append((file,content.split()))
                            
                        #print("selected files : ", file)
                        
        
        return documentTuple
    
    def getNouns(self):
        
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(self.query)
        nounList = []
        
        for token in doc:
            #print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_, token.shape_, token.is_alpha, token.is_stop)
            if token.pos_ == "NOUN" or token.pos_ == "PROPN" :
                nounList.append(token.text)
            
        print("noun list : ", nounList)        
        return nounList
    
    def createBM25Model(self):
        '''
        Return a created BM25 model.
        '''
        return gensim.summarization.bm25.BM25([x[1] for x in self.folderDocumentContent])
    
    def rankDocuments(self):
        '''
        Rank the documents in the corpus wrt the query. 
        '''
        
        query = self.query.lower().split()
        scores = self.bm25Model.get_scores(query)
        documentScores =  [(self.folderDocumentContent[i][0],scores[i]) for i in range(len(scores))]
        return documentScores
    
    def returnTopK(self,k=5):
        '''
        Return top k ranked documents wrt given user query
        '''
        
        scoreDict = self.rankDocuments()
        return sorted(scoreDict , key = lambda x: x[1], reverse = True)[:k]
    
    def returnTopDocuments(self):
        '''
        Return top documents wrt given user query. This uses a different approach from our 
        previous function. We return all documents with score a standard deviation above the
        mean score of our corpus
        '''
        
        scoreTup = self.rankDocuments()
        #scoreDict = dict(scoreTup)
        scores = np.array([x[1] for x in scoreTup])
        #scores = np.array(list(scoreDict.values()))
        meanScore = np.mean(scores)
        sdScore = np.std(scores)
        maxThreshold = meanScore + sdScore
        topScoresDict = [x for x in scoreTup if x[1] > maxThreshold]
        topDocumentScores = sorted(topScoresDict, key = lambda x: x[1], reverse = True)
        
        return topDocumentScores
    
    def returnTopDocumentsData(self):
        '''
        Return data from the top documents retrieved by returnTopDocuments
        '''
        #query = self.query
        topDocumentScores = self.returnTopDocuments()
        print("topDocumentScores  : ", topDocumentScores)
        topDocumentNames = [x[0] for x in topDocumentScores]
        #print(topDocumentNames)
        
        topDocumentText = [x for x in self.folderDocumentContent if x[0] in topDocumentNames]
        return topDocumentText
    

class PassageRanker():
    
    def __init__(self, query, topDocumentContent):
        
        self.query = query
        self.topDocumentContent = topDocumentContent
        #self.BM25Model = self.createBM25Model()
        
    def createBM25Model(self,documentContent):
        '''
        Return a created BM25 model.
        '''
        #return gensim.summarization.bm25.BM25([x[1] for x in self.topDocumentContent])
        return gensim.summarization.bm25.BM25(documentContent)
    
    def getNouns(self):
        
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(self.query.lower())
        nounList = []
        
        for token in doc:
            #print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_, token.shape_, token.is_alpha, token.is_stop)
            if token.pos_ == "NOUN" or token.pos_ == "PROPN" :
                nounList.append(token.text)
            
        #print("noun list : ", nounList)        
        return nounList
    
    def returnParagraphList(self,content):
        '''
        Return pargaraph in the form of list of lists to be fed to the BM25 Model
        '''
        paragraphList = []
        sepCounter = 0
        nounList = self.getNouns()
        for i,term in enumerate(content):
            
            if term == "--------------------------":
                paragraph = content[sepCounter:i] # " ".join() <-
                if all(nouns in paragraph for nouns in nounList):
                    paragraphList.append(paragraph)
                
                sepCounter = i+1
        
        return paragraphList
    
    
    def returnParagraphScores(self,bm25Model,query):
        '''
        Return the score of a paragraph given a model.
        '''
        return bm25Model.get_scores(query)
        
    
    def returnTopPassages(self, k=10):
        '''
        Rank each paragraph from the document and return the top 10 passages from the collection of documents
        '''
        query = self.query.lower().split()
        
        #documentParagraphScores = [(document[0],self.rankPassages(document[1])) for document in topDocumentContent]
        paragraphScoreTup = []
        paragraphLoL = []
        for documents in self.topDocumentContent:
            #print(documents)
            paragraphLoL.extend(self.returnParagraphList(documents[1]))
        
        
        print(len(paragraphLoL))
        passageBM25Model = self.createBM25Model(paragraphLoL)
        
        #for documents in self.topDocumentContent:
        paragraphScores = self.returnParagraphScores(passageBM25Model, query)
        for i,paragraph in enumerate(paragraphLoL):
                
            paragraphScoreTup.append((paragraph,paragraphScores[i]))
        
        print(" length of paragraphScoreTup : ", len(paragraphScoreTup))
        
        self.topParagraphScores = sorted(paragraphScoreTup, key = lambda x: x[1], reverse = True)
        
        return self.topParagraphScores#[:k]
                
                
                
        #print(documentParagraphScores)
        #documentParagraphs = [(document[0],self.returnParagraphList(document[1])) for document in topDocumentContent]
        
        
        
        

#class PassageRanker():
    
    
        
    

if __name__ == "__main__":
    
    
    query = "what is volatility"
    docRanker = DocumentRanker(query)
    #docRanker.bm25Model.idf['covariance']
    #docRanker.bm25Model.idf['measure']
    #print(docRanker.bm25Model.get_scores("What is Black Scholes"))
    #print(docRanker.returnTopK("What is Black Scholes Model",30))
    topDocuments = docRanker.returnTopDocumentsData()
    passageRanker = PassageRanker(topDocuments)
    passageRanking = passageRanker.returnTopPassages(100)
    for values in passageRanking :
        
        print(values)