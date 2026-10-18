import sys
print("stdout line from pythonw")
sys.stderr.write("stderr line from pythonw\n")
print("err/out captured:", bool(sys.stdout))
