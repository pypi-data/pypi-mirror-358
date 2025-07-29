# Stack Overflow for Teams for LangChain

This library provides a basic LangChain document loader for Stack Overflow for Teams.

## Document Loader Usage

### Get articles from Teams Basic or Business

```
from langchain_stack_overflow_for_teams import StackOverflowTeamsApiV3Loader

loader = StackOverflowTeamsApiV3Loader(
   access_token=os.environ.get("SO_PAT"),
   team="my team",
   content_type="articles",
)
docs = loader.load()
```

### Get questions with answers from Teams Basic or Business

```
from langchain_stack_overflow_for_teams import StackOverflowTeamsApiV3Loader

loader = StackOverflowTeamsApiV3Loader(
   access_token=os.environ.get("SO_PAT"),
   team="my team",
   content_type="questions",
)
docs = loader.load()
```

### Get articles from Teams Enterprise

```
from langchain_stack_overflow_for_teams import StackOverflowTeamsApiV3Loader

loader = StackOverflowTeamsApiV3Loader(
   endpoint="[your_site].stackenterprise.co/api",
   access_token=os.environ.get("SO_API_TOKEN"),
   content_type="articles",
)
docs = loader.load()
```

### Get articles from a private team in Teams Enterprise

```
from langchain_stack_overflow_for_teams import StackOverflowTeamsApiV3Loader

loader = StackOverflowTeamsApiV3Loader(
   endpoint="[your_site].stackenterprise.co/api",
   access_token=os.environ.get("SO_API_TOKEN"),
   team="my team",
   content_type="articles",
)
docs = loader.load()
```

### Full Example - Questions from Teams Enterprise

This example retrieves content from a Stack Overflow for Teams Enterprise site and loads it into a LanceDB vector store for access by an LLM-based system.

```
""" This script demonstrates use the Langchain add_documents model to naively load all documents every time (easy, but not efficient) """
import os
from dotenv import load_dotenv
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import LanceDB
from langchain_text_splitters import HTMLSemanticPreservingSplitter
from lib.stackoverflow.loader import StackOverflowTeamsApiV3Loader




def main():
   load_dotenv()


   embeddings = AzureOpenAIEmbeddings()
   db = LanceDB(
       table_name="docs",
       uri="./db/lancedb",
       embedding=embeddings,
   )


   # load documents
   loader = StackOverflowTeamsApiV3Loader(
       endpoint="[your_site].stackenterprise.co/api",
       access_token=os.environ.get("SO_API_TOKEN"),
       team="[your_team]",
       date_from="2021-05-01T00:00:00Z",
       sort="activity",
       order="desc",
       content_type="questions",
       is_answered="true",
       has_accepted_answer="true",
   )
   docs = loader.load()
   print(f"Loaded {len(docs)} documents")


   # chunk documents
   print("Chunking documents...")
   documents = HTMLSemanticPreservingSplitter(
       headers_to_split_on=[("h1", "Header 1"), ("h2", "Header 2")],
       max_chunk_size=1000,
       chunk_overlap=200,
       preserve_parent_metadata=True
   ).transform_documents(docs)
   print(f"Chunked {len(documents)} documents.")
   if len(documents) > 0:
       print(documents[0])


       # load embeddings into lancedb
       db.add_documents(documents)




if __name__ == "__main__":
   main()
```
