
#include <math.h>

#include "../noise/generator.h"

extern "C" {

void vec_lerp(double *start, double *end, double factor, double *output) {
	int i;

	for (i = 0; i < 3; i++)
		output[i] = start[i] + (end[i] - start[i])*factor;
}

void vec_normalise(double *v) {
	int i;
	double len = sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2]);

	for (i = 0; i < 3; i++)
		v[i] /= len;
}

void cube_to_sphere(double *v) {
	double x = v[0], y = v[1], z = v[2];

	v[0] = x * sqrt(1.0 - y*y*0.5 - z*z*0.5 + y*y*z*z/3.0);
	v[1] = y * sqrt(1.0 - z*z*0.5 - x*x*0.5 + z*z*x*x/3.0);
	v[2] = z * sqrt(1.0 - x*x*0.5 - y*y*0.5 + x*x*y*y/3.0);
}

void vec_mulf(double *v, double f) {
	int i;

	for (i = 0; i < 3; i++)
		v[i] *= f;
}

void vec_sub(double *v1, double *v2) {
	int i;

	for (i = 0; i < 3; i++)
		v1[i] -= v2[i];
}


void generate_vertices(double center[3], double v0[3], double v1[3], double v2[3], double v3[3], int size, float *vertices, double radius, double scale, void *params) {
	double lo[3], hi[3], v[3];

	int size1 = size - 1;

	int i, j, k;

	for (i = 0; i < size; i++) {
		vec_lerp(v0, v3, i/(double)(size1), lo);
		vec_lerp(v1, v2, i/(double)(size1), hi);

		for (j = 0; j < size; j++) {
			vec_lerp(lo, hi, j/(double)(size1), v);

			cube_to_sphere(v);

			double h = noise_generate((noise_generator *)params, v[0], v[1], v[2]);

			h = (h < -1.0) ? -1.0 : h;
			h = (h > 1.0) ? 1.0 : h;

			vec_mulf(v, radius + h*scale);

			vec_sub(v, center);

			k = (j*size + i) * 3;

			vertices[k+0] = v[0];
			vertices[k+1] = v[1];
			vertices[k+2] = v[2];
		}
	}
}

double query_height(double v[3], double radius, double scale, void *params) {
	vec_normalise(v);

	double h = noise_generate((noise_generator *)params, v[0], v[1], v[2]);

	h = (h < -1.0) ? -1.0 : h;
	h = (h > 1.0) ? 1.0 : h;

	return radius + h*scale;
}

}
