import asyncio
from openai import AsyncOpenAI
import os
import argparse
import time
import statistics

#MODEL="meta-llama/Llama-3.2-3B"


async def get_request(api_endpoint: str, prompt: str, model: str):
    if api_endpoint == 'completions':
        response = await client.completions.create(
                            model=model,
                            prompt=prompt
                            )
        return prompt, response 
    elif api_endpoint == 'embeddings':
        response = await client.embeddings.create(
                            input=prompt,
                            model=model,
                            )
        return prompt, response
    else:
        raise ValueError("Invalid API endpoint specified")

def get_prompts(filename, system_prompt_filename):
    #get system prompt if any
    if system_prompt_filename != '':
        if not os.path.exists(system_prompt_filename):
            parser.error(f"The system prompt file {system_prompt_filename} does not exist!")
        with open(system_prompt_filename, 'r') as iff:
            system_prompt = iff.read().strip() + ' '
    else:
        system_prompt = ''

    #get prompts
    if not os.path.exists(args.filename):
        parser.error(f"The prompts file {args.filename} does not exist!")
    with open(filename, 'r') as iff:
        return [system_prompt+x.strip() for x in iff.readlines()]

def generate_n(seq: [], n: int) -> []:
    ''' generates n items from a sequence, replicating items as necessary '''
    if n <= len(seq):
        n_seq = seq[:n]
    else:
        full_seq = seq * math.ceil(n/len(seq))
        n_seq = full_seq[:n]
    assert len(n_seq) == n
    return n_seq

async def main(args):
    prompts = get_prompts(args.filename, args.system_prompt_filename)
    #by default, send all requests, otherwise use specified num_requests
    if args.num_requests != None:
        prompts = generate_n(prompts, args.num_requests)

    start_time = time.time()
    tasks = [get_request(args.api_endpoint, prompt, args.model) for prompt in prompts]
    results = await asyncio.gather(*tasks)
    end_time = time.time()
    print(f"Example result: {results[0]}")
    prompt_token_counts = []

    if args.api_endpoint == 'completions':
        #report completion throughput metrics
        completion_token_counts = []
        for result in results:
            completion_token_counts.append(result[1].usage.completion_tokens)
            prompt_token_counts.append(result[1].usage.prompt_tokens)
        total_time = end_time - start_time
        print(f"total time: {total_time}")
        print(f"Prompt tokens/sec: {sum(prompt_token_counts)/total_time}")
        print(f"Completion tokens/sec: {sum(completion_token_counts)/total_time}")
        print(f"Combined tokens/sec: {(sum(completion_token_counts)+sum(prompt_token_counts))/total_time}")
        print(f"Completions requests/sec: {len(results)/total_time}")

        #report dataset metrics
        print(f"Median prompt length: {statistics.median(prompt_token_counts)}")
        print(f"Median completion length: {statistics.median(completion_token_counts)}")

    elif args.api_endpoint == 'embeddings':
        #report embeddings throughput metrics
        for result in results:
            prompt_token_counts.append(result[1].usage.prompt_tokens)
        total_time = end_time - start_time
        print(f"Embeddings requests/sec: {len(results)/total_time}")
        print(f"Embeddings prompt tokens/sec: {sum(prompt_token_counts)/total_time}")
        print(f"Median prompt length: {statistics.median(prompt_token_counts)}")



#get args
parser = argparse.ArgumentParser(description='Send prompts to OpenAI API server')
parser.add_argument('--filename', help='Input filename, one prompt per line', required=True)
parser.add_argument('--num_requests', help='Number of prompt requests to send; default is all', type=int)
parser.add_argument('--model', help='Name of model to use, following HuggingFace naming', required=True)
parser.add_argument('--base_url', help='Base URL to send API requests to', required=True)
parser.add_argument('--api_token', help='API token for authorization', default="None")
parser.add_argument('--api_endpoint', help='API endpoint to send requests to; default is completions', choices=['completions', 'embeddings'], default='completions')
parser.add_argument('--system_prompt_filename', help='Filename with additional message to prepend to each prompt such as instructions', default='')

args = parser.parse_args()

#add trailing '/' to endpoint if user does not supply it
if not args.base_url.endswith("/"):
    args.base_url = args.base_url+"/"

#create OpenAI client
client = AsyncOpenAI(api_key=args.api_token,
                     base_url=args.base_url)

#send API requests
asyncio.run(main(args))
