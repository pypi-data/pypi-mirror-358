import json
from urllib.parse import urlparse
from erioon.read import handle_get_all, handle_get_data, handle_classify_vector
from erioon.create import handle_insert_one, handle_insert_many, handle_vector, handle_insert_many_vectors
from erioon.delete import handle_delete_one, handle_delete_many
from erioon.update import handle_update_query
from erioon.ping import handle_connection_ping

class Collection:
    def __init__(
        self,
        user_id,
        db_id,
        coll_id,
        metadata,
        database,
        cluster,
        sas_url,
    ):
        
        """
        Initialize a Collection object that wraps Erioon collection access.

        Args:
            user_id (str): The authenticated user's ID.
            db_id (str): The database ID.
            coll_id (str): The collection ID.
            metadata (dict): Metadata info about this collection (e.g., schema, indexing, etc.).
            database (str): Name or ID of the database.
            cluster (str): Cluster name or ID hosting the database.
            sas_url (str): Full SAS URL used to access the storage container.
        """
        
        self.user_id = user_id
        self.db_id = db_id
        self.coll_id = coll_id
        self.metadata = metadata
        self.database = database
        self.cluster = cluster

        parsed_url = urlparse(sas_url.rstrip("/"))
        container_name = parsed_url.path.lstrip("/").split("/")[0]
        account_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        sas_token = parsed_url.query
        self.container_url = f"{account_url}/{container_name}?{sas_token}"

    def _print_loading(self):
        """Prints a loading message (likely for UX in CLI or SDK usage)."""
        print("Erioon is loading...")

    def _is_read_only(self):
        """Check if the current database is marked as read-only."""
        return self.database == "read"
    
    def _read_only_response(self):
        """Standardized error response for blocked write operations."""
        return "This user is not allowed to perform write operations.", 403

    def get_all(self, limit=1000000):
        """
        Fetch all records from the collection (up to a limit).
        
        Args:
            limit (int): Max number of records to fetch.
        Returns:
            list: Collection of records.
        """
        self._print_loading()
        result, status_code = handle_get_all(
            user_id=self.user_id,
            db_id=self.db_id,
            coll_id=self.coll_id,
            limit=limit,
            container_url=self.container_url,
        )
        return result

    def get_specific(self, filters: dict | None = None, limit: int = 1000):
        """
        Fetch records that match specific key-value filters.
        
        Args:
            filters (dict): Dictionary of exact match filters.
            limit (int): Max number of matching records to return.

        Returns:
            list: Filtered records from the collection.
        """
        if limit > 500_000:
            raise ValueError("Limit of 500,000 exceeded")
        self._print_loading()

        if filters is None:
            filters = {}

        search_criteria = [{k: v} for k, v in filters.items()]
        print(search_criteria)

        result, status_code = handle_get_data(
            user_id=self.user_id,
            db_id=self.db_id,
            coll_id=self.coll_id,
            search_criteria=search_criteria,
            limit=limit,
            container_url=self.container_url,
        )
        return result

    def insert_one(self, record):
        """
        Insert a single record into the collection.

        Args:
            record (dict): Record to insert.

        Returns:
            tuple: (response message, HTTP status code)
        """
        if self._is_read_only():
            return self._read_only_response()
        return handle_insert_one(
            user_id_cont=self.user_id,
            database=self.db_id,
            collection=self.coll_id,
            record=record,
            container_url=self.container_url,
        )

    def insert_many(self, data):
        """
        Insert multiple records into the collection.

        Args:
            data (list of dicts): Multiple records to insert.

        Returns:
            tuple: (response message, HTTP status code)
        """
        if self._is_read_only():
            return self._read_only_response()
        return handle_insert_many(
            user_id_cont=self.user_id,
            database=self.db_id,
            collection=self.coll_id,
            data=data,
            container_url=self.container_url,
        )

    def delete_one(self, record_to_delete):
        """
        Delete a single record based on its _id or nested key.

        Args:
            record_to_delete (dict): Identification of the record.

        Returns:
            tuple: (response message, HTTP status code)
        """
        if self._is_read_only():
            return self._read_only_response()
        return handle_delete_one(
            user_id=self.user_id,
            db_id=self.db_id,
            coll_id=self.coll_id,
            data_to_delete=record_to_delete,
            container_url=self.container_url,
        )

    def delete_many(self, records_to_delete_list, batch_size=10):
        """
        Delete multiple records in batches.

        Args:
            records_to_delete_list (list): List of record identifiers.
            batch_size (int): How many to delete at once (for efficiency).

        Returns:
            tuple: (response message, HTTP status code)
        """
        if self._is_read_only():
            return self._read_only_response()
        return handle_delete_many(
            user_id=self.user_id,
            db_id=self.db_id,
            coll_id=self.coll_id,
            data_to_delete_list=records_to_delete_list,
            batch_size=batch_size,
            container_url=self.container_url,
        )

    def update_query(self, filter_query: dict, update_query: dict):
        """
        Update a record in-place by filtering and applying update logic.

        Args:
            filter_query (dict): Dict describing what record(s) to match.
            update_query (dict): Dict describing update operators ($set, $push, $remove).

        Returns:
            tuple: (response message, HTTP status code)
        """
        if self._is_read_only():
            return self._read_only_response()
        return handle_update_query(
            user_id=self.user_id,
            db_id=self.db_id,
            coll_id=self.coll_id,
            filter_query=filter_query,
            update_query=update_query,
            container_url=self.container_url,
        )
        
    def ping(self):
        """
        Health check / ping to verify collection accessibility.

        Returns:
            tuple: (response message, HTTP status code)
        """
        return handle_connection_ping(
            user_id=self.user_id,
            db_id=self.db_id,
            coll_id=self.coll_id,
            container_url=self.container_url,
        )
        
    def insert_one_vector(self, vector_data, metadata):
        """
        Insert a single record into the collection.

        Args:
            record (dict): Record to insert.

        Returns:
            tuple: (response message, HTTP status code)
        """
        if self._is_read_only():
            return self._read_only_response()
        self._print_loading()
        return handle_vector(
            user_id_cont=self.user_id,
            database=self.db_id,
            collection=self.coll_id,
            vector=vector_data,
            metadata=metadata,
            container_url=self.container_url,
        )
        
    def insert_many_vectors(self, records):
        """
        Insert multiple vector records into the collection.

        Args:
            records (list): List of dicts, each with keys 'vector', 'metadata', and optional '_id'.

        Returns:
            tuple: (response message, HTTP status code)
        """
        if self._is_read_only():
            return self._read_only_response()
        self._print_loading()
        return handle_insert_many_vectors(
            user_id_cont=self.user_id,
            database=self.db_id,
            collection=self.coll_id,
            records=records,
            container_url=self.container_url,
        )
        
    def classify_vector(self, k=3):
        """
        Retrieve all vector records from the collection and classify them using k-NN.

        Args:
            k (int): Number of neighbors to use for classification.

        Returns:
            tuple: (response message, HTTP status code)
        """
        if self._is_read_only():
            return self._read_only_response()
        self._print_loading()
        return handle_classify_vector(
            user_id=self.user_id,
            db_id=self.db_id,
            coll_id=self.coll_id,
            container_url=self.container_url,
            k=k
        )


    def __str__(self):
        """Pretty print the collection metadata."""
        return json.dumps(self.metadata, indent=4)

    def __repr__(self):
        """Simplified representation for debugging or introspection."""
        return f"<Collection coll_id={self.coll_id}>"
