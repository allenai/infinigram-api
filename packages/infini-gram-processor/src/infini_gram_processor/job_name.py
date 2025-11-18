from infini_gram_processor.index_mappings import AvailableInfiniGramIndexId

BASE_JOB_NAME = "attribute"


def get_attribute_job_name_for_index(index_id: AvailableInfiniGramIndexId) -> str:
    return f"${BASE_JOB_NAME}_${index_id.value}"
