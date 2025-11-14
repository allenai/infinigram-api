import transformers

tokenizer = transformers.AutoTokenizer.from_pretrained('allenai/dolma2-tokenizer', add_bos_token=False, add_eos_token=False)

token_to_id = tokenizer.get_vocab()

bow_token_ids = []
for token, token_id in token_to_id.items():
    # Ġ (U+120) marks the beginning of words
    if token[0] == 'Ġ':
        bow_token_ids.append(token_id)

bow_token_ids = sorted(bow_token_ids)

for token_id in bow_token_ids:
    print(token_id)