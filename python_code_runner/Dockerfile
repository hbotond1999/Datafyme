FROM python:3.11-slim

# Set working directory in the container
WORKDIR /app

# Copy requirements.txt to the working directory
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code to the working directory
COPY . .

EXPOSE 8050

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8050"]
