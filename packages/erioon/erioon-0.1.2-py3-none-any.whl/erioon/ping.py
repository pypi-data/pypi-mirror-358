from erioon.functions import async_log
from azure.storage.blob import ContainerClient

def handle_connection_ping(user_id, db_id, coll_id, container_url):
    """
    Checks if a specific collection exists within an Blob Storage container 
    and logs the status of the connection attempt asynchronously.

    Parameters:
    - user_id (str): Identifier of the user making the request.
    - db_id (str): Database identifier (used as a folder prefix).
    - coll_id (str): Collection identifier (used as a folder prefix).
    - container_url (str): URL of the Blob Storage container.

    Returns:
    - tuple(dict, int): A tuple containing a status dictionary and an HTTP status code.
        - If collection is found, returns status "OK" and HTTP 200.
        - If collection is missing, returns status "KO" with HTTP 404.
        - On any exception, returns status "KO" with HTTP 500.
    """
    try:
        container_client = ContainerClient.from_container_url(container_url)
        directory_path = f"{db_id}/{coll_id}/"

        blobs = container_client.list_blobs(name_starts_with=directory_path)
        blob_names = [blob.name for blob in blobs]

        if not blob_names:
            async_log(user_id, db_id, coll_id, "PING", "ERROR", f"No collection {coll_id} found.", 1, container_url)
            return {"status": "KO", "error": f"No collection {coll_id} found."}, 404

        async_log(user_id, db_id, coll_id, "PING", "SUCCESS", "Connection successful", 1, container_url)
        return {"status": "OK", "message": "Connection successful"}, 200

    except Exception as e:
        async_log(user_id, db_id, coll_id, "PING", "ERROR", f"Connection failed: {str(e)}", 1, container_url)
        return {"status": "KO", "error": "Connection failed", "message": str(e)}, 500
