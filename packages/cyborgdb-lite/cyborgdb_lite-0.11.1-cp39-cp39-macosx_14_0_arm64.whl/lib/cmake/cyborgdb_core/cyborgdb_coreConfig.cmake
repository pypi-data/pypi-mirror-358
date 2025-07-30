include(CMakeFindDependencyMacro)

    # Find all required dependencies
    find_dependency(ZLIB REQUIRED)
    find_dependency(OpenSSL REQUIRED)
    find_dependency(CURL REQUIRED)
    find_dependency(BLAS REQUIRED)
    find_dependency(LAPACK REQUIRED)

    # For shared builds, also find PostgreSQL and Redis
    if(NOT DEFINED BUILD_SHARED_LIBS OR NOT BUILD_SHARED_LIBS)
    find_dependency(PostgreSQL REQUIRED)
    # Redis dependencies
    find_library(REDIS_LIBRARY hiredis REQUIRED)
    find_library(REDIS_SSL_LIBRARY hiredis_ssl REQUIRED)
    endif()

    # Add include directories for consuming projects
    set(CYBORGDB_CORE_INCLUDE_DIRS "${CMAKE_CURRENT_LIST_DIR}/../../include")
    set(CYBORGDB_CORE_INCLUDE_DIR "${CMAKE_CURRENT_LIST_DIR}/../../include")

    # Finally include the targets file
    include("${CMAKE_CURRENT_LIST_DIR}/cyborgdb_coreTargets.cmake")

    # Set include directories for imported target if not already set
    if(TARGET cyborgdb::cyborgdb_core)
    get_target_property(_CYBORGDB_HAS_INTERFACE_INCLUDES cyborgdb::cyborgdb_core INTERFACE_INCLUDE_DIRECTORIES)
    if(NOT _CYBORGDB_HAS_INTERFACE_INCLUDES)
        set_target_properties(cyborgdb::cyborgdb_core PROPERTIES
        INTERFACE_INCLUDE_DIRECTORIES "${CYBORGDB_CORE_INCLUDE_DIRS}")
    endif()
    endif()

    set(cyborgdb_core_FOUND TRUE)