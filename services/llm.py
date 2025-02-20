from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import UnstructuredFileLoader
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from typing import List, Dict, Any
import os

class LLMService:
    def __init__(self):
        self.llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0.7,
            api_key=os.getenv('OPENAI_API_KEY')
        )
        self.embeddings = OpenAIEmbeddings(
            api_key=os.getenv('OPENAI_API_KEY')
        )
        
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for a list of texts"""
        return self.embeddings.embed_documents(texts)
    
    def process_document(self, file_path: str) -> List[str]:
        """Process a document and split it into chunks"""
        loader = UnstructuredFileLoader(file_path)
        documents = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        return text_splitter.split_documents(documents)
    
    def create_vector_store(self, documents: List[str], collection_name: str) -> Chroma:
        """Create a vector store from documents"""
        return Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            collection_name=collection_name
        )
    
    def create_qa_chain(self, vector_store: Chroma) -> ConversationalRetrievalChain:
        """Create a conversational QA chain"""
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        return ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=vector_store.as_retriever(),
            memory=memory
        )
    
    def chat(self, message: str, context: Dict[str, Any] = None) -> str:
        """Simple chat completion"""
        response = self.llm.predict(message)
        return response
