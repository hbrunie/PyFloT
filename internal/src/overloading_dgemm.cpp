#include <alloca.h>
#include <assert.h>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iostream>
#include <limits.h>
#include <sstream>

#include <dlfcn.h>
#include <sys/resource.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <unistd.h>

#include "PrecisionTuner.hpp"

using namespace std;

#ifndef TEST_VERSION
/******** Globals variables **********/

static PrecisionTuner ptuner;

/******** Function definitions **********/

extern "C"{
  void dgemm_(char const *transa, char const *transb, int *m, int *n, int *k,
              double *alpha, double *A, int *lda, double *B, int *ldb,
              double *beta, double *C, int *ldc);
  void sgemm_(char const *transa, char const *transb, int *m, int *n, int *k,
              float *alpha, float *A, int *lda, float *B, int *ldb, float *beta,
              float *C, int *ldc);

}
/* *** Overloading functions *** */

extern "C"{
double dnrm2_(int* n, double *x, int* incx);
double cblas_dnrm2(int n, double *x, int incx);
  float cblas_snrm2(int n, float *x, int incx);
  }

void __overloaded_dgemm(char const *transa, char const *transb, int *m, int *n, int* k,
                        double* alpha, double *A, int *lda, double *B, int* ldb,
                        double *beta, double *C, int* ldc){
    string label = "noLabel";
    struct dgemm_args_s dgemm_args = {transa, transb, m, n, k, alpha, A, lda, B, ldb, beta, C, ldc};
    struct sgemm_args_s sgemm_args;
    ptuner.overloading_function("dgemm_",sgemm_,dgemm_, dgemm_args, sgemm_args, label);
}
void __overloaded_sgemm(char const *transa, char const *transb, int* m, int* n, int* k,
                        float *alpha, float *A, int* lda, float *B, int* ldb,
                        float *beta, float *C, int* ldc){
    string label = "noLabel";
    struct sgemm_args_s sgemm_args = {transa, transb, m, n, k, alpha, A, lda, B, ldb, beta, C, ldc};
    struct dgemm_args_s args;
    ptuner.overloading_function("sgemm_",sgemm_,dgemm_, args, sgemm_args, label);
}

//extern "C" void cblas_dgemm_pyflot(const CBLAS_LAYOUT Layout, const CBLAS_TRANSPOSE transa, const CBLAS_TRANSPOSE transb, const MKL_INT m, const MKL_INT n, const MKL_INT k, const double alpha, const double *A, const MKL_INT lda, const double *B, const MKL_INT ldb, const double beta, double *C, const MKL_INT ldc){
//    struct dgemm_args_s dgemm_args = {Layout, transa, transb, m, n, k, alpha, A, lda, B, ldb, beta, C, ldc};
//    struct sgemm_args_s sgemm_args;
//    string label("cblas dgemm");
//    ptuner.overloading_function("dgemm",cblas_sgemm,cblas_dgemm, dgemm_args, sgemm_args, label);
//
//}

#endif
