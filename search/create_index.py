from azure.core.credentials import AzureKeyCredential
import os
from dotenv import load_dotenv
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    SearchField,
    SearchFieldDataType
)

load_dotenv()

endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
key = os.getenv("AZURE_SEARCH_KEY")

index_name = "news-index"

client = SearchIndexClient(endpoint, AzureKeyCredential(key))

fields = [
    SimpleField(name="id", type="Edm.String", key=True),
    SearchableField(name="title", type="Edm.String"),
    SearchableField(name="content", type="Edm.String"),
    SimpleField(name="published", type="Edm.String"),
    SearchField(
        name="contentVector",
        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
        vector_search_dimensions=768,
        vector_search_profile_name="vector-profile"
    )
]
vector_search = VectorSearch(
    algorithms=[
        HnswAlgorithmConfiguration(name="hnsw")
    ],
    profiles=[
        VectorSearchProfile(
            name="vector-profile",
            algorithm_configuration_name="hnsw"
        )
    ]
)
index = SearchIndex(
    name=index_name,
    fields=fields,
    vector_search=vector_search
)

client.create_or_update_index(index)

print("Index created successfully")