# autogpt
# Restaurant Recommendation Chatbot

## Overview

This project implements a chatbot for restaurant recommendations. The chatbot utilizes OpenAI's GPT-3.5 language model for natural language processing and incorporates a restaurant recommendation tool based on user input.

## Features

- Interactive chat with the chatbot to find the best restaurant recommendations.
- Utilizes OpenAI's GPT-3.5 for generating responses.
- Restaurant recommendation tool to suggest top restaurants based on user input.
- Data vectorization using text embeddings for efficient processing.
- Scraping and processing restaurant data from a website.

## Project Structure

- `main.py`: Main script to run the chatbot and interact with the OpenAI API.
- `web_scraping.py`: Module for scraping restaurant data from a website.
- `output/`: Directory to store chat history files.
- `data/`: Directory to store processed restaurant data.

## Setup

1. Install dependencies: `pip install openai pandas scipy beautifulsoup4`.
2. Obtain OpenAI API key and set it as an environment variable (e.g., `export OPENAI_API_KEY=<your-api-key>`).
3. Run the `main.py` script.

## Usage

1. Run the `main.py` script.
2. Interact with the chatbot by entering user inputs.
3. Follow the chatbot's instructions to find restaurant recommendations.
4. The chat history is saved in the `output/` directory.

## Additional Notes

- Ensure proper internet connectivity for accessing the OpenAI API.
- Customize the `web_scraping.py` module based on the website structure.
- Adapt the code for specific use cases or integrate additional features.

## Author

[Clara Adam]

