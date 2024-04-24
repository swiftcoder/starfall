
#ifndef generator_h
#define generator_h

#ifdef __cplusplus
extern "C" {
#endif

struct Generator;
typedef struct Generator noise_generator;

void noise_generator_destroy(noise_generator *generator);

noise_generator *noise_generator_constant_create(double value);
noise_generator *noise_generator_simplex_create();
noise_generator *noise_generator_ridged_multifractal_create(noise_generator *basis, noise_generator *octaves, noise_generator *lacunarity, noise_generator *gain, noise_generator *offset, noise_generator *h, noise_generator *weight, noise_generator *freq);

double noise_generator_constant_value_get(noise_generator *generator);
void noise_generator_constant_value_set(noise_generator *generator, double value);

double noise_generate(noise_generator *generator, double x, double y, double z);

#ifdef __cplusplus
}
#endif

#endif
