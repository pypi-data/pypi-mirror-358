#ifndef CLIENT_HPP_
#define CLIENT_HPP_

#include "encrypted_index.hpp"
#include "logger.hpp"

namespace cyborg {
namespace internal {
// Forward declaration
class TelemetryAggregator;
class ApiKeyValidator;
}  // namespace internal

class Client {
   public:
    /**
     * @brief Destructor for Client.
     */
    ~Client();

    /**
     * @brief Construct a new Client object.
     *
     * @param api_key API key for your CyborgDB account.
     * @param index_location Configuration details for the location of the index storage.
     * @param config_location Configuration details for the location of the configuration storage.
     * @param items_location Configuration details for the location of the items storage.
     * @param cpu_threads Number of CPU threads to use (default is 0).
     * @param gpu_accelerate Whether to use GPU acceleration (default is false).
     *
     * @todo Add overloads for no items_location & no device_config -> v1.1
     * @todo Change Location enum in cyborg-encrypted-index from k(memory type) to all Uppercase (no
     * k) -> v1.1
     */
    Client(const std::string& api_key, const DBConfig& index_location,
           const DBConfig& config_location, const DBConfig& items_location, const int cpu_threads,
           const bool gpu_accelerate);

    // Overloaded constructor with path prefix for Python installs
    Client(const std::string& api_key, const DBConfig& index_location,
           const DBConfig& config_location, const DBConfig& items_location, const int cpu_threads,
           const bool gpu_accelerate, std::string& path_prefix);

    /**
     * @brief Creates an index based on the specified configuration and parameters.
     *
     * This function initializes the index creation process by setting up necessary
     * member variables and configurations based on the provided parameters. It also
     * determines whether to include a payload based on the type of index being created.
     *
     * @param index_name The name of the index to be created.
     * @param index_key An array containing the encryption keys for the index.
     * @param index_config A reference to a IndexConfig object that contains
     *                     configuration details specific to the index type being created.
     * @param max_cache_size max size for cache size
     * @todo Handle store_items_ in IndexConfig -> v1.1
     */
    std::unique_ptr<cyborg::EncryptedIndex> CreateIndex(
        const std::string index_name, const std::array<uint8_t, 32>& index_key,
        const IndexConfig& index_config, const std::optional<size_t>& max_cache_size = 0,
        cyborg::Logger* logger = nullptr);

    /**
     * @brief Loads an existing index based on the specified name and keys.
     *
     * This function initializes the index loading process by setting up necessary
     * member variables and configurations based on the provided parameters. It also
     * determines whether to include a payload based on the type of index being loaded.
     *
     * @param index_name The name of the index to be loaded.
     * @param index_key An array containing the encryption keys for the index.
     * @param max_cache_size max size for cache size
     * @todo Make these params const references -> v1.1
     * @todo Handle store_items_ in IndexConfig -> v1.1
     */
    std::unique_ptr<cyborg::EncryptedIndex> LoadIndex(
        const std::string index_name, const std::array<uint8_t, 32>& index_key,
        const std::optional<size_t>& max_cache_size = 0, cyborg::Logger* logger = nullptr);

    /**
     * @brief Returns a list of encrypted index names which are accessible to the client.
     */
    std::vector<std::string> ListIndexes();

    /**
     * @brief This function is only for internal use.
     */
    std::unique_ptr<cyborg::EncryptedIndex> LoadSerializedIndex(
        const std::vector<uint8_t>& serialized_config, const std::array<uint8_t, 32>& index_key,
        cyborg::Logger* logger = nullptr);

    /**
     * @brief Get the number of CPU threads configured for this client
     * @return The number of CPU threads
     */
    int cpu_threads() const;

    /**
     * @brief Check if GPU acceleration is enabled for this client
     * @return True if GPU acceleration is enabled, false otherwise
     */
    bool gpu_accelerate() const;

   private:
    // Configuration for storage locations
    DBConfig index_location_;
    DBConfig config_location_;
    DBConfig items_location_;
    DBConfig data_location_;
    std::string api_key_;
    int cpu_threads_;
    bool gpu_accelerate_;
    std::optional<std::string> path_prefix_;
    std::unique_ptr<cyborg_encrypted_index::Client> cei_client_;
    std::shared_ptr<internal::TelemetryAggregator> telemetry_aggregator_;
    internal::ApiKeyValidator* api_key_validator_;
};
}  // namespace cyborg
#endif  // CLIENT_HPP_