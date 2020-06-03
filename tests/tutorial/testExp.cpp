#include <cstdlib>
#include <iostream>
#include <cmath>
using namespace std;
/* Launch this test with:
    ${PYFLOT_ROOT}/public/pyflot/profiling.py --binary ./testExp --dumpdir .pyflot-testExp/
*/
int main(int ac, char * av[]){
    double a = exp(atof(av[0]));
    cout << "SUCCESS: "<< a << endl;
    return 0;
}
/*
 * alias pyflot-profiling=${PYFLOT_ROOT}/public/pyflot/profiling.py
 >>$ pyflot-profiling --binary ./testExp --dumpdir .pyflot-testExp/
         Profiling application ...
         Namespace(binary='./testExp', conf_file=None, dumpdir='.pyflot-testExp/', outputfile='output', params='', profilefile='profile.json', verif_text='VERIFICATION SUCCESSFUL')
         env: TARGET_FILENAME=./testExp PRECISION_TUNER_OUTPUT_DIRECTORY=.pyflot-testExp/ OMP_NUM_THREADS=1 PRECISION_TUNER_DUMPJSON=.pyflot-testExp/profile.json
         PROFILING Command:  ['./testExp ']
         ./testExp
        stargetExe./testExp
        3
        targetExe:./testExp
        ./testExp() [0x400a15]
        /lib64/libc.so.6(__libc_start_main+0xea) [0x2aaaab85234a]
        ./testExp() [0x40094a]
        ./testExp3
        Application profiled

>>$ ls .pyflot-testExp
    dumpCSVdynCallSite-0.csv  output                    profile.json

>>$ cat .pyflot-testExp/profile.json
    {
      "IndependantCallStacks" :
      [
        {
          "Addr2lineCallStack" :
          [
            "/global/u1/h/hbrunie/utils/tools/precisiontuning/tests/tutorial/testExp.cpp:6",
            "??:0",
            "/home/abuild/rpmbuild/BUILD/glibc-2.26/csu/../sysdeps/x86_64/start.S:122"
          ],
            "CSVFileName" : "dumpCSVdynCallSite-0.csv",
            "CallStack" :
          [
          "./testExp() [0x400a15]",
          "/lib64/libc.so.6(__libc_start_main+0xea) [0x2aaaab85234a]",
          "./testExp() [0x40094a]"
          ],
          "CallsCount" : 1,
          "HashKey" : "0x2aaaab85234a",
          "Index" : 0,
          "Labels" : null,
          "LowerBound" : 4294967295,
          "LowerCount" : 0,
          "UpperBound" : 0
        }
      ],
      "TotalCallStacks" : 1
    }

>>$ cat .pyflot-testExp/output
    SUCCESS: 1

>>$ cat .pyflot-testExp/dumpCSVdynCallSite-0.csv
    index timeStamp argument doubleP singleP absErr relErr spBoolean callSite
    0 38.465000 0.000000 1.000000 1.000000 0.000000 0.000000 0 0
*/
