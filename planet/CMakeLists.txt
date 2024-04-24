
add_library(planet_c SHARED planet_c.cpp)
set_target_properties(planet_c PROPERTIES LINKER_LANGUAGE C)

target_link_libraries(planet_c noise_c)
