import asyncio
import aiohttp #pip install aiohttp aiodns
import json
import random
import statistics
import math
import argparse
import os

async def fetch( session: aiohttp.ClientSession, prompt: str, models: [str], token: str, randomize_model: bool, **kwargs) -> dict:
    url = "generate"
    method = "POST"
    headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    if randomize_model:
        model = random.choice(models)
    else:
        model = models[0]
    data={"model": model, "prompt": prompt, "stream": "true"} #TODO make stream setting configurable

    resp = await session.request(method=method, 
                                 url=url, 
                                 headers=headers,
                                 json=data,
                                 **kwargs)
    data = await resp.read()
    if not data:
        return {}
    else:
        return data

async def main( prompts: [str], models: [str], base_url: str, token: str, randomize_model: bool, **kwargs):
    session_timeout =   aiohttp.ClientTimeout(total=None,sock_connect=300,sock_read=300)
    async with aiohttp.ClientSession(base_url=base_url, timeout=session_timeout) as session:
        tasks = []
        for p in prompts:
            tasks.append(fetch(session=session, prompt=p, models=models, token=token, randomize_model=randomize_model, **kwargs))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return parse_results(results)

def parse_results(results):
    parsed = ""
    total_durations = []
    eval_durations = []
    total_token_counts = []
    for result in results: #loop over requests
        if result != None: 
            json_strings = result.decode('utf-8').strip().split('\n')
            parsed_jsons = [json.loads(js) for js in json_strings] 
            result_words = []
            for json_item in parsed_jsons: #loop over streamed jsons
                #print(json_item)
                if json_item['done'] != True:
                    #accumulate word from non-final json
                    result_words.append(json_item['response'])
                elif json_item['done'] == True:
                    total_durations.append(json_item['total_duration'])  #example timing code
                    total_token_counts.append(json_item['eval_count'])
                    eval_durations.append(json_item['eval_duration'])
                #your code here
            print(f"Response: {"".join(result_words)}\n")

    #process timing info
    total_durations = [dur / (10**9) for dur in total_durations] 
    eval_durations = [dur / (10**9) for dur in eval_durations] 

    print(f"number of requests: {len(results)}")
    print(f"errors: {len(results)-len(total_durations)}")

    print(f"Total durations: {total_durations}")
    print(f"Mean total duration: {statistics.mean(total_durations)}")
    print(f"Median total duration: {statistics.median(total_durations)}")

    print(f"Eval durations: {eval_durations}")
    print(f"Mean eval duration: {statistics.mean(eval_durations)}")
    print(f"Median eval duration: {statistics.median(eval_durations)}")

    print(f"Total token counts: {total_token_counts}")
    print(f"Token throughput (user): {sum(total_token_counts) / float(statistics.mean(total_durations))} tokens/sec")
    print(f"Request throughput (user): {len(total_token_counts) / float(statistics.mean(total_durations))} requests/sec")
    print(f"Token throughput (eval only): {sum(total_token_counts) / float(statistics.mean(eval_durations))} tokens/sec")
    print(f"Request throughput (eval only): {len(total_token_counts) / float(statistics.mean(eval_durations))} requests/sec")
    

    return parsed 

def generate_n(seq: [], n: int) -> []:
    ''' generates n items from a sequence, replicating items as necessary '''
    if n <= len(seq):
        n_seq = seq[:n]
    else:
        full_seq = seq * math.ceil(n/len(seq))
        n_seq = full_seq[:n]
    assert len(n_seq) == n
    return n_seq

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Send prompts to OpenAI API server')
    parser.add_argument('--filename', help='Input filename, one prompt per line', required=True)
    parser.add_argument('--num_requests', help='Number of prompt requests to send, default is all', type=int)
    parser.add_argument('--models', nargs='+', help='Name of model(s) to use')
    parser.add_argument('--randomize_models', help='Use random model for each request', type=bool, default=False)
    parser.add_argument('--base_url', help='Base URL to send API requests to', required=True)
    parser.add_argument('--api_token', help='API token for authorization')
    args = parser.parse_args()

    #get prompts from file
    if not os.path.exists(args.filename):
        parser.error(f"The file {args.filename} does not exist!")

    with open(args.filename, 'r') as file:
        prompts = [line.strip() for line in file]

    #by default, send all requests, otherwise use specified num_requests
    if args.num_requests != None:
        prompts = generate_n(prompts, args.num_requests)
    
    asyncio.run(main(prompts, models=args.models, base_url=args.base_url, token=args.api_token, randomize_model=args.randomize_models))
