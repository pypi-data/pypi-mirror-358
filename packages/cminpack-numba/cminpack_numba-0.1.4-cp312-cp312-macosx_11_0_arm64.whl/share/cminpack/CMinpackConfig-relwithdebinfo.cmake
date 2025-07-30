#----------------------------------------------------------------
# Generated CMake target import file for configuration "RelWithDebInfo".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "cminpack::cminpacks" for configuration "RelWithDebInfo"
set_property(TARGET cminpack::cminpacks APPEND PROPERTY IMPORTED_CONFIGURATIONS RELWITHDEBINFO)
set_target_properties(cminpack::cminpacks PROPERTIES
  IMPORTED_LOCATION_RELWITHDEBINFO "${_IMPORT_PREFIX}/cminpack_numba/libcminpacks.1.3.11.dylib"
  IMPORTED_SONAME_RELWITHDEBINFO "@rpath/libcminpacks.1.dylib"
  )

list(APPEND _cmake_import_check_targets cminpack::cminpacks )
list(APPEND _cmake_import_check_files_for_cminpack::cminpacks "${_IMPORT_PREFIX}/cminpack_numba/libcminpacks.1.3.11.dylib" )

# Import target "cminpack::cminpack" for configuration "RelWithDebInfo"
set_property(TARGET cminpack::cminpack APPEND PROPERTY IMPORTED_CONFIGURATIONS RELWITHDEBINFO)
set_target_properties(cminpack::cminpack PROPERTIES
  IMPORTED_LOCATION_RELWITHDEBINFO "${_IMPORT_PREFIX}/cminpack_numba/libcminpack.1.3.11.dylib"
  IMPORTED_SONAME_RELWITHDEBINFO "@rpath/libcminpack.1.dylib"
  )

list(APPEND _cmake_import_check_targets cminpack::cminpack )
list(APPEND _cmake_import_check_files_for_cminpack::cminpack "${_IMPORT_PREFIX}/cminpack_numba/libcminpack.1.3.11.dylib" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
