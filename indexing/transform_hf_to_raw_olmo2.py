import datasets
import json
import os

output_dir = '/weka/oe-training-default/jiachengl/he-infinigram-api/raw'

# SFT
# ds_names = ['tulu-3-sft-olmo-2-mixture', 'tulu-3-sft-olmo-2-mixture-0225']
ds_names = ['tulu-3-sft-olmo-2-mixture-0225']
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
# ds_names = ['olmoe-0125-1b-7b-preference-mix', 'olmo-2-1124-13b-preference-mix', 'olmo-2-0325-32b-preference-mix']
ds_names = ['olmoe-0125-1b-7b-preference-mix', 'olmo-2-0325-32b-preference-mix']
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
# ds_names = ['RLVR-GSM', 'RLVR-GSM-MATH-IF-Mixed-Constraints']
ds_names = ['RLVR-GSM']
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
