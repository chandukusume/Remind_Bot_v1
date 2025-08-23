# In Dockerfile.actions
FROM rasa/rasa-sdk:latest

WORKDIR /app

# Tell Python to look for modules in the /app directory
ENV PYTHONPATH=/app

COPY requirements.txt .

# Switch to the root user to install packages
USER root

# Install python dependencies
RUN pip install -r requirements.txt

# Switch back to the default user
USER 1001

# Copy your custom action code
COPY actions /app/actions

CMD ["start", "--actions", "actions"]