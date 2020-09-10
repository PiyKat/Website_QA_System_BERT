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
from nltk import SnowballStemmer
from queryProcess import queryProcess
import Levenshtein

class DocumentRanker():
    
    def __init__(self, query, folderPath):
        
        self.documentFolderPath = folderPath
        print("folderPath  : ", folderPath)
        self.queryList = query.returnDRQuery()
        self.folderDocumentContent = self.loadDocuments()  # Store the content of all the files in dictionary
        self.bm25Model = self.createBM25Model()
    
    
    def loadDocuments(self):
        '''
        Load documents from the invest_data folder into a dictionary
        '''
        documentTuple = []
        #nounList = self.getNouns()
        nlp = spacy.load("en_core_web_sm",disable = ['ner', 'parser', 'textcat'])
        fileList = []
        for root, dirs, files in os.walk(self.documentFolderPath):
    
            for file in files:
                if file.endswith('txt'):
                    with open(os.path.abspath(os.path.join(root, file)), 'r' , encoding="utf8" ) as f:
                        content = f.read()
                        content = content.lower()
                        doc = nlp(content)
                        tokenizedContent = [tokens.text for tokens in doc]# if tokens.text not in ["a","an","the"]]         # Change 1 
                        
                        if file not in fileList:
                            fileList.append(file)
                            documentTuple.append((file,tokenizedContent))
        
       
        return documentTuple
    
        
    def createBM25Model(self):
        '''
        Return a created BM25 model.
        '''
        return gensim.summarization.bm25.BM25([x[1] for x in self.folderDocumentContent])
    
    def rankDocuments(self):
        '''
        Rank the documents in the corpus wrt the query. 
        '''
        
        scores = self.bm25Model.get_scores(self.queryList)
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
        topDocumentScores = self.returnTopK(5)
        #print("topDocumentScores  : ", topDocumentScores)
        topDocumentNames = [x[0] for x in topDocumentScores]
        topDocumentText = [x for x in self.folderDocumentContent if x[0] in topDocumentNames]
        return topDocumentText
        #return (topDocumentNames, topDocumentText)
    

class PassageRanker():
    
    def __init__(self, query, topDocumentContent):
        
        self.queryList,self.nounList = query.returnPRQuery()
        self.topDocumentContent = topDocumentContent
        #self.BM25Model = self.createBM25Model()
    
    def createBM25Model(self,documentContent):
        '''
        Return a created BM25 model.
        '''
        #return gensim.summarization.bm25.BM25([x[1] for x in self.topDocumentContent])
        return gensim.summarization.bm25.BM25(documentContent)
    
    
    def checkNounMatch(self,paragraph,nounList):
        '''
        A function to see if each noun is matching for a paragraph
        '''
        nounBool = True

        stemmer = SnowballStemmer("english")
        paragraphContent = " ".join([stemmer.stem(token) for token in paragraph])
        
        
        for nouns in self.nounList:
            
            if stemmer.stem(nouns) in paragraphContent:
                nounBool = True
            else:
                nounBool = False
                break
        
        return nounBool
                
            
    def returnParagraphList(self,content):
        '''
        Return pargaraph in the form of list of lists to be fed to the BM25 Model
        '''
        paragraphList = []
        sepCounter = 0
        
        for i,term in enumerate(content):
            
            if term == "--------------------------":
                paragraph = content[sepCounter:i] # " ".join() <-
                if self.checkNounMatch(paragraph,self.nounList):
                #if all(nouns in paragraph for nouns in nounList):
                    paragraphList.append(paragraph)
                
                sepCounter = i+1
        
        return paragraphList
    
    
    def returnParagraphScores(self,bm25Model):
        '''
        Return the score of a paragraph given a model.
        '''
        return bm25Model.get_scores(self.queryList)
        
    
    def returnTopPassages(self, k=5):
        '''
        Rank each paragraph from the document and return the top 10 passages from the collection of documents
        '''
        #query = [tokens.text for tokens in self.queryList if not tokens.is_punct]
        
        paragraphScoreTup = []
        
        for documents in self.topDocumentContent:
            docName = documents[0].replace(".txt","").lower()
            paragraphScoreTup.append((docName , self.calculateLD(docName,self.queryList),documents[1]))
            

        print(" length of paragraphScoreTup : ", len(paragraphScoreTup))
        
        self.topParagraphScores = sorted(paragraphScoreTup, key = lambda x: x[1], reverse = True)
        
        return self.topParagraphScores[:k]
    
    
    def calculateLD(self,docName,query):
        '''
        Return the levenstein distance between query and title of the document
        '''
        return Levenshtein.ratio(docName,"".join(query))*10
        
    

if __name__ == "__main__":
    
    
    query = "what is volatility?"
    docRanker = DocumentRanker(query,".\invest_corpus")
    #docRanker.bm25Model.idf['covariance']
    #docRanker.bm25Model.idf['measure']
    #print(docRanker.bm25Model.get_scores("What is Black Scholes"))
    #print(docRanker.returnTopK("What is Black Scholes Model",30))
    topDocuments = docRanker.returnTopDocumentsData()
    print(topDocuments)
    passageRanker = PassageRanker(query,topDocuments)
    passageRanking = passageRanker.returnTopPassages(5)
    for values in passageRanking :
        
        print(values)