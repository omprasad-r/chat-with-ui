#import pinecone
from pinecone import Pinecone, ServerlessSpec
from bs4 import BeautifulSoup
import pandas as pd
import requests
import streamlit as st
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain.embeddings import SentenceTransformerEmbeddings
from sentence_transformers import SentenceTransformer,util
model = SentenceTransformer('all-MiniLM-L6-v2') #384 dimensional
from scrape import *


###########------------------------------Pinecone indexs--------------------------------############################
index_name = st.secrets["index_name"]
index_api_key = st.secrets["index_api_key"]
index_environment = st.secrets["index_environment"]

#pinecone.init(api_key=index_api_key, environment=index_environment)
pc = Pinecone(api_key=index_api_key)
#self.pinecone = pinecone.Pinecone(api_key=index_api_key)
index = pc.Index(index_name)

##******----------------------velux index------------------------*********##

# pinecone.init(api_key="89c890aa-ead7-4c56-93d4-57968c3698c2", environment="asia-southeast1-gcp-free")
# index = pinecone.Index("velux-index-1")

# pinecone.init(api_key=st.secrets["index_api_key"], environment=st.secrets["index_environment"])
# index = pinecone.Index(st.secrets["index_name"])

### ************ Novartis Pinecone env details **********

# pinecone.init(api_key="312f1c16-1f6f-48ea-983a-f0a7b76a29ea", environment="gcp-starter")
# index = pinecone.Index("novartis-index")
##

#directory = 'D:\Rohit\Adobe\GenAI\chat-ui-app\content'


def init_pinecone(selected_index):
    print("pinecode2",selected_index)
    print(selected_index)
    if(selected_index != "--select index--"):
        vector_databases = st.secrets["vector-databases"]
        key = st.secrets[selected_index+"_api_key"]
        env = st.secrets[selected_index+"_environment"]
      
        #pinecone.init(api_key=index_api_key, environment=index_environment)
        pc = Pinecone(api_key=key)
        index = pc.Index(selected_index)

###########-----------------------------query index--------------------------------############################

def find_match(query):
    print("-------------changed---------------")
    docs,res = find_match_private(query,2)
    context= "\n\n".join(res)
    return context

def find_match_private(query,k):
    query_em = model.encode(query).tolist()
    #print(query_em)
    result = index.query(vector=query_em, top_k=k, includeMetadata=True)
    #print("index is ----- ",index_api_key)
    #print("result --",result)
    return [result['matches'][i]['metadata']['title'] for i in range(k)],[result['matches'][i]['metadata']['context'] for i in range(k)]


###########-----------------------------add content to index--------------------------------############################

def get_html_content(url):
    print("Getting HTML content for the URLL")
    headers = requests.utils.default_headers()
    headers.update(
     {
       'User-Agent': 'Chrome/114.0.5735.199'
     }
    )
    req = requests.Session()
    response = req.get(url, headers=headers, timeout=1000)
    #response = requests.get(url)

    print("-----response for url---------"+url)
    print(response.status_code)
    
    return response.content

def get_plain_text(html_content):
    print("Getting plaint text from the HTML content for the URL")
    soup = BeautifulSoup(html_content, 'html.parser')
    for script in soup(["script"]):
        script.extract()
    text = soup.get_text()
    print("URL content : "+text)
    return text

def split_text_into_chunks(plain_text, max_chars=2000):
    print("Splitting plain text in to chunks")
    text_chunks = []
    current_chunk = ""
    for line in plain_text.split("\n"):
        if len(current_chunk) + len(line) + 1 <= max_chars:
            current_chunk += line + " "
        else:
            text_chunks.append(current_chunk.strip())
            current_chunk = line + " "
    if current_chunk:
        text_chunks.append(current_chunk.strip())
    #print(text_chunks)
    return text_chunks

def scrape_text_from_url(url, max_chars=2000):
    print("URL to scrape is :: "+url)
    url = url.strip()
    html_content = get_html_content(url)
    plain_text = get_plain_text(html_content)
    ##plain_text = scrape_url(url)
    text_chunks = split_text_into_chunks(plain_text, 2000)
    #print(text_chunks)
    return text_chunks

def add_chunks_to_index(url):
    try:
        return addData(scrape_text_from_url(url),url)
    except Exception as e:
        # Handle the exception
        print("An error occurred:", e)
        return "failure"
    return "success"
##
# index data to Pincecone vector database
##
def addData(corpusData,url):
    id = index.describe_index_stats()['total_vector_count']
    for i in range(len(corpusData)):
        chunk=corpusData[i]
        chunkInfo=(str(id+i),
                model.encode(chunk).tolist(),
                {'title': url,'context': chunk})
        if(i == 0):
            print(chunkInfo)
        index.upsert(vectors=[chunkInfo])
    return "success"

###########-----------------------------add file content to index--------------------------------############################

def index_file_content(content, url):
    try:
        text_chunks = split_text_into_chunks(content)
        print("chunks length ")
        print(len(text_chunks))
        return addData(text_chunks,url)
    except Exception as e:
        # Handle the exception
        print("An error occurred:", e)
        return "failure"
    return "success"


##
# index documents to Pincecone vector database
# docsData[page_content,metadata[source]]
##
def addDocumentsData(docsData):
    id = index.describe_index_stats()['total_vector_count']
    for i in range(len(docsData)):
        chunk=docsData[i].page_content
        chunkInfo=(str(id+i),
                model.encode(chunk).tolist(),
                {'title': docsData[i].metadata['source'],'context': chunk})
        if(i == 5):
            print(chunkInfo)
        index.upsert(vectors=[chunkInfo])
    return "success"
##
# load documents from Directory
# documents[Document(page_content,metadata['source'])]
##
def load_docs(directory):
  print("inside load docs")
  loader = DirectoryLoader(directory)
  documents = loader.load()
  return documents

def delete_all_vectors():
    index.delete(delete_all=True, namespace='')

#delete_all_vectors()
#documents = load_docs(directory)
# print(len(documents))
# print(documents)

##
# split the documents into chunks
##
def split_docs(documents,chunk_size=2000,chunk_overlap=50):
  print("inside split docs")
  text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
  docs = text_splitter.split_documents(documents)
  return docs

# docs = split_docs(documents)

# addDocumentsData(docs)

# for doc in docs:
#    print(doc.metadata['source'])


# print(len(docs))
# print("----------------------------------------------")
# print(docs[3])
# print("-----------------content---------------------------")
# print(docs[3].page_content)
# print("-----------------metadata---------------------------")
# print(docs[3].metadata['source'])