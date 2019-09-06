class Strategy:
    __min = 0
    __max = 100
    __readJsonProfileFile = "None"
    __readJsonStratFile = "None"
    __dumpJsonStratResultFile = "None"
    def __init__(self, readJsonProfileFile, readJsonStratFile, dumpJsonStratResultFile):
        __readJsonProfileFile = readJsonProfileFile
        __readJsonStratFile = readJsonStratFile
        __dumpJsonStratResultFile = dumpJsonStratResultFile
        return None

    def applyStrategy():
        procenv = os.environ.copy()
        procenv["READJSONPROFILINGFILE"] = __readJsonProfileFile
        procenv["READJSONSTRATFILE"]     = __readJsonStratFile
        procenv["STRATRESULTJSONFILE"]   = __dumpJsonStratResultFile
 
        command = []
        command.append(self.__binary)
        out = subprocess.check_output(command, stderr=subprocess.STDOUT, env=procenv)
        strout = out.decode("utf-8")
        # Stop searching?
        if score > maxScore:
            return False
        else:
            return True
