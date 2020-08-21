#include <cstdlib>
#include <cmath>
#include <iostream>
#include <mkl.h>
#ifdef USE_PTUNER
#include <ptuner_gemm.hpp>
#endif

using namespace std;
int main(){
    int m = 12;
    int n = 12;
    int k = 12;
#ifdef USE_MKL
    double * A = (double*) mkl_malloc(m*k*sizeof(double), 64);
    double * B = (double*) mkl_malloc(k*n*sizeof(double), 64);
    double * C = (double*) mkl_malloc(m*n*sizeof(double), 64);
#else
    double * A = (double*) malloc(m*k*sizeof(double));
    double * B = (double*) malloc(k*n*sizeof(double));
    double * C = (double*) malloc(m*n*sizeof(double));
#endif
    for(int i=0; i<m*k;i++)
        A[i] = i;
    for(int i=0; i<n*k;i++)
        B[i] = i;
    double alpha = 1.0;
    double beta = 0.0;
#ifndef USE_PTUNER
    cblas_dgemm(CblasRowMajor,CblasNoTrans,CblasNoTrans, m, n, k, alpha, A, k, B, n, beta, C, n);
#else
    ptuner_dgemm("CblasNoTrans","CblasNoTrans", &m, &n, &k, &alpha, A, &k, B, &n, &beta, C, &n);
#endif
    double res = 0.;//cblas_dnrm2(m*n,C,n);
    cout << "SUCCESS: "<< res << endl;
#ifdef USE_MKL
    mkl_free(A);
    mkl_free(B);
    mkl_free(C);
#else
    free(A);
    free(B);
    free(C);
#endif
    return 0;
}
