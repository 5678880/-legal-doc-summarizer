FROM python:3.10-slim

# System dependencies
RUN apt-get update && apt-get install -y \
    git curl libgl1 ghostscript poppler-utils tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama


# Expose Ollama + Streamlit ports
EXPOSE 11434
EXPOSE 8501

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code
WORKDIR /app
COPY . .

# Run Ollama in background, then start app
CMD ollama serve & streamlit run app.py --server.port=8501 --server.enableCORS false
