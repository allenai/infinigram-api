import gzip
import csv
import glob
from tqdm import tqdm

# Dolma3-dolmino-official prefixes
DOLMA3_DOLMINO_PREFIXES = [
    'code-meta-reasoning/',
    'common_crawl-high-quality_19_adult_content/',
    'common_crawl-high-quality_19_art_and_design/',
    'common_crawl-high-quality_19_crime_and_law/',
    'common_crawl-high-quality_19_education_and_jobs/',
    'common_crawl-high-quality_19_electronics_and_hardware/',
    'common_crawl-high-quality_19_entertainment/',
    'common_crawl-high-quality_19_fashion_and_beauty/',
    'common_crawl-high-quality_19_finance_and_business/',
    'common_crawl-high-quality_19_food_and_dining/',
    'common_crawl-high-quality_19_games/',
    'common_crawl-high-quality_19_health/',
    'common_crawl-high-quality_19_history_and_geography/',
    'common_crawl-high-quality_19_home_and_hobbies/',
    'common_crawl-high-quality_19_industrial/',
    'common_crawl-high-quality_19_literature/',
    'common_crawl-high-quality_19_politics/',
    'common_crawl-high-quality_19_religion/',
    'common_crawl-high-quality_19_science_math_and_technology/',
    'common_crawl-high-quality_19_social_life/',
    'common_crawl-high-quality_19_software/',
    'common_crawl-high-quality_19_software_development/',
    'common_crawl-high-quality_19_sports_and_fitness/',
    'common_crawl-high-quality_19_transportation/',
    'common_crawl-high-quality_19_travel_and_tourism/',
    'common_crawl-high-quality_20_adult_content/',
    'common_crawl-high-quality_20_art_and_design/',
    'common_crawl-high-quality_20_crime_and_law/',
    'common_crawl-high-quality_20_education_and_jobs/',
    'common_crawl-high-quality_20_electronics_and_hardware/',
    'common_crawl-high-quality_20_entertainment/',
    'common_crawl-high-quality_20_fashion_and_beauty/',
    'common_crawl-high-quality_20_finance_and_business/',
    'common_crawl-high-quality_20_food_and_dining/',
    'common_crawl-high-quality_20_games/',
    'common_crawl-high-quality_20_health/',
    'common_crawl-high-quality_20_history_and_geography/',
    'common_crawl-high-quality_20_home_and_hobbies/',
    'common_crawl-high-quality_20_industrial/',
    'common_crawl-high-quality_20_literature/',
    'common_crawl-high-quality_20_politics/',
    'common_crawl-high-quality_20_religion/',
    'common_crawl-high-quality_20_science_math_and_technology/',
    'common_crawl-high-quality_20_social_life/',
    'common_crawl-high-quality_20_software/',
    'common_crawl-high-quality_20_software_development/',
    'common_crawl-high-quality_20_sports_and_fitness/',
    'common_crawl-high-quality_20_transportation/',
    'common_crawl-high-quality_20_travel_and_tourism/',
    'cranecode/',
    'cranemath/',
    'dolmino-math/',
    'dolmino_1-flan/',
    'gemini-reasoning-traces/',
    'general_reasoning_mix/',
    'llama_nemotron-reasoning-traces/',
    'math-meta-reasoning/',
    'megamatt/',
    'nemotron-synth-qa/',
    'olmocr_science_pdfs-high_quality-art_design-2e12/',
    'olmocr_science_pdfs-high_quality-art_design-2e13/',
    'olmocr_science_pdfs-high_quality-crime_law-2e12/',
    'olmocr_science_pdfs-high_quality-crime_law-2e13/',
    'olmocr_science_pdfs-high_quality-education_jobs-2e12/',
    'olmocr_science_pdfs-high_quality-education_jobs-2e13/',
    'olmocr_science_pdfs-high_quality-entertainment-2e12/',
    'olmocr_science_pdfs-high_quality-entertainment-2e13/',
    'olmocr_science_pdfs-high_quality-finance_business-2e12/',
    'olmocr_science_pdfs-high_quality-finance_business-2e13/',
    'olmocr_science_pdfs-high_quality-hardware-2e12/',
    'olmocr_science_pdfs-high_quality-hardware-2e13/',
    'olmocr_science_pdfs-high_quality-health-2e12/',
    'olmocr_science_pdfs-high_quality-health-2e13/',
    'olmocr_science_pdfs-high_quality-history-2e12/',
    'olmocr_science_pdfs-high_quality-history-2e13/',
    'olmocr_science_pdfs-high_quality-home_hobbies-2e12/',
    'olmocr_science_pdfs-high_quality-home_hobbies-2e13/',
    'olmocr_science_pdfs-high_quality-industrial-2e12/',
    'olmocr_science_pdfs-high_quality-industrial-2e13/',
    'olmocr_science_pdfs-high_quality-literature-2e12/',
    'olmocr_science_pdfs-high_quality-literature-2e13/',
    'olmocr_science_pdfs-high_quality-politics-2e12/',
    'olmocr_science_pdfs-high_quality-politics-2e13/',
    'olmocr_science_pdfs-high_quality-religion-2e12/',
    'olmocr_science_pdfs-high_quality-religion-2e13/',
    'olmocr_science_pdfs-high_quality-science_tech-2e12/',
    'olmocr_science_pdfs-high_quality-science_tech-2e13/',
    'olmocr_science_pdfs-high_quality-software-2e12/',
    'olmocr_science_pdfs-high_quality-software-2e13/',
    'olmocr_science_pdfs-high_quality-software_dev-2e12/',
    'olmocr_science_pdfs-high_quality-software_dev-2e13/',
    'olmocr_science_pdfs-high_quality-sports_fitness-2e12/',
    'olmocr_science_pdfs-high_quality-sports_fitness-2e13/',
    'olmocr_science_pdfs-high_quality-transportation-2e12/',
    'olmocr_science_pdfs-high_quality-transportation-2e13/',
    'omr-rewrite-fullthoughts/',
    'openthoughts2-reasoning-traces/',
    'program_verifiable/',
    'qwq-reasoning-traces/',
    'reddit_to_flashcards/',
    'stack_edu-fim_vigintile_15_C/',
    'stack_edu-fim_vigintile_15_CSharp/',
    'stack_edu-fim_vigintile_15_Cpp/',
    'stack_edu-fim_vigintile_15_Go/',
    'stack_edu-fim_vigintile_15_Java/',
    'stack_edu-fim_vigintile_15_JavaScript/',
    'stack_edu-fim_vigintile_15_Markdown/',
    'stack_edu-fim_vigintile_15_PHP/',
    'stack_edu-fim_vigintile_15_Python/',
    'stack_edu-fim_vigintile_15_Ruby/',
    'stack_edu-fim_vigintile_15_Rust/',
    'stack_edu-fim_vigintile_15_SQL/',
    'stack_edu-fim_vigintile_15_Shell/',
    'stack_edu-fim_vigintile_15_Swift/',
    'stack_edu-fim_vigintile_15_TypeScript/',
    'stack_edu-fim_vigintile_16_C/',
    'stack_edu-fim_vigintile_16_CSharp/',
    'stack_edu-fim_vigintile_16_Cpp/',
    'stack_edu-fim_vigintile_16_Go/',
    'stack_edu-fim_vigintile_16_Java/',
    'stack_edu-fim_vigintile_16_JavaScript/',
    'stack_edu-fim_vigintile_16_Markdown/',
    'stack_edu-fim_vigintile_16_PHP/',
    'stack_edu-fim_vigintile_16_Python/',
    'stack_edu-fim_vigintile_16_Ruby/',
    'stack_edu-fim_vigintile_16_Rust/',
    'stack_edu-fim_vigintile_16_SQL/',
    'stack_edu-fim_vigintile_16_Shell/',
    'stack_edu-fim_vigintile_16_Swift/',
    'stack_edu-fim_vigintile_16_TypeScript/',
    'stack_edu-fim_vigintile_17_C/',
    'stack_edu-fim_vigintile_17_CSharp/',
    'stack_edu-fim_vigintile_17_Cpp/',
    'stack_edu-fim_vigintile_17_Go/',
    'stack_edu-fim_vigintile_17_Java/',
    'stack_edu-fim_vigintile_17_JavaScript/',
    'stack_edu-fim_vigintile_17_Markdown/',
    'stack_edu-fim_vigintile_17_PHP/',
    'stack_edu-fim_vigintile_17_Python/',
    'stack_edu-fim_vigintile_17_Ruby/',
    'stack_edu-fim_vigintile_17_Rust/',
    'stack_edu-fim_vigintile_17_SQL/',
    'stack_edu-fim_vigintile_17_Shell/',
    'stack_edu-fim_vigintile_17_Swift/',
    'stack_edu-fim_vigintile_17_TypeScript/',
    'stack_edu-fim_vigintile_19_C/',
    'stack_edu-fim_vigintile_19_CSharp/',
    'stack_edu-fim_vigintile_19_Cpp/',
    'stack_edu-fim_vigintile_19_Go/',
    'stack_edu-fim_vigintile_19_Java/',
    'stack_edu-fim_vigintile_19_JavaScript/',
    'stack_edu-fim_vigintile_19_Markdown/',
    'stack_edu-fim_vigintile_19_PHP/',
    'stack_edu-fim_vigintile_19_Python/',
    'stack_edu-fim_vigintile_19_Ruby/',
    'stack_edu-fim_vigintile_19_Rust/',
    'stack_edu-fim_vigintile_19_SQL/',
    'stack_edu-fim_vigintile_19_Shell/',
    'stack_edu-fim_vigintile_19_Swift/',
    'stack_edu-fim_vigintile_19_TypeScript/',
    'stem-heavy-crawl/',
    'tinymath-mind/',
    'tinymath-pot/',
    'tulu-3-sft/',
    'wiki_to_rcqa-part1/',
    'wiki_to_rcqa-part2/',
    'wiki_to_rcqa-part3/',
]

csv_paths = list(sorted(glob.glob(f'/data_c/tokenized/**/*.csv.gz', recursive=True)))
raw_s3_paths = set()

for csv_path in tqdm(csv_paths):
    with gzip.open(csv_path, 'rt') as f:
        reader = csv.reader(f)
        for row in reader:
            raw_s3_path = row[3]
            if raw_s3_path not in raw_s3_paths:
                raw_s3_paths.add(raw_s3_path)

with open(f's5cmd_files_v02/raw.s5cmd', 'w') as f:
    for raw_s3_path in raw_s3_paths:
        if raw_s3_path.startswith('s3://'):
            pass
        elif 'pretraining-data' in raw_s3_path: # stack-edu, s2pdf
            raw_s3_path = 's3://ai2-llm/pretraining-data' + 'pretraining-data'.join(raw_s3_path.split('pretraining-data')[1:])
        elif '/mnt/raid0/pdfs-reshard/software_dev/' in raw_s3_path:
            raise NotImplementedError('Software dev is not supported')
            import re
            match = re.search(r'/shard_0*([0-9]+)\.jsonl\.zst$', raw_s3_path)
            if match:
                shard_num = match.group(1).zfill(4) if len(match.group(1)) < 4 else match.group(1)
            else:
                raise ValueError(f"Cannot extract shard number from {raw_s3_path}")
            raw_s3_path = f's3://ai2-llm/pretraining-data/sources/s2pdf_dedupe_minhash_v1_with_no_pii_basic_quality_datadelve_norefs_mdtables_v2_denylisted/software_dev/step_final/step_final/s2pdf_datadelve_software_dev-{shard_num}.jsonl.gz'
        elif '/mnt/raid0/pdfs-reshard/software/' in raw_s3_path:
            raise NotImplementedError('Software is not supported')
            import re
            match = re.search(r'/shard_0*([0-9]+)\.jsonl\.zst$', raw_s3_path)
            if match:
                shard_num = match.group(1).zfill(4) if len(match.group(1)) < 4 else match.group(1)
            else:
                raise ValueError(f"Cannot extract shard number from {raw_s3_path}")
            raw_s3_path = f's3://ai2-llm/pretraining-data/sources/s2pdf_dedupe_minhash_v1_with_no_pii_basic_quality_datadelve_norefs_mdtables_v2_denylisted/software/step_final/step_final/s2pdf_datadelve_software-{shard_num}.jsonl.gz'
        elif any(raw_s3_path.startswith(prefix) for prefix in DOLMA3_DOLMINO_PREFIXES):
            raw_s3_path = f's3://ai2-llm/pretraining-data/sources/dolma3-dolmino-official/100B/{raw_s3_path}'
        else:
            raise NotImplementedError(f'{raw_s3_path} is not supported')
        assert raw_s3_path.startswith('s3://'), raw_s3_path
        raw_local_path = raw_s3_path.replace('s3://', '/data_c/raw/')
        f.write(f'cp {raw_s3_path} {raw_local_path}\n')
