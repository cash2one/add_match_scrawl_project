#!/usr/bin/env python
# encoding=utf-8


"""segment,do not remove single word, use forward/backward_pair to match, do  keep len=1 word in sentence
1)get district,city etc structure from address,
2)remove noise like ( ) |first repeated word |number |appear in the end, not begaining of addresss

denoise
index_1:1-gram,hanzi

database50w record
index string keyword(1gram_onlyMoreThan2Word,2gram_onlySingleWord)->5w record
tfidf:vector every500/batch
'beijng' reduce
"""

#import sys;
#reload(sys);
#sys.setdefaultencoding('utf-8')

import pandas as pd
import chardet,re,jieba,time,math,random,copy
import numpy as np

def get_DistrictName():
    districtNameComplete=[]
    dataDic=grab('/home/yr/intellicredit/data/district_dict')
    for level1,v1 in dataDic.items()[:]:
        name=level1.strip(' ').decode('utf-8')
        districtNameComplete.append(name)
        if isinstance(v1,dict):
            for level2,v2 in v1.items():
                name=level2.strip(' ').decode('utf-8')
                districtNameComplete.append(name)


    return districtNameComplete


def grab(filename):
    import pickle
    fr = open(filename)
    return pickle.load(fr)



def store(inputTree,filename):
    import pickle
    fw = open(filename,'w')
    pickle.dump(inputTree,fw)
    fw.close()

def score_notwell(pair):#[string,string]
    from fuzzywuzzy import fuzz
    score1=fuzz.token_sort_ratio(pair[0],pair[1])
    score2=fuzz.partial_ratio(pair[0],pair[1])
    return (score1+score2)/2.

def calc_EuDistance(test,compare):#[1,d],[n,d]
    testMat=np.tile(test,(compare.shape[0],1));#[1,d]->[n,d]
    dist=testMat-compare
    dist=np.sqrt(np.sum(dist*dist,axis=1))#[n,d]->[n,]
    return dist

def strUnique(string):
    strList=string.split(' ')
    uniqueList=[]
    for w in strList:
        if w not in uniqueList:
            uniqueList.append(w)
    return ' '.join(uniqueList)

def score(testStr,candList1):
    batch_sz=1000
    from sklearn.feature_extraction.text import TfidfVectorizer
    totCandidate=[]
    batch_num=int(math.ceil(len(candList)/float(batch_sz))) #51/50.0->2.0
    for batch in range(batch_num)[:]:
        corpus=np.array(candList1)[batch*batch_sz:(batch+1)*batch_sz];#list print corpus[0],corpus[1] #'北京市 海淀区 西三旗' '人民日报社 爱玛 客 餐厅'
        #############
        # tf idf
        vectorizer = TfidfVectorizer(ngram_range=(1,1),min_df=1)
        corpus=list(corpus)
        corpus.append(testStr)
        rst=vectorizer.fit_transform(corpus)#the last one is testStr
        #print vectorizer.get_feature_names()
        #for w in vectorizer.get_feature_names():
            # print w ##no '客'
        rst=rst.toarray()
        #print 'feature',rst.shape #[n,dim]
        ################
        # calculate distance
        test=rst[-1,:].reshape((1,-1))#[1,d]
        compare=rst[:-1,:] #[n,d]
        dist=calc_EuDistance(test,compare)
        rank=np.argsort(dist)[:20]#index ,from smallScore->largeScore sort
        candidateList=[corpus[ii] for ii in rank]#list
        totCandidate=totCandidate+candidateList
        #score=dist[rank] #array
        #for i in range(len(candidateList))[:]:
         #   print candidateList[i],'eu-dist',score[i]
    #############
    print 'tot candidate',len(totCandidate)
    ###################
    # total candidate
    ## idf
    vectorizer = TfidfVectorizer(ngram_range=(1,1),min_df=1)
    corpus=totCandidate
    corpus.append(testStr)
    rst=vectorizer.fit_transform(corpus)
    rst=rst.toarray()
    # distance
    test=rst[-1,:].reshape((1,-1))#[1,d]
    compare=rst[:-1,:] #[n,d]
    dist=calc_EuDistance(test,compare)
    rank=np.argsort(dist)[:20]#index ,from smallScore->largeScore sort
    candidateList=[corpus[ii] for ii in rank]#list
    score=dist[rank] #array
    for i in range(len(candidateList))[:]:
        print strUnique(candidateList[i]),'eu-dist',score[i]



    ############





def get2gram(strList):#list ['北京市', '区', '西三旗']
    def hasSingle(word2):
        sz=[len(w) for w in word2]
        if 1 in sz:return True
        else:return False
    #####################
    gram2List=[]
    for wInd in range(len(strList))[1:]:
        #w=strList[wInd]
        #if isinstance(w,unicode)==False:w=unicode(w)
        word2=(strList[wInd-1].strip(' '),strList[wInd].strip(' ') );#print word2
        ##### word2=[x,xx] not [xx,xx]  #no [123,093]
        if hasSingle(word2) and ''.join(word2).isdigit()==False:
            word2str=''.join(word2);#print word2str
            gram2List.append(word2str)
    ##############
    return gram2List #['北京市区', '区西三旗']

def addSingle2Bigram(candiArr,testStr):
    #print 'add single'
    # test
    testList1=testStr.split(' ')
    testList2=get2gram(testList1)
    testStr=' '.join(testList2+testList1);#print testStr
    ######### candidate
    canList=[]
    for i in range(len(candiArr))[:]:
        strList1=candiArr[i].split(' ');#print strList1
        strList2=get2gram(strList1);#print strList2
        stringi=' '.join(strList2+strList1);#print stringi
        canList.append(stringi)
    return canList,testStr


def reduceDistrictWeight(candList,testStr):
    print 'reduce district weight...'
    districtNameCompleteList=get_DistrictName()
    ###
    testStrList1=copy.copy(testStr.split(' '))
    for word in testStr.split(' '):
        if word not in districtNameCompleteList:
            testStrList1.append(word)
    testStr=' '.join(testStrList1);#print testStr
    ###########candidate
    candList1=[]
    for cand in candList:
        obsList=copy.copy(cand.split(' '))
        for word in cand.split(' '):
            if word not in districtNameCompleteList:
                obsList.append(word)
        candList1.append(' '.join(obsList))
    #print candList1[0]
    return candList1,testStr




if __name__=="__main__":
    start_time=time.time()

    nameList=['homeAdd','workAdd','workname']
    fname=nameList[0]



    ##########
    # load index ,load database ,load query
    db_df=pd.read_csv('../data/'+fname+'_segmentDenoise.csv',encoding='utf-8')
    print db_df.columns #homeAdd', u'homeAdd_raw'
    wordIndDic1=grab('../data/'+fname+'_wordIndexDict1')
    wordIndDic2=grab('../data/'+fname+'_wordIndexDict2')
    ############
    # query
    string=db_df['homeAdd_raw'].values;print string.shape
    string_seg=db_df['homeAdd'].values
    rng=random.choice(range(string_seg.shape[0])) #6
    query=string[rng];print 'query',rng
    query_preprocess=string_seg[rng];print 'query',query_preprocess
    query_preprocess=query_preprocess.split(' ')#list
    print query_preprocess
    ###########
    # get doc-ind1

    docInd1=[]
    for word in query_preprocess:
        #print word
        if word in wordIndDic1:
            indList1=wordIndDic1[word];
            docInd1=docInd1+indList1
    print 'docind',len(docInd1),len(set(docInd1))


    ################
    # get doc-ind2
    print '2gram...'
    query_preprocess2=get2gram(query_preprocess)#['a','erf']->['aerf']
    print query_preprocess2

    docInd2=[]
    for word in query_preprocess2:
        #print word
        if word in wordIndDic2:
            indList2=wordIndDic2[word];
            docInd2=docInd2+indList2
    print 'docind2',len(docInd2),len(set(docInd2))

    ###################
    # pair score
    candiInd=list(set(docInd1+docInd2))

    scoreList=[]
    candiArr=string_seg[candiInd][:];print 'candidate',candiArr.shape,candiArr[0]
    testStr=string_seg[rng];print testStr
    #[爱玛, 客, 餐厅] ->[爱玛客 ,客餐厅]
    candList,testStr=addSingle2Bigram(candiArr,testStr);print len(candList),candList[0],testStr
    candList1,testStr1=reduceDistrictWeight(candList,testStr)
    score(testStr1,candList1)












    end_time=time.time()
    print 'time: %f minute'%((end_time-start_time)/float(60))













