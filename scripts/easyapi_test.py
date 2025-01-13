import easyapi
import time
import os

# export EASY_URL=http://neptune-cs-aus-267.reviz.ai2.in:5000
api = easyapi.Api()
model_name = 'Qwen/Qwen2-7B-Instruct'
hf_token = os.environ.get('HF_TOKEN', '') # only needed if your model needs it
if not api.has_model(model_name):
    api.launch_model(model_name, gpus=1, hf_token=hf_token) # launch on jupiter

while not api.has_model(model_name): time.sleep(5)

prompt = "Barack Obama was born in"
r = api.generate(prompt, model=model_name, temp=0.1, max_tokens=256)
print(r)
