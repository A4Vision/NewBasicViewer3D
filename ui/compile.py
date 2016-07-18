import os

from utils import my_commands
import sys
PATH = r"C:\Anaconda2\Lib\site-packages\PyQt4\uic"


def compile_ui(fname):
    cmd = "python.exe {1}\\pyuic.py {0}.ui -o {0}.py".format(fname.replace(".ui", ""), PATH)
    print 'cmd=', cmd
    print my_commands.getstatusoutput(cmd)


def compile_resource(fname):
    cmd = "pyrcc4 {0}.qrc -o {0}_rc.py".format(fname.replace(".qrc", ""))
    print 'cmd=', cmd
    print my_commands.getstatusoutput(cmd)


def main():
    compile_ui("motion_control.ui")
    s = open("motion_control.py", "rb").read()
    open("motion_control.py", "wb").write(s.replace("import icons_rc", "from icons import icons_rc"))
    os.chdir("../icons")
    compile_resource("icons.qrc")
    print 'done'


if __name__ == '__main__':
    main()