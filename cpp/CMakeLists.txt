cmake_minimum_required(VERSION 3.16)
project(axiom_cpp LANGUAGES CXX)

add_library(axiom_cpp SHARED src/lif.cpp)
target_include_directories(axiom_cpp PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_compile_features(axiom_cpp PUBLIC cxx_std_17)
target_compile_definitions(axiom_cpp PRIVATE AXIOM_CPP_BUILD)
set_target_properties(axiom_cpp PROPERTIES
    CXX_VISIBILITY_PRESET hidden
    VISIBILITY_INLINES_HIDDEN YES
    OUTPUT_NAME axiom_cpp
)

include(CTest)
if(BUILD_TESTING)
    add_executable(axiom_cpp_test tests/test_lif.cpp)
    target_link_libraries(axiom_cpp_test PRIVATE axiom_cpp)
    add_test(NAME axiom_cpp_test COMMAND axiom_cpp_test)
endif()
