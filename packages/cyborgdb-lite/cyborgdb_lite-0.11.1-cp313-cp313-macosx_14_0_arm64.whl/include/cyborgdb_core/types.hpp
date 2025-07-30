#ifndef CVS_TYPES_HPP_
#define CVS_TYPES_HPP_

#include "cyborg_common_types.hpp"

#include <array>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <memory>
#include <optional>
#include <string>
#include <vector>

namespace cyborg {

/**
 * @brief Configuration class for the device used in vector search operations.
 *
 * This class holds the configuration details for the device, such as the number of CPU threads
 * and whether to accelerate computations using a GPU.
 *
 * @todo Change this to a struct, as it's just a collection of data members
 */
class DeviceConfig {
   public:
    /**
     * @brief Construct a new DeviceConfig object.
     *
     * @param cpu_threads Number of CPU threads to use (default is 0).
     * @param gpu_accelerate Whether to use GPU acceleration (default is false).
     * @todo Should we add the getter methods to the documentation?
     */
    explicit DeviceConfig(const int cpu_threads = 0, const bool gpu_accelerate = false)
        : cpu_threads_(cpu_threads), gpu_accelerate_(gpu_accelerate) {}

    /**
     * @brief Get the number of CPU threads configured.
     *
     * @return int Number of CPU threads.
     */
    int cpu_threads() const { return cpu_threads_; }

    /**
     * @brief Check if GPU acceleration is enabled.
     *
     * @return bool True if GPU acceleration is enabled, otherwise false.
     */
    bool gpu_accelerate() const { return gpu_accelerate_; }

   private:
    int cpu_threads_;      ///< Number of CPU threads to use.
    bool gpu_accelerate_;  ///< Whether to use GPU acceleration.
};

/**
 * @brief Index types supported by CyborgDB
 */
enum IndexType {
#ifdef LITE
    IVFFLAT  // Only allow IVFFLAT in Lite mode
#else
    IVF,
    IVFPQ,
    IVFFLAT
#endif
};

/**
 * @brief Distance metrics supported by CyborgDB
 */
enum class DistanceMetric { Cosine, Euclidean, SquaredEuclidean };

/**
 * @brief Size of the integer used to represent an item ID
 *
 * @todo Determine whether 64-bit is the best choice for this, or make it configurable
 */
// using ItemID = uint64_t;
using ItemID = std::string;

/**
 * @brief Struct to hold an item's ID, vector, contents, and metadata
 */
struct Item {
    const std::string id;
    const std::vector<float> vector;
    const std::vector<uint8_t> contents;
    const std::string metadata;
};

/**
 * @brief Abstract base class for index configurations
 */
class IndexConfig {
   protected:
    size_t dimension_;                            //< Dimension of the vectors
    DistanceMetric metric_;                       //< Distance metric used in the index
    IndexType index_type_;                        //< Type of the index
    std::optional<std::string> embedding_model_;  //< Optional model name for embeddings

   public:
    /**
     * @brief Default virtual destructor
     */
    virtual ~IndexConfig() = default;

    /**
     * @brief Construct a new Index Config object
     *
     * @param dimension Vector dimensionality
     * @param index_type Index type
     * @param metric Distance metric (default: Euclidean)
     */
    IndexConfig(size_t dimension, IndexType index_type,
                DistanceMetric metric = DistanceMetric::Euclidean,
                std::optional<std::string> embedding_model = std::nullopt)
        : dimension_(dimension),
          metric_(metric),
          index_type_(index_type),
          embedding_model_(std::move(embedding_model)) {}

    /**
     * @brief Returns the vector dimensionality
     *
     * @return size_t Vector dimensionality
     */
    size_t dimension() const { return dimension_; }

    /**
     * @brief Returns the distance metric
     *
     * @return DistanceMetric distance metric used in the index
     */
    DistanceMetric metric() const { return metric_; }

    /**
     * @brief Returns the index type
     *
     * @return IndexType index type
     */
    IndexType index_type() const { return index_type_; }

    /**
     * @brief Returns the model name if available
     *
     * @return std::optional<std::string> Model name, if set
     */
    std::optional<std::string> embedding_model() const { return embedding_model_; }

    // Pure virtual methods for derived classes to implement
    virtual size_t n_lists() const = 0;
    virtual size_t pq_dim() const { return 0; }              // Default to 0 if not applicable
    virtual size_t pq_bits() const { return 0; }             // Default to 0 if not applicable
    virtual std::unique_ptr<IndexConfig> clone() const = 0;  // Pure virtual clone method
};

#ifndef LITE  // Exclude IVF and IVFPQ in Lite mode

/**
 * @brief IVFPQ Index configuration
 */
class IndexIVFPQ : public IndexConfig {
   private:
    size_t n_lists_;
    size_t pq_dim_;
    size_t pq_bits_;

   public:
    /**
     * @brief Construct a new IVFPQ Index config
     *
     * @param dimension Vector dimensionality
     * @param n_lists Number of lists (coarse clusters)
     * @param pq_dim Dimensionality of the product-quantized vectors
     * @param pq_bits Number of bits per quantizer (2^N clusters)
     * @param metric Distance metric (default: Euclidean)
     */
    IndexIVFPQ(size_t dimension, size_t n_lists, size_t pq_dim, size_t pq_bits,
               DistanceMetric metric = DistanceMetric::Euclidean,
               std::optional<std::string> embedding_model = "")
        : IndexConfig(dimension, IndexType::IVFPQ, metric, std::move(embedding_model)),
          n_lists_(n_lists),
          pq_dim_(pq_dim),
          pq_bits_(pq_bits) {}

    /**
     * @brief Returns the number of lists (coarse clusters)
     *
     * @return size_t Number of lists
     */
    size_t n_lists() const override { return n_lists_; }

    /**
     * @brief Returns the dimensionality of the product-quantized vectors
     *
     * @return size_t Dimensionality of the product-quantized vectors
     */
    size_t pq_dim() const override { return pq_dim_; }

    /**
     * @brief Returns the number of bits per quantizer
     *
     * @return size_t Bits per quantizer
     */
    size_t pq_bits() const override { return pq_bits_; }

    /**
     * @brief Clone the IVFPQ index configuration
     *
     * @return std::unique_ptr<IndexConfig> Cloned index configuration
     */
    std::unique_ptr<IndexConfig> clone() const override {
        return std::make_unique<IndexIVFPQ>(*this);
    }
};

/**
 * @brief IVF Index configuration
 */
class IndexIVF : public IndexConfig {
   private:
    size_t n_lists_;

   public:
    /**
     * @brief Construct a new IVF Index config
     *
     * @param dimension Vector dimensionality
     * @param n_lists Number of lists (coarse clusters)
     * @param metric Distance metric (default: Euclidean)
     */
    IndexIVF(size_t dimension, size_t n_lists, DistanceMetric metric = DistanceMetric::Euclidean,
             std::optional<std::string> embedding_model = "")
        : IndexConfig(dimension, IndexType::IVF, metric, std::move(embedding_model)),
          n_lists_(n_lists) {}

    /**
     * @brief Returns the number of lists (coarse clusters)
     *
     * @return size_t Number of lists
     */
    size_t n_lists() const override { return n_lists_; }

    /**
     * @brief Clone the IVF index configuration
     *
     * @return std::unique_ptr<IndexConfig> Cloned index configuration
     */
    std::unique_ptr<IndexConfig> clone() const override {
        return std::make_unique<IndexIVF>(*this);
    }
};

#endif  // End of `#ifndef LITE` block (IVF and IVFPQ are excluded in Lite mode)
/**
 * @brief IVFFlat Index configuration
 */
class IndexIVFFlat : public IndexConfig {
   private:
    size_t n_lists_;

   public:
    /**
     * @brief Construct a new IVFFlat Index config
     *
     * @param dimension Vector dimensionality
     * @param n_lists Number of lists (coarse clusters)
     * @param metric Distance metric (default: Euclidean)
     */
    IndexIVFFlat(size_t dimension, size_t n_lists,
                 DistanceMetric metric = DistanceMetric::Euclidean,
                 std::optional<std::string> embedding_model = "")
        : IndexConfig(dimension, IndexType::IVFFLAT, metric, std::move(embedding_model)),
          n_lists_(n_lists) {}

    /**
     * @brief Returns the number of lists (coarse clusters)
     *
     * @return size_t Number of lists
     */
    size_t n_lists() const override { return n_lists_; }

    /**
     * @brief Clone the IVFFlat index configuration
     *
     * @return std::unique_ptr<IndexConfig> Cloned index configuration
     */
    std::unique_ptr<IndexConfig> clone() const override {
        return std::make_unique<IndexIVFFlat>(*this);
    }
};

/**
 * @brief Class to hold all IDs and distances for multiple queries in a contiguous memory block.
 */
class QueryResults {
   public:
    // Constructor: Preallocate the space for the ids and distances
    QueryResults(size_t num_queries, size_t top_k)
        : num_queries_(num_queries),
          top_k_(top_k),
          ids_(num_queries, top_k),
          distances_(num_queries, top_k),
          num_results_(num_queries, 0),
          metadata_(num_queries) {}

    // Constructor that also intializes a decrypted items buffer
    QueryResults(size_t num_queries, size_t top_k, size_t item_size)
        : num_queries_(num_queries),
          top_k_(top_k),
          ids_(num_queries, top_k),
          distances_(num_queries, top_k),
          num_results_(num_queries, 0),
          metadata_(num_queries) {  // Initialize metadata vector
        vectors_.resize(num_queries);
    }

    // Empty constructor
    QueryResults() = default;

    /**
     * @brief Struct that holds views (spans) of IDs and distances for a query.
     */
    struct Result {
        Span<ItemID> ids;                    // Span over the ids
        Span<float> distances;               // Span over the distances
        uint32_t& num_results;               // Number of results
        std::vector<std::string>& metadata;  // Metadata associated with results
    };

    /**
     * @brief Struct that holds views (spans) of IDs and distances for a query (read-only).
     */
    struct ConstResult {
        Span<const ItemID> ids;                    // Span over the ids
        Span<const float> distances;               // Span over the distances
        uint32_t num_results;                      // Number of results
        const std::vector<std::string>& metadata;  // Metadata associated with results
    };

    // Return a ConstResult for a specific query (read-only)
    ConstResult operator[](size_t query_idx) const {
        if (query_idx >= num_queries_) {
            throw std::out_of_range("Query index is out of bounds");
        }

        return ConstResult{
            Span<const ItemID>{ids_.data() + query_idx * top_k_, num_results_[query_idx]},
            Span<const float>{distances_.data() + query_idx * top_k_, num_results_[query_idx]},
            num_results_[query_idx],  // Number of results
            metadata_[query_idx]      // Metadata for this query
        };
    }

    // Return a Result for a specific query (read-write)
    Result operator[](size_t query_idx) {
        if (query_idx >= num_queries_) {
            throw std::out_of_range("Query index is out of bounds");
        }

        return Result{
            Span<ItemID>{ids_.data() + query_idx * top_k_, top_k_},
            Span<float>{distances_.data() + query_idx * top_k_, top_k_},
            num_results_[query_idx],  // Number of results
            metadata_[query_idx]      // Metadata for this query
        };
    }

    // Return the IDs as a 1D vector (read-only)
    const Array2D<ItemID>& ids() const { return ids_; }

    // Return the IDs as a 1D vector (read-write)
    Array2D<ItemID>& ids() { return ids_; }

    // Return the distances as a 1D vector (read-only)
    const Array2D<float>& distances() const { return distances_; }

    // Return the distances as a 1D vector (read-write)
    Array2D<float>& distances() { return distances_; }

    // Return the number of results per query as a 1D vector (read-only)
    const std::vector<uint32_t>& num_results() const { return num_results_; }

    // Return the number of results per query as a 1D vector (read-write)
    std::vector<uint32_t>& num_results() { return num_results_; }

    // Return the number of queries
    size_t num_queries() const { return num_queries_; }

    // Return the number of top_k items per query
    size_t top_k() const { return top_k_; }

    // Return whether the query results are empty
    bool empty() const { return num_queries_ == 0; }

    // Return metadata
    std::vector<std::vector<std::string>>& metadata() { return metadata_; }

   private:
    size_t num_queries_;        // Number of queries
    size_t top_k_;              // Number of top_k items per query
    Array2D<ItemID> ids_;       // Contiguous block for all ids (size: num_queries * top_k)
    Array2D<float> distances_;  // Contiguous block for all distances (size: num_queries * top_k)
    std::vector<uint32_t> num_results_;               // Number of results per query
    std::vector<std::vector<float>> vectors_;         // Decrypted vectors
    std::vector<std::vector<std::string>> metadata_;  // Metadata for each query
};

/**
 * @brief Index parameters for training
 */
struct TrainingConfig {
    /**
     * @brief Construct a new Training Config object
     *
     * @param batch_size Batch size (optional, set to 0 for auto)
     * @param max_iters Maximum number of iterations (optional, set to 0 for auto)
     * @param tolerance Tolerance for convergence (optional, default = 1e-6)
     * @param max_memory Maximum memory usage in MB (optional, set to 0 for auto)
     */
    TrainingConfig(size_t batch_size = 0, size_t max_iters = 0, double tolerance = 1e-6,
                   size_t max_memory = 0)
        : batch_size(batch_size),
          max_iters(max_iters),
          tolerance(tolerance),
          max_memory(max_memory) {}

    size_t batch_size;  //< Batch size
    size_t max_iters;   //< Maximum number of iterations
    double tolerance;   //< Tolerance for convergence
    size_t max_memory;  //< Maximum memory usage in MB
};

// Enum for specifying which include to include in a query.
enum class ResultFields {
    kDistance,  // Include distance scores in query results
    // kVectors,      // Include vector in query results
    kMetadata,  // Include metadata in query results
};

/**
 * @brief Query parameters for encrypted ANN search
 */
struct QueryParams {
    /**
     * @brief Construct a new Query Params object
     *
     * @param top_k Number of top results to return
     * @param n_probes Number of probes for IVF search
     * @param return_items Whether to return the items along with the IDs (default = false)
     * @param return_metdata Whether to return the metadata along with the IDs (default = false)
     * @param filters JSON-like metadata filters for post-query filtering
     */
    explicit QueryParams(size_t top_k = 100, size_t n_probes = 1, std::string filters = "",
                         std::vector<ResultFields> include = {}, bool greedy = false)
        : top_k(top_k),
          n_probes(n_probes),
          filters(std::move(filters)),
          include(include),
          greedy(greedy) {}

    size_t top_k;                       //< Number of top results to return
    size_t n_probes;                    //< Number of probes for IVF search
    std::vector<ResultFields> include;  //< include to include in a query
    bool greedy;                        //< Whether to use greedy search
    std::string filters;                //< Metadata filters for post-query filtering
};

struct MetadataCentroid {
    uint32_t centroid;                      // Equivalent to uint32_t
    double min_val = 9876543211.0;          // 64-bit float
    double max_val = -9876543211.0;         // 64-bit float
    std::vector<uint32_t> metadata_values;  // Array of uint16_t (string hashes)
};
}  // namespace cyborg

#endif  // CVS_TYPES_HPP_
