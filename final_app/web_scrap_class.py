# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 10:31:37 2019

@author: prateek.sethi
"""

import bs4
import urllib.request
import re
import timeit
import os
import spacy

class WebsiteData():
    
    def __init__(self, website,depth, pathName):#,website,parser = 'lxml'):
        '''
        Constructor of the class. We let the user choose the parser type, but keep it default to the fastest parser.
        We are keeping the bsObject private because the end user should NOT get access to any HTML information.
        '''
        self.website = website
        self.pageDict = {}
        self.depth = depth
        self.pathName = pathName
        '''
        try:
            sauce = urllib.request.urlopen(self.website)
            self.__bsObject = bs4.BeautifulSoup(sauce,parser)
        except:
            print("Website not accessible : " ,self.website)
            self.__bsObject = None
            return None
        '''
            
    def parseBaseWebsite(self, parser = 'lxml'):
        try:
            sauce = urllib.request.urlopen(self.website)
            self.__bsObject = bs4.BeautifulSoup(sauce,parser)
            return 1
        except Exception as e:
            print("Website not accessible. Exception :  " ,e)
            self.__bsObject = None
            return None
    
    def __getBaseURL(self):
        '''
        Return the base url of the website being parsed
        '''
        count = 0
        base1 = []
        base = ''
        if re.findall('http[s]?', self.website):
            for i in self.website:
                if i == '/':
                    count= count+1
                if count == 3:
                    break
                base1.append(i)
        
            base = base.join(base1)
        
        return base
    
    def displayHtml(self):
        '''
        Display website in HTML Structure 
        '''
        print(self.__bsObject.prettify())
    
    def retrieveHrefs(self):
        '''
        Retrieve links from the HREF Tags in the webpage 
        '''
        self.__linksList = []
        baseUrl = self.__getBaseURL()
        print("base url : ", baseUrl)
        
       
        bodyContent = self.__bsObject.find("div", attrs = {'id': 'mntl-sc-page_1-0'})
        
        
        for link in bodyContent.find_all('a'):
            #print(link)
            suffixURL = link.get('href')
            #print(type(suffixURL))
            print(suffixURL)
            
            if (suffixURL is not None) and ('www.investopedia.com' in suffixURL) and (suffixURL.endswith('.asp'))  :
                self.__linksList.append(str(suffixURL))
                
         
        return self.__linksList
    
    def saveWebsiteData(self, levels):
        '''
        Save the data from the website in a txt file. The method creates a file with the topic of the link as the file name.
        The code will be extended to store the data from all the links in the linksList in the future.
        '''
        #nlp = spacy.load("en_core_web_sm",disable = ['ner', 'parser', 'textcat'])
        
        pathName = self.pathName
        if levels == 0 :
            pathName = pathName
        else:
            for counter in range(levels):
                pathName = pathName +  "/level" + str(counter+1 )
                
        if not os.path.exists(os.path.join(os.getcwd(),pathName)):
            os.mkdir(os.path.join(os.getcwd(),pathName ))
                

        #headerContent = self.__bsObject.find_all("span", attrs = {'class': 'mntl-sc-block-heading__text'})
 
            
            
        
        #print(headerContent)
        bodyContent = self.__bsObject.find("div", attrs = {'id': 'mntl-sc-page_1-0'})
        paragraphs = bodyContent.find_all('p')
        #headers = headerContent.find_all('')

        print("writing data")        
        file_name = os.path.join(os.path.join(os.getcwd(), pathName), (self.website).split("/")[-1] + ".txt")
        print(file_name)
        
        maxParaLen = 0
        sumParaLen = 0
        nlp = spacy.load("en_core_web_sm",disable=['ner', 'parser', 'textcat'])
        totalParaLen = len(paragraphs)
        #print(paragraphs)
        count = 0 
        prevHeadingText = ""
        fileText = ""
        for paragraph in paragraphs:
            fileName = (self.website).split("/")[-1]
            fileName = fileName.split(".asp")[0]
            #print(fileName)
            #with open( os.path.join(os.path.join(os.getcwd(), pathName) , fileName + str(count)+ ".txt"),"w+", encoding='utf-8') as f:
               
            
            if paragraph.find_parent('div').find_previous('h3') is not None:
                heading = paragraph.find_parent('div').find_previous('h3')
                if heading.find('span') is not None:
                    heading_text = heading.find('span').text
                    
                else:
                    heading_text = heading.text
            else:
                heading = paragraph.find_parent('div').find_previous('h1')
                heading_text = heading.text
            
            
            heading_text = heading_text.replace('\n', "")
            heading_clean = re.sub('[^A-Za-z0-9]+', '', heading_text)
            
            
            
            if heading_text != prevHeadingText:
                sizeBuffer = 0
                counter = 0
                
                paraText = heading_text+ ". " + paragraph.getText()
                fileText = paraText
                
                prevHeadingText = heading_text
                file_clean_name = heading_clean
                
                #sizeBuffer = len(fileText.split())
                doc = nlp(fileText)
                fileDoc = [tokens for tokens in doc]
                sizeBuffer = len(fileDoc)
                print(" sizeBuffer1 : ", sizeBuffer )
                with open( os.path.join(os.path.join(os.getcwd(), pathName) , file_clean_name + ".txt"),"w+", encoding='utf-8') as f:
                    f.write(fileText)
                    
                
            else:
                doc = nlp(paragraph.getText())
                paraDoc = [tokens for tokens in doc]
                #print("this condition :" , len(paragraph.getText().split()) + sizeBuffer)
                #if (len(paragraph.getText().split()) + sizeBuffer) > 460:
                if (len(paraDoc) + sizeBuffer) > 460:
                    
                    print ("special case :", heading_clean + str(counter+1) )
                    counter = counter + 1
                    
                    heading_clean =  heading_clean + str(counter)
                    
                    file_clean_name = heading_clean
                    fileText = heading_text+ ". " + paragraph.getText()
                    #sizeBuffer = len(fileText.split())
                    doc = nlp(fileText)
                    fileDoc = [tokens for tokens in doc]
                    sizeBuffer = len(fileDoc)
                    print(" sizeBuffer2 : ", sizeBuffer )
                    with open( os.path.join(os.path.join(os.getcwd(), pathName) , file_clean_name + ".txt"),"w+", encoding='utf-8') as f1:
                        f1.write(fileText)
                        
                    
                else:
                    #fileText = fileText + " " + paragraph.getText()
                    fileText = heading_text+ ". " + paragraph.getText()
                    #sizeBuffer = sizeBuffer + len(fileText.split())
                    doc = nlp(fileText)
                    fileDoc = [tokens for tokens in doc]
                    sizeBuffer = sizeBuffer + len(fileDoc)
                    print(" sizeBuffer3 : ", sizeBuffer )
                    with open( os.path.join(os.path.join(os.getcwd(), pathName) , file_clean_name + ".txt"),"a", encoding='utf-8') as f2:
                        f2.write(fileText)
                        
                
           
            
            '''
            paraText = paragraph.getText()
            print("paraText   :   ", paraText)
            paraTextDoc = nlp(paraText)
            paraTextDocList = [tokens.text for tokens in paraTextDoc if tokens.text.strip() != '']
            paraLen = len(paraTextDocList)
            paraText = " ".join(paraTextDocList)
            sumParaLen = sumParaLen + paraLen
            if paraLen > maxParaLen:
                maxParaLen = paraLen

            f.write(paraText)
            '''
            
            count+=1
                

            #avgParaLen = (sumParaLen/totalParaLen)
            #self.pageDict[(self.website).split("/")[-1]] = (maxParaLen , avgParaLen)

            #f.close()
        return self.pageDict
        


class WebsiteParser:
    
    def __init__(self,baseWebsite,level, pathName):
        
        self.baseWebsite = baseWebsite
        self.level = level
        self.pathName = pathName
    
    def parseWebsite(self):
        
        pageDict ={}
        linkDict = {}
        
        for level in range(self.level):
            
            if level == 0:
                obj = WebsiteData(self.baseWebsite,level, self.pathName)
                objret = obj.parseBaseWebsite()
                linkDict[level +1] = obj.retrieveHrefs()
                if objret is not None: 
                    data = obj.saveWebsiteData(level) 
                    pageDict.update(data)
            else:
                linkDict[level +1] = []
        
                if level < (self.level - 1):
                
                    for link in set(linkDict[level]):
                        obj1 = WebsiteData(link, level, self.pathName)
                        obj1ret = obj1.parseBaseWebsite()
                       
                        linkDict[level +1].extend(obj1.retrieveHrefs())
                        
                        if obj1ret is not None: 
                            data = obj1.saveWebsiteData(level) 
                            pageDict.update(data)
                
                else:
                    for link in set(linkDict[level]):
                        obj1 = WebsiteData(link, level, self.pathName)
                        obj1ret = obj1.parseBaseWebsite()
                        
                        if obj1ret is not None: 
                            data = obj1.saveWebsiteData(level) 
                            pageDict.update(data)
                
            

if __name__ == "__main__":
    sampleObj = WebsiteParser('https://www.irissoftware.com/',3 , "iris-data")
    try:
        status = 1 
        sampleObj.parseWebsite()
    except Exception:
        status = 0 
        pass
    
    print(status)        
        

'''
numLevels = 3
initLink = 'https://www.investopedia.com/terms/r/riskmanagement.asp'
pageDict ={}
linkDict = {}


obj = WebsiteData(initLink)
print(obj.parseWebsite())



for levels in range(numLevels):
    if levels == 0:
        obj = WebsiteData(initLink)
        objret = obj.parseWebsite()
        linkDict[levels +1] = obj.retrieveHrefs()
        #print(linkDict)
        
        if objret is not None: 
            data = obj.saveWebsiteData(levels) 
            pageDict.update(data)
       
    else:
        linkDict[levels +1] = []
        
        if levels < (numLevels - 1):
        
            for link in linkDict[levels]:
                obj1 = WebsiteData(link)
                obj1ret = obj1.parseWebsite()
               
                linkDict[levels +1].extend(obj1.retrieveHrefs())
                
                if obj1ret is not None: 
                    data = obj1.saveWebsiteData(levels) 
                    pageDict.update(data)
        
        else:
            for link in linkDict[levels]:
                obj1 = WebsiteData(link)
                obj1ret = obj1.parseWebsite()
               
                #linkDict[levels +1].extend(obj1.retrieveHrefs())
                
                if obj1ret is not None: 
                    data = obj1.saveWebsiteData(levels) 
                    pageDict.update(data)
        
'''
    
'''    
for link in linkDict[2][174:]:
    if link.endswith('.asp'):
        obj1 = WebsiteData(link)
        obj1ret = obj1.parseWebsite()
       
        #linkDict[levels +1].extend(obj1.retrieveHrefs())
        
        if obj1ret is not None: 
            data = obj1.saveWebsiteData(2) 
            pageDict.update(data)
''' 
