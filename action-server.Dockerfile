# In Dockerfile.actions
FROM rasa/rasa-sdk:latest

WORKDIR /app

# Copy all files
COPY . .

# Install Python dependencies
RUN pip install -r requirements.txt

# Expose the port the action server runs on
EXPOSE 5055

# Command to run when the container starts
CMD ["run", "actions"]