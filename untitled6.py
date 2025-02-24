# -*- coding: utf-8 -*-
"""Untitled6.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1DEm80vtCesUarEgZjQ1R7yR3_E0NZNNp
"""

import streamlit as st
import os
from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# 🔑 Fixed API Key (Or use Streamlit Secrets)
GOOGLE_API_KEY = "your-fixed-api-key-here"  # Replace with your actual key

# Streamlit UI
st.title("📄 AI PDF Q&A with Gemini Pro")

# Upload PDF
uploaded_file = st.file_uploader("📂 Upload a PDF", type=["pdf"])

if uploaded_file:
    with st.spinner("🔄 Processing PDF..."):
        # Save file temporarily
        temp_file_path = f"./temp_{uploaded_file.name}"
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.read())

        # Load PDF
        pdf_loader = PyPDFLoader(temp_file_path)  # Use saved file path
        pages = pdf_loader.load_and_split()

        # Prepare context
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
        context = "\n\n".join(str(p.page_content) for p in pages)
        texts = text_splitter.split_text(context)

        # Initialize Model & Embeddings
        model = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=GOOGLE_API_KEY, temperature=0.2)
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GOOGLE_API_KEY)

        # Create Vector Store
        vector_index = Chroma.from_texts(texts, embeddings).as_retriever(search_kwargs={"k": 5})

        # QA Chain
        qa_chain = RetrievalQA.from_chain_type(model, retriever=vector_index, return_source_documents=True)

        # User Question
        question = st.text_input("❓ Ask a question about the PDF")

        if st.button("🔍 Get Answer"):
            with st.spinner("🤖 Thinking..."):
                result = qa_chain({"query": question})
                st.write("💬 **Answer:**", result["result"])

        # Cleanup temporary file
        os.remove(temp_file_path)