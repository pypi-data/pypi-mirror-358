import msgpack
from azure.storage.blob import ContainerClient
from erioon.functions import async_log


def handle_update_query(user_id, db_id, coll_id, filter_query, update_query, container_url):
    """
    Updates a single record in a collection stored in Blob Storage based on a filter condition,
    applying one of the supported update operations, and logs the result asynchronously.

    Supported operations in `update_query`:
    - "$set": Overwrites the value at the specified (possibly nested) key.
    - "$push": Appends a value to a list at the specified key, or initializes the list if it doesn't exist.
    - "$remove": Deletes the specified key from the record.

    Parameters:
    - user_id (str): Identifier of the user making the update request.
    - db_id (str): Database identifier (used as a directory prefix).
    - coll_id (str): Collection identifier (used as a subdirectory under the database).
    - filter_query (dict): Key-value pairs that must match exactly in the record for it to be updated.
    - update_query (dict): Update operations to apply, using one of the supported operators ($set, $push, $remove).
    - container_url (str): URL of the Blob Storage container where the data is stored.

    Behavior:
    - Iterates through all shard blobs in the target collection folder.
    - Loads and unpacks each blob's data as a list of records.
    - Finds the first record that matches all key-value pairs in `filter_query`.
    - Applies the specified update operation(s) to the matched record:
        - Dot notation (e.g., "user.name") is supported for nested updates.
    - Re-serializes the modified records and overwrites the original blob.
    - Stops processing after the first successful match and update.

    Returns:
    - tuple(dict, int): A tuple containing:
        - A dictionary with either:
            - "success": Confirmation message if update succeeded.
            - "error": Error message if update failed.
        - HTTP status code:
            - 200 if a matching record is updated successfully.
            - 404 if no collections or matching records are found.
            - No 500s are explicitly returned; internal exceptions are silently caught.
    """
    container_client = ContainerClient.from_container_url(container_url)
    directory_path = f"{db_id}/{coll_id}/"

    blob_list = container_client.list_blobs(name_starts_with=directory_path)
    blob_names = [blob.name for blob in blob_list if blob.name.endswith(".msgpack")]

    if not blob_names:
        async_log(user_id, db_id, coll_id, "PATCH_UPDT", "ERROR",
                  f"No collections found for the database {db_id}", 1, container_url)
        return {"error": f"No collections found for the database {db_id}"}, 404

    updated = False

    for blob_name in blob_names:
        try:
            blob_client = container_client.get_blob_client(blob_name)
            msgpack_data = blob_client.download_blob().readall()

            if not msgpack_data:
                continue

            data_records = msgpack.unpackb(msgpack_data, raw=False)
            modified_records = []
            local_updated = False

            for record in data_records:
                match_found = all(record.get(k) == v for k, v in filter_query.items())

                if match_found:
                    for op, changes in update_query.items():
                        if op == "$set":
                            for key, new_value in changes.items():
                                keys = key.split(".")
                                nested_obj = record
                                for k in keys[:-1]:
                                    nested_obj = nested_obj.setdefault(k, {})
                                nested_obj[keys[-1]] = new_value

                        elif op == "$push":
                            for key, new_value in changes.items():
                                keys = key.split(".")
                                nested_obj = record
                                for k in keys[:-1]:
                                    nested_obj = nested_obj.setdefault(k, {})
                                last_key = keys[-1]
                                if last_key not in nested_obj:
                                    nested_obj[last_key] = [new_value]
                                elif isinstance(nested_obj[last_key], list):
                                    nested_obj[last_key].append(new_value)
                                else:
                                    nested_obj[last_key] = [nested_obj[last_key], new_value]

                        elif op == "$remove":
                            for key in changes:
                                keys = key.split(".")
                                nested_obj = record
                                for k in keys[:-1]:
                                    nested_obj = nested_obj.get(k, {})
                                last_key = keys[-1]
                                if isinstance(nested_obj, dict) and last_key in nested_obj:
                                    del nested_obj[last_key]

                    updated = True
                    local_updated = True

                modified_records.append(record)

            if local_updated:
                packed_data = msgpack.packb(modified_records, use_bin_type=True)
                blob_client.upload_blob(packed_data, overwrite=True)
                async_log(user_id, db_id, coll_id, "PATCH_UPDT", "SUCCESS",
                          "Record updated successfully", len(modified_records), container_url)
                return {"success": "Record updated successfully"}, 200

        except Exception:
            continue

    if not updated:
        async_log(user_id, db_id, coll_id, "PATCH_UPDT", "ERROR",
                  "No matching record found", 1, container_url)
        return {"error": "No matching record found"}, 404
