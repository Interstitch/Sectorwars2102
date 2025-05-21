FROM python:3.11

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app/

# Add executable permission to the scripts
RUN chmod +x /app/setup_admin.py
RUN chmod +x /app/start.sh

# Keep the container running with the start script
CMD ["sh", "-c", "python /app/setup_admin.py && /app/start.sh"]
