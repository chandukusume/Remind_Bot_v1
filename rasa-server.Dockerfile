# In rasa-server.Dockerfile
FROM rasa/rasa:latest-full

# Copy your entire project into the container 
WORKDIR /app
COPY . .

# Install Python dependencies
RUN pip install -r requirements.txt

# Expose the port Rasa will run on 
EXPOSE 5005

# Command to run when the container starts
CMD ["run", "--enable-api", "--cors", "*", "--credentials", "credentials.yml", "--endpoints", "endpoints.yml", "--connector", "telegram"]