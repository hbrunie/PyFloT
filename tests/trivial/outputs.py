outputs = []
## Test Constructor
output = """PROFILING Command:  ['./testConstructor ']
PrecisionTuner: MODE PROFILING
PrecisionTuner: MODE PROFILING

"""
outputs.append(output)

output = """Error no callstacks\n"""
outputs.append(output)

output = """Strategy Command:  ['./testConstructor ']
Strategy: 1, STEP reached: NoOccurence
No more strategy to test.\n"""
outputs.append(output)

## Test Exp
output = """PROFILING Command:  ['./testExp ']
PrecisionTuner: MODE PROFILING
SUCCESS: 23.1039\n\n"""
outputs.append(output)

output = """No more strategy to generate.
"""
outputs.append(output)

output = """Strategy Command:  ['./testExp ']
Strategy: 1, STEP reached: NoOccurence
No more strategy to test.
"""
outputs.append(output)

## Test Header
output = """PROFILING Command:  ['./testHeader ']
PrecisionTuner: MODE PROFILING

"""
outputs.append(output)

output = """Error no callstacks
"""
outputs.append(output)

output = """Strategy Command:  ['./testHeader ']
Strategy: 1, STEP reached: NoOccurence
No more strategy to test.
"""
outputs.append(output)

## Test MathFunctions
output = """PROFILING Command:  ['./testMathFunctions ']
PrecisionTuner: MODE PROFILING
THRESHOLD=0.100000, reference=1911391536333.537109 a=1911391536333.537109
SUCCESS

"""
outputs.append(output)

output = """No more strategy to generate.
"""
outputs.append(output)

output = """Strategy Command:  ['./testMathFunctions ']
Strategy: 1, STEP reached: NoOccurence
No more strategy to test.\n"""
outputs.append(output)
