#include <cstdlib>
#include <cmath>
#include <iostream>
#include <iomanip>
#include <mkl.h>
#ifdef USE_MKL
#include <mkl.h>
#endif

using namespace std;
extern "C"{
    void ptuner_dgemm_(char const *transa, char const *transb, int *m, int *n, int *k,
            double *alpha, double *A, int *lda, double *B, int *ldb,
            double *beta, double *C, int *ldc);
    void dgemm_(char const *transa, char const *transb, int *m, int *n, int *k,
            double *alpha, double *A, int *lda, double *B, int *ldb,
            double *beta, double *C, int *ldc);
    void sgemm_(char const *transa, char const *transb, int *m, int *n, int *k,
            float *alpha, float *A, int *lda, float *B, int *ldb, float *beta,
            float *C, int *ldc);
}
#include "record.hpp"
int main(){
    cerr << setprecision(6);
    int m = 12;
    int n = 12;
    int k = 12;
    int lda = k;
    int ldb = n;
    int ldc = n;
    srand(42);
#ifdef USE_MKL
    double * A = (double*) mkl_malloc(m*k*sizeof(double), 64);
    double * B = (double*) mkl_malloc(k*n*sizeof(double), 64);
    double * C = (double*) mkl_malloc(m*n*sizeof(double), 64);
#else
    double * A = (double*) malloc(m*k*sizeof(double));
    double * B = (double*) malloc(k*n*sizeof(double));
    double * C = (double*) malloc(m*n*sizeof(double));
#endif
    for(int i=0; i<n*k;i++)
        B[i] = i;
    for(int testId = 0 ; testId < 100 ; testId++){
        for(int i=0; i<m*k;i++){
            A[i] = (double)rand()/(double)RAND_MAX;
        }
        double alpha = 1.0;
        double beta = 0.0;
#ifndef USE_PTUNER
        dgemm_("n","n", &m, &n, &k, &alpha, A, &lda, B, &ldb,
                &beta, C, &ldc);
#else
        ptuner_dgemm_("n","n", &m, &n, &k, &alpha, A, &lda, B, &ldb, &beta, C, &ldc);
#endif
        double res = cblas_dnrm2(m*n,C,1);
        cerr << "dgemm norm2 res("<<res << ") recorded["<< testId<< "](" << recorded[testId]<< ") relErr(" << fabs(res-recorded[testId]) / recorded[testId] << ")"<< endl;
    }

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
