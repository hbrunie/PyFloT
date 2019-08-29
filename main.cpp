#include<stdio.h>
#include<stdlib.h>

#include<PT_math.h>

double g(double a, int c){
    if(c/2==0)
        a = a * exp(-a);
    else
        a = a * pow(-a,a)*log(a);
    return a;
}

double f(double a, int c){
    double b =10.;
    if(c%2==1)
        b = a*cos(a)*b;
    else
        b = g(b,c)*sin(a)*b;
    b = fabs(b);
    return b;
}
double refvalue = 1911391536333.537109;
int main(int argc, char ** argv){
    char * th = getenv("THRESHOLD");
    double threshold = 0.1;
    if(th)
        threshold = atof(th);

    double a = 0.00001;
    a = a * exp(a+0.0005);
    a = f(a,0);
    for(int i = 0;i<5;i++)
        a = f(a,i);
    fprintf(stderr, "THRESHOLD=%f, reference=%f a=%f\n",
            threshold, refvalue, a);
    if(fabs(a-refvalue)/fabs(a) < threshold)
        fprintf(stderr, "SUCCESS\n");
    else
        fprintf(stderr, "FAILURE\n");

    
    return 0;
}
