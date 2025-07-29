from azure.storage.blob import ContainerClient
import uuid
import json
from erioon.functions import (
    create_msgpack_file,
    update_index_file_insert,
    calculate_shard_number,
    async_log
)

def get_index_data(user_id_cont, database, collection, container_url):
    """
    Retrieves the content of the index.json file that tracks which records are stored in which shards.

    Args:
        user_id_cont: User identifier or context.
        database: Database name.
        collection: Collection name.
        container_url: Blob Storage container SAS URL.

    Returns:
        List of shard mappings (list of dicts) or empty list if file not found or error.
    """
    container_client = ContainerClient.from_container_url(container_url)
    index_blob_client = container_client.get_blob_client(blob=f"{database}/{collection}/index.json")

    try:
        index_data = index_blob_client.download_blob().readall()
        return json.loads(index_data) if index_data else []
    except Exception:
        return []

def is_duplicate_id(user_id_cont, database, collection, _id, container_url):
    """
    Checks if the given record _id is already present in the index.json across shards.

    Args:
        user_id_cont: User identifier.
        database: Database name.
        collection: Collection name.
        _id: Record ID to check.
        container_url: Blob Storage container SAS URL.

    Returns:
        True if _id exists in any shard, else False.
    """
    index_data = get_index_data(user_id_cont, database, collection, container_url)

    for shard in index_data:
        for shard_name, ids in shard.items():
            if _id in ids:
                return True 
    return False

def handle_insert_one(user_id_cont, database, collection, record, container_url):
    """
    Insert a single record into the collection.

    - If no '_id' provided, generate a new UUID.
    - If provided '_id' is duplicate, generate a new one and update the record.
    - Create or append the record in a shard file.
    - Update index.json to map the record to the appropriate shard.
    - Log success or errors asynchronously.

    Args:
        user_id_cont: User identifier.
        database: Database name.
        collection: Collection name.
        record: Dict representing the record to insert.
        container_url: Blob Storage container SAS URL.

    Returns:
        Tuple (response dict, status code) indicating success or failure.
    """
    try:
        if "_id" not in record or not record["_id"]:
            record["_id"] = str(uuid.uuid4())

        rec_id = record["_id"]

        if is_duplicate_id(user_id_cont, database, collection, rec_id, container_url):
            new_id = str(uuid.uuid4())
            record["_id"] = new_id
            rec_id = new_id
            msg = f"Record inserted successfully in {collection} with a new _id {rec_id} because the provided _id was already present."
        else:
            msg = f"Record inserted successfully in {collection} with _id {rec_id}"

        async_log(user_id_cont, database, collection, "POST", "SUCCESS", msg, 1, container_url)

        create_msgpack_file(user_id_cont, database, collection, record, container_url)

        shard_number = calculate_shard_number(user_id_cont, database, collection, container_url)
        update_index_file_insert(user_id_cont, database, collection, rec_id, shard_number, container_url)

        return {"status": "OK", "message": msg, "record": record}, 200

    except Exception as e:
        error_msg = f"An error occurred during insert in {collection}: {str(e)}"
        async_log(user_id_cont, database, collection,"POST", "ERROR", error_msg, 1, container_url)
        return {"status": "KO", "message": "Failed to insert record.", "error": str(e)}, 500

def handle_insert_many(user_id_cont, database, collection, data, container_url):
    """
    Insert multiple records in bulk.

    - For each record:
      - Ensure it has a unique _id (generate new UUID if missing or duplicate).
      - Write the record to the appropriate shard.
      - Update index.json with _id to shard mapping.
    - Log the batch insert operation with details.
    - Return aggregate success or failure response.

    Args:
        user_id_cont: User identifier.
        database: Database name.
        collection: Collection name.
        data: Dict with key "records" containing list of record dicts.
        container_url: Blob Storage container SAS URL.

    Returns:
        Tuple (response dict, status code) with summary of insert results.
    """
    insert_results = []
    records = data.get("records", [])
    count = len(records)
    
    try:
        for record in records:
            if "_id" not in record or not record["_id"]:
                record["_id"] = str(uuid.uuid4())

            rec_id = record["_id"]

            if is_duplicate_id(user_id_cont, database, collection, rec_id, container_url):
                new_id = str(uuid.uuid4())
                record["_id"] = new_id
                rec_id = new_id
                msg = f"Inserted with new _id {rec_id} (original _id was already present)."
            else:
                msg = f"Inserted with _id {rec_id}."

            create_msgpack_file(user_id_cont, database, collection, record, container_url)

            shard_number = calculate_shard_number(user_id_cont, database, collection, container_url)
            update_index_file_insert(
                user_id_cont, database, collection, rec_id, shard_number, container_url
            )

            insert_results.append({"_id": rec_id, "message": msg})

        async_log(user_id_cont, database, collection, "POST", "SUCCESS", insert_results, count, container_url)
        return {"success": "Records inserted successfully", "details": insert_results}, 200
        

    except Exception as e:
        general_error_msg = f"Unexpected error during bulk insert: {str(e)}"
        async_log(user_id_cont, database, collection, "POST", "ERROR", general_error_msg, 1, container_url)
        return {"status": "KO", "message": general_error_msg}, 500

def handle_vector(user_id_cont, database, collection, vector, metadata, container_url, _id=None):
    """
    Inserts a vector embedding with its metadata into the blob-based vector DB.

    Args:
        user_id_cont: User identifier or context.
        database: Database name.
        collection: Collection name.
        vector: List of floats representing the embedding.
        metadata: Dictionary of associated metadata.
        container_url: Azure Blob container SAS URL.
        _id: Optional. Custom record ID. If None, UUID is generated.

    Returns:
        Tuple of (response dict, status code).
    """
    try:
        if not isinstance(vector, list) or not all(isinstance(v, (float, int)) for v in vector):
            return {"status": "KO", "message": "Invalid vector format. Must be a list of floats."}, 400

        record = {
            "_id": _id or str(uuid.uuid4()),
            "vector": vector,
            "metadata": metadata or {}
        }

        return handle_insert_one(user_id_cont, database, collection, record, container_url)

    except Exception as e:
        error_msg = f"Error in handle_vector: {str(e)}"
        async_log(user_id_cont, database, collection, "POST", "ERROR", error_msg, 1, container_url)
        return {"status": "KO", "message": "Failed to insert vector record.", "error": str(e)}, 500


def handle_insert_many_vectors(user_id_cont, database, collection, records, container_url):
    """
    Bulk insert multiple vector embedding records with metadata into the blob-based vector DB.

    Args:
        user_id_cont: User identifier or context.
        database: Database name.
        collection: Collection name.
        records: List of dicts, each with keys 'vector', 'metadata', and optional '_id'.
        container_url: Azure Blob container SAS URL.

    Returns:
        Tuple of (response dict, status code).
    """
    insert_results = []

    try:
        for record in records:
            vector = record.get("vector")
            metadata = record.get("metadata", {})
            _id = record.get("_id")

            # Validate vector format
            if not isinstance(vector, list) or not all(isinstance(v, (float, int)) for v in vector):
                insert_results.append({
                    "_id": _id,
                    "status": "KO",
                    "message": "Invalid vector format. Must be a list of floats."
                })
                continue

            # Build record to insert
            rec_to_insert = {
                "_id": _id or str(uuid.uuid4()),
                "vector": vector,
                "metadata": metadata,
            }

            # Insert single vector record
            response, status_code = handle_insert_one(
                user_id_cont,
                database,
                collection,
                rec_to_insert,
                container_url
            )

            insert_results.append({
                "_id": rec_to_insert["_id"],
                "status": "OK" if status_code == 200 else "KO",
                "message": response.get("message", "") if isinstance(response, dict) else str(response)
            })

        # Log bulk insert operation asynchronously
        async_log(
            user_id_cont,
            database,
            collection,
            "POST",
            "SUCCESS",
            insert_results,
            len(records),
            container_url
        )

        return {"success": "Bulk vector insert completed.", "details": insert_results}, 200

    except Exception as e:
        error_msg = f"Unexpected error during bulk vector insert: {str(e)}"
        async_log(user_id_cont, database, collection, "POST", "ERROR", error_msg, 1, container_url)
        return {"status": "KO", "message": error_msg}, 500
