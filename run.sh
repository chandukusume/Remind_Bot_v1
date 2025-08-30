#!/bin/bash

# This ensures background processes are killed when the script exits
trap 'kill $(jobs -p)' EXIT

# Start your specific Rasa server command in the background.
# NOTE: The port is changed to 7860 for Hugging Face's default web preview.
rasa run --enable-api --cors "*" --credentials credentials.yml --endpoints endpoints.yml --connector telegram --port 7860 &

# Start the action server in the foreground to keep the container running.
rasa run actions