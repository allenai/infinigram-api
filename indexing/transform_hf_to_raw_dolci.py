import datasets
import json
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--output_dir', type=str, default='/data_c/raw')
args = parser.parse_args()

# Base output directory
output_dir = args.output_dir

# Datasets to index
ds_names = [
    'allenai/Dolci-Think-SFT-7B',
    'allenai/Dolci-Think-SFT-32B',
    'allenai/Dolci-Instruct-SFT-7B'
]

for ds_path in ds_names:
    print(f"Processing {ds_path}...")
    try:
        ds = datasets.load_dataset(ds_path, split='train')
    except Exception as e:
        print(f"Failed to load {ds_path}: {e}")
        continue

    # Use the last part of the name for the directory
    short_name = ds_path.split('/')[-1]
    os.makedirs(f'{output_dir}/{short_name}', exist_ok=True)
    
    # Write to 0.jsonl
    with open(f'{output_dir}/{short_name}/0.jsonl', 'w') as f:
        for item in ds:
            text = ''
            if 'messages' in item:
                for message in item['messages']:
                    role = message['role']
                    content = message['content']
                    if content is None:
                        content = ''
                    # assert role in ['user', 'assistant', 'system']
                    text += '\n' + f'<|{role}|>' + '\n' + content
            else:
                # Fallback or error if structure is different
                print(f"Warning: 'messages' key not found in {ds_path}")
                continue
                
            text = text.lstrip('\n')
            f.write(json.dumps({'text': text, 'source': short_name}) + '\n')

print("Done.")

