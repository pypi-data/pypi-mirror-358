#!/usr/bin/env python3

import argparse, os, json, httpx
from termcolor import colored

def get_request(base_url: str, key: str):
    headers = { 'Authorization': f'Bearer {key}' } if key else {}
    return httpx.Client(base_url=base_url, headers=headers, timeout=30)

def get_input():
    content = ''
    while not content.strip():
        content = input(colored('>>> ', 'green'))
    return content

chat_history: list[dict] = []

def run_chat(request: httpx.Client, model: str, stream = True, history = True):
    url = f'/chat/completions'

    messages = [{ 'role': 'user', 'content': get_input() }]
    if history:
        chat_history.extend(messages)
        messages = chat_history
    payload = { 'model': model, 'messages': messages, 'stream': stream }

    if not stream:
        content_text = ''
        response = request.post(url, json=payload)
        if response.status_code != 200:
            if history:
                chat_history.pop()
            print(colored(f'{json.dumps(response.json(), indent=2)}', 'red'))
            return

        data = response.json()
        if 'choices' in data and len(data['choices']) > 0:
            choice = data['choices'][0]
            if 'message' in choice and 'content' in choice['message']:
                content_text = choice['message']['content']
        print(content_text)
        if history:
            chat_history.append({ 'role': 'assistant', 'content': content_text })
        return

    with request.stream(method='POST', url=url, json=payload) as response:
        if response.status_code != 200:
            if history:
                chat_history.pop()
            body = ''.join([chunk for chunk in response.iter_lines()])
            print(colored(f'{json.dumps(json.loads(body), indent=2)}', 'red'))
            return

        content_text = ''
        for chunk in response.iter_lines():
            chunk = chunk.strip()
            if chunk.startswith('data:'):
                chunk = chunk[5:].strip()
            if not chunk or chunk == '[DONE]':
                continue
            data = json.loads(chunk)
            if not data.get('choices'):
                continue
            choice = data['choices'][0]
            if 'delta' in choice and 'content' in choice['delta']:
                content_text += choice['delta']['content']
                print(choice['delta']['content'], end='', flush=True)
        print()
        if history:
            chat_history.append({ 'role': 'assistant', 'content': content_text })

def run_completion(request: httpx.Client, model: str, stream = True):
    url = f'/completions'
    payload = { 'model': model, 'prompt': get_input(), 'stream': stream }

    if not stream:
        content_text = ''
        response = request.post(url, json=payload)
        if response.status_code != 200:
            print(colored(f'{json.dumps(response.json(), indent=2)}', 'red'))
            return

        data = response.json()
        if 'choices' in data and len(data['choices']) > 0:
            choice = data['choices'][0]
            if 'text' in choice:
                content_text = choice['text']
        print(content_text)
        return

    with request.stream(method='POST', url=url, json=payload) as response:
        if response.status_code != 200:
            body = ''.join([chunk for chunk in response.iter_lines()])
            print(colored(f'{json.dumps(json.loads(body), indent=2)}', 'red'))
            return
        for chunk in response.iter_lines():
            chunk = chunk.strip()
            if chunk.startswith('data:'):
                chunk = chunk[5:].strip()
            if not chunk or chunk == '[DONE]':
                continue
            data = json.loads(chunk)
            if not data.get('choices'):
                continue
            choice = data['choices'][0]
            if 'text' in choice:
                print(choice['text'], end='', flush=True)
        print()


def run_embed(request: httpx.Client, model: str):
    url = f'/embeddings'
    payload = { 'model': model, 'input': get_input() }

    response = request.post(url, json=payload)
    if response.status_code != 200:
        print(colored(f'{json.dumps(response.json(), indent=2)}', 'red'))
        return

    data = response.json()
    if 'data' in data and len(data['data']) > 0:
        embedding = data['data'][0].get('embedding')
        if embedding:
            print(embedding)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, required=False, help='model name')
    parser.add_argument('--chat', action='store_true', help='chat mode (default)')
    parser.add_argument('--complete', action='store_true', help='completion mode')
    parser.add_argument('--embed', action='store_true', help='embedding mode')
    parser.add_argument('--no-stream', action='store_true', help='no stream mode (chat/complete mode)')
    parser.add_argument('--no-history', action='store_true', help='no history (chat mode)')

    api_key = os.environ.get('SVLLM_API_KEY')
    parser.add_argument('--key', type=str, required=False, default=api_key, help='API key for authentication')
    parser.add_argument('base_url', type=str, nargs='?', default='http://127.0.0.1:5261/v1', help='base URL for the API')

    cmd_args = parser.parse_args()

    if not cmd_args.chat and not cmd_args.complete and not cmd_args.embed:
        cmd_args.chat = True
    if not cmd_args.model:
        cmd_args.model = 'svllm-chat' if cmd_args.chat else \
                         'svllm-complete' if cmd_args.complete else \
                         'svllm-embed'

    request = get_request(cmd_args.base_url, cmd_args.key)
    if cmd_args.chat:
        print(colored(f'Chat mode with model: {cmd_args.model}', 'blue'))
        while True:
            try:
                run_chat(request, cmd_args.model, not cmd_args.no_stream, not cmd_args.no_history)
            except KeyboardInterrupt:
                print(colored('\nExiting chat mode.', 'red'))
                break
    elif cmd_args.complete:
        print(colored(f'Completion mode with model: {cmd_args.model}', 'blue'))
        while True:
            try:
                run_completion(request, cmd_args.model, not cmd_args.no_stream)
            except KeyboardInterrupt:
                print(colored('\nExiting completion mode.', 'red'))
                break
    elif cmd_args.embed:
        print(colored(f'Embedding mode with model: {cmd_args.model}', 'blue'))
        while True:
            try:
                run_embed(request, cmd_args.model)
            except KeyboardInterrupt:
                print(colored('\nExiting embedding mode.', 'red'))
                break

if __name__ == "__main__":
    main()
