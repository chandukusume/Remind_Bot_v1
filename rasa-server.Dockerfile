# In Dockerfile.rasa
FROM rasa/rasa:latest-full

WORKDIR /app

COPY . .

# Switch to the root user to install packages
USER root

RUN pip install -r requirements.txt

# Switch back to the default user
USER 1001

# The CMD line now includes the Telegram connector
CMD ["run", "--enable-api", "--cors", "*", "--credentials", "credentials.yml", "--endpoints", "endpoints.yml", "--connector", "telegram"]