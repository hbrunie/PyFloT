import os
import json
import subprocess
class Strategy:
    __count = 0
    __readJsonProfileFile = "None"
    __readJsonStratFile = "None"
    __dumpJsonStratResultFile = "None"
    __binary = "None"
    __last = False
    def __init__(self, binary, directory, readJsonProfileFile):
        count = self.__count
        self.__readJsonStratFile = directory + "readJsonStrat_{}.json".format(count)
        self.__dumpJsonStratResultFile = directory + "dumpJsonStratResults_{}.json".format(count)
        self.__binary = binary
        self.__count += 1
        ## Dev strategy
        with open(readJsonProfileFile, 'r') as json_file:
            profile = json.load(json_file)
        print(profile)
        self.__strategy = {"min": 0, "max": 1}
        with open(self.__readJsonStratFile, 'w') as json_file:
            json.dump(self.__strategy, json_file)
        return None

    def applyStrategy(self, checkString):
        procenv = os.environ.copy()
        ## TODO: No need of profile file for these executions 
        ## by the PrecisionTuner library
        #procenv["READJSONPROFILINGFILE"] = self.__readJsonProfileFile
        procenv["READJSONSTRATFILE"]     = self.__readJsonStratFile
        procenv["STRATRESULTJSONFILE"]   = self.__dumpJsonStratResultFile
        #procenv["DEBUG"] = "info,infoplus"
 
        command = []
        command.append(self.__binary)
        out = subprocess.check_output(command, stderr=subprocess.STDOUT, env=procenv)
        strout = out.decode("utf-8")
        #get count of lowered from output
        if checkString in strout:
            return True
        else:
            self.__last = True
            return False
    
    def isLast(self):
        return self.__last
