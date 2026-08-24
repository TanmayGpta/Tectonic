# Use official lightweight Python image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first (for caching)
COPY requirements.txt ./

# Install dependencies (ignoring errors if requirements.txt is missing/incomplete)
RUN pip install --no-cache-dir -r requirements.txt || true

# Explicitly install all the required libraries for our pipeline
RUN pip install streamlit beautifulsoup4 chromadb requests langgraph langchain-core pydantic docker

# Copy the rest of the application code into the container
COPY . .

# Expose the port Streamlit runs on
EXPOSE 8501

# Command to run the Streamlit dashboard
CMD ["streamlit", "run", "demo_streamlit_rag.py", "--server.address=0.0.0.0"]
