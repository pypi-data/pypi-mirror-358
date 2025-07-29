import requests
from typing import Union, List, Optional, Dict, Tuple, Callable
from .collection import DocumentNotFound, InvalidLookup, WriteError, LockingError


class APIError(Exception):
    """Raised for general API errors that don't map to a specific CollectionError."""
    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code
    
    def __str__(self):
        if self.status_code:
            return f"[Status {self.status_code}] {super().__str__()}"
        return super().__str__()


class RemoteCollection:
    """
    Provides a remote interface to a Collection on a server, mirroring the methods
    of the local Collection class.
    """
    def __init__(self, url: str, collection_name: str, token_provider: Optional[Callable[[], Optional[str]]] = None):
        """
        Initializes the remote collection interface.

        :param str url: The base URL of the dua server.
        :param str collection_name: The name of the collection to interact with.
        :param Optional[Callable[[], Optional[str]]] token_provider: A function that returns a bearer token string, or None.
        """
        self.collection_url = f"{url.rstrip('/')}/{collection_name}"
        self.session = requests.Session()
        self.token_provider = token_provider if token_provider else lambda: None

    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        Internal method for making requests to the API and handling errors.
        """
        url = f"{self.collection_url}/{endpoint.lstrip('/')}"
        
        # Dynamically get the token for each request
        token = self.token_provider()
        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})
        elif "Authorization" in self.session.headers:
            # Remove header if token is no longer provided
            del self.session.headers["Authorization"]

        try:
            response = self.session.request(method, url, **kwargs)
            if 400 <= response.status_code < 600:
                try:
                    error_data = response.json()
                    message = error_data.get("error", "An unknown API error occurred.")
                except requests.exceptions.JSONDecodeError:
                    message = response.text

                # Map HTTP status codes and messages back to specific Collection exceptions
                if response.status_code == 404:
                    raise DocumentNotFound(message)
                if response.status_code == 400:
                    raise InvalidLookup(message)
                if response.status_code == 500:
                    if 'lock' in message.lower():
                        raise LockingError(message)
                    raise WriteError(message) # Default for other server errors
                
                # Fallback for any other HTTP error codes
                raise APIError(message, response.status_code)
                
            return response
        except requests.exceptions.RequestException as e:
            # For network-level errors
            raise APIError(f"Request failed: {e}") from e

    def get_all(self) -> List[Dict]:
        """
        Retrieves all documents from the collection.

        :return: A list of dictionaries, where each dictionary is a document.
        :rtype: List[Dict]
        """
        response = self._request("GET", "get_all")
        return response.json()

    def get(self, lookup: Union[str, dict]) -> Optional[Dict]:
        """
        Retrieves a single document from the collection.

        :param Union[str, dict] lookup: The query to find the document. 
                                        If a string, it's a primary key lookup. 
                                        If a dict, it's a query against document fields.
        :return: A dictionary representing the found document, or None if not found.
        :rtype: Optional[Dict]
        :raises InvalidLookup: If the lookup type is not a string or a dictionary.
        """
        response = self._request("POST", "get", json={"lookup": lookup})
        return response.json()

    def get_many(self, lookup: Dict) -> List[Dict]:
        """
        Retrieves all documents that match a given lookup dictionary.

        :param Dict lookup: The query dictionary to match against documents.
        :return: A list of matching documents.
        :rtype: List[Dict]
        :raises InvalidLookup: If the lookup is not a dictionary.
        """
        response = self._request("POST", "get_many", json={"lookup": lookup})
        return response.json()

    def get_batch(self, lookups: List[Union[str, dict]]) -> List[Dict]:
        """
        Retrieves multiple documents based on a list of lookups.

        :param List[Union[str, dict]] lookups: A list of primary keys or lookup dictionaries.
        :return: A list of found documents. Duplicates may be included if lookups match the same document.
        :rtype: List[Dict]
        """
        response = self._request("POST", "get_batch", json={"lookups": lookups})
        return response.json()

    def set(self, data: dict, lookup: Optional[Union[str, dict]] = None, upsert: bool = True) -> str:
        """
        Creates a new document or updates an existing one.

        :param dict data: The document data to set.
        :param Optional[Union[str, dict]] lookup: The query to find an existing document. If None, a new document is created.
        :param bool upsert: If True (default), new data is merged with existing data. If False, the existing document is completely overwritten.
        :return: The primary key of the created or updated document.
        :rtype: str
        """
        payload = {"data": data, "lookup": lookup, "upsert": upsert}
        response = self._request("POST", "set", json=payload)
        return response.json()["id"]

    def set_batch(self, operations: List[Tuple[Dict, Union[str, Dict]]], upsert: bool = True):
        """
        Performs multiple 'set' operations in a batch.

        :param List[Tuple[Dict, Union[str, Dict]]] operations: A list of tuples, where each tuple contains (data, lookup) for a set operation.
        :param bool upsert: The upsert behavior to apply to all operations. Defaults to True.
        """
        payload = {"operations": operations, "upsert": upsert}
        self._request("POST", "set_batch", json=payload)

    def delete(self, lookup: Union[str, dict]) -> str:
        """
        Deletes a document from the collection.

        :param Union[str, dict] lookup: The query to find the document to delete.
        :return: The primary key of the deleted document.
        :rtype: str
        :raises DocumentNotFound: If no document matches the lookup query.
        """
        response = self._request("POST", "delete", json={"lookup": lookup})
        return response.json()["deleted_id"]

    def add_secondary_key(self, key_name: str):
        """
        Creates a new secondary key and builds an index for it from existing documents.

        :param str key_name: The field name to designate as a new secondary key.
        """
        self._request("POST", "add_secondary_key", json={"key_name": key_name})


class Interface:
    """
    Main entry point for interacting with the Dua API.
    """
    def __init__(self, url: str, token_provider: Optional[Union[str, Callable[[], Optional[str]]]] = None):
        """
        Initializes the Interface.

        :param str url: The base URL of the Dua server (e.g., http://127.0.0.1:5000).
        :param Optional[Union[str, Callable[[], Optional[str]]]] token_provider: An optional bearer token string, 
               or a function that returns a bearer token string (or None).
        """
        self.url = url
        if isinstance(token_provider, str):
            # If a static string is provided, wrap it in a callable
            self.token_provider = lambda: token_provider
        else:
            # Otherwise, assume it's a callable or None
            self.token_provider = token_provider
        
    def get_collection(self, collection_name: str) -> RemoteCollection:
        """
        Gets a RemoteCollection instance for interacting with a specific collection.

        :param str collection_name: The name of the collection.
        :return: An instance of RemoteCollection.
        :rtype: RemoteCollection
        """
        return RemoteCollection(self.url, collection_name, self.token_provider)
