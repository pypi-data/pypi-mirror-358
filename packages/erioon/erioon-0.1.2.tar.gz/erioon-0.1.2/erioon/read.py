import io
import msgpack
from azure.storage.blob import ContainerClient
from erioon.functions import async_log
from sklearn.neighbors import KNeighborsClassifier


def handle_get_all(user_id, db_id, coll_id, limit, container_url):
    """
    Retrieves up to a specified number of records from a collection stored in Blob Storage 
    and logs the operation status asynchronously.

    Parameters:
    - user_id (str): Identifier of the user making the request.
    - db_id (str): Database identifier (used as the directory prefix).
    - coll_id (str): Collection identifier (subdirectory under the database).
    - limit (int): Maximum number of records to retrieve (must not exceed 1,000,000).
    - container_url (str): URL to the Blob Storage container.

    Behavior:
    - Scans all blobs in the specified collection path (`db_id/coll_id/`).
    - Reads shard files, each containing a list of records.
    - Skips duplicate records by checking their `_id`.
    - Stops reading once the record limit is reached.
    - Skips empty or non-conforming blobs gracefully.

    Returns:
    - tuple(dict, int): A tuple containing:
        - A status dictionary with:
            - "status": "OK" or "KO"
            - "count": number of records returned (0 if none)
            - "results": list of records (only for successful responses)
            - "error": error message (on failure)
        - HTTP status code:
            - 200 if data is successfully returned.
            - 404 if collection is missing or no data found.
            - 500 on unexpected errors.
    """
    if limit > 1_000_000:
        async_log(user_id, db_id, coll_id, "GET", "ERROR", "Limit of 1,000,000 exceeded", 1, container_url)
        return {"status": "KO", "count": 0, "error": "Limit of 1,000,000 exceeded"}, 404

    directory_path = f"{db_id}/{coll_id}/"
    container_client = ContainerClient.from_container_url(container_url)

    blob_list = container_client.list_blobs(name_starts_with=directory_path)
    blob_names = [blob.name for blob in blob_list]

    if not blob_names:
        async_log(user_id, db_id, coll_id, "GET", "ERROR", f"No collection {coll_id} found.", 1, container_url)
        return {"status": "KO", "count": 0, "error": f"No collection {coll_id} found."}, 404

    results = []
    seen_ids = set()

    for blob in blob_names:
        try:
            if blob.endswith(".msgpack"):
                blob_client = container_client.get_blob_client(blob)
                msgpack_data = blob_client.download_blob().readall()

                if not msgpack_data:
                    continue

                with io.BytesIO(msgpack_data) as buffer:
                    unpacked_data = msgpack.unpackb(buffer.read(), raw=False)
                    if isinstance(unpacked_data, list):
                        for record in unpacked_data:
                            if record["_id"] in seen_ids:
                                continue

                            results.append(record)
                            seen_ids.add(record["_id"])

                            if len(results) >= limit:
                                async_log(user_id, db_id, coll_id, "GET", "SUCCESS", f"OK", len(results), container_url)
                                return {"status": "OK", "count": len(results), "results": results}, 200

        except Exception:
            continue

    if results:
        async_log(user_id, db_id, coll_id, "GET", "SUCCESS", f"OK", len(results), container_url)
        return {"status": "OK", "count": len(results), "results": results}, 200

    async_log(user_id, db_id, coll_id, "GET", "ERROR", "No data found", 1, container_url)
    return {"status": "KO", "count": 0, "error": "No data found"}, 404


def handle_get_data(user_id, db_id, coll_id, search_criteria, limit, container_url):
    """
    Searches for records within a collection in Blob Storage that match specified search criteria,
    and logs the query attempt asynchronously.

    Parameters:
    - user_id (str): Identifier of the user making the request.
    - db_id (str): Database identifier (used as the directory prefix).
    - coll_id (str): Collection identifier (subdirectory under the database).
    - search_criteria (list[dict]): A list of key-value conditions to match (supports dot notation for nested keys).
    - limit (int): Maximum number of matching records to return.
    - container_url (str): URL to the Blob Storage container.

    Behavior:
    - Iterates over blobs in the collection path (`db_id/coll_id/`).
    - Filters shard blobs containing lists of records.
    - Each record is checked against all `search_criteria`.
        - Supports nested key matching using dot notation (e.g., "user.name").
    - Skips duplicates based on `_id`.
    - Stops when enough matching records are found or blobs are exhausted.
    - Handles and skips corrupted or unreadable blobs gracefully.

    Returns:
    - tuple(dict, int): A tuple containing:
        - A status dictionary with:
            - "status": "OK" or "KO"
            - "count": number of records returned (0 if none)
            - "results": list of records (only for successful responses)
            - "error": error message (on failure)
        - HTTP status code:
            - 200 if matching records are found.
            - 404 if the collection or matching data is not found.
            - 500 on unexpected errors.
    """
    directory_path = f"{db_id}/{coll_id}/"
    container_client = ContainerClient.from_container_url(container_url)

    blob_list = container_client.list_blobs(name_starts_with=directory_path)
    blob_names = [blob.name for blob in blob_list]

    if not blob_names:
        async_log(user_id, db_id, coll_id, "GET", "ERROR", f"No collection {coll_id} found.", 1, container_url)
        return {"status": "KO", "count": 0, "error": f"No collection {coll_id} found."}, 404

    results = []
    seen_ids = set()

    for blob in blob_names:
        try:
            if blob.endswith(".msgpack"):
                blob_client = container_client.get_blob_client(blob)
                msgpack_data = blob_client.download_blob().readall()

                if not msgpack_data:
                    continue

                with io.BytesIO(msgpack_data) as buffer:
                    unpacked_data = msgpack.unpackb(buffer.read(), raw=False)
                    if isinstance(unpacked_data, list):
                        for record in unpacked_data:
                            if record["_id"] in seen_ids:
                                continue

                            match_found = False
                            for criteria in search_criteria:
                                print(criteria)
                                key, value = list(criteria.items())[0]

                                if key == "_id" and record.get("_id") == value:
                                    match_found = True
                                else:
                                    keys = key.split(".")
                                    nested_value = record
                                    for k in keys:
                                        if isinstance(nested_value, dict) and k in nested_value:
                                            nested_value = nested_value[k]
                                        else:
                                            nested_value = None
                                            break
                                    if nested_value == value:
                                        match_found = True

                                if match_found:
                                    results.append(record)
                                    seen_ids.add(record["_id"])
                                    if len(results) >= limit:
                                        async_log(user_id, db_id, coll_id, "GET", "SUCCESS", "OK", len(results), container_url)
                                        return {"status": "OK", "count": len(results), "results": results}, 200
                                    break

        except Exception:
            continue

    async_log(user_id, db_id, coll_id, "GET", "ERROR", "No matching record found", 1, container_url)
    return {"status": "KO", "count": 0, "error": "No matching record found"}, 404


def handle_classify_vector(user_id, db_id, coll_id, container_url, k=3):
    # 1. Retrieve all data from collection
    response, status = handle_get_all(user_id, db_id, coll_id, limit=10000, container_url=container_url)
    if status != 200:
        return {"status": "KO", "message": "Failed to fetch data for classification", "error": response.get("error", "")}, status

    records = response.get("results", [])
    if not records:
        return {"status": "KO", "message": "No data found for classification"}, 404

    # 2. Prepare dataset for classification
    vectors = []
    labels = []
    unknown_vectors = []
    unknown_ids = []

    for rec in records:
        vec = rec.get("vector")
        meta = rec.get("metadata", {})
        if not vec:
            continue
        vectors.append(vec)
        labels.append(meta.get("class", "unknown"))
    
    # If some records don’t have classes, you might want to separate them or remove them
    known_vectors = []
    known_labels = []
    for v, l in zip(vectors, labels):
        if l != "unknown" and l is not None:
            known_vectors.append(v)
            known_labels.append(l)
        else:
            unknown_vectors.append(v)
            unknown_ids.append(rec.get("_id"))

    if not known_vectors:
        return {"status": "KO", "message": "No labeled data for training classification"}, 404

    # 3. Train k-NN classifier on known labeled vectors
    knn = KNeighborsClassifier(n_neighbors=k)
    knn.fit(known_vectors, known_labels)

    # 4. Predict class for unknown vectors (if any)
    predictions = {}
    if unknown_vectors:
        predicted_labels = knn.predict(unknown_vectors)
        for _id, pred in zip(unknown_ids, predicted_labels):
            predictions[_id] = pred

    # 5. Return predictions (or full classification result)
    return {
        "status": "OK",
        "message": f"Classification done on {len(unknown_vectors)} unknown vectors",
        "predictions": predictions,
    }, 200