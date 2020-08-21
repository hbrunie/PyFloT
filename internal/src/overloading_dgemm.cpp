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
#include <mkl.h>

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

void ptuner_dgemm(char const *transa, char const *transb, int *m, int *n, int* k,
                        double* alpha, double *A, int *lda, double *B, int* ldb,
                        double *beta, double *C, int* ldc){
    string label = "noLabel";
    struct dgemm_args_s dgemm_args = {transa, transb, m, n, k, alpha, A, lda, B, ldb, beta, C, ldc};
    struct sgemm_args_s sgemm_args;
    cerr << __FUNCTION__ << endl;
    ptuner.overloading_function("dgemm",dgemm_args, sgemm_args, label);
}

#endif
