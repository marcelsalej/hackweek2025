# Use a slim Python base image
FROM python:3.11-slim


# Set working directory
WORKDIR /app

# Ensure Python prints logs right away
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# Install any needed dependencies (adjust this as needed)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN chown -R 1000:1000 /app

# Run the CLI entry point
CMD ["python", "agent_cli.py"]