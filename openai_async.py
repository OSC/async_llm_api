import asyncio
from openai import AsyncOpenAI
import os
import argparse

#MODEL="meta-llama/Llama-3.2-3B"


async def get_completion(prompt: str, model: str):
    print(f"creating completion for model {model} and prompt {prompt}")
    response = await client.completions.create(
                        model=model,
                        prompt=prompt
                        )
    return prompt, response 

def get_prompts(filename):
    with open(filename, 'r') as iff:
        return [x.strip() for x in iff.readlines()]

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
    if not os.path.exists(args.filename):
        parser.error(f"The file {args.filename} does not exist!")
    prompts = get_prompts(args.filename)
    #by default, send all requests, otherwise use specified num_requests
    if args.num_requests != None:
        prompts = generate_n(prompts, args.num_requests)

    tasks = [get_completion(prompt, args.model) for prompt in prompts]
    results = await asyncio.gather(*tasks)
    for res in results:
        print(res)

#get args
parser = argparse.ArgumentParser(description='Send prompts to OpenAI API server')
parser.add_argument('--filename', help='Input filename, one prompt per line', required=True)
parser.add_argument('--num_requests', help='Number of prompt requests to send, default is all', type=int)
parser.add_argument('--model', help='Name of model to use', required=True)
parser.add_argument('--base_url', help='Base URL to send API requests to', required=True)
parser.add_argument('--api_token', help='API token for authorization')
args = parser.parse_args()

#add trailing '/' to endpoint if user does not supply it
if not args.base_url.endswith("/"):
    args.base_url = args.base_url+"/"

#create OpenAI client
client = AsyncOpenAI(api_key=args.api_token,
                     base_url=args.base_url)

#send API requests
asyncio.run(main(args))
