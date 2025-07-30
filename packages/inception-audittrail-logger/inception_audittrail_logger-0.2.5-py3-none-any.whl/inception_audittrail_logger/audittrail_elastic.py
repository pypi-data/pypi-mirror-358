from elasticsearch import Elasticsearch
from inception_audittrail_logger.settings_audittrail import get_audittrail_setting
from elasticsearch import Elasticsearch

audittrail_setting = get_audittrail_setting()
AUDITTRAIL_INDEX_NAME = "audittrail"
SYSTEM_ERROR_INDEX_NAME = "system_error"

# Connect to ES
es = Elasticsearch(audittrail_setting.elasticsearch_url)

# ✅ Confirm connection
if es.ping():
    print("✅ Successfully connected to Audittrail Elasticsearch!")
else:
    print("❌ Failed to connect to Audittrail Elasticsearch.")


async def index_document(index_name: str, document_id: str, body: dict):
    response = es.index(index=index_name, id=document_id, document=body)
    print(f"✅ Successfully indexed document into Elasticsearch: {document_id}")
    return response


async def search_es_documents(index_name: str, query: dict):
    response = es.search(index=index_name, body=query)
    print(f"✅ Successfully searched Elasticsearch: {response}")
    return response


def get_audittrail_es_client() -> Elasticsearch:
    return es
