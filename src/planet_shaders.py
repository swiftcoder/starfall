
from pyglet.gl import *

from .shader import Shader

# Ysaneya's fast computed noise:
# http://www.gamedev.net/community/forums/topic.asp?topic_id=502913
computed_noise_inc = '''
vec4 randomizer4(const vec4 x)
{
    vec4 z = mod(x, vec4(5612.0));
    z = mod(z, vec4(3.1415927 * 2.0));
    return(fract(cos(z) * vec4(56812.5453)));
}

const float A = 1.0;
const float B = 57.0;
const float C = 113.0;
const vec3 ABC = vec3(A, B, C);
const vec4 A3 = vec4(0, B, C, C+B);
const vec4 A4 = vec4(A, A+B, C+A, C+A+B);

float cnoise(const in vec3 xx)
{
    vec3 x = mod(xx + 32768.0, 65536.0);
    vec3 ix = floor(x);
    vec3 fx = fract(x);
    vec3 wx = fx*fx*(3.0-2.0*fx);
    float nn = dot(ix, ABC);

    vec4 N1 = nn + A3;
    vec4 N2 = nn + A4;
    vec4 R1 = randomizer4(N1);
    vec4 R2 = randomizer4(N2);
    vec4 R = mix(R1, R2, wx.x);
    float re = mix(mix(R.x, R.y, wx.y), mix(R.z, R.w, wx.y), wx.z);

    return 1.0 - 2.0 * re;
}
'''
build_vertices_vs = '''
varying vec3 normal;

void main() {
	normal = gl_MultiTexCoord0.xyz;
	gl_Position = ftransform();
}'''
build_vertices_fs = '''
uniform vec3 center;
uniform float radius, scale;

varying vec3 normal;

vec3 cube_to_sphere(vec3 v) {
	return v * sqrt(vec3(
		1.0 - v.y*v.y*0.5 - v.z*v.z*0.5 + v.y*v.y*v.z*v.z/3.0,
		1.0 - v.z*v.z*0.5 - v.x*v.x*0.5 + v.z*v.z*v.x*v.x/3.0,
		1.0 - v.x*v.x*0.5 - v.y*v.y*0.5 + v.x*v.x*v.y*v.y/3.0
	));
}

void main() {
	vec3 v = cube_to_sphere(normal);
	float h = %(noise)s *0.5 + 0.5;

	h = clamp(h, 0.0, 1.0);

	h = radius + h*scale;

	gl_FragColor = vec4(normalize(normal)*h - center, 1.0);
}
'''

build_height_map_vs = '''
varying vec3 normal;

void main() {
	normal = gl_MultiTexCoord0.xyz;
	gl_Position = ftransform();
}
'''
build_height_map_fs = '''
varying vec3 normal;

vec3 cube_to_sphere(vec3 v) {
	return v * sqrt(vec3(
		1.0 - v.y*v.y*0.5 - v.z*v.z*0.5 + v.y*v.y*v.z*v.z/3.0,
		1.0 - v.z*v.z*0.5 - v.x*v.x*0.5 + v.z*v.z*v.x*v.x/3.0,
		1.0 - v.x*v.x*0.5 - v.y*v.y*0.5 + v.x*v.x*v.y*v.y/3.0
	));
}

void main() {
	vec3 v = cube_to_sphere(normal);
	float h = %(noise)s *0.5 + 0.5;

	h = clamp(h, 0.0, 1.0);

	gl_FragColor = vec4(h);
}
'''
#if __debug__:
#	print 'loading height map shader'
#build_height_map_shader = Shader([build_height_map_vs], [simplex_noise_inc, computed_noise_inc, build_height_map_fs])

build_normal_map_vs = '''
varying vec3 normal;
varying vec2 coord;

uniform vec2 offset, bias;

void main() {
	normal = gl_MultiTexCoord0.xyz;
	coord = offset + gl_Vertex.xy*bias;
	gl_Position = ftransform();
}
'''
build_normal_map_fs = '''
varying vec3 normal;
varying vec2 coord;

uniform float scale, pixel;
uniform sampler2D heightMap;

mat3 build_rotation_matrix(vec3 f, vec3 t) {
	vec3 v = cross(f, t);
	float c = dot(f, t);
	float h = (1.0 - c)/dot(v,v);

	mat3 m = mat3(
				vec3( c + h*v.x*v.x, h*v.x*v.y - v.z, h*v.x*v.z + v.y ),
				vec3( h*v.x*v.y + v.z, c + h*v.y*v.y, h*v.y*v.z - v.x ),
				vec3( h*v.x*v.z - v.y, h*v.y*v.z + v.x, c + h*v.z*v.z )
			);

	return m;
}

void main() {
	float h00 = texture2D(heightMap, coord + vec2( 1,-1)*pixel).r;
	float h10 = texture2D(heightMap, coord + vec2( 0,-1)*pixel).r;
	float h20 = texture2D(heightMap, coord + vec2(-1,-1)*pixel).r;

	float h01 = texture2D(heightMap, coord + vec2( 1, 0)*pixel).r;
	float h11 = texture2D(heightMap, coord + vec2( 0, 0)*pixel).r;
	float h21 = texture2D(heightMap, coord + vec2(-1, 0)*pixel).r;

	float h02 = texture2D(heightMap, coord + vec2( 1, 1)*pixel).r;
	float h12 = texture2D(heightMap, coord + vec2( 0, 1)*pixel).r;
	float h22 = texture2D(heightMap, coord + vec2(-1, 1)*pixel).r;

	float Gx = h00 - h20 + 2.0 * h01 - 2.0 * h21 + h02 - h22;
	float Gy = h00 + 2.0 * h10 + h20 - h02 - 2.0 * h12 - h22;

	vec3 n = normalize(vec3(Gx, 2.0*scale, Gy));

	/*float h11 = texture2D(heightMap, coord + vec2(0, 0)*pixel).r;

	float h0 = texture2D(heightMap, coord + vec2(-1, 0)*pixel).r;
	float h1 = texture2D(heightMap, coord + vec2( 0, 1)*pixel).r;
	float h2 = texture2D(heightMap, coord + vec2( 1, 0)*pixel).r;
	float h3 = texture2D(heightMap, coord + vec2( 0,-1)*pixel).r;

	vec3 n = normalize(vec3(h2 - h1, scale, h3 - h1));*/

	mat3 m = build_rotation_matrix(vec3(0, 1, 0), normalize(normal));

	vec3 v = n * m;

	gl_FragColor = vec4(v*0.5 + 0.5, h11);
}
'''
if __debug__:
	print('loading normal map shader')
build_normal_map_shader = Shader([build_normal_map_vs], [build_normal_map_fs])

planet_vs = '''
varying vec3 direction;
varying vec4 primary, secondary;

uniform mat4 model_matrix;

uniform vec3 viewer;
uniform vec3 sun;

uniform float cameraHeight;
uniform float waterRadius;
uniform float atmosphereRadius;
uniform float atmosphereScale;
uniform vec3 invWavelength;

const float scaleDepth = 0.25;
const float Kr4PI = 0.03141;
const float Km4PI = 0.01885;
const float KrESun = 0.0375;
const float KmESun = 0.0225;

const int nSamples = 8;
const float fSamples = 8.0;

float scale(float fCos)
{
	float x = 1.0 - fCos;
	return scaleDepth * exp(-0.00287 + x*(0.459 + x*(3.83 + x*(-6.80 + x*5.25))));
}

void main( void )
{
	gl_TexCoord[0] = gl_MultiTexCoord0;

	vec3 pos = (model_matrix * gl_Vertex).xyz;

		// ray from camera to vertex, and its length (distance through atmosphere)
	vec3 ray = pos - viewer;
	float far = length(ray);
	ray /= far;

#ifdef SPACE

	float B = 2.0 * dot(viewer, ray);
	float C = cameraHeight*cameraHeight - atmosphereRadius*atmosphereRadius;
	float det = max(0.0, B*B - 4.0 * C);
	float near = 0.5 * (-B - sqrt(det));

	// ray origin and scattering offset
	vec3 start = viewer + ray * near;
	far -= near;
	float depth = exp((waterRadius - atmosphereRadius) / scaleDepth);

#else

	vec3 start = viewer;
	float depth = exp((waterRadius - cameraHeight) / scaleDepth);

#endif

	float cameraAngle = dot(-ray, pos) / length(pos);
	float lightAngle = dot(sun, pos) / length(pos);
	float cameraScale = scale(cameraAngle);
	float lightScale = scale(lightAngle);
	float cameraOffset = depth*cameraScale;
	float temp = lightScale + cameraScale;

	// loop variables
	float sampleLength = far / fSamples;
	float scaledLength = sampleLength * atmosphereScale;
	vec3 sampleRay = ray * sampleLength;
	vec3 samplePoint = start + sampleRay*0.5;

	// loop itself
	vec3 frontColor = vec3(0.0);
	vec3 attenuate;
	for (int i = 0; i < nSamples; i++)
	{
		float height = length(samplePoint);
		float depth = exp((atmosphereScale / scaleDepth) * (waterRadius - height));
		float scatter = depth*temp - cameraOffset;
		attenuate = exp(-scatter * (invWavelength * Kr4PI + Km4PI));
		frontColor += attenuate * (depth * scaledLength);
		samplePoint += sampleRay;
	}

	primary.rgb = frontColor * (invWavelength * KrESun + KmESun);
	secondary.rgb = attenuate;

	direction = pos - viewer;

	gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
}
'''
planet_fs = '''
uniform vec3 viewer, sun;
uniform float exposure;

uniform sampler2D lut, normalMap, detail;

varying vec3 direction;
varying vec4 primary, secondary;

void main() {
	vec4 map = texture2D(normalMap, gl_TexCoord[0].xy);

	vec3 normal = normalize(map.xyz*2.0 - 1.0);
	float height = map.w;

	float bump = max(dot(normal, sun), 0.0);
	float specular = 0.0;

	vec4 color;

#ifdef WATER
	vec3 eye = normalize(direction);
	vec3 refl = reflect(sun, normal);
	specular = pow(clamp(dot(refl, eye), 0.0, 1.0), 16.0);

	color = vec4(0.2, 0.2, 0.5, 0.8);
#else
	color = texture2D(lut, vec2(0.0, height));
	color += texture2D(detail, gl_TexCoord[0].xy*4.0);

	/*if (height <= 0.5) {
		vec3 eye = normalize(direction);
		vec3 refl = reflect(sun, normal);
		specular = pow(clamp(dot(refl, eye), 0.0, 1.0), 16.0);
		bump = 1.0;

		color = mix(color, vec4(0.2, 0.2, 0.5, 0.8), 1.0 - height*0.2);
	} */
#endif

	vec4 frag_color = primary + secondary * (color * bump + specular);

	gl_FragColor = 1.0 - exp( (-exposure) * frag_color );

	//gl_FragColor = color*bump;
	//gl_FragColor = vec4(normal*0.5 + 0.5, 1.0);
	//gl_FragColor = vec4(bump);
}
'''
terrain_shader_space = Shader(['#define SPACE\n', planet_vs], [planet_fs])
terrain_shader_atmos = Shader([planet_vs], [planet_fs])

water_shader_space = Shader(['#define SPACE\n', planet_vs], ['#define WATER\n', planet_fs])
water_shader_atmos = Shader([planet_vs], ['#define WATER\n', planet_fs])

atmos_vs = '''
varying vec3 direction;
varying vec4 primary, secondary;

uniform mat4 model_matrix;

uniform vec3 viewer;
uniform vec3 sun;

uniform float cameraHeight;
uniform float waterRadius;
uniform float atmosphereRadius;
uniform float atmosphereScale;
uniform vec3 invWavelength;

const float scaleDepth = 0.25;
const float Kr4PI = 0.03141;
const float Km4PI = 0.01885;
const float KrESun = 0.0375;
const float KmESun = 0.0225;

const int nSamples = 8;
const float fSamples = 8.0;

float scale(float fCos)
{
	float x = 1.0 - fCos;
	return scaleDepth * exp(-0.00287 + x*(0.459 + x*(3.83 + x*(-6.80 + x*5.25))));
}

void main( void )
{
	vec3 pos = gl_Vertex.xyz;

	// ray from camera to vertex, and its length (distance through atmosphere)
	vec3 ray = pos - viewer;
	//pos = normalize(pos);
	float far = length(ray);
	ray /= far;

#ifdef SPACE

	float B = 2.0 * dot(viewer, ray);
	float C = cameraHeight*cameraHeight - atmosphereRadius*atmosphereRadius;
	float det = max(0.0, B*B - 4.0 * C);
	float near = 0.5 * (-B - sqrt(det));

	// ray origin and scattering offset
	vec3 start = viewer + ray * near;
	far -= near;
	float startAngle = dot(ray, start) / atmosphereRadius;
	float startDepth = exp(-1.0 / scaleDepth);
	float startOffset = startDepth*scale(startAngle);

#else

	vec3 start = viewer;
	float height = length(start);
	float depth = exp( (atmosphereScale / scaleDepth) * (waterRadius - cameraHeight) );
	float startAngle = dot(ray, start) / height;
	float startOffset = depth*scale(startAngle);

#endif

	// loop variables
	float sampleLength = far / fSamples;
	float scaledLength = sampleLength * atmosphereScale;
	vec3 sampleRay = ray * sampleLength;
	vec3 samplePoint = start + sampleRay*0.5;

	// loop itself
	vec3 frontColor = vec3(0.0);
	for(int i = 0; i < nSamples; i++)
	{
		float height = length(samplePoint);
		float depth = exp((atmosphereScale / scaleDepth) * (waterRadius - height));
		float lightAngle = dot(sun, samplePoint) / height;
		float cameraAngle = dot(ray, samplePoint) / height;
		float scatter = startOffset + depth*(scale(lightAngle) - scale(cameraAngle));
		vec3 attenuate = exp(-scatter * (invWavelength * Kr4PI + Km4PI));
		frontColor += attenuate * (depth * scaledLength);
		samplePoint += sampleRay;
	}

	secondary.rgb = frontColor * KmESun;
	primary.rgb = frontColor * (invWavelength * KrESun);

	direction = viewer - pos;

	gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
}
'''
atmos_fs = '''
uniform vec3 sun;
uniform float exposure;

const float g = -0.95;
const float g2 = 0.9025;

varying vec3 direction;
varying vec4 primary, secondary;

void main() {
	float fCos = dot(sun, direction) / length(direction);
	float rayleighPhase = 0.75 * (1.0 + fCos*fCos);
	float miePhase = 1.5 * ((1.0 - g2) / (2.0 + g2)) * (1.0 + fCos*fCos) / pow(1.0 + g2 - 2.0*g*fCos, 1.5);

	vec4 frag_color = rayleighPhase * primary + miePhase * secondary;

	gl_FragColor = 1.0 - exp( (-exposure) * frag_color );
}
'''
atmos_shader_space = Shader(['#define SPACE\n', atmos_vs], ['#define SPACE\n', atmos_fs])
atmos_shader_atmos = Shader([atmos_vs], [atmos_fs])

tree_vs = '''
uniform mat4 model_matrix;

uniform vec3 viewer;

void main() {
	vec3 pos = (model_matrix * gl_Vertex).xyz;
	vec3 eye = normalize(viewer - pos);

	vec3 dir = cross(eye, normalize(gl_Normal))*5.0;

	gl_TexCoord[0] = gl_MultiTexCoord0;
	gl_Position = gl_ModelViewProjectionMatrix * vec4(gl_Vertex.xyz + dir, 1.0);
}
'''
tree_fs = '''
uniform sampler2D tree;

void main() {
	vec4 color = texture2D(tree, gl_TexCoord[0].xy);

	gl_FragColor = color;
	//gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);
}
'''
tree_shader = Shader([tree_vs], [tree_fs])
