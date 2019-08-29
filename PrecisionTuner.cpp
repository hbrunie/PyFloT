#include <stdlib.h>
#include <cstdio>
#include "PrecisionTuner.hpp"    
PrecisionTuner::PrecisionTuner(){
    char * tmp = getenv("MINBOUND");
    if(tmp)
        MINBOUND = atol(tmp);
    tmp = getenv("MAXBOUND");
    if(tmp)
        MAXBOUND = atol(tmp);
}

PrecisionTuner::~PrecisionTuner(){
    display();
}

double PrecisionTuner::overloading_function(float (*sp_func) (float, float), double (*func)(double, double), 
        double value, double parameter){
    float fvalue = (float)value;
    float fparameter = (float)parameter;
    double res;

    if(dyncount >= MINBOUND && dyncount < MAXBOUND){
        res = (double) sp_func(fvalue, fparameter);
        lowered_count ++;
    }else{
        res = func(value, parameter);
    }
    dyncount++;
    return res;
}

double PrecisionTuner::overloading_function(float (*sp_func) (float), double (*func)(double), double value){
    float fvalue = (float)value;
    double res;

    if(dyncount >= MINBOUND && dyncount < MAXBOUND){
        res = (double) sp_func(fvalue);
        lowered_count ++;
    }else{
        res = func(value);
    }
    dyncount++;
    return res;
}

void PrecisionTuner::display(){
    fprintf(stderr,"LOWERED %lu\n", (unsigned long) lowered_count);
    fprintf(stderr,"TOTAL_DYNCOUNT %lu\n", (unsigned long) dyncount);
    fprintf(stderr,"MAXBOUND %lu MINBOUND %lu\n", MAXBOUND, MINBOUND);
}
