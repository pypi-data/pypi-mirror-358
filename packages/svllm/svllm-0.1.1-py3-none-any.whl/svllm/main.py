#!/usr/bin/env python3

import sys, argparse, importlib, svllm, uvicorn
from termcolor import colored

def import_from(location: str, name: str):
    module_str, _, attrs_str = location.partition(':')
    if not module_str:
        raise ValueError(f'{name} must be in the format \'module:attr\'.')
    instance = importlib.import_module(module_str)
    for attr in (attrs_str or name).split('.'):
        instance = getattr(instance, attr, None)
    if not instance:
        raise ImportError(f'\'{attrs_str or name}\' not found in \'{module_str}\'')
    return (instance, f'{module_str}:{attrs_str or name}')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--chat', type=str, required=False, help='chat function')
    parser.add_argument('--complete', type=str, required=False, help='complete function')
    parser.add_argument('--embed', type=str, required=False, help='embed function')

    parser.add_argument('--prefix', type=str, default='/v1', required=False, help='api prefix')
    parser.add_argument('--host', type=str, default='127.0.0.1', required=False, help='host address')
    parser.add_argument('--port', type=int, default=5261, required=False, help='port number')
    parser.add_argument('--quiet', action='store_true', help='suppress output')

    cmd_args = parser.parse_args()
    sys.path.insert(0, '.')

    def log(message: str, error = False):
        if not cmd_args.quiet:
            color: str = 'red' if error else 'green'
            print(colored('SVLLM', color) + f':    {message}')

    if cmd_args.chat:
        chat, location = import_from(cmd_args.chat, 'chat')
        svllm.base.set_chat(chat)
        log(f'Chat function set to ' + colored(location, 'yellow'))

    if cmd_args.complete:
        complete, location = import_from(cmd_args.complete, 'complete')
        svllm.base.set_complete(complete)
        log(f'Complete function set to ' + colored(location, 'yellow'))

    if cmd_args.embed:
        embed, location = import_from(cmd_args.embed, 'embed')
        svllm.base.set_embed(embed)
        log(f'Embed function set to ' + colored(location, 'yellow'))

    log_level = 'warning' if cmd_args.quiet else 'info'
    app = svllm.create_app(prefix=cmd_args.prefix)
    uvicorn.run(app, host=cmd_args.host, port=cmd_args.port, log_level=log_level)

if __name__ == "__main__":
    main()
