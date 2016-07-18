import subprocess

def getstatusoutput(cmd):
    """Return (status, output) of executing cmd in a shell."""
    """This new implementation should work on all platforms."""

    pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, universal_newlines=True)
    output = "".join(pipe.stdout.readlines())
    sts = pipe.returncode
    if sts is None: sts = 0
    return sts, output
