# README.md

This project sends chat prompts to an OpenAI API generate endpoint, enabling batch processing of multiple requests.

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
python async_api.py --filename prompts.txt --num_requests 10 --models model1 model2 --base_url https://your/server/api --randomize_models False --api_token $API_TOKEN 
```

Arguments:\
--filename - Path to file with prompts, one prompt per line\
--num_requests - Number of requests to send, defaults to all
--models - Model names, one or more models must be specified\
--base_url - Base URL of OpenAI API compliant server\
--randomize_models - Whether or not use random model from list for each request\
--api-token - JWT token for auth header
