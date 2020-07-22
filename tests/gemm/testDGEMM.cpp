#include <cstdlib>
#include <cmath>
#ifdef USE_MKL
#include <mkl.h>
#else
extern "C" {
//#include"cblas.h"
}
#endif
#include <iostream>

extern "C"{
  extern void dgemm_(char const *transa, char const *transb, int *m, int *n, int *k,
              double *alpha, double *A, int *lda, double *B, int *ldb,
              double *beta, double *C, int *ldc);
  extern void sgemm_(char const *transa, char const *transb, int *m, int *n, int *k,
              float *alpha, float *A, int *lda, float *B, int *ldb, float *beta,
              float *C, int *ldc);
}
//extern "C" void start_test(void);
using namespace std;
int main(){
    //start_test();
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
    //cblas_dgemm(CblasRowMajor,CblasNoTrans,CblasNoTrans, m, n, k, alpha, A, k, B, n, beta, C, n);
    dgemm_("CblasNoTrans","CblasNoTrans", &m, &n, &k, &alpha, A, &k, B, &n, &beta, C, &n);
    double res = 0.;//cblas_dnrm2(m*n,C,n);
    for(int i=0; i<3;i++)
        fprintf(stderr, "C[%d] = %f\n", i, C[i]);
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
