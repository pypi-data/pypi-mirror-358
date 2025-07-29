from typing import Union, List, Optional, Dict, Callable, Tuple
from flask import Flask, Blueprint, request, jsonify
from .collection import Collection, DocumentNotFound, InvalidLookup, InitializationError, WriteError, LockingError
from functools import wraps

def token_authentication(token):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return False

    try:
        auth_type, provided_token = auth_header.split()
    except ValueError:
        return False

    if auth_type.lower() != 'bearer' or provided_token != token:
        return False
    
    return True

def server(
        collections: List[Collection], 
        is_blueprint: bool = False, 
        localhost_authentication: bool = True, 
        authentication_function: Callable = lambda: True
    ):
    if is_blueprint:
        server = Blueprint("dua", __name__)
    else:
        server = Flask(__name__)
        
    if not isinstance(collections, list):
        raise ValueError("The collections parameter should be a list of Collection objects.")
    
    for collection in collections:
        if not isinstance(collection, Collection):
            raise ValueError(f"The collections parameter should be a list of Collection objects (expected type Collection, got {type(collection)}).")
        
    def authentication(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            is_localhost = request.remote_addr in ('127.0.0.1', '::1')
            if is_localhost and not localhost_authentication:
                return f(*args, **kwargs)
            print(authentication_function())
            if authentication_function():
                return f(*args, **kwargs)
            else:
                return jsonify({"error": "Unauthorized"}), 401
        return decorated
    
    collections_index = {collection.name: collection for collection in collections}

    @server.errorhandler(DocumentNotFound)
    def handle_document_not_found(e):
        return jsonify({"error": str(e)}), 404

    @server.errorhandler(InvalidLookup)
    def handle_invalid_lookup(e):
        return jsonify({"error": str(e)}), 400

    @server.errorhandler(ValueError)
    def handle_value_error(e):
        return jsonify({"error": str(e)}), 400
        
    @server.errorhandler(WriteError)
    def handle_write_error(e):
        return jsonify({"error": str(e)}), 500

    @server.errorhandler(LockingError)
    def handle_locking_error(e):
        return jsonify({"error": str(e)}), 500

    @server.route("/<collection_name>/get_all", methods=['GET'])
    @authentication
    def get_all(collection_name):
        if collection_name in collections_index:
            return jsonify(collections_index[collection_name].get_all())
        return jsonify({"error": "Collection not found"}), 404

    @server.route("/<collection_name>/get", methods=['POST'])
    @authentication
    def get_doc(collection_name):
        if collection_name not in collections_index:
            return jsonify({"error": "Collection not found"}), 404
        
        body = request.get_json()
        if not body or 'lookup' not in body:
            return jsonify({"error": "Request body must contain 'lookup'"}), 400
        
        collection = collections_index[collection_name]
        doc = collection.get(body['lookup'])
        if doc:
            return jsonify(doc)
        return jsonify(None), 200 # Or 404, but returning null is also valid

    @server.route("/<collection_name>/get_many", methods=['POST'])
    @authentication
    def get_many_docs(collection_name):
        if collection_name not in collections_index:
            return jsonify({"error": "Collection not found"}), 404
        
        body = request.get_json()
        if not body or 'lookup' not in body:
            return jsonify({"error": "Request body must contain 'lookup'"}), 400

        collection = collections_index[collection_name]
        docs = collection.get_many(body['lookup'])
        return jsonify(docs)

    @server.route("/<collection_name>/get_batch", methods=['POST'])
    @authentication
    def get_batch_docs(collection_name):
        if collection_name not in collections_index:
            return jsonify({"error": "Collection not found"}), 404
        
        body = request.get_json()
        if not body or 'lookups' not in body:
            return jsonify({"error": "Request body must contain 'lookups'"}), 400

        collection = collections_index[collection_name]
        docs = collection.get_batch(body['lookups'])
        return jsonify(docs)

    @server.route("/<collection_name>/set", methods=['POST'])
    @authentication
    def set_doc(collection_name):
        if collection_name not in collections_index:
            return jsonify({"error": "Collection not found"}), 404
        
        body = request.get_json()
        if not body or 'data' not in body:
            return jsonify({"error": "Request body must contain 'data'"}), 400
        
        data = body['data']
        lookup = body.get('lookup')
        upsert = body.get('upsert', True)
        
        collection = collections_index[collection_name]
        doc_id = collection.set(data=data, lookup=lookup, upsert=upsert)
        return jsonify({"id": doc_id})

    @server.route("/<collection_name>/set_batch", methods=['POST'])
    @authentication
    def set_batch_docs(collection_name):
        if collection_name not in collections_index:
            return jsonify({"error": "Collection not found"}), 404

        body = request.get_json()
        if not body or 'operations' not in body:
            return jsonify({"error": "Request body must contain 'operations'"}), 400

        collection = collections_index[collection_name]
        collection.set_batch(operations=body['operations'], upsert=body.get('upsert', True))
        return jsonify({"status": "ok"})

    @server.route("/<collection_name>/delete", methods=['POST'])
    @authentication
    def delete_doc(collection_name):
        if collection_name not in collections_index:
            return jsonify({"error": "Collection not found"}), 404

        body = request.get_json()
        if not body or 'lookup' not in body:
            return jsonify({"error": "Request body must contain 'lookup'"}), 400

        collection = collections_index[collection_name]
        deleted_id = collection.delete(body['lookup'])
        return jsonify({"deleted_id": deleted_id})

    @server.route("/<collection_name>/add_secondary_key", methods=['POST'])
    @authentication
    def add_secondary_key(collection_name):
        if collection_name not in collections_index:
            return jsonify({"error": "Collection not found"}), 404

        body = request.get_json()
        if not body or 'key_name' not in body:
            return jsonify({"error": "Request body must contain 'key_name'"}), 400

        collection = collections_index[collection_name]
        collection.add_secondary_key(body['key_name'])
        return jsonify({"status": "ok"})

    return server
