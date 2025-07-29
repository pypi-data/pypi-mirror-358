import json
import io
import msgpack
from azure.storage.blob import ContainerClient
from erioon.functions import update_index_file_delete, check_nested_key, async_log

def handle_delete_one(user_id, db_id, coll_id, data_to_delete, container_url):
    """
    Delete a single record from a collection.

    The record can be identified either by the unique '_id' field or by a nested key-value pair.

    Args:
        user_id: Identifier of the user performing the operation.
        db_id: Database ID containing the collection.
        coll_id: Collection ID.
        data_to_delete: Dictionary containing either '_id' or key-value pair to match.
        container_url: SAS URL pointing to the storage container.

    Returns:
        A tuple (response dict, status code) indicating success or failure.
    """
    if "_id" in data_to_delete:
        record_id = data_to_delete["_id"]
        return handle_delete_with_id(user_id, db_id, coll_id, record_id, container_url)
    else:
        return handle_delete_without_id(user_id, db_id, coll_id, data_to_delete, container_url)

def handle_delete_with_id(user_id, db_id, coll_id, record_id, container_url):
    """
    Delete a record exactly matching the given '_id'.

    Steps:
    - Parse container URL and create a ContainerClient.
    - Load the index.json file which maps shards to record IDs.
    - Locate the shard containing the target record_id.
    - Download and unpack the shard blob.
    - Remove the record from the shard data.
    - Repack and upload the updated shard if record found.
    - Update index.json to reflect deletion.
    - Log success or errors asynchronously.

    Args:
        user_id, db_id, coll_id: Identifiers for user, database, and collection.
        record_id: The unique '_id' of the record to delete.
        container_url: Azure Blob Storage container SAS URL.

    Returns:
        Tuple (response dict, status code) indicating operation result.
    """
    parsed_url = container_url.split("?")
    container_path = parsed_url[0].split("/")[-1]
    sas_token = parsed_url[1] if len(parsed_url) > 1 else ""
    container_client = ContainerClient.from_container_url(container_url)

    index_blob_client = container_client.get_blob_client(f"{db_id}/{coll_id}/index.json")

    if not index_blob_client.exists():
        return {"error": "Index file does not exist"}, 404

    index_data = json.loads(index_blob_client.download_blob().readall())
    shard_number = None

    for shard in index_data:
        for shard_key, ids in shard.items():
            if record_id in ids:
                shard_number = int(shard_key.split("_")[-1])
                break
        if shard_number:
            break

    if shard_number is None:
        async_log(user_id, db_id, coll_id, "DELETE", "ERROR", f"Record with _id {record_id} not found", 1, container_url)
        return {"error": f"Record with _id {record_id} not found"}, 404

    msgpack_blob_client = container_client.get_blob_client(f"{db_id}/{coll_id}/{coll_id}_{shard_number}.msgpack")

    try:
        msgpack_data = msgpack_blob_client.download_blob().readall()
        with io.BytesIO(msgpack_data) as buffer:
            records = []
            original_length = 0

            unpacked_data = msgpack.unpackb(buffer.read(), raw=False)
            if isinstance(unpacked_data, list):
                for record in unpacked_data:
                    original_length += 1
                    if record.get("_id") == record_id:
                        continue
                    records.append(record)

            if len(records) < original_length:
                with io.BytesIO() as out_file:
                    packed_data = msgpack.packb(records)
                    out_file.write(packed_data)
                    out_file.seek(0)
                    msgpack_blob_client.upload_blob(out_file, overwrite=True)

                update_index_file_delete(user_id, db_id, coll_id, record_id, shard_number, container_url)
                async_log(user_id, db_id, coll_id, "DELETE", "SUCCESS", f"Record with _id {record_id} deleted successfully", 1, container_url)
                return {"success": f"Record with _id {record_id} deleted successfully"}, 200
            else:
                async_log(user_id, db_id, coll_id, "DELETE", "ERROR", f"Record with _id {record_id} not found in shard", 1, container_url)
                return {"error": f"Record with _id {record_id} not found in shard"}, 404

    except Exception as e:
        async_log(user_id, db_id, coll_id, "DELETE", "ERROR", f"Error deleting record {record_id}: {str(e)}", 1, container_url)
        return {"error": f"Error deleting record {record_id}: {str(e)}"}, 500

def handle_delete_without_id(user_id, db_id, coll_id, data_to_delete, container_url):
    """
    Delete records matching a nested key-value pair when '_id' is not provided.

    Steps:
    - Extract the single key-value pair to search for.
    - List all shards in the collection.
    - Download and unpack each shard, check each record for matching key-value.
    - Collect all matching record '_id's.
    - If no matches found, return error.
    - For each matched '_id', call `handle_delete_with_id` to delete it.
    - Return summary of deleted record count.

    Args:
        user_id, db_id, coll_id: Identifiers for user, database, and collection.
        data_to_delete: Dict with one nested key-value pair to match.
        container_url: Blob storage container SAS URL.

    Returns:
        Tuple (response dict, status code) with success or error message.
    """
    container_client = ContainerClient.from_container_url(container_url)

    nested_key = list(data_to_delete.keys())[0]
    key, value = nested_key, data_to_delete[nested_key]

    coll_id_data = []
    directory_path = f"{db_id}/{coll_id}/"
    blob_list = container_client.list_blobs(name_starts_with=directory_path)

    for blob in blob_list:
        if blob.name.endswith(".msgpack"):
            try:
                blob_client = container_client.get_blob_client(blob.name)
                msgpack_data = blob_client.download_blob().readall()

                with io.BytesIO(msgpack_data) as buffer:
                    unpacked_data = msgpack.unpackb(buffer.read(), raw=False)
                    if isinstance(unpacked_data, list):
                        for record in unpacked_data:
                            if check_nested_key(record, key, value):
                                coll_id_data.append(record["_id"])
            except Exception:
                continue

    if not coll_id_data:
        async_log(user_id, db_id, coll_id, "DELETE", "ERROR", f"No matching records found for key-value pair", 1, container_url)
        return {"error": "No matching records found for the specified key-value pair"}, 404

    for record_id in coll_id_data:
        try:
            handle_delete_with_id(user_id, db_id, coll_id, record_id, container_url)
        except Exception:
            continue

    count = len(coll_id_data)
    return (
        {"success": f"{count} record(s) '{key}':'{value}' deleted successfully"},
        200
    )

def handle_delete_many(user_id, db_id, coll_id, data_to_delete_list, container_url, batch_size=10):
    """
    Delete multiple records in batches to improve performance and error management.

    For each batch of deletion queries:
    - Determine whether to delete by '_id' or key-value.
    - Collect individual successes and errors.
    - Aggregate batch results.

    Args:
        user_id, db_id, coll_id: Identifiers for user, database, collection.
        data_to_delete_list: List of dicts, each with '_id' or nested key-value pair.
        container_url: storage container SAS URL.
        batch_size: Number of deletions processed per batch.

    Returns:
        Tuple (response dict, status code) with aggregated success or error info.
    """
    batch_results = []

    for i in range(0, len(data_to_delete_list), batch_size):
        batch = data_to_delete_list[i : i + batch_size]
        batch_success = []
        batch_errors = []

        for data_to_delete in batch:
            try:
                if "_id" in data_to_delete:
                    record_id = data_to_delete["_id"]
                    result = handle_delete_with_id(
                        user_id, db_id, coll_id, record_id, container_url
                    )
                else:
                    result = handle_delete_without_id(
                        user_id, db_id, coll_id, data_to_delete, container_url
                    )

                if result is not None:
                    response, status_code = result
                    if status_code == 200:
                        batch_success.append(
                            {
                                "delete_query": data_to_delete,
                                "message": response.get(
                                    "success", "Record deleted successfully"
                                ),
                            }
                        )
                    else:
                        batch_errors.append(
                            {
                                "delete_query": data_to_delete,
                                "error": response.get(
                                    "error",
                                    f"Failed to delete record - Status code {status_code}",
                                ),
                            }
                        )
                else:
                    batch_errors.append(
                        {
                            "delete_query": data_to_delete,
                            "error": "No result returned from delete function",
                        }
                    )

            except Exception as e:
                batch_errors.append({"delete_query": data_to_delete, "error": str(e)})

        batch_results.append(
            {"queries": len(batch), "success": batch_success, "errors": batch_errors}
        )

    total_success = sum(len(batch["success"]) for batch in batch_results)
    total_errors = sum(len(batch["errors"]) for batch in batch_results)

    if total_errors == 0:
        return (
            {
                "success": f"Selected records deleted successfully",
                "details": batch_results,
            }
        ), 200
    else:
        return (
            {"error": f"Error deleting selected records", "details": batch_results}
        ), 500
