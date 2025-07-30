"""
Pybind11 bindings for CyborgDB
"""
from __future__ import annotations
import numpy
import pybind11_stubgen.typing_ext
import typing
__all__ = ['Client', 'DBConfig', 'EncryptedIndex', 'IndexConfig', 'IndexIVFFlat', 'Logger', 'set_working_dir']
class Client:
    def __init__(self, api_key: str, index_location: DBConfig, config_location: DBConfig, items_location: DBConfig = ..., cpu_threads: int = 0, gpu_accelerate: bool = False) -> None:
        """
        Initialize a new instance of Client.
        
                    Parameters:
                        api_key (str): API key for your CyborgDB account.
                        index_location (DBConfig): Configuration for index storage location.
                        config_location (DBConfig): Configuration for index metadata storage.
                        items_location (DBConfig, optional): Configuration for future item storage. Pass DBConfig with Location.NONE.
                        cpu_threads (int, optional): Number of CPU threads to use, max 4 cores with the lite version.
        
                    Raises:
                        ValueError: If cpu_threads is less than 0, if any DBConfig is invalid, if the backing store is not available,
                        or if the Client could not be initialized.
        
                    Example:
                        >>> api_key = "your_api_key"
                        >>> index_location = DBConfig("memory")
                        >>> config_location = DBConfig("postgres", connection_string="host:127.0.0.1,port:6379,db:0")
                        >>> items_location = DBConfig("none")
                        >>> client = Client(index_location, config_location, items_location, cpu_threads=4)
        """
    def create_index(self, index_name: str, 
                    index_key: typing.Annotated[list[int], pybind11_stubgen.typing_ext.FixedSize(32)], 
                    index_config: IndexConfig, 
                    embedding_model: str | None = None, 
                    max_cache_size: int | None = 0,
                    logger: Logger | None = None) -> EncryptedIndex:
        """
        Creates and returns a new encrypted index based on the provided configuration.
        
        Parameters:
            index_name (str): Name of the index to create (must be unique).
            index_key (bytes): 32-byte encryption key for the index, used to secure index data.
            index_config (IndexConfig): Configuration for the index type (IndexIVFFlat only with the lite version).
            embedding_model (str, optional): Name of the SentenceTransformer model to use for text embeddings.
            max_cache_size (int, optional): Maximum size for the local cache. Defaults to 0.
            logger (Logger, optional): Logger instance for capturing operation logs. Defaults to None.
        
        Returns:
            EncryptedIndex: A pointer to the newly created index.
        
        Raises:
            ValueError: If the index name is not unique, if the index configuration is invalid, 
                        or if the index could not be created.
        """
    def list_indexes(self) -> list[str]:
        """
        Returns a list of all encrypted index names accessible via the client.
        
                    Returns:
                        list[str]: A list of index names.
        
                    Raises:
                        ValueError: If the list of indexes could not be retrieved.
        
                    Example:
                        >>> indexes = client.list_indexes()
                        >>> for name in indexes:
                        ...     print(name)
        """
    def load_index(self, index_name: str, 
                  index_key: typing.Annotated[list[int], pybind11_stubgen.typing_ext.FixedSize(32)], 
                  max_cache_size: int | None = 0,
                  logger: Logger | None = None) -> EncryptedIndex:
        """
        Loads an existing encrypted index and returns an instance of EncryptedIndex.
        
        Parameters:
            index_name (str): Name of the index to load.
            index_key (bytes): 32-byte encryption key for the index, used to secure index data.
            max_cache_size (int, optional): Maximum size for the local cache. Defaults to 0.
            logger (Logger, optional): Logger instance for capturing operation logs. Defaults to None.
        
        Returns:
            EncryptedIndex: A pointer to the loaded index.
        
        Raises:
            ValueError: If the index name does not exist, if the index could not be loaded or decrypted.
        """
    def load_serialized_index(self, serialized_index: bytes, index_key: typing.Annotated[list[int], pybind11_stubgen.typing_ext.FixedSize(32)]) -> ...:
        """
        Internal method to load an encrypted index from serialized data.
        """
class DBConfig:
    def __init__(self, location: str, table_name: str | None = None, connection_string: str | None = None) -> None:
        ...
class EncryptedIndex:
    def delete(self, ids: list[str]) -> None:
        """
        Deletes the specified encrypted items stored in the index.
        
                    Removes all associated fields (vector, contents, metadata) for the given IDs.
        
                    Warning:
                        This action is irreversible. Proceed with caution.
        
                    Parameters:
                        ids (list[str]): IDs to delete.
        
                    Raises:
                        ValueError: If the items could not be deleted.
        
                    Example:
                        >>> index.delete(["item_1", "item_2"])
        """
    def delete_index(self) -> None:
        """
        Deletes the current index and all its associated data.
        
                    Warning:
                        This action is irreversible. Proceed with caution.
        
                    Raises:
                        ValueError: If the index could not be deleted.
        
                    Example:
                        >>> index.delete_index()
        """
    def get(self, ids: list[str], include: list[str] = ['vector', 'contents', 'metadata']) -> list:
        """
        Retrieves and decrypts items associated with the specified IDs.
        
                    Parameters:
                        ids (list[str]): IDs to retrieve.
                        include (list[str], optional): List of item fields to return. Can include 'vector', 'contents', 
                                                    and 'metadata'. Defaults to ['vector', 'contents', 'metadata'].
        
                    Returns:
                        list[dict]: Decrypted items with requested fields. IDs will always be included in the returned items.
        
                    Raises:
                        ValueError: If the items could not be retrieved or decrypted.
        
                    Example:
                        >>> items = index.get(["item_1", "item_2"], include=["contents"])
                        >>> for item in items:
                        ...     print(f"ID: {item['id']}")
        """
    def index_config(self) -> dict:
        """
        Gets the configuration of the index.
        
                    Returns:
                        dict: A dictionary containing the configuration of the index with the following keys:
                            - 'dimension': The dimensionality of the vectors.
                            - 'metric': The distance metric used (e.g., 'euclidean', 'cosine').
                            - 'index_type': The type of the index (e.g., 'ivf', 'ivfpq', 'ivfflat').
                            - 'n_lists': The number of inverted lists in the index.
                            - 'pq_dim': The PQ dimension (if applicable).
                            - 'pq_bits': The PQ bits (if applicable).
        """
    def index_name(self) -> str:
        """
        Get the name of the index.
        
        Returns:
            str: The name of the index.
        """
    def index_type(self) -> str:
        """
        Gets the index type.
        
                    Returns:
                        str: The type of the index (e.g., 'ivf', 'ivfpq', or 'ivfflat').
        """
    def is_trained(self) -> bool:
        """
        Checks if the index has been trained.
        
                    Returns:
                        bool: True if the index is trained, otherwise False.
        """
    def query(self, query_vector: typing.Any = None, query_contents: typing.Any = None, top_k: int = 100, n_probes: int = 1, filters: dict = {}, include: list[str] = ['distance', 'metadata'], greedy: bool = False) -> list:
        """
        Retrieves the nearest neighbors for given query vectors.
        
                    Parameters:
                        query_vectors (Union[np.ndarray, list], optional): Query vectors to search. Can be a 1D array for a single query
                                                                or a 2D array for multiple queries.
                        query_contents (str, optional): Text contents to search if auto-embedding is enabled. Defaults to None.
                        top_k (int, optional): Number of nearest neighbors to return for each query. Defaults to 100.
                        n_probes (int, optional): Number of lists to probe during the query. Defaults to 1.
                        filters (dict, optional): JSON-like dictionary specifying metadata filters. Defaults to {}.
                        include (list[str], optional): List of fields to include in results. Can contain "distance", "metadata". 
                                                    Defaults to ["distance", "metadata"].
                        greedy (bool, optional): Whether to use greedy search. Defaults to False.
        
                    Returns:
                        Union[list[dict], list[list[dict]]]: For a single query, returns a list of dictionaries where each 
                        dictionary contains 'id', 'distance', and optionally 'metadata'. For multiple queries, returns a list 
                        of such lists.
        
                    Raises:
                        ValueError: If the query vectors have incompatible dimensions with the index,
                                    if the index was not created or loaded yet, or if the query could not be executed.
                        TypeError: If query_vectors is not a 1D or 2D NumPy array or List[List[float]].
        
                    Note:
                        If this function is called on an index where train() has not been executed, the query will
                        use encrypted exhaustive search, which may be slower.
        
                    Example:
                        >>> # Single query
                        >>> results = index.query([0.1, 0.2, 0.3], top_k=5, n_probes=2)
                        >>> for r in results:
                        ...     print(f"ID: {r['id']}, Distance: {r['distance']}")
                        >>> 
                        >>> # Multiple queries with filters
                        >>> results = index.query([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]], 
                        ...                       filters={"type": "image"})
        """
    def train(self, batch_size: int = 2048, max_iters: int = 100, tolerance: float = 1e-06, max_memory: int = 0) -> None:
        """
        Builds the index using the specified training configuration.
        
                    Prior to calling this, all queries will be conducted using encrypted exhaustive search.
                    After, they will be conducted using encrypted ANN search.
        
                    Parameters:
                        batch_size (int, optional): Size of each batch for training. Default is 2048.
                        max_iters (int, optional): Maximum iterations for training. Default is 100.
                        tolerance (float, optional): Convergence tolerance for training. Default is 1e-6.
                        max_memory (int, optional): Maximum memory (MB) usage during training. Default is 0 (no limit).
        
                    Note:
                        There must be at least 2 * n_lists vector embeddings in the index prior to calling this function.
        
                    Raises:
                        ValueError: If there are not enough vector embeddings in the index for training, 
                                    or if the index could not be trained.
        
                    Example:
                        >>> index.train(batch_size=128, max_iters=10, tolerance=1e-4, max_memory=1024)
        """
    def train_and_serialize(self, vectors: numpy.ndarray[numpy.float32], batch_size: int = 0, max_iters: int = 0, tolerance: float = 1e-06, max_memory: int = 0, delete_index: bool = True) -> bytes:
        """
        Internal function to train the index and serialize it to a bytes object.
        """
    def upsert(self, arg1: typing.Any, arg2: typing.Any = None) -> None:
        """
        Adds or updates vector embeddings in the index.
        
                    If an item already exists at the specified ID, it will be overwritten.
        
                    This method can be called in one of two ways:
                    1. With a list of dictionaries, each containing 'id', 'vector', and optional 'contents' and 'metadata'.
                        - If the index was created with an embedding model and 'vector' is not provided, 'contents' will be
                            automatically embedded using that model in an efficient batch operation.
                    2. With separate IDs and vectors arrays.
        
                    Parameters:
                        arg1: Either a list of dictionaries or a list/array of IDs.
                        arg2 (optional): If arg1 is a list of IDs, this should be an array of vector embeddings.
        
                    Raises:
                        ValueError: If vector dimensions are incompatible with the index configuration,
                                    if index was not created or loaded yet, if there is a mismatch between
                                    the number of vectors, IDs, contents or metadata, or if the vectors
                                    could not be upserted.
                        TypeError: If the arguments do not match expected types.
        
                    Example:
                        >>> # Method 1: List of dictionaries
                        >>> items = [
                        ...     {"id": "item_1", "vector": [0.1, 0.2, 0.3], "contents": b"abc", "metadata": {"type": "image"}},
                        ...     {"id": "item_2", "vector": [0.4, 0.5, 0.6], "contents": b"def", "metadata": {"type": "text"}}
                        ... ]
                        >>> index.upsert(items)
                        >>> 
                        >>> # Method 2: Separate IDs and vectors
                        >>> ids = ["item_1", "item_2"]
                        >>> vectors = np.array([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]], dtype=np.float32)
                        >>> index.upsert(ids, vectors)
        """
class IndexConfig:
    """
    Abstract base class for index configurations. This class provides the core properties of an index configuration, including dimension, distance metric and index type
    """
    def clone(self) -> IndexConfig:
        """
        Clone this IndexConfig object.
        
        Returns:
            IndexConfig: A unique pointer to a cloned IndexConfig object.
        """
    def n_lists(self) -> int:
        """
        Get the number of lists (coarse clusters) in the index.
        
        Returns:
            int: The number of lists, relevant for certain index types (e.g., IVF, IVFPQ).
        """
    def pq_bits(self) -> int:
        """
        Get the number of bits per PQ code, if applicable.
        
        Returns:
            int: The number of bits per PQ code, or 0 if not applicable.
        """
    def pq_dim(self) -> int:
        """
        Get the Product Quantization (PQ) dimension, if applicable.
        
        Returns:
            int: The PQ dimension, or 0 if not applicable.
        """
    @property
    def dimension(self) -> int:
        """
        Get the vector dimensionality.
        
        Returns:
            int: The dimensionality of the vectors stored in the index.
        """
    @property
    def index_type(self) -> str:
        """
        Get the index type as a lowercase string.
        
        Returns:
            str: The type of the index (e.g., 'ivf', 'ivfpq', 'ivfflat').
        """
    @property
    def metric(self) -> str:
        """
        Get the distance metric used in the index.
        
        Returns:
            string: The distance metric (euclidean, cosine, or squared_euclidean).
        """
class IndexIVFFlat(IndexConfig):
    """
    Configuration for an IVFFlat index, which uses flat quantization for coarse clustering.
    """
    def __init__(self, dimension: int, n_lists: int, metric: str = 'euclidean') -> None:
        """
        Initialize the IVFFlat index configuration.
        
        Parameters:
            dimension (int): Dimensionality of the vectors.
            n_lists (int): Number of coarse clusters (lists).
            metric (string): Distance metric (euclidean, cosine, or squared_euclidean), default is euclidean.
        """
    def n_lists(self) -> int:
        """
        Get the number of lists in the IVFFlat index.
        
        Returns:
            int: The number of coarse clusters (lists) in the index.
        """


class Logger:
    @staticmethod
    def instance() -> 'Logger':
        """
        Returns the singleton instance of the logger.
        
        Returns:
            Logger: The singleton logger instance.
        """
        ...
    
    def configure(self, level: str, to_file: bool = False, file_path: str | None = None) -> None:
        """
        Configure the logger instance.
        
        Args:
            level (str): Log level ("debug", "info", "warning", "error", "critical").
            to_file (bool): Whether to write logs to a file.
            file_path (str, optional): Path to the log file.
        """
        ...
    
    def info(self, message: str) -> None:
        """
        Log a message at INFO level.
        
        Args:
            message (str): The message to log.
        """
        ...
    
    def debug(self, message: str) -> None:
        """
        Log a message at DEBUG level.
        
        Args:
            message (str): The message to log.
        """
        ...
    
    def warning(self, message: str) -> None:
        """
        Log a message at WARNING level.
        
        Args:
            message (str): The message to log.
        """
        ...
    
    def error(self, message: str) -> None:
        """
        Log a message at ERROR level.
        
        Args:
            message (str): The message to log.
        """
        ...
    
    def critical(self, message: str) -> None:
        """
        Log a message at CRITICAL level.
        
        Args:
            message (str): The message to log.
        """
        ...

def set_working_dir(path: str) -> None:
    """
    Sets the working directory for the CyborgDB client.
    
    Parameters:
        path (str): Path to the working directory.
    """