# Suggested base image 
FROM python:3.9-slim

WORKDIR /app

# Install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Include data.csv and config.yaml in container [cite: 85]
COPY run.py config.yaml data.csv ./

# Command to ensure docker run --rm mlops-task works exactly as requested [cite: 83]
# and produces metrics.json and run.log [cite: 86]
CMD ["python", "run.py", "--input", "data.csv", "--config", "config.yaml", "--output", "metrics.json", "--log-file", "run.log"]