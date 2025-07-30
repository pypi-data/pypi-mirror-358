#ifndef CYBORG_COMMON_TYPES_HPP_
#define CYBORG_COMMON_TYPES_HPP_

#include <algorithm>
#include <array>
#include <iostream>
#include <optional>
#include <stdexcept>
#include <vector>

#include "logger.hpp"

#ifdef NDEBUG
constexpr bool BOUNDS_CHECK = false;  // In Release mode, disable bounds checking
#else
constexpr bool BOUNDS_CHECK = true;  // In Debug mode, enable bounds checking
#endif

namespace cyborg {

/**
 * @brief Custom implementation of a span to provide a view over a contiguous memory block
 *
 * Implemented because std::span is C++20-specific, and is not compatible with CUDA 12.x
 *
 * @tparam T The type of data to store in the Span
 */
template <typename T>
class Span {
   public:
    /**
     * @brief Construct a new Span object from a pointer and size
     *
     * @param data Pointer to the data
     * @param size Size of the data
     */
    Span(T* data, size_t size) : data_(data), size_(size) {}

    /**
     * @brief Construct a new Span object from a const 1D vector
     *
     * @param data 1D vector to store in the Span
     * @note This constructor is only enabled for const data
     */
    template <typename U>
    explicit Span(const std::vector<U>& data) : data_(data.data()), size_(data.size()) {}

    /**
     * @brief Construct a new Span object from a 1D vector
     *
     * @param data 1D vector to store in the Span
     * @note This constructor is only enabled for non-const data
     */
    template <typename U>
    explicit Span(std::vector<U>& data) : data_(data.data()), size_(data.size()) {}

    /**
     * @brief Return a reference to the element at a specific index (read-write)
     *
     * @param idx Index to access
     * @return T& element at the specified index
     */
    inline T& operator[](size_t idx) {
        if constexpr (BOUNDS_CHECK) {
            CheckBounds(idx, size_);
        }
        return data_[idx];
    }

    /**
     * @brief Return a reference to the element at a specific index (read-only)
     *
     * @param idx Index to access
     * @return const T& element at the specified index
     */
    inline const T& operator[](size_t idx) const {
        if constexpr (BOUNDS_CHECK) {
            CheckBounds(idx, size_);
        }
        return data_[idx];
    }

    /**
     * @brief Return a pointer to the data (read-write)
     *
     * @return T* pointer to the data
     */
    inline T* data() noexcept { return data_; }

    /**
     * @brief Return a pointer to the data (read-only)
     *
     * @return const T* pointer to the data
     */
    inline const T* data() const noexcept { return data_; }

    /**
     * @brief Return the size of the Span
     *
     * @return size_t size of the Span
     */
    inline size_t size() const noexcept { return size_; }

    /**
     * @brief Return an iterator to the beginning of the Span (read-write)
     *
     * @return T* iterator to the beginning of the Span
     */
    inline T* begin() noexcept { return data_; }

    /**
     * @brief Return an iterator to the beginning of the Span (read-only)
     *
     * @return const T* iterator to the beginning of the Span
     */
    inline const T* begin() const noexcept { return data_; }

    /**
     * @brief Return an iterator to the end of the Span (read-write)
     *
     * @return T* iterator to the end of the Span
     */
    inline T* end() noexcept { return data_ + size_; }

    /**
     * @brief Return an iterator to the end of the Span (read-only)
     *
     * @return const T* iterator to the end of the Span
     */
    inline const T* end() const noexcept { return data_ + size_; }  // Const iterator

   private:
    T* data_;      // Pointer to the data
    size_t size_;  // Size of the Span

    /**
     * @brief Helper function to check if an index is within bounds
     *
     * @param idx Index to check
     * @param size Size of the Span
     * @throws std::out_of_range if the index is out of bounds
     * @note This function should only be called in debug mode (BOUNDS_CHECK=true)
     */
    void CheckBounds(size_t idx, size_t size) const {
        if (idx >= size) {
            throw std::out_of_range("Index #" + std::to_string(idx) +
                                    " out of bounds (size=" + std::to_string(size) + ")");
        }
    }
};

/**
 * @brief 2D array class to store data in a contiguous memory block
 *
 * Implemented because std::array is not suitable for 2D arrays, and std::vector is not contiguous.
 * This class attempts to bring NumPy-like functionality to C++ while using std::vector for memory.
 *
 * @tparam T The type of data to store in the array
 */
template <typename T>
class Array2D {
   public:
    /**
     * @brief Construct a new Array2D object with a specific number of rows and columns
     *
     * @param rows Number of rows
     * @param cols Number of columns
     * @param initial_value (Optional) Initial value to fill the array with
     */
    Array2D(size_t rows, size_t cols, const T& initial_value = T())
        : rows_(rows), cols_(cols), data_(rows * cols, initial_value) {}

    /**
     * @brief Construct a new Array 2D object from another Array2D object of the same type without
     * copying
     *
     * @param other Handle to the other Array2D object
     * @note This is the explicit move constructor
     */
    Array2D(Array2D&& other) noexcept {
        rows_ = other.rows_;
        cols_ = other.cols_;
        data_ = std::move(other.vector());
        other.Reset();
    }

    /**
     * @brief Construct a new Array2D object from another Array2D object of different type without
     * copying
     *
     * @tparam U Type of the other Array2D object
     * @param other Handle to the other Array2D object
     * @throws std::invalid_argument if the data size is not compatible
     */
    template <typename U>
    explicit Array2D(Array2D<U>&& other) {
        const size_t current_element_size = sizeof(T);
        const size_t new_element_size = sizeof(U);

        // Adjust number of columns based on the size of T and U
        rows_ = other.rows();
        if (current_element_size < new_element_size) {
            // More columns when converting to a smaller type (T < U)
            if (other.cols() * new_element_size % current_element_size != 0) {
                throw std::invalid_argument("Data size mismatch during conversion");
            }
            cols_ = other.cols() * new_element_size / current_element_size;
        } else {
            // Fewer columns when converting to a larger type (T >= U)
            if (current_element_size % new_element_size != 0) {
                throw std::invalid_argument("Data size mismatch during conversion");
            }
            cols_ = other.cols() / (current_element_size / new_element_size);
        }

        // Move the data using std::move to avoid copies
        data_ = std::move(reinterpret_cast<std::vector<T>&>(other.vector()));

        // Clear the other array to release its ownership of the moved vector
        other.Reset();
    }

    /**
     * @brief Construct a new Array2D object from an initializer list of initializer lists
     *
     * @param init_list Initializer list of initializer lists
     * @throws std::invalid_argument if the rows are empty or have different number of columns
     * @note This is only really used for testing purposes, as it's not very efficient
     */
    Array2D(std::initializer_list<std::initializer_list<T>> init_list) {
        // If the initializer list is empty, create an empty 2D array (0 rows, 0 cols)
        if (init_list.size() == 0) {
            rows_ = 0;
            cols_ = 0;
            return;
        }

        rows_ = init_list.size();

        // Check if the first row is valid (to prevent dereferencing nullptr)
        if (init_list.begin()->size() == 0) {
            throw std::invalid_argument("Rows in the initializer list cannot be empty");
        }

        // Assumes all rows have the same number of columns
        cols_ = init_list.begin()->size();
        for (const auto& row : init_list) {
            if (row.size() != cols_) {
                throw std::invalid_argument("All rows must have the same number of columns");
            }
            data_.insert(data_.end(), row.begin(), row.end());
        }
    }

    /**
     * @brief Construct a new Array2D object from a 1D vector and the number of columns
     *
     * @param data Handle to vector to store in the Array2D (will be moved, not copied)
     * @param cols Number of columns (size of each row)
     * @throws std::invalid_argument if the data size is not a multiple of the number of columns
     */
    Array2D(std::vector<T>&& data, size_t cols) : cols_(cols) {
        // Check if the data size is a multiple of the number of columns
        if (cols == 0 || data.size() % cols != 0) {
            throw std::invalid_argument("Data size must be a multiple of the number of columns");
        }
        rows_ = data.size() / cols;
        data_ = std::move(data);
    }

    /**
     * @brief Construct a new Array2D object from a const 1D vector and the number of columns
     *
     * @param data Vector to store in the Array2D (will be copied)
     * @param cols Number of columns (size of each row)
     * @throws std::invalid_argument if the data size is not a multiple of the number of columns
     * @todo Remove this in favor of the rvalue reference constructor (using std::move)
     */
    Array2D(const std::vector<T>& data, size_t cols) : cols_(cols) {
        // Check if the data size is a multiple of the number of columns
        if (cols == 0 || data.size() % cols != 0) {
            throw std::invalid_argument("Data size must be a multiple of the number of columns");
        }
        rows_ = data.size() / cols;
        data_ = data;
    }

    /**
     * @brief Construct a new Array 2D object by copying another Array2D object of the same type
     *
     * @param other Other Array2D object
     * @note This is the explicit copy constructor
     */
    Array2D(const Array2D& other) = default;

    /**
     * @brief Construct an empty Array2D object (0 rows, 0 cols)
     */
    Array2D() : rows_(0), cols_(0) {}

    /**
     * @brief Construct a new Array2D object from another Array2D object of different type without
     * copying
     *
     * @param other Handle to the other Array2D object
     * @note This is the explicit move assignment constructor
     */
    Array2D& operator=(Array2D&& other) noexcept {
        rows_ = other.rows_;
        cols_ = other.cols_;
        data_ = std::move(other.vector());
        other.Reset();
        return *this;
    }

    /**
     * @brief Copy assignment operator
     *
     * @param other Other Array2D object
     * @return Array2D& New Array2D object
     * @note This is the explicit copy assignment operator
     */
    Array2D& operator=(const Array2D& other) {
        if (this != &other) {
            this->rows_ = other.rows_;
            this->cols_ = other.cols_;
            this->data_ = other.data_;  // Deep copy of the vector
        }
        return *this;
    }

    /**
     * @brief Return a row as a Span (read-only)
     *
     * @param row Index of the row to access
     * @return Span<const T> Span object representing the row (read-only)
     */
    inline Span<const T> operator[](size_t row) const {
        if constexpr (BOUNDS_CHECK) {
            CheckBounds(row, rows_);
        }
        return Span<const T>(&data_[row * cols_], cols_);
    }

    /**
     * @brief Return a row as a Span (read-write)
     *
     * @param row Index of the row to access
     * @return Span<T> Span object representing the row (read-write)
     */
    inline Span<T> operator[](size_t row) {
        if constexpr (BOUNDS_CHECK) {
            CheckBounds(row, rows_);
        }
        return Span<T>(&data_[row * cols_], cols_);
    }

    /**
     * @brief Access element (read-only)
     *
     * @param row Row index
     * @param col Column index
     * @return const T& element at the specified row and column
     */
    inline const T& operator()(size_t row, size_t col) const {
        if constexpr (BOUNDS_CHECK) {
            CheckBounds(row, rows_);
            CheckBounds(col, cols_);
        }
        return data_[row * cols_ + col];
    }

    /**
     * @brief Access element (read-write)
     *
     * @param row Row index
     * @param col Column index
     * @return T& element at the specified row and column
     */
    inline T& operator()(size_t row, size_t col) {
        if constexpr (BOUNDS_CHECK) {
            CheckBounds(row, rows_);
            CheckBounds(col, cols_);
        }
        return data_[row * cols_ + col];
    }

    /**
     * @brief Return all data as a read-only pointer
     *
     * @return const T* pointer to the data (read-only)
     */
    inline const T* data() const noexcept { return data_.data(); }

    /**
     * @brief Return all data as a writable pointer
     *
     * @return T* pointer to the data (read-write)
     */
    inline T* data() noexcept { return data_.data(); }

    /**
     * @brief Return all data as a read-only 1D vector
     *
     * @return const std::vector<T>& 1D vector representing the data (read-only)
     */
    inline const std::vector<T>& vector() const noexcept { return data_; }

    /**
     * @brief Return all data as a writable 1D vector
     *
     * @return std::vector<T>& 1D vector representing the data (read-write)
     */
    inline std::vector<T>& vector() noexcept { return data_; }

    /**
     * @brief Return the number of rows
     *
     * @return size_t number of rows
     */
    inline size_t rows() const noexcept { return rows_; }

    /**
     * @brief Return the number of columns
     *
     * @return size_t number of columns
     */
    inline size_t cols() const noexcept { return cols_; }

    /**
     * @brief Return the total number of elements in the array
     *
     * @return size_t number of elements
     */
    inline size_t size() const noexcept { return rows_ * cols_; }

    /**
     * @brief Fill the array with a specific value
     *
     * @param value value to fill the array with
     */
    void Fill(const T& value) { std::fill(data_.begin(), data_.end(), value); }

    /**
     * @brief Print the array to the console
     */
    void Print() const {
        for (size_t i = 0; i < rows_; ++i) {
            for (size_t j = 0; j < cols_; ++j) {
                std::cout << static_cast<int>((*this)(i, j)) << ' ';
            }
            std::cout << '\n';
        }
    }

    /**
     * @brief Reset the array to an empty state (0 rows, 0 cols)
     */
    void Reset() {
        data_.clear();
        rows_ = 0;
        cols_ = 0;
    }

    /**
     * @brief Check if two Array2D objects are equal
     *
     * @param other Other Array2D object to compare with
     * @return true if the two objects are equal, false otherwise
     */
    bool operator==(const Array2D<T>& other) const {
        // Check if dimensions are the same
        if (rows_ != other.rows_ || cols_ != other.cols_) {
            return false;
        }

        // Check if data is the same
        return data_ == other.data_;
    }

   private:
    size_t rows_, cols_;   // Dimensions of the array
    std::vector<T> data_;  // 1D vector to store 2D array in contiguous memory

    /**
     * @brief Helper function to check if an index is within bounds.
     *
     * @param idx Index to check (row or column)
     * @param size Size of the Array2D (rows or columns)
     * @throws std::out_of_range if the index is out of bounds
     * @note This function should only be called in debug mode (BOUNDS_CHECK=true)
     */
    void CheckBounds(size_t idx, size_t size) const {
        if (idx >= size) {
            throw std::out_of_range("Index #" + std::to_string(idx) +
                                    " out of bounds (size=" + std::to_string(size) + ")");
        }
    }
};

/**
 * @brief Backing store locations supported by CEI/CVS
 */
enum class Location { kRedis, kMemory, kPostgres, kMongoDB, kNone };

/**
 * @brief Class to store the configuration of a backing store location
 *
 */
class DBConfig {
   public:
    /**
     * @brief Construct a new DBConfig object
     *
     * @param location Location of the backing store
     * @param table_name (Optional) Name of the table in the database
     * @param db_connection_string (Optional) Connection string for the database
     */
    explicit DBConfig(Location location,
                      const std::optional<std::string>& table_name = std::nullopt,
                      const std::optional<std::string>& db_connection_string = std::nullopt)
        : location_(location),
          table_name_(table_name),
          db_connection_string_(db_connection_string) {}
    /**
     * @brief Return the location of the backing store
     *
     * @return Location Location of the backing store
     */
    Location location() const { return location_; }

    /**
     * @brief Return the name of the table in the database
     *
     * @return std::optional<std::string> Name of the table in the database
     */
    std::optional<std::string> table_name() const { return table_name_; }

    /**
     * @brief Return the connection string for the database
     *
     * @return std::optional<std::string> Connection string for the database
     */
    std::optional<std::string> db_connection_string() const { return db_connection_string_; }

   private:
    Location location_;                                //< Location of the backing store
    std::optional<std::string> table_name_;            //< Name of the table in the database
    std::optional<std::string> db_connection_string_;  //< Connection string for the database
};

// Enum for specifying which fields to include in returned items.
enum class ItemFields {
    kVector,       // Include vector in returned items
    kMetadata,     // Include metadata in returned items
    kContents,      // Include content data in returned items
};

struct LoggingConfig {
    LogLevel level = LogLevel::Error;  // Log level
    bool to_file = false;    // Log to file
    std::string file_path = "";  // File path for log file
};

}  // namespace cyborg

#endif  // CYBORG_COMMON_TYPES_HPP_