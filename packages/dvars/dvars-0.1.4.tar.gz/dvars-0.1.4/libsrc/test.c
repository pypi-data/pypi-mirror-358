


void dars(float damp, int na, float dt, float* a, int nf, double freq1, double freq2, double* freq,
	       	double* reldis, double* absacc);

// Test the dars function
#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include <time.h>
#include "dars.h"

int main() {
    // Define parameters
    float damp = 0.05; // Damping ratio
    int na = 1000; // Number of acceleration points
    float dt = 0.01; // Sampling interval
    int nf = 20; // Number of frequency points
    double freq1 = 0.1; // Minimum frequency
    double freq2 = 50.0; // Maximum frequency

    // Allocate memory for acceleration time history and response spectrum
    float* a = (float*)malloc(na * sizeof(float));
    double* freq = (double*)malloc(nf * sizeof(double));
    double* reldis = (double*)malloc(nf * sizeof(double));
    double* absacc = (double*)malloc(nf * sizeof(double));

    // Generate a sample acceleration time history (random values)
    srand(time(NULL));
    for (int i = 0; i < na; i++) {
	a[i] = ((float)rand() / RAND_MAX) * 2.0 - 1.0; // Random values between -1 and 1
    }

    // Call the dars function
    dars(damp, na, dt, a, nf, freq1, freq2, freq, reldis, absacc);

    // Print the results
    printf("Frequency Response Spectrum:\n");
    for (int i = 0; i < nf; i++) {
	printf("Freq: %.2f Hz, Rel Displacement: %.4f, Abs Acceleration: %.4f\n", 
	       freq[i], reldis[i], absacc[i]);
    }

    // Free allocated memory
    free(a);
    free(freq);
    free(reldis);
    free(absacc);

    return 0;
}
