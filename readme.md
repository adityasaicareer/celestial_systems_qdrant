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
The above Code was used to split the loaded document each with 500 Characters and 100 characters overlap with the Previous chunk to avoid Information loss


