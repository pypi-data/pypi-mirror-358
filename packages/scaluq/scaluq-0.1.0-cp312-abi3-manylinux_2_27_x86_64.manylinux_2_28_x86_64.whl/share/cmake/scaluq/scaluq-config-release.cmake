#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "scaluq::scaluq_base" for configuration "Release"
set_property(TARGET scaluq::scaluq_base APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(scaluq::scaluq_base PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib64/libscaluq_base.a"
  )

list(APPEND _cmake_import_check_targets scaluq::scaluq_base )
list(APPEND _cmake_import_check_files_for_scaluq::scaluq_base "${_IMPORT_PREFIX}/lib64/libscaluq_base.a" )

# Import target "scaluq::scaluq_default_f32" for configuration "Release"
set_property(TARGET scaluq::scaluq_default_f32 APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(scaluq::scaluq_default_f32 PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib64/libscaluq_default_f32.a"
  )

list(APPEND _cmake_import_check_targets scaluq::scaluq_default_f32 )
list(APPEND _cmake_import_check_files_for_scaluq::scaluq_default_f32 "${_IMPORT_PREFIX}/lib64/libscaluq_default_f32.a" )

# Import target "scaluq::scaluq_default_f64" for configuration "Release"
set_property(TARGET scaluq::scaluq_default_f64 APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(scaluq::scaluq_default_f64 PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib64/libscaluq_default_f64.a"
  )

list(APPEND _cmake_import_check_targets scaluq::scaluq_default_f64 )
list(APPEND _cmake_import_check_files_for_scaluq::scaluq_default_f64 "${_IMPORT_PREFIX}/lib64/libscaluq_default_f64.a" )

# Import target "scaluq::kokkoscore" for configuration "Release"
set_property(TARGET scaluq::kokkoscore APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(scaluq::kokkoscore PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib64/libkokkoscore.a"
  )

list(APPEND _cmake_import_check_targets scaluq::kokkoscore )
list(APPEND _cmake_import_check_files_for_scaluq::kokkoscore "${_IMPORT_PREFIX}/lib64/libkokkoscore.a" )

# Import target "scaluq::kokkoscontainers" for configuration "Release"
set_property(TARGET scaluq::kokkoscontainers APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(scaluq::kokkoscontainers PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib64/libkokkoscontainers.a"
  )

list(APPEND _cmake_import_check_targets scaluq::kokkoscontainers )
list(APPEND _cmake_import_check_files_for_scaluq::kokkoscontainers "${_IMPORT_PREFIX}/lib64/libkokkoscontainers.a" )

# Import target "scaluq::kokkossimd" for configuration "Release"
set_property(TARGET scaluq::kokkossimd APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(scaluq::kokkossimd PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib64/libkokkossimd.a"
  )

list(APPEND _cmake_import_check_targets scaluq::kokkossimd )
list(APPEND _cmake_import_check_files_for_scaluq::kokkossimd "${_IMPORT_PREFIX}/lib64/libkokkossimd.a" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
