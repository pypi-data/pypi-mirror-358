import requests
import secrets
import json
from vecx.exceptions import raise_exception
from vecx.index import Index
from vecx.hybrid import HybridIndex
from vecx.user import User
from vecx.crypto import get_checksum
from vecx.utils import is_valid_index_name
from functools import lru_cache

SUPPORTED_REGIONS = ["us-west", "india-west", "local"]
class VectorX:
    def __init__(self, token:str|None=None):
        self.token = token
        self.region = "local"
        self.base_url = "http://127.0.0.1:8080/api/v1"
        # Token will be of the format user:token:region
        if token:
            token_parts = self.token.split(":")
            if len(token_parts) > 2:
                self.base_url = f"https://{token_parts[2]}.vectorxdb.ai/api/v1"
                self.token = f"{token_parts[0]}:{token_parts[1]}"
        self.version = 1

    def __str__(self):
        return self.token

    def set_token(self, token:str):
        self.token = token
        self.region = self.token.split (":")[1]
    
    def set_base_url(self, base_url:str):
        self.base_url = base_url
    
    def generate_key(self)->str:
        # Generate a random hex key of length 32
        key = secrets.token_hex(16)  # 16 bytes * 2 hex chars/byte = 32 chars
        print("Store this encryption key in a secure location. Loss of the key will result in the irreversible loss of associated vector data.\nKey: ",key)
        return key

    def create_index(self, name:str, dimension:int, space_type:str, M:int=16, key:str|None=None, ef_con:int=128, use_fp16:bool=True, version:int=None):
        if is_valid_index_name(name) == False:
            raise ValueError("Invalid index name. Index name must be alphanumeric and can contain underscores and less than 48 characters")
        if dimension > 10000:
            raise ValueError("Dimension cannot be greater than 10000")
        space_type = space_type.lower()
        if space_type not in ["cosine", "l2", "ip"]:
            raise ValueError(f"Invalid space type: {space_type}")
        headers = {
            'Authorization': f'{self.token}',
            'Content-Type': 'application/json'
        }
        data = {
            'index_name': name,
            'dim': dimension,
            'space_type': space_type,
            'M':M,
            'ef_con': ef_con,
            'checksum': get_checksum(key),
            'use_fp16': use_fp16,
            'version': version
        }
        response = requests.post(f'{self.base_url}/index/create', headers=headers, json=data)
        if response.status_code != 200:
            print(response.text)
            raise_exception(response.status_code, response.text)
        return "Index created successfully"

    def create_hybrid_index(self, name: str, dimension: int, vocab_size: int, space_type: str = "cosine", 
                           M: int = 16, key: str = None, ef_con: int = 128, use_fp16: bool = True, 
                           version: int = None):
        """
        Create a hybrid index that supports both dense and sparse vectors.
        
        Args:
            name: Index name (alphanumeric and underscores only, max 48 chars)
            dimension: Dimension of dense vectors
            vocab_size: Size of sparse vector vocabulary (e.g., 30522 for BERT)
            space_type: Distance metric ("cosine", "l2", "ip")
            M: HNSW graph connectivity parameter (default: 16)
            key: Encryption key (optional)
            ef_con: HNSW construction parameter (default: 128)
            use_fp16: Use half-precision storage (default: True)
            version: Index version (optional)
            
        Returns:
            Success message string
        """
        if not is_valid_index_name(name):
            raise ValueError("Invalid index name. Index name must be alphanumeric and can contain underscores and less than 48 characters")
        
        if dimension > 10000:
            raise ValueError("Dimension cannot be greater than 10000")
            
        if vocab_size <= 0 or vocab_size > 1000000:
            raise ValueError("Vocab size must be between 1 and 1,000,000")
            
        space_type = space_type.lower()
        if space_type not in ["cosine", "l2", "ip"]:
            raise ValueError(f"Invalid space type: {space_type}")
        
        headers = {
            'Authorization': f'{self.token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'index_name': name,
            'dim': dimension,
            'vocab_size': vocab_size,
            'space_type': space_type,
            'M': M,
            'ef_con': ef_con,
            'checksum': get_checksum(key),
            'use_fp16': use_fp16,
            'version': version
        }
        
        response = requests.post(f'{self.base_url}/hybrid/unified/create', headers=headers, json=data)
        
        if response.status_code not in [200, 201]:
            print(response.text)
            raise_exception(response.status_code, response.text)
        
        return "Hybrid index created successfully"

    def list_indexes(self):
        headers = {
            'Authorization': f'{self.token}',
        }
        response = requests.get(f'{self.base_url}/index/list', headers=headers)
        if response.status_code != 200:
            raise_exception(response.status_code, response.text)
        indexes = response.json()
        return indexes
    
    # TODO - Delete the index cache if the index is deleted
    def delete_index(self, name:str):
        headers = {
            'Authorization': f'{self.token}',
        }
        response = requests.delete(f'{self.base_url}/index/{name}/delete', headers=headers)
        if response.status_code != 200:
            print(response.text)
            raise_exception(response.status_code, response.text)
        return f'Index {name} deleted successfully'

    def delete_hybrid_index(self, name: str):
        """
        Delete a hybrid index.
        
        Args:
            name: Name of the hybrid index to delete
            
        Returns:
            Success message string
        """
        headers = {
            'Authorization': f'{self.token}',
        }
        
        response = requests.delete(f'{self.base_url}/hybrid/unified/{name}/delete', headers=headers)
        
        if response.status_code != 200:
            print(response.text)
            raise_exception(response.status_code, response.text)
        
        return f'Hybrid index {name} deleted successfully'

    # Keep in lru cache for sometime
    @lru_cache(maxsize=10)
    def get_index(self, name:str, key:str|None=None):
        headers = {
            'Authorization': f'{self.token}',
            'Content-Type': 'application/json'
        }
        # Get index details from the server
        response = requests.get(f'{self.base_url}/index/{name}/info', headers=headers)
        if response.status_code != 200:
            raise_exception(response.status_code, response.text)
        data = response.json()
        #print(data)
        #print(data)
        # Raise error if checksum does not match
        checksum = get_checksum(key)
        if checksum != data['checksum']:
            raise_exception(403, "Checksum does not match. Please check the key.")
        idx = Index(name=name, key=key, token=self.token, url=self.base_url, version=self.version, params=data)
        return idx

    @lru_cache(maxsize=10)
    def get_hybrid_index(self, name: str, key: str = None):
        """
        Get a hybrid index instance for operations.
        
        Args:
            name: Name of the hybrid index
            key: Encryption key (optional, not used for hybrid indexes as encryption is disabled)
            
        Returns:
            HybridIndex instance for performing operations
        """
        headers = {
            'Authorization': f'{self.token}',
            'Content-Type': 'application/json'
        }
        
        # Get hybrid index details from the server
        # Note: We'll try to get info from the regular index endpoint first
        # If that doesn't work, we may need a dedicated hybrid info endpoint
        try:
            response = requests.get(f'{self.base_url}/index/{name}/info', headers=headers)
            if response.status_code == 200:
                data = response.json()
                # Check if this is a hybrid index by looking for vocab_size
                if 'vocab_size' not in data:
                    # Try hybrid-specific endpoint if available
                    response = requests.get(f'{self.base_url}/hybrid/unified/{name}/info', headers=headers)
                    if response.status_code == 200:
                        data = response.json()
                    else:
                        # Assume it's a hybrid index with default vocab_size
                        data['vocab_size'] = 30522
            else:
                raise_exception(response.status_code, response.text)
        except Exception as e:
            # Fallback: create a basic hybrid index object with minimal parameters
            data = {
                'dimension': 128,  # default
                'vocab_size': 30522,  # default
                'space_type': 'cosine',
                'M': 16,
                'use_fp16': False,
                'total_elements': 0,
                'lib_token': None,
                'checksum': get_checksum(key) if key else -1  # Default checksum when no key
            }
        
        # No encryption validation needed for hybrid indexes
        # Encryption is disabled, so we don't validate the checksum
        
        # Create hybrid index instance
        hybrid_idx = HybridIndex(
            name=name, 
            key=key, 
            token=self.token, 
            url=self.base_url, 
            version=self.version, 
            params=data
        )
        
        return hybrid_idx
    
    def get_user(self):
        return User(self.base_url, self.token)

