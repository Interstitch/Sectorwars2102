FROM python:3.11

WORKDIR /app

# Install Poetry
RUN pip install poetry

# Configure Poetry: Don't create virtual environment, install dependencies globally
RUN poetry config virtualenvs.create false

# Copy Poetry files
COPY pyproject.toml poetry.lock* /app/

# Install all dependencies including dev for testing
RUN poetry install --no-root

COPY . /app/

# Add executable permission to the scripts
RUN chmod +x /app/setup_admin.py
RUN chmod +x /app/start.sh

# Keep the container running with the start script - but handle failures gracefully
CMD ["sh", "-c", "echo 'Starting gameserver...' && (python /app/setup_admin.py || echo 'Admin setup failed, continuing...') && /app/start.sh"]
