# We use rasa:latest-full because it contains everything needed 
# to run both the full server and the actions SDK.
FROM rasa/rasa:latest-full

# Set the working directory
WORKDIR /app

# Copy all your project files into the container
COPY . .

# Install all Python dependencies from a single requirements file
RUN pip install -r requirements.txt

# Copy and make the new startup script executable
COPY run.sh .
RUN chmod +x ./run.sh

# The final command that starts everything!
CMD ["./run.sh"]