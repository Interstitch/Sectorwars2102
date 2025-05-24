FROM python:3.11

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app/

# Add executable permission to the scripts
RUN chmod +x /app/setup_admin.py
RUN chmod +x /app/start.sh

# Keep the container running with the start script - but handle failures gracefully
CMD ["sh", "-c", "echo 'Starting gameserver...' && (python /app/setup_admin.py || echo 'Admin setup failed, continuing...') && /app/start.sh"]
