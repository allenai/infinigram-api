import datasets
import json
import os

output_dir = '/weka/oe-training-default/jiachengl/he-infinigram-api/raw'

# SFT
ds_names = ['tulu-3-sft-mixture']
for ds_name in ds_names:
    ds = datasets.load_dataset(f'allenai/{ds_name}', split='train')
    os.makedirs(f'{output_dir}/{ds_name}', exist_ok=True)
    with open(f'{output_dir}/{ds_name}/0.jsonl', 'w') as f:
        for item in ds:
            text = ''
            for message in item['messages']:
                assert message['role'] in ['user', 'assistant', 'system']
                text += '\n' + f'<|{message["role"]}|>' + '\n' + message['content']
            text = text.lstrip('\n')
            f.write(json.dumps({'text': text, 'source': ds_name}) + '\n')

# DPO
ds_names = ['llama-3.1-tulu-3-8b-preference-mixture', 'llama-3.1-tulu-3-70b-preference-mixture', 'llama-3.1-tulu-3-405b-preference-mixture']
for ds_name in ds_names:
    ds = datasets.load_dataset(f'allenai/{ds_name}', split='train')
    os.makedirs(f'{output_dir}/{ds_name}', exist_ok=True)
    with open(f'{output_dir}/{ds_name}/0.jsonl', 'w') as f:
        for item in ds:
            text = ''
            for message in item['chosen']:
                assert message['role'] in ['user', 'assistant']
                text += '\n' + f'<|{message["role"]}|>' + '\n' + message['content']
            text = text.lstrip('\n')
            f.write(json.dumps({'text': text, 'source': ds_name}) + '\n')

            text = ''
            for message in item['rejected']:
                assert message['role'] in ['user', 'assistant']
                text += '\n' + f'<|{message["role"]}|>' + '\n' + message['content']
            text = text.lstrip('\n')
            f.write(json.dumps({'text': text, 'source': ds_name}) + '\n')

# RLVR
ds_names = ['RLVR-MATH']
for ds_name in ds_names:
    ds = datasets.load_dataset(f'allenai/{ds_name}', split='train')
    os.makedirs(f'{output_dir}/{ds_name}', exist_ok=True)
    with open(f'{output_dir}/{ds_name}/0.jsonl', 'w') as f:
        for item in ds:
            text = ''
            for message in item['messages']:
                assert message['role'] in ['user']
                text += '\n' + f'<|{message["role"]}|>' + '\n' + message['content']
            text = text.lstrip('\n')
            f.write(json.dumps({'text': text, 'source': ds_name}) + '\n')
