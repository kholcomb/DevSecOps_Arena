FROM python:3.11-slim

WORKDIR /app

# Install Flask
RUN pip install --no-cache-dir flask

# Copy application
COPY app.py .
COPY init_db.py .

# Initialize database
RUN python init_db.py

# Expose port
EXPOSE 5000

# Run application
CMD ["python", "app.py"]
