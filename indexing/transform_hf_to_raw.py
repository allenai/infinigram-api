import datasets
import json
import os

# output_dir = '/weka/oe-training-default/jiachengl/raw'
output_dir = './raw'

ds_name = 'tulu-v3.1-mix-preview-4096-OLMoE'
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

ds_name = 'ultrafeedback_binarized_cleaned'
ds = datasets.load_dataset(f'allenai/{ds_name}', split='train_prefs')
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
