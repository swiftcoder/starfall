
add_library(noise_c SHARED noise_c.cpp generator.cpp)
set_target_properties(noise_c PROPERTIES LINKER_LANGUAGE C)
