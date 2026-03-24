FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Make the 'pair' command available in the container
RUN printf '#!/bin/sh\nexec python -m ecobee-exporter pair "$@"\n' > /usr/local/bin/pair && \
    chmod +x /usr/local/bin/pair

EXPOSE 9101

CMD ["python", "-m", "ecobee_exporter", "run"]
