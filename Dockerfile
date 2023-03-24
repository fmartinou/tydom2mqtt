FROM python:3.11-alpine3.17

# App base dir
WORKDIR /app

# Copy app
COPY /app .

# Install dependencies
RUN pip3 install -r requirements.txt

# Export OPENSSL_CONF with UnsafeLegacyRenegotiation enabled
ENV OPENSSL_CONF=./openssl_conf.cnf

# Main command
CMD [ "python", "-u", "main.py" ]