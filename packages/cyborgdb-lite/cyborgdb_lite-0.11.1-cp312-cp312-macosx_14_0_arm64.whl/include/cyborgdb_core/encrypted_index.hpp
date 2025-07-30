#ifndef ENCRYPTED_INDEX_HPP_
#define ENCRYPTED_INDEX_HPP_

#include "logger.hpp"
#include "types.hpp"

#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

// Forward declarations
namespace cyborg_encrypted_index {
class Client;
class NewIndexConfig;
class ExistingIndexConfig;
class QueryResult;
}  // namespace cyborg_encrypted_index
namespace cyborg {
namespace internal {
class TelemetryAggregator;
struct QuantizerModels;
}  // namespace internal
namespace config {
struct QuantizerModels;
struct IndexConfig;
}  // namespace config
}  // namespace cyborg
// End of forward declarations

namespace cyborg {

/**
 * @brief Main class for Encrypted Index, providing methods for creating and interacting
 *        with an encrypted vector index.
 *
 * This class manages the lifecycle of a vector index, including creation, ingestion, and
 * retrieval of vector data. It supports different indexing methods such as IVF, IVFPQ, and
 * IVFFLAT, and can be configured to use different distance metrics.
 */
class EncryptedIndex {
   public:
    /**
     * @brief Destructor for EncryptedIndex.
     */
    ~EncryptedIndex();

    /**
     * @brief Construct a new EncryptedIndex object.
     *
     * This class provides functionality to create or load an encrypted index for secure vector
     * search.
     *
     * @param index_name A string representing the name of the index.
     * @param index_key A 32-byte array used as the encryption key for the index.
     * @param index_config Configuration settings specific to the index structure and properties
     * (used for new index creation).
     * @param db_config Database configuration, either for creating a new index or loading an
     * existing one.
     * @param path_prefix Path prefix for Python installs (optional).
     *
     * @note Overloads:
     * - The first constructor initializes a new encrypted index with specific configurations.
     * - The second constructor is used for loading an existing encrypted index with its
     * configuration.
     *
     * @todo Add overloads to handle scenarios:
     * - Without `items_location`.
     * - Without `device_config`. Target: v1.1.
     *
     * @todo Update `Location` enum in `cyborg-encrypted-index`:
     * - Change from `k(memory_type)` to all uppercase (e.g., `MEMORY_TYPE`) for consistency.
     * Target: v1.1.
     */
    EncryptedIndex(const std::string& index_name, const std::array<uint8_t, 32>& index_key,
                   const IndexConfig& index_config,
                   cyborg_encrypted_index::NewIndexConfig& db_config,
                   std::optional<std::string>& path_prefix, cyborg::Logger& logger,
                   std::shared_ptr<internal::TelemetryAggregator> telemetry_aggregator);

    EncryptedIndex(const std::string& index_name, const std::array<uint8_t, 32>& index_key,
                   cyborg_encrypted_index::ExistingIndexConfig& db_config,
                   std::optional<std::string>& path_prefix, cyborg::Logger& logger,
                   std::shared_ptr<internal::TelemetryAggregator> telemetry_aggregator);

    EncryptedIndex(const std::string& index_name, const std::array<uint8_t, 32>& index_key,
                   const IndexConfig& index_config,
                   cyborg_encrypted_index::NewIndexConfig& db_config,
                   internal::QuantizerModels& quantizer_models, bool is_trained,
                   std::optional<std::string>& path_prefix, cyborg::Logger& logger,
                   std::shared_ptr<internal::TelemetryAggregator> telemetry_aggregator);

    /**
     * @brief Ingests vectors into the index by performing quantization and adding items to the
     * encrypted index.
     *
     * This method performs quantization on the input vectors using the configured quantizers and
     * adds the quantized embeddings to the encrypted index. It handles different index types such
     * as IVF, IVFPQ, and IVFFLAT by applying the appropriate quantization strategy.
     *
     * @param ids Vector of ItemIDs that uniquely identify the items corresponding to the vectors.
     * @param vectors Array2D of floats representing the input vectors to be ingested.
     * @param contents A vector of vectors of uint8_t containing the item contents (optional).
     * @param json_metadata_array A vector of vectors of string containing the metadata (optional).
     * @throws If the vector dimensions do not match the index configuration or a runtime error
     * occurs.
     *
     * @todo Make `vector` const
     */
    void Upsert(const std::vector<cyborg::ItemID> ids, Array2D<float>& vectors,
                const std::vector<std::vector<uint8_t>> contents = {},
                const std::vector<std::string> json_metadata_array = {});

    /**
     * @brief Triggers an index build. Must be called after ingestion to finalize the index.
     *
     * Prior to calling this method, all queries will perform an exhaustive encrypted search,
     * which can be slow. After the index is built, queries will be much faster.
     *
     * @param training_config Training configuration for the index build (optional).
     */
    void TrainIndex(const TrainingConfig& training_config = TrainingConfig());

    /**
     * @brief Retrieves the top-k nearest neighbors for a set of queries from the encrypted index.
     *
     * @param query_vectors Array2D of query vector embeddings.
     * @param query_params Query parameters for the search (optional).
     * @return QueryResults A QueryResults object containing the decrypted ranked nearest neighbors
     * for each query.
     *
     * @note If this method is called prior to `TrainIndex` (i.e., `is_trained()` is false), it will
     * perform an exhaustive encrypted search, which can be slow.
     * @ todo Make `query_vectors` const
     */
    QueryResults Query(Array2D<float>& query_vectors,
                       const QueryParams& query_params = QueryParams());

    /**
     * @brief Retrieves and decrypts multiple items from the encrypted index.
     *
     * This function acts as a wrapper around the `RetrieveItems` function provided by the `Client`
     * class. It uses the client to fetch multiple encrypted items in a batch from the storage
     * system, decrypts each item, and returns the results as a vector of decrypted items.
     *
     * @param ids a vector of string ids to get from the database
     * @param include a vector of filters to let the cei what to return back

     * @return std::vector<Item> A vector containing the items
     */
    std::vector<Item> Get(const std::vector<std::string>& ids,
                          const std::vector<cyborg::ItemFields>& include);

    /**
     * @brief Deletes the index and all associated data. Proceed with caution.
     *
     * @throws std::runtime_error If index was not loaded or created, or if an error occurs.
     */
    void DeleteIndex();

    /**
     * @brief Deletes the entry with the ids givens
     * @param ids list of ids to delete
     *
     */
    void Delete(const std::vector<std::string>& ids);

    size_t NumVectors();

    // Getter methods

    /**
     * @brief Checks if the index has been trained.
     *
     * @return bool True if the index is trained, otherwise false.
     */
    bool is_trained() const { return is_trained_; }

    /**
     * @brief Gets the name of the index.
     *
     * @return std::string The name of the index.
     */
    std::string index_name() const { return index_name_; }

    /**
     * @brief Gets the index type.
     *
     * @return IndexType The type of the index.
     */
    IndexType index_type() const { return index_config_->index_type(); }

    /**
     * @brief Gets the configuration of the index.
     *
     * @return IndexConfig* A pointer to the index configuration.
     */
    IndexConfig* index_config() const { return index_config_.get(); }

    /**
     *
     * @todo Make TrainAndSerialize a private function
     */
    std::vector<uint8_t> TrainAndSerialize(Array2D<float>&, const TrainingConfig&, bool = true);

    // TODO - hide this as internal
    void TestPreFiltering() { test_flag_pre_filtering_ = true; }

   private:
    // Configuration for storage locations
    DeviceConfig device_config_;  ///< Configuration for the device used in vector search.
    std::string index_name_;      ///< The name of the index.
    std::unique_ptr<IndexConfig> index_config_;        ///< Pointer to the index configuration.
    std::array<uint8_t, 32> index_key_;                ///< The encryption key for the index.
    internal::QuantizerModels* quantizer_models_ptr_;  //< The coarse and pq models
    bool is_trained_;                                  ///< The training flag
    std::unique_ptr<cyborg_encrypted_index::Client>
        client_;  ///< Unique pointer to the client handling database communication and operations.
    bool test_flag_pre_filtering_ = false;
    Logger& logger_;
    std::shared_ptr<internal::TelemetryAggregator> telemetry_aggregator_;

    /**
     * Pre-filters centroids based on metadata constraints before retrieving neighbors.
     *
     * - Extracts unique metadata keys from the provided filter.
     * - Retrieves metadata buffers corresponding to these keys from the client.
     * - Converts retrieved metadata into structured maps.
     * - Uses a metadata query evaluator to filter centroids based on conditions.
     *
     * If no filters are applied, the original set of centroids is returned unchanged.
     *
     * @param filters A JSON object containing metadata-based filtering conditions.
     * @param query_centroids A vector of centroid IDs that are candidates for filtering.
     * @return A filtered list of centroid IDs that satisfy the metadata conditions.
     * @throws std::runtime_error If metadata retrieval fails or processing encounters an error.
     */

    std::pair<std::vector<uint32_t>, internal::QuantizerModels> PreFiltering(
        const std::string& filters);

    internal::QuantizerModels BuildFilteredQuantizers(
        const internal::QuantizerModels& original_quantizers,
        const std::vector<uint32_t>& filtered_centroids);

    /**
     * Updates the metadata stored in the index by extracting keys, merging with existing metadata,
     * and storing the updated data back in the client.
     *
     * - Parses metadata JSON strings into structured metadata centroids.
     * - Extracts unique metadata keys for querying existing metadata.
     * - Retrieves current metadata from the client.
     * - Updates metadata FlatBuffers and stores the new version back in the client.
     *
     * @param metadata_list A list of JSON metadata strings to be updated.
     * @param centroids A list of centroid IDs corresponding to the metadata entries.
     */
    void UpdateMetadata(std::vector<std::string>& metadata_list, std::vector<uint32_t>& centroids);

    /**
     * Filters a given QueryResult by metadata.
     *
     * @param candidates The full set of candidate results.
     * @param filters A JSON object representing the metadata filter.
     *
     * @return A new QueryResult containing only the candidates that pass the metadata filter.
     *
     * If the filters JSON is empty, the function returns the original candidates.
     */
    cyborg_encrypted_index::QueryResult PostFiltering(
        const cyborg_encrypted_index::QueryResult& candidates, const std::string& filters);

    void IngestTrained(Array2D<float>, const std::vector<ItemID>, std::vector<std::vector<uint8_t>>,
                       std::vector<std::string>);

    /**
     * @brief Ingests vectors into the index, if the index is not trained
     *
     * @param vectors Vector to be ingested
     * @param ids IDs corresponding to the vectors
     * @param items Items corresponding to the vectors
     * @param json_metadata_array A vector of vectors of string containing the metadata (optional).
     */
    void IngestUntrained(Array2D<float>, const std::vector<ItemID>,
                         std::vector<std::vector<uint8_t>>, std::vector<std::string>);

    /**
     * @brief Trains the product quantizers for the index.
     *
     * @param training_config Training configuration for the index build (optional).
     *
     * @todo Make the inputs const
     */
    void TrainQuantizers(Array2D<float>, const TrainingConfig&);

    /**
     * @brief Retrieves the top-k nearest neighbors for a set of queries via encrypted ANN search.
     *
     * @param query_vectors Query vector embeddings.
     * @param query_params Query parameters (optional).
     * @return QueryResults Ranked nearest neighbors for each query.
     *
     * @todo Implement return_items
     * @todo Make query_vectors const
     */
    QueryResults RetrieveTrained(Array2D<float>&, const QueryParams&);

    /**
     * @brief Retrieves the top-k nearest neighbors for a set of queries via encrypted exhaustive
     * search.
     *
     * @param query_vectors Query vector embeddings.
     * @param query_params Query parameters (optional).
     * @return QueryResults Ranked nearest neighbors for each query.
     *
     * @todo Implement return_items
     * @todo Make query_vectors const
     */
    QueryResults RetrieveUntrained(Array2D<float>&, const QueryParams&);

    /**
     * @brief Serializes the index config & quantizers in a FlatBuffer for storage.
     *
     * @return std::vector<uint8_t> FlatBuffer in a vector of bytes.
     */
    std::vector<uint8_t> SerializeIndexClass();

    /**
     * @brief Deserializes the index config & quantizers from a FlatBuffer, and applies them to the
     * class.
     *
     * @param serialized_config FlatBuffer in a vector of bytes.
     */
    void DeserializeIndexClass(const std::vector<uint8_t>& serialized_config);
};

namespace internal {

/**
 * @brief Deserializes a QuantizerModels object from a FlatBuffer.
 *
 * @param fb_quantizer_models Serialized FlatBuffer to deserialize.
 * @return QuantizerModels QuantizerModels object.
 */
QuantizerModels DeserializeQuantizerModels(
    const cyborg::config::QuantizerModels* fb_quantizer_models);

/**
 * @brief Deserializes an IndexConfig object from a FlatBuffer.
 *
 * @param fb_index_config Serialized FlatBuffer to deserialize.
 * @return IndexConfig IndexConfig object.
 */
std::unique_ptr<IndexConfig> DeserializeIndexConfig(const config::IndexConfig* fb_index_config);

}  // namespace internal
}  // namespace cyborg
#endif  // ENCRYPTED_INDEX_HPP_
