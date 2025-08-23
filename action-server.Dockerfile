# In Dockerfile.actions
FROM rasa/rasa-sdk:latest

WORKDIR /app

# Tell Python to look for modules in the /app directory
ENV PYTHONPATH=/app

# Copy ALL project files into the container
COPY . .

# Switch to the root user to install packages
USER root

# Install python dependencies
RUN pip install -r requirements.txt

# Switch back to the default user
USER 1001

# Start the action server
CMD ["start", "--actions", "actions"]