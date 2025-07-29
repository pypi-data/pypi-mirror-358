from typing import Union, List, Optional, Dict, Callable, Tuple
from pathlib import Path
import json
import time
import os


class CollectionError(Exception):
    """Base exception class for the Collection."""
    pass

class DocumentNotFound(CollectionError):
    """Raised when a document cannot be found."""
    pass

class InvalidLookup(CollectionError):
    """Raised when the type of a lookup is invalid."""
    pass

class InitializationError(CollectionError):
    """Raised on errors during collection initialization."""
    pass

class WriteError(CollectionError):
    """Raised when a file write operation fails."""
    pass

class LockingError(CollectionError):
    """Raised when acquiring a lock fails."""
    pass


class Collection:
    """
    Manages a collection of JSON documents stored as individual files in a directory.
    Provides methods for creating, retrieving, updating, and deleting documents,
    as well as support for secondary key indexing for faster lookups.
    """

    def __init__(self, name: str, directory: str, primary_key: str = "_id", timestamp_documents: bool = True, primary_key_generation: Optional[Callable] = None):
        """
        Initializes a new or existing Collection instance.

        :param str name: The name of the collection. This will also be the directory name.
        :param str directory: The root directory where the collection will be stored.
        :param str primary_key: The field name to use as the primary key for documents. Defaults to "_id".
        :param bool timestamp_documents: If True, automatically adds 'created_at' and 'updated_at' unix timestamps to documents. Defaults to True.
        :param Optional[Callable] primary_key_generation: A function to call to generate a new primary key when one is not provided.
        :raises InitializationError: If the provided directory is invalid.
        """
        root_directory_path = Path(directory)
        if not root_directory_path.is_dir():
            raise InitializationError("Invalid directory provided. It must be an existing directory.")

        self.path = root_directory_path / name
        self.path.mkdir(parents=True, exist_ok=True)
        self.data_folder = self.path / ".dua"
        self.data_folder.mkdir(exist_ok=True)

        self.name = name
        self.primary_key = primary_key
        self.timestamp_documents = timestamp_documents
        self.primary_key_generation = primary_key_generation
        self.secondary_keys = self._load_secondary_keys()

    def _load_secondary_keys(self) -> List[str]:
        """
        Loads the list of secondary key names from the index files in the .dua directory.

        :return: A list of secondary key names.
        :rtype: List[str]
        """
        return [f.stem.replace('.index', '') for f in self.data_folder.glob("*.index.json")]

    def _lock_index(self, key_name: str, timeout: int = 5) -> Path:
        """
        Creates a lock for a given index to prevent race conditions during writes.
        This is done by creating a directory, which is an atomic operation on most filesystems.

        :param str key_name: The name of the secondary key to lock.
        :param int timeout: The number of seconds to wait to acquire the lock.
        :return: The path to the lock directory.
        :rtype: Path
        :raises LockingError: If the lock cannot be acquired within the timeout period.
        """
        lock_path = self.data_folder / f"{key_name}.index.lock"
        start_time = time.monotonic()
        while True:
            try:
                os.mkdir(lock_path)
                return lock_path
            except FileExistsError:
                if time.monotonic() - start_time > timeout:
                    raise LockingError(f"Could not acquire lock for index '{key_name}' after {timeout} seconds.")
                time.sleep(0.1)

    def _unlock_index(self, lock_path: Path):
        """
        Releases the lock on an index file by removing the lock directory.

        :param Path lock_path: The path to the lock directory to release.
        """
        try:
            if lock_path.is_dir():
                os.rmdir(lock_path)
        except OSError:
            # This can happen in rare race conditions, but it's safe to ignore.
            pass

    def _read_index(self, key_name: str) -> Dict:
        """
        Reads the contents of a secondary key index file.

        :param str key_name: The name of the secondary key index to read.
        :return: A dictionary containing the index data. Returns an empty dict if the index doesn't exist or is corrupted.
        :rtype: Dict
        """
        index_path = self.data_folder / f"{key_name}.index.json"
        if not index_path.exists():
            return {}
        try:
            with open(index_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}

    def _write_index(self, key_name: str, index_data: Dict):
        """
        Writes data to a secondary key index file.

        :param str key_name: The name of the secondary key index to write to.
        :param Dict index_data: The dictionary of data to write to the index.
        """
        index_path = self.data_folder / f"{key_name}.index.json"
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(index_data, f, indent=4)

    def _update_indexes(self, doc_id: str, old_data: Optional[Dict], new_data: Dict):
        """
        Updates all secondary key indexes based on changes to a document.

        :param str doc_id: The primary key of the document being updated.
        :param Optional[Dict] old_data: The document's data before the update. None for new documents.
        :param Dict new_data: The document's data after the update.
        """
        for key in self.secondary_keys:
            old_value = old_data.get(key) if old_data else None
            new_value = new_data.get(key)
            if old_value == new_value:
                continue

            lock_path = None
            try:
                lock_path = self._lock_index(key)
                index = self._read_index(key)
                if old_value is not None:
                    value_str = str(old_value)
                    if value_str in index and doc_id in index[value_str]:
                        index[value_str].remove(doc_id)
                        if not index[value_str]:
                            del index[value_str]
                
                if new_value is not None:
                    value_str = str(new_value)
                    if value_str not in index:
                        index[value_str] = []
                    if doc_id not in index[value_str]:
                        index[value_str].append(doc_id)
                self._write_index(key, index)
            finally:
                if lock_path:
                    self._unlock_index(lock_path)

    def _remove_from_indexes(self, doc_data: Dict):
        """
        Removes a document's entries from all secondary key indexes.

        :param Dict doc_data: The data of the document being deleted.
        """
        doc_id = doc_data.get(self.primary_key)
        if not doc_id:
            return
            
        for key in self.secondary_keys:
            if key in doc_data:
                value = doc_data[key]
                lock_path = None
                try:
                    lock_path = self._lock_index(key)
                    index = self._read_index(key)
                    value_str = str(value)
                    if value_str in index and doc_id in index[value_str]:
                        index[value_str].remove(doc_id)
                        if not index[value_str]:
                            del index[value_str]
                        self._write_index(key, index)
                finally:
                    if lock_path:
                        self._unlock_index(lock_path)

    def add_secondary_key(self, key_name: str):
        """
        Creates a new secondary key and builds an index for it from existing documents.

        :param str key_name: The field name to designate as a new secondary key.
        """
        if key_name in self.secondary_keys:
            return
        
        lock_path = None
        try:
            lock_path = self._lock_index(key_name)
            index = {}
            for filepath in self.path.glob("*.json"):
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        doc = json.load(f)
                    if key_name in doc:
                        value = str(doc[key_name])
                        doc_id = doc[self.primary_key]
                        if value not in index:
                            index[value] = []
                        index[value].append(doc_id)
                except (json.JSONDecodeError, IOError, KeyError):
                    # Ignore corrupted files or docs missing a primary key
                    continue
        finally:
            if lock_path:
                self._unlock_index(lock_path)

    def get_all(self) -> List[Dict]:
        """
        Retrieves all documents from the collection.

        :return: A list of dictionaries, where each dictionary is a document.
        :rtype: List[Dict]
        """
        docs = []
        for filepath in self.path.glob("*.json"):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    docs.append(json.load(f))
            except (json.JSONDecodeError, IOError):
                continue
        return docs

    def _get_from_index(self, lookup: Dict) -> Optional[List[str]]:
        """
        Uses secondary key indexes to find potential matching document IDs.

        :param Dict lookup: The query dictionary.
        :return: A list of document IDs that might match, or None if no relevant indexes are used.
        :rtype: Optional[List[str]]
        """
        indexed_lookups = {k: v for k, v in lookup.items() if k in self.secondary_keys}
        if not indexed_lookups:
            return None

        doc_id_sets = []
        for key, value in indexed_lookups.items():
            index = self._read_index(key)
            doc_ids = index.get(str(value), [])
            doc_id_sets.append(set(doc_ids))

        if not doc_id_sets:
            return []
            
        final_ids = set.intersection(*doc_id_sets)
        return list(final_ids)

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
        if isinstance(lookup, str):
            document_path = self.path / (lookup + ".json")
            try:
                with open(document_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                return None

        if isinstance(lookup, dict):
            if not lookup:
                return None
            
            doc_ids = self._get_from_index(lookup)
            
            if doc_ids is not None:
                # Indexed search
                for doc_id in doc_ids:
                    doc = self.get(doc_id)
                    if doc and all(doc.get(key) == value for key, value in lookup.items()):
                        return doc
                return None

            # Full scan (fallback)
            for filepath in self.path.glob("*.json"):
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if all(data.get(key) == value for key, value in lookup.items()):
                        return data
                except (json.JSONDecodeError, IOError):
                    continue
            return None

        raise InvalidLookup(f"lookup must be a string or a dictionary, not {type(lookup)}")

    def get_many(self, lookup: Dict) -> List[Dict]:
        """
        Retrieves all documents that match a given lookup dictionary.

        :param Dict lookup: The query dictionary to match against documents.
        :return: A list of matching documents.
        :rtype: List[Dict]
        :raises InvalidLookup: If the lookup is not a dictionary.
        """
        if not isinstance(lookup, dict):
            raise InvalidLookup(f"lookup must be a dictionary, not {type(lookup)}")
        if not lookup:
            return []

        doc_ids = self._get_from_index(lookup)
        found_docs = []

        target_files = [self.path / (doc_id + ".json") for doc_id in doc_ids] if doc_ids is not None else self.path.glob("*.json")
        
        for filepath in target_files:
            if not filepath.exists():
                continue
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if all(data.get(key) == value for key, value in lookup.items()):
                    found_docs.append(data)
            except (json.JSONDecodeError, IOError):
                continue
        return found_docs

    def get_batch(self, lookups: List[Union[str, dict]]) -> List[Dict]:
        """
        Retrieves multiple documents based on a list of lookups.

        :param List[Union[str, dict]] lookups: A list of primary keys or lookup dictionaries.
        :return: A list of found documents. Duplicates may be included if lookups match the same document.
        :rtype: List[Dict]
        """
        found_docs = []
        for lookup in lookups:
            doc = self.get(lookup)
            if doc:
                found_docs.append(doc)
        return found_docs

    def _write_document(self, filepath: Path, data: dict):
        """
        Serializes and writes a document's data to a file.

        :param Path filepath: The path to the file to be written.
        :param dict data: The data to write.
        :raises WriteError: If the data is not serializable or the file cannot be written.
        """
        try:
            json_data = json.dumps(data, indent=4)
        except TypeError as e:
            raise WriteError(f"Data contains non-serializable types: {e}") from e

        try:
            with open(filepath, "w", encoding="utf-8") as file:
                file.write(json_data)
        except IOError as e:
            raise WriteError(f"Failed to write document to {filepath}: {e}") from e

    def set(self, data: dict, lookup: Optional[Union[str, dict]] = None, upsert: bool = True) -> str:
        """
        Creates a new document or updates an existing one.

        :param dict data: The document data to set.
        :param Optional[Union[str, dict]] lookup: The query to find an existing document. If None, a new document is created.
        :param bool upsert: If True (default), new data is merged with existing data. If False, the existing document is completely overwritten.
        :return: The primary key of the created or updated document.
        :rtype: str
        :raises ValueError: If a new document is created without a primary key or a generation function.
        :raises ValueError: If no lookup is supplied but there is a primary key in the supplied data.
        :raises ValueError: If the primary key in the supplied data doesn't match the result of getting the data with the lookup.
        """
        if data.get(self.primary_key) and not lookup:
            raise ValueError(f"To create or update a document with a specific ID, pass the ID in the 'lookup' parameter, not in the data. ({data.get(self.primary_key)} was the primary key of the supplied data, but no lookup was provided)")
        
        existing_doc = self.get(lookup) if lookup else None
        if lookup and not existing_doc and isinstance(lookup, dict):
            raise ValueError(
                f"Query {lookup} did not match any documents. "
                "To create a new document, either provide its primary key as a string in the "
                "lookup parameter or call set() with no lookup at all."
            )
        doc_id = None
        
        if existing_doc:
            doc_id = existing_doc[self.primary_key]
            
            if self.primary_key in data:
                if data[self.primary_key] != doc_id:
                    raise ValueError(f"Cannot change the primary key of an existing document. Attempted to change '{doc_id}' to '{data[self.primary_key]}'.")
                data.pop(self.primary_key, None)
            
            updated_data = {**existing_doc, **data} if upsert else {**data, self.primary_key: doc_id}
            if self.timestamp_documents and "updated_at" not in updated_data:
                updated_data["updated_at"] = time.time()
        else:
            if isinstance(lookup, str):
                doc_id = lookup
            elif self.primary_key in data:
                doc_id = data[self.primary_key]
            elif self.primary_key_generation:
                doc_id = str(self.primary_key_generation())
            else:
                raise ValueError("Cannot create new document: no primary key provided in data or lookup, and no primary_key_generation function is set.")
            
            updated_data = data.copy()
            updated_data[self.primary_key] = doc_id
            if self.timestamp_documents and "created_at" not in updated_data:
                updated_data["created_at"] = time.time()
        
        document_path = self.path / (str(doc_id) + ".json")
        self._write_document(document_path, updated_data)
        self._update_indexes(str(doc_id), existing_doc, updated_data)
        
        return str(doc_id)

    def set_batch(self, operations: List[Tuple[Dict, Union[str, Dict]]], upsert: bool = True):
        """
        Performs multiple 'set' operations in a batch.

        :param List[Tuple[Dict, Union[str, Dict]]] operations: A list of tuples, where each tuple contains (data, lookup) for a set operation.
        :param bool upsert: The upsert behavior to apply to all operations. Defaults to True.
        """
        for data, lookup in operations:
            self.set(data, lookup, upsert=upsert)

    def delete(self, lookup: Union[str, dict]) -> str:
        """
        Deletes a document from the collection.

        :param Union[str, dict] lookup: The query to find the document to delete.
        :return: The primary key of the deleted document.
        :rtype: str
        :raises DocumentNotFound: If no document matches the lookup query.
        """
        doc_to_delete = self.get(lookup)
        if not doc_to_delete:
            raise DocumentNotFound("Document not found for the given lookup.")
        
        doc_id = doc_to_delete[self.primary_key]
        document_path = self.path / (str(doc_id) + ".json")
        
        if document_path.exists():
            # 1. Delete the file first to make it inaccessible
            document_path.unlink() 
            # 2. Then remove it from the indexes
            self._remove_from_indexes(doc_to_delete)
            return str(doc_id)
        else:
            # This case is unlikely if get() is working correctly but serves as a safeguard.
            raise DocumentNotFound("Document file path not found after being located by get().")
