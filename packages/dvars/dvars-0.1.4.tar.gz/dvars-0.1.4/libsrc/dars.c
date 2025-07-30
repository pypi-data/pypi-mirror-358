#include <math.h>
#include <stdlib.h>

void rdcalcdp(float *acc, int na, float omega, float damp, float dt, double *reldis, double *absacc);

void dars(float damp, int na, float dt, float* a, int nf, double freq1, double freq2, double* freq,
	       	double* reldis, double* absacc) {
// This code calculates the response spectrum of a single-degree-of-freedom
// system to a given acceleration time record by calling the rdcalcdp
// subroutine, which calculates the system response to a single frequency
// using Duhamel's step integral method (Nigam and Jennings, 1968).
// The input acceleration time history is assumed to be uniformly sampled
// with a sampling interval dt.
// The output is the response spectrum sampled at nf frequency points
// in the range [freq1,freq2] in logarithmically spaced intervals.
// Input arguments:
// - damp: damping ratio
// - na: number of acceleration time history points
// - dt: sampling interval
// - a: acceleration time history
// - nf: number of frequency points
// - freq1: minimum frequency
// - freq2: maximum frequency
// Output:
// - freq: frequency points
// - reldis: relative displacement response spectrum
// - absacc: absolute acceleration response spectrum

    int k;
    double frinc, lf1, lf2;
    freq[0]=freq1;
    if (nf > 1) {
        // Calculate the frequency points
        if (freq1 > 0.0 && freq2 > 0.0) {
            lf1 = log(freq1);
            lf2 = log(freq2);
            frinc = (lf2 - lf1) / (double)(nf - 1);
            for (k = 1; k < nf; k++) {
                freq[k] = exp(lf1 + k * frinc);
            }
        } else {
            // "Error: freq1 and freq2 must be greater than zero"
            exit(1);
        }
    }

    float om;
    double sd, aa;
    for (k = 0; k < nf; k++) {
        om = 2.0 * M_PI * freq[k];
        rdcalcdp(a, na, om, damp, dt, &sd, &aa);
        reldis[k] = sd;
        absacc[k] = aa;
    }
}

