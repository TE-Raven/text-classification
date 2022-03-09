# -*- coding: utf-8 -*-
"""part2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/19CPZhFXu6aUR5KDgkoygf37hyDP1Q74a

import moduls
"""

from google.colab import drive #connect to colab
import numpy as np #data processing tools
import pandas as pd #data processing tools
import os #for file reading
from sklearn.model_selection import train_test_split #Divide the dataset
from gensim import utils #unicode encoding conversion
import gensim.parsing.preprocessing as gsp #Data cleaning
import nltk  #Data cleaning
nltk.download('omw-1.4')
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
import sklearn #machine learning library
import operator # The itemgetter function provided by the operator module is used to obtain the data of which dimensions of the object, and the parameters are some serial numbers
drive.mount('/content/drive') #cloud disk path
from sklearn.feature_extraction.text import TfidfVectorizer #tfidf feature extraction library
from sklearn import svm #svm classifier
from sklearn.linear_model import LogisticRegression #logistic regression classifier
from sklearn.metrics import classification_report #Classification performance report
from sklearn.feature_selection import chi2 #Feature selection filter -chi2 (chi-square statistic)
from sklearn.feature_selection import SelectKBest #Score features and select features from high to low
from sklearn.feature_extraction.text import CountVectorizer #Numerical computation of features
from sklearn.pipeline import Pipeline #The training data and test data are processed in a unified way

"""dataprocessing"""

root=r"/content/drive/MyDrive/news_classifacation/bbc"
filename=[]
dirs=os.listdir(root)#Get the folder name in the path
mark=0 #Label
data= pd.DataFrame(columns=('text','mark'))#Create a dataframe and use the text column to store the data, and the mark column to store the label
#print(dirs)
for dir in dirs:
    dir_path = root +'/' +dir #Get dataset folder path
    names = os.listdir(dir_path) #Get a list of dataset txt file names
    if dir == 'business':
        mark =0
    if dir == 'entertainment':
        mark =1
    if dir == 'politics':
        mark =2
    if dir == 'sport':
        mark =3
    if dir == 'tech':
        mark =4
    for n in names:
     filename.append(dir_path + '/'+ n )# Get the data set txt file path
    for m in filename:
        with open(m, encoding='gb18030', errors='ignore') as content:
            # text=content.rstrip('\n')
            a = content.read() #Read dataset file contents
            b = a.replace('\n', '').replace('\r', '') #remove newlines
            data1 = pd.DataFrame({'text': b, "mark": mark}, index=[0])#write to temporary dataframe
            data = data.append(data1, ignore_index=True) #Add to the dataset dataframe
    filename=[]
#data.to_csv("dataset.csv") this command can generate a dataset file for check or other using

data1=data[['text','mark']] #Get the dataset dataframe
lable=data['mark'] #get label

"""set filters"""

filters = [
               gsp.strip_punctuation,     # remove punctuation     
               gsp.strip_multiple_whitespaces, # delete multiple lines 
               gsp.strip_numeric,       # delete numbers      
               gsp.remove_stopwords,      # Remove stop words (and, to, the in English)    
               gsp.strip_short,        # lowercase formal words      
               gsp.stem_text          # Extract stem to etymological form          
      ]

"""data cleaning"""

data=pd.DataFrame(columns=(['text']))
for i in range(0,len(data1)):
    a=data1.iloc[i]['text']
    a=a.lower()
    a=utils.to_unicode(a)#unicode encoding conversion
    for f in filters: #text cleaning
        a=f(a)
    d = pd.DataFrame({'text': a}, index=[0])
    data = data.append(d, ignore_index=True) #Add the cleaned text back to the dataframe

data['mark']=lable#rewrite the labels to the dataframe

"""data_set_spilt"""

x_train,x_test,y_train,y_test = train_test_split(data['text'],data['mark'],test_size=0.2 , stratify=data['mark'],random_state=389 )

"""X_train,X_test, y_train, y_test =sklearn.model_selection.train_test_split(train_data,train_target,test_size=0.4, random_state=0,stratify=y_train)
train_data: The sample feature set to be divided
train_target: The sample result to be divided
test_size: sample proportion, if it is an integer, it is the number of samples
random_state: is the seed of the random number.

Random number seed: In fact, it is the number of the random number of the group. When the experiment needs to be repeated, it is guaranteed to get the same set of random numbers. For example, if you fill in 1 every time, the random array you get is the same when the other parameters are the same. But fill in 0 or not fill in, each time will be different.

stratify is to preserve the distribution of the pre-split classes. For example, there are 100 pieces of data, 80 belong to class A and 20 belong to class B. If train_test_split(... test_size=0.25, stratify = y_all), then the data after split is as follows:
training: 75 data, of which 60 belong to class A and 15 belong to class B.
testing: 25 data, of which 20 belong to class A and 5 belong to class B.
With the stratify parameter, the ratio of the classes in the training set and the testing set is A:B=4:1, which is equivalent to the ratio before split (80:20). Stratify is usually used in such cases where the class distribution is unbalanced.

Stratify=X is to distribute according to the proportion in X
Stratify=y is to distribute according to the proportion in y

word frequency
"""

#get feature
lemmatizer = nltk.stem.WordNetLemmatizer()#Use the lemmatization tool to combine different spellings of the same root.

def get_list_tokens(string): #get list tokens
  sentence_split=nltk.tokenize.sent_tokenize(string)
  list_tokens=[]
  for sentence in sentence_split:
    list_tokens_sentence=nltk.tokenize.word_tokenize(sentence)
    for token in list_tokens_sentence:
      list_tokens.append(lemmatizer.lemmatize(token).lower())
  return list_tokens

stopwords=set(nltk.corpus.stopwords.words('english'))
stopwords.add(".")
stopwords.add(",")
stopwords.add("--")
stopwords.add("``")

dict_word_frequency={}
#get word frequency in text
for i in x_train:
    sentence_tokens = get_list_tokens(i)
    for word in sentence_tokens:
        if word in stopwords: continue
        if word not in dict_word_frequency:
            dict_word_frequency[word] = 1
        else:
            dict_word_frequency[word] += 1
sorted_list = sorted(dict_word_frequency.items(), key=operator.itemgetter(1), reverse=True)[:1000] #Get the top 1000 words of frequency

vocabulary=[] #write word to table
for word,frequency in sorted_list:
  vocabulary.append(word)


# transform sentences into vectors
def get_vector_text(list_vocab,string):
  vector_text=np.zeros(len(list_vocab))
  list_tokens_string=get_list_tokens(string)
  for i, word in enumerate(list_vocab):
    if word in list_tokens_string:
      vector_text[i]=list_tokens_string.count(word)
  return vector_text

df_train=[]
df_test=[]
x_test_1=[]
for i in x_train:
    vector_review = get_vector_text(vocabulary, i)
    df_train.append(vector_review)
for i in x_test:
    vector_review = get_vector_text(vocabulary, i)
    df_test.append(vector_review)
for i in x_test:
    vector_review = get_vector_text(vocabulary, i)
    x_test_1.append(vector_review)

#convert to array
X_train_sentanalysis=np.asarray(df_train)
Y_train_sentanalysis=np.asarray(y_train)
x_test_1_sentanalysis=np.asarray(x_test_1)

#Feature selection, use chi-square for feature selection, select the top 500 features as training features
#The value of k is to select the largest number of features
fs_sentanalysis=SelectKBest(chi2,k=500).fit(X_train_sentanalysis,Y_train_sentanalysis.astype('int'))
X_train_sentanalysis_new=fs_sentanalysis.transform(X_train_sentanalysis)
x_test_sentanalysis_new=fs_sentanalysis.transform(x_test_1_sentanalysis)

svm_clf_sentanalysis=sklearn.svm.SVC(kernel="linear",gamma='auto')
#The type of sum function used in the algorithm, the kernel function is a method used to transform a nonlinear problem into a linear problem. The parameter options are RBF, Linear, Poly, Sigmoid, precomputed or a custom kernel function. The default is "RBF", which is the radial basis kernel, which is the Gaussian kernel function; Linear refers to the linear kernel function, and Poly refers to is a polynomial kernel, and Sigmoid refers to the hyperbolic tangent function tanh kernel;
#Kernel function coefficient, this parameter is the kernel coefficient of rbf, poly and sigmoid; the default is 'auto', then the inverse of the number of features will be used, ie 1 / n_features. (i.e. the bandwidth of the kernel function, the radius of the hypercircle). The larger the gamma, the smaller the σ, which makes the Gaussian distribution tall and thin, so that the model can only act near the support vector, which may lead to overfitting; on the contrary, the smaller the gamma, the larger the σ, and the Gaussian distribution will be too smooth. Poor classification on the set may lead to underfitting.
svm_clf_sentanalysis.fit(X_train_sentanalysis_new,Y_train_sentanalysis.astype('int')) #Train the model
print('word frequency')
print(classification_report(y_test.astype('int'),svm_clf_sentanalysis.predict(x_test_sentanalysis_new)))#The result is obtained by the classification_report function

"""TFIDF"""

tfidf=TfidfVectorizer(ngram_range=(1,2),max_features=20,stop_words=['english'],max_df=0.6)
x_train_new=tfidf.fit_transform(x_train)#Get the word frequency inverse document frequency feature
x_test_new=tfidf.fit_transform(x_test)#Get the word frequency inverse document frequency feature
#feature selection
fs_sentanalysis=SelectKBest(chi2,k=10).fit(x_train_new,y_train.astype('int'))
x_train_1=fs_sentanalysis.transform(x_train_new)
x_test_1=fs_sentanalysis.transform(x_test_new)
svm_clf_sentanalysis=sklearn.svm.SVC(kernel="linear",gamma='auto')


svm_clf_sentanalysis.fit(x_train_new,y_train.astype('int'))#train the Model

print(classification_report(y_test.astype('int'),svm_clf_sentanalysis.predict(x_test_new)))#The result is obtained by the classification_report function

"""TfidfVectorizer Parameter introduction

input: string{'filename', 'file', 'content'}

    If 'filename', the sequence is passed as an argument to the fitter, expected to be a list of filenames, which needs to read the raw content for analysis

    If 'file', the sequence item must have a 'read' method (a file-like object) that is called to get the number of bytes in memory

    Otherwise, the input is expected to be a sequence string, or byte data items are expected to be parsed directly.

encoding: string, 'utf-8' by default

    If given bytes or files to parse, this encoding will be used for decoding

decode_error: {'strict', 'ignore', 'replace'}

    Indicates what to do if a given byte sequence contains characters that are not in the given encoding. By default it is 'strict' which means UnicodeDecodeError will be raised, other values ​​are 'ignore' and 'replace'

strip_accents: {'ascii', 'unicode', None}

    Remove encoding rules (accents) in the preprocessing step, "ASCII" is a fast method, only if there is a direct ASCII character mapping, "unicode" is a slightly slower method, None (default) what neither do

analyzer: string, {'word', 'char'} or callable

    Defines features as words or n-gram characters, if the call passed to it is used to extract feature sequences from unprocessed input source files

preprocessor: callable or None (default)

    Override the preprocessing (string transformation) stage when preserving tokens and "n-gram" generation steps

tokenizer: callable or None (default)

    Override the string token step when keeping the preprocessing and n-gram generation steps

ngram_range: tuple(min_n, max_n)

    Lower and upper range of n-values ​​of n-grams to be extracted, all values ​​of n in the interval min_n <= n <= max_n

stop_words: string {'english'}, list, or None (default)

    If not english, the built-in stopword list for English

    If not listed, the list is assumed to contain stop words and all words in the list will be removed from the token

    If None, stopwords are not used. max_df can be set to a value in the range [0.7, 1.0) to automatically detect and filter stop words based on internal expected word frequencies

lowercase: boolean, default True

    Convert all characters to lowercase before tokenization

token_pattern: string

    The regular expression showing the composition of "token" is only used when analyzer == 'word'. Regular expression of two or more alphanumeric characters (punctuation is completely ignored, always treated as a token separator).

max_df: float in range [0.0, 1.0] or int, optional, 1.0 by default

    When building the vocabulary, terms with document frequencies above a given threshold are strictly ignored, corpus-specified stopwords. If it is a floating point value, this parameter represents the proportion of the document, an integer absolute count value, if the vocabulary is not None, this parameter is ignored.

min_df: float in range [0.0, 1.0] or int, optional, 1.0 by default

When building the vocabulary, terms with a document frequency lower than a given threshold are strictly ignored, stopwords specified by the corpus. If it is a floating point value, this parameter represents the proportion of the document, an integer absolute count value, if the vocabulary is not None, this parameter is ignored.

max_features: optional, None by default

    If not None, build a vocabulary, only consider max_features--sort by corpus word frequency, if the vocabulary is not None, this parameter is ignored

vocabulary: Mapping or iterable, optional

    Also a Map (eg, a dictionary) where the keys are the terms and the values ​​are indices in the feature matrix, or iterators in the terms. If not given, the vocabulary is determined from the input file. There must be no duplication of indices in the map, and no gaps between 0 and the maximum index value.

binary: boolean, False by default

    If not True, all non-zero counts are set to 1, which is useful for discrete probability models, modeling binary events instead of integer counts

dtype: type, optional

    The type of the matrix returned by fit_transform() or transform()

norm: 'l1', 'l2', or None, optional

    Norms are used to normalize term vectors. None for non-normalization

use_idf: boolean, optional

    Start inverse-document-frequency to recalculate weights

smooth_idf: boolean, optional

    Smooth the idf weights by adding 1 to the document frequency, adding an extra document to prevent division by zero

sublinear_tf: boolean, optional

    Apply a linear scaling TF, e.g. overwrite tf with 1+log(tf)

bio_gram
"""

sel = SelectKBest(chi2, k=3000)#Define Feature Selection Parameters
pipe=Pipeline([('vec',CountVectorizer(ngram_range=(2,2),min_df=3,max_df=0.9,max_features=4500)),
               ('sel',sel),
               ('clf',LogisticRegression(C=4,dual=False,max_iter=10000))])
clf=pipe.fit(x_train,y_train.astype('int'))
print('bio_gram')
print(classification_report(y_test.astype('int'),clf.predict(x_test)))

"""CountVectorizer parameter introduction

input: string {'filename', 'file', 'content'}

If 'filename', passed as argument in a suitable sequence is expected to be a list of filenames that need to be read to get the raw content to parse.
If 'file', the sequence item must have a 'read' method (file-like object) that is called to get the bytes in memory.
Otherwise, the expected input is a sequence string or bytes items are expected to be parsed directly.
encoding: string, defaults to 'utf-8'.

If bytes or files are given for analysis, this encoding is used for decoding.
decode_error: {'strict', 'ignore', 'replace'}

Indicates what to do if a byte sequence is given to parse containing characters that are not in the given encoding. By default, it is 'strict', which means UnicodeDecodeError is raised. Other values ​​are "ignore" and "replace".
strip_accents: {'ascii', 'unicode', None}

Whether to remove accents in the preprocessing step. 'ascii' is a fast method that only works for characters with direct ASCII mapping. 'unicode' is a slightly slower method that works for any character. None (default) does nothing.
analyzer: string, {'word', 'char', 'char_wb'} or callable

Whether the feature should consist of word or character n-grams. Option 'char_wb' creates character n-grams only from text within word boundaries; n-grams at word edges are padded with spaces.
If passed a callable, it will be used to extract the sequence of features from the raw unprocessed input.
preprocessor: callable or None (default)

Overrides the preprocessing (string transformation) stage while retaining the tokenizing and n-grams generation steps.
tokenizer: callable or None (default)

Rewrite the string tokenization step while preserving the preprocessing and n-grams generation steps.
only works with analyzer == 'word'
ngram_range: tuple(min_n, max_n)

Lower and upper bounds of the range of n values ​​for the different n-grams to extract.
All values ​​of n will be used such that min_n <= n <= max_n.
stop_words: string {'english'}, list, or None (default)

"english", using the built-in English stopword list.
"list", if a list, is assumed to contain stop words, then all words in the list will be removed from the resulting token. only works with analyzer == 'word'
"None", stopwords will not be processed. max_df can be set to a value in the range [0.7, 1.0) to automatically detect and filter stop words based on term internal corpus document frequency.
lowercase: boolean, True (default)

Convert all characters to lowercase before calculating 'tf'.
token_pattern: string

Regular expression that defaults to filtering mixed alphanumeric characters of length >= 2 (punctuation is completely ignored and always treated as a token separator). Only used when analyzer=='word' is used.
max_df: float (in [0.0, 1.0]), or int, default = 1.0

Words with a document frequency strictly above a given threshold (corpus-specific stopwords) are ignored when building the vocabulary. If float, the parameter represents the scale of the document, i.e. an integer absolute count.
This parameter is ignored if vocabulary is not None.
min_df: float (in [0.0, 1.0]) or int, default = 1

If an int, words with a document frequency strictly below the given threshold are ignored when building the vocabulary. This value is also called cutoff value in the literature;
If float, the parameter represents the scale of the document;
This parameter is ignored if vocabulary is not None.
max_features: int or None (default)

If not None, build a vocabulary and create a corpus with only the top max_features words sorted by word frequency.
This parameter is ignored if vocabulary is not None.
vocabulary: Mapping or iterable

Mapping (for example, a dictionary) where keys are terms and values ​​are indices in the feature matrix;
iterable, an iterable over terms;
If not given, the vocabulary is determined from the input file. mapping, the exponents should not be repeated and there should not be any gap between 0 and the maximum exponent.
binary: boolean, default is False

If True, all non-zero counts are set to 1. (i.e., tf has only values ​​0 and 1, indicating occurrences and non-occurrences)
This is useful for discrete probability models that model binary events rather than integer counts.
dtype: type, optional

The type of matrix returned by fit_transform() or transform().

Introduction to Pipeline Mechanism

The pipeline mechanism realizes the streaming encapsulation and management of all steps
Steps that can be placed in the Pipeline may be:
Feature standardization can be used as the first link
Data dimensionality reduction (feature selection) can be added in the middle
Defining the classifier is the last step

tri_gram
"""

sel=SelectKBest(chi2,k=2500)
pipe=Pipeline([('vec',CountVectorizer(ngram_range=(3,3),min_df=3,max_df=0.9,max_features=3000)),
        ('sel',sel),
        ('clf',LogisticRegression(C=4,dual=False,max_iter=10000))])
clf=pipe.fit(x_train,y_train.astype('int'))
print('tri_gram')
print(classification_report(y_test.astype('int'),clf.predict(x_test)))