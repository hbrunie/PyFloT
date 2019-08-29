class PrecisionTuner
{
    private:
    unsigned long lowered_count = 0;
    unsigned long dyncount = 0;
    unsigned long MINBOUND = 0;
    unsigned long MAXBOUND = 0;
    void display();

    public:
    PrecisionTuner();
    ~PrecisionTuner();
    double overloading_function(float (*sp_func) (float, float), double (*func)(double, double), 
            double value, double parameter);
    double overloading_function(float (*sp_func) (float), double (*func)(double), double value);
};
