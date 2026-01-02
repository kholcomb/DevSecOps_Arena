FROM python:3.11-slim

WORKDIR /app

# Install Flask
RUN pip install --no-cache-dir flask

# Copy application
COPY app.py .

# Expose port
EXPOSE 5000

# Run application
CMD ["python", "app.py"]
