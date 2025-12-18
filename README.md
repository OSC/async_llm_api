# README.md

This project sends chat prompts to an OpenAI API completions endpoint, enabling batch processing of multiple requests.\
It is intended as example code and meant to be extended for your specific uses.

## Installation
1. Install uv
   - `pip install uv`
2. Create an environment
   - `uv venv`
3. Activate environment
   - `source .venv/bin/activate`
4. In activated environment, install requirements
   - `pip install -f requirements.txt`

## Usage
```
python openai_async.py --filename prompts.txt --num_requests 10 --model modelname --base_url https://your/server/v1/ --api_token $API_TOKEN 
```

Arguments:\
--filename - Path to file with prompts, one prompt per line\
--num_requests - Number of requests to send, defaults to all\
--model - Model name, must be specified\
--base_url - Base URL of OpenAI API compliant server. E.g., https://localhost:$API_PORT/v1/ \
--api-token - JWT token for auth header
