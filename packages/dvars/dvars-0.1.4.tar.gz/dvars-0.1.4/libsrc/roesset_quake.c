// Source: Part of the EXSIM code from GFZ Potsdam
// https://github.com/GFZ-Centre-for-Early-Warning/exsim/EXSIM12.for

#include <math.h>

void rdcalcdp(float *acc, int na, float omega, float damp, float dt,
	       	double *reldis, double *absacc) {

// This is a modified version of "Quake.For", originally written
// by J.M. Roesset in 1971 and modified
// by Stavros A. Anagnostopoulos, Oct. 1986.
// The formulation is that of Nigam and Jennings (BSSA, v. 59, 909-922, 1969).
// This modification returns the relative displacement and absolute acceleration.
//   acc = acceleration time series
//    na = length of time series
// omega = 2*pi/per
//  damp = fractional damping (e.g., 0.05)
//    dt = time spacing of input
// reldis = relative displacement of oscillator, output
// absacc = absolute acceleration of oscillator, output
// Dates: 05/06/95 - Modified by David M. Boore
//        04/15/96 - Changed name to RD_CALC and added comment lines
//                   indicating changes needed for storing the oscillator
//                   time series and computing the relative velocity and
//                   absolute acceleration
//        03/11/01 - Double precision version of Rd_Calc
//        01/31/03 - Moved implicit statement before the type declarations
//        11/05/25 - Added the absolute acceleration output
//                   Code ported to C from Fortran.

double omt, d2, bom, d3, omd, om2, omdt, c1, c2, c3, c4;
	omt = omega * dt;
	d2 = 1 - damp * damp;
	d2 = sqrt(d2);
	bom = damp * omega;
	d3 = 2.0 * bom;                 // for aa
	omd = omega * d2;
	om2 = omega * omega;
	omdt = omd * dt;
	c1 = 1.0 / om2;
	c2 = 2.0 * damp / (om2 * omt);
	c3 = c1 + c2;
	c4 = 1.0 / (omega * omt);
double ss, cc, bomt, ee, s1, s2, s3, a11, a12, a21, a22, s4, s5;
	ss = sin(omdt);
	cc = cos(omdt);
	bomt = damp * omt;
	ee = exp(-bomt);
	ss = ss * ee;
	cc = cc * ee;
	s1 = ss / omd;
	s2 = s1 * bom;
	s3 = s2 + cc;
	a11 = s3;
	a12 = s1;
	a21 = -om2 * s1;
	a22 = cc - s2;
	s4 = c4 * (1.0 - s3);
	s5 = s1 * c4 + c2;
double b11, b12, b21, b22;
	b11 = s3 * c3 - s5;
	b12 = -c2 * s3 + s5 - c1;
	b21 = -s1 + s4;
	b22 = -s4;
	double rd = 0.0;  // relative displacement
        double rv = 0.0;  // relative velocity
	double aa = 0.0;  // absolute acceleration
double y, ydot, y1, z, z1, ra, z2;
	int n1 = na - 1;
	y = 0.0;
	ydot = 0.0;
      for (int i = 0; i < n1; i++) {
        y1 = a11 * y + a12 * ydot + b11 * acc[i] + b12 * acc[i + 1];
        ydot = a21 * y + a22 * ydot + b21 * acc[i] + b22 * acc[i + 1];
        y = y1;           // y is the oscillator output at time corresponding to index i
        z = fabs(y);
        if (z > rd) rd = z;
        z1 = fabs(ydot);                                                  // for rv
        if (z1 > rv) rv = z1;                                             // for rv
        ra = -d3 * ydot - om2 * y1;                                       // for aa
        z2 = fabs(ra);                                                    // for aa
        if (z2 > aa) aa = z2;                                             // for aa
      }
   *reldis = rd;
   *absacc = aa;                                                      // for aa
}
