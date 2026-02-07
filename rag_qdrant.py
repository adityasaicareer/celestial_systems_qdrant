from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams,Distance,PointStruct
import re
import pprint


filepath="./example.pdf"

loader=PyPDFLoader(filepath)
print(loader)

docs=loader.load()

""" we use the RecursiveCharacterTextSplitter to maintain the context and paragraphs intact"""

text_splitter=RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=100)

chunks=text_splitter.split_documents(docs)

for idx,chunk in enumerate(chunks):
  chunk.metadata["chunk_id"]=idx


embedings=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

texts=[chunk.page_content for chunk in chunks]
metadata=[chunk.metadata for chunk in chunks]
ids=[str(chunk.metadata["chunk_id"]) for chunk in chunks]
vectors=embedings.embed_documents(texts)

client=QdrantClient(path="./vectordb/qdrant")
client.recreate_collection(
  collection_name="ragdata",
  vectors_config=VectorParams(
    size=384,
    distance=Distance.COSINE
  )
)
vectors=embedings.embed_documents(texts)
points=[]
for chunk,vector in zip(chunks,vectors):
  points.append(
    PointStruct(
      id=chunk.metadata["chunk_id"],
      vector=vector,
      payload={
        "text":chunk.page_content,
        **chunk.metadata
      }
    )
  )


client.upsert(
  collection_name="ragdata",
  points=points
)

info=client.get_collection("ragdata")
print(info.points_count)

query="What are the requirements for establishing and communicating the information security policy?"

topk=5

query_embeding=embedings.embed_query(query)
results=client.query_points(
  collection_name="ragdata",  
  query=query_embeding,
  limit=topk
)
print("\n\n")
print(f"The Query :  {query}")

for index,i in enumerate(results.points):
  print("\n\n")
  print('-'*40)
  print(f"\nResult : {index+1}")
  print(f"\nChunk ID : {i.id}")
  print(f"\nChunk Content :{i.payload['text']}")

  print(f"\nScore : {i.score}")
  print(f"\nPage :{i.payload['page']}")
  print(f"\nSource : {i.payload['source']}")

client.close()

