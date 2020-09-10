# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import torch
import transformers
import pickle
#import numpy as np
#from sklearn.preprocessing import normalize,scale
from queryProcess import queryProcess

class bertQAModel():
    
    def __init__(self):
        
        self.tokenizerModel,self.bertQAModel = self.__initializeModel()
        
    
    def __initializeModel(self):
        '''
        Initialize the Beret Tokenizer and the QA model. Note that this is currently compatible with
        transformers module, NOT pytorch/tensorflow
        '''
        with open("./models/bertTokenizer.pkl","rb") as f:
            tokenizerModel = pickle.load(f)
        
        with open("./models/bertQAModel.pkl","rb") as f:
            bertQAModel = pickle.load(f)
        
        return tokenizerModel, bertQAModel
    
    def stringProcess(self,answer):
        answerSplit = answer.split(" ##")
        return "".join(answerSplit)
    
    def predict(self,text,question):
        '''
        Predict the answer given a passage and a question.
        '''
        #questionObj = queryProcess(question)
        question = question.returnInferenceQuery()
        input_text = "[CLS] " + question + " [SEP] " + text + " [SEP]"
        #print("INPUT_TEXT : ")
        #print(input_text)
        input_ids = self.tokenizerModel.encode(input_text)
        #print("TOKENIZED TEXT : ")
        #print(input_ids)
        token_type_ids = [0 if i <= input_ids.index(102) else 1 for i in range(len(input_ids))]

        #start_scores, end_scores = self.bertQAModel(torch.tensor([input_ids]), token_type_ids=torch.tensor([token_type_ids]))
        
        if len(input_ids) < 512:
            start_scores, end_scores = self.bertQAModel(torch.tensor([input_ids]), token_type_ids=torch.tensor([token_type_ids]))
            
            #start_scores_sort = np.sort(start_scores.detach().numpy().flatten())[-2]
            #end_scores_sort = np.sort(end_scores.detach().numpy().flatten())[-2]
            
            #print(start_scores_sort, " --", end_scores_sort )
            
            #start_scores_sort = torch.argsort(-start_scores, descending=True)[1]
            #end_scores_sort = torch.argsort(-end_scores,descending=True)[1]
        

            all_tokens = self.tokenizerModel.convert_ids_to_tokens(input_ids)
            answer = ' '.join(all_tokens[torch.argmax(start_scores) : torch.argmax(end_scores)+1])
            
            #answer_new = ' '.join(all_tokens[(start_scores_sort) : (end_scores_sort)+1])
            
            startScoreInd,endScoreInd = torch.argmax(start_scores),torch.argmax(end_scores)
            startScoresVec = start_scores.detach().numpy().flatten()
            endScoresVec = end_scores.detach().numpy().flatten()

            startScoreMax, endScoreMax = startScoresVec[startScoreInd] , endScoresVec[endScoreInd]
            #avgScore = float(np.absolute(startScoreMax) + np.absolute(endScoreMax))
            #avgScore = float(startScoreMax + endScoreMax)
            #print("ANSWER RETRIEVED : ")
            #print(self.stringProcess(answer))
            #print(self.stringProcess(answer_new))
            return (self.stringProcess(answer),startScoreMax)
        else:
            return ("", 0.0)
        
        
        
        
        all_tokens = self.tokenizerModel.convert_ids_to_tokens(input_ids)
        answer = ' '.join(all_tokens[torch.argmax(start_scores) : torch.argmax(end_scores)+1])
        startScoreInd,endScoreInd = torch.argmax(start_scores),torch.argmax(end_scores)
        startScoresVec = start_scores.detach().numpy().flatten()
        endScoresVec = end_scores.detach().numpy().flatten()
        
        startScoreMax, endScoreMax = startScoresVec[startScoreInd] , endScoresVec[endScoreInd]
        #avgScore = float(np.absolute(startScoreMax) + np.absolute(endScoreMax))
        #avgScore = float(startScoreMax + endScoreMax)
        print("ANSWER RETRIEVED : ")
        print(self.stringProcess(answer))
        return (self.stringProcess(answer),startScoreMax)
    
if __name__ == "__main__" :
    
    obj = bertQAModel()
    text = "s&p ’s leveraged commentary & data ( lcd ) , which is a provider of leveraged loan news and analytics , places a loan in its leveraged loan universe if the loan is rated bb- or lower . alternatively , a loan that is nonrated or bbb- or higher is often classified as a leveraged loan if the spread is libor plus 125 basis points or higher and is secured by a first or second lien . example of a leveraged loan ."
    text2 = "example of a leveraged loan . s&p ’s leveraged commentary & data ( lcd ) , which is a provider of leveraged loan news and analytics , places a loan in its leveraged loan universe if the loan is rated bb- or lower . alternatively , a loan that is nonrated or bbb- or higher is often classified as a leveraged loan if the spread is libor plus 125 basis points or higher and is secured by a first or second lien ."
    question = "Give me an example of leveraged loan."
    print(obj.predict(text,question))
    print(obj.predict(text2,question))
    #obj.predict("Narendar Modi said that there is a lack of good employment opportunities in India","What did Narendar Modi say?")
    
    #pass