add_library(boost-python
    pxr/boost/python/converter/arg_to_python_base.cpp
    pxr/boost/python/converter/builtin_converters.cpp
    pxr/boost/python/converter/from_python.cpp
    pxr/boost/python/converter/registry.cpp
    pxr/boost/python/converter/type_id.cpp
    pxr/boost/python/dict.cpp
    pxr/boost/python/errors.cpp
    pxr/boost/python/exec.cpp
    pxr/boost/python/import.cpp
    pxr/boost/python/list.cpp
    pxr/boost/python/long.cpp
    pxr/boost/python/module.cpp
    pxr/boost/python/object/class.cpp
    pxr/boost/python/object/enum.cpp
    pxr/boost/python/object/function.cpp
    pxr/boost/python/object/function_doc_signature.cpp
    pxr/boost/python/object/inheritance.cpp
    pxr/boost/python/object/iterator.cpp
    pxr/boost/python/object/life_support.cpp
    pxr/boost/python/object/pickle_support.cpp
    pxr/boost/python/object/stl_iterator.cpp
    pxr/boost/python/object_operators.cpp
    pxr/boost/python/object_protocol.cpp
    pxr/boost/python/slice.cpp
    pxr/boost/python/str.cpp
    pxr/boost/python/tuple.cpp
    pxr/boost/python/wrapper.cpp
)

target_include_directories(boost-python
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
        $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)

target_link_libraries(boost-python
    PUBLIC
        Python::Python
)

set_target_properties(boost-python
    PROPERTIES
        POSITION_INDEPENDENT_CODE ON
        OUTPUT_NAME "PxrBoostPython"
)

# Add PXR_BOOST_PYTHON_SOURCE when building this library to ensure symbols
# decorated with PXR_BOOST_PYTHON_DECL are exported.
target_compile_definitions(boost-python
    PRIVATE
        PXR_BOOST_PYTHON_SOURCE
)

# Disable insertion of C++ signatures in docstrings. We generate this
# information separately via our Python doc build process.
target_compile_definitions(boost-python
    PUBLIC
        PXR_BOOST_PYTHON_NO_PY_SIGNATURES
)

# By default CMake defines NDEBUG in CMAKE_CXX_FLAGS_<config> for
# non-debug build configurations, which applies to all targets
# created in this directory. This disables assert calls in unit
# tests, rendering them useless in those configurations.
#
# To avoid this, we remove NDEBUG from CMAKE_CXX_FLAGS_<config>
# and reapply it only to the main library itself below.
if (MSVC)
    set(ndebug_flag "/DNDEBUG")
else()
    set(ndebug_flag "-DNDEBUG")
endif()

foreach(config RELEASE RELWITHDEBINFO MINSIZEREL)
    string(REPLACE
        ${ndebug_flag} ""
        CMAKE_CXX_FLAGS_${config} ${CMAKE_CXX_FLAGS_${config}}
    )
endforeach()

target_compile_definitions(boost-python
    PRIVATE
        $<$<NOT:$<CONFIG:Debug>>:NDEBUG>
)

install(
    TARGETS boost-python EXPORT ${PROJECT_NAME}
    RUNTIME DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

install(
    DIRECTORY pxr
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    FILES_MATCHING PATTERN "*.hpp"
)

install(EXPORT ${PROJECT_NAME}
    FILE pxr-boost-targets.cmake
    NAMESPACE pxr::
    DESTINATION ${CMAKE_INSTALL_DATAROOTDIR}/cmake/pxr-boost
)