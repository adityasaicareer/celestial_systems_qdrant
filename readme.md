# Documentation for Qdrant Code

**Important:** This Code could run both in 3.11 and 3.14


Libraries Required:

```
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams,Distance,PointStruct
import re
import pprint
```

### The above were all Required Libraries

* langchain_community.document_loader import PyPDFLoader helps us to pase the pdf document.
* langchain_text_splitters import RecursiveCharacterTextSplitter helps to chunk the parsed data from documents.
* langchain_hugging_face import HuggingFaceEmbeddings helps us to use the embeding model sentence-transformers/all-MiniLM-L6-v2 
* qdrant_client import QdrantClient helps us to create and use the qdrant Vector DB
* qdrant_client.http.models import VectorParams,Distance,PointStruct helps us to configure the qdrant setup the Distance and get Vectorparams and PointStruct a structure of data to insert to Qdrant

### Loading the PDF Docuement 

```
filepath="./example.pdf"

loader=PyPDFLoader(filepath)
print(loader)

docs=loader.load()
```

### Chunking the Docuemnt

```
text_splitter=RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=100)

chunks=text_splitter.split_documents(docs)

for idx,chunk in enumerate(chunks):
  chunk.metadata["chunk_id"]=idx

```
The above Code was used to split the loaded document into chunks each with 500 Characters and 100 characters overlap with the Previous chunk to avoid Information loss and add the chunk index using for loop.


### Embedding Loading

```
embedings=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

texts=[chunk.page_content for chunk in chunks]
metadata=[chunk.metadata for chunk in chunks]
ids=[str(chunk.metadata["chunk_id"]) for chunk in chunks]
vectors=embedings.embed_documents(texts)

```

Loading the embeding model using the HuggingFace Library **sentence-transformers/all-MiniLM-L6-v2** Used to embed the Chunk which was an Industry Standard

Destructure the Document Chunks into Text,Metadata,Chunk Id and then producing the Vectors using HuggingFace model


### Creating the Qdrant Client and Preparing the Data to Insert

```
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

```

* The Above Code will create a Qdrant Client that will initiate the Qdrant Database 

* We create the Collection named **ragdata** and configure the collection with vector_config set the size for parameters to **384** and Store using the **COSINE** Function

* Prepare the All the Points to be inserted to the Qdrant using a PointStruct imported from qdrant_client.http.models including the vectors and metadata

### Insert the Data Into the QbridDB

```

client.upsert(
  collection_name="ragdata",
  points=points
)

info=client.get_collection("ragdata")
print(info.points_count)

```
we use the client.upsert to insert the data into the QubridDB and get_collection to have the info and metadata of data.








