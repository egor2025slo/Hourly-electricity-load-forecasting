FROM python:3.9-slim

# exclude unnecessary files from the image
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# working directory inside the container
WORKDIR /app

# copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# all source code
COPY . .

# expose port 8000 for the FastAPI app
EXPOSE 8000

# run the app with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
