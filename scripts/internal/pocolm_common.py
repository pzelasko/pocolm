#!/usr/bin/env python

# we're using python 3.x style print but want it to work in python 2.x,
from __future__ import print_function
import os
import sys
import subprocess
import time
from subprocess import CalledProcessError


def ExitProgram(message):
    print("{0}: {1}".format(os.path.basename(sys.argv[0]),
                            message), file=sys.stderr)
    # we exit in this way in case we're inside a thread in a multi-threaded
    # program; we want the entire program to exit.
    os._exit(1)


def RunCommand(command, log_file, verbose=False):
    if verbose:
        print("{0}: running command '{1}', log in {2}".format(
                os.path.basename(sys.argv[0]), command, log_file),
              file=sys.stderr)
    try:
        f = open(log_file, 'w')
    except:
        ExitProgram('error opening log file {0} for writing'.format(log_file))

    # print the command to the log file.
    print('# {0}'.format(command), file=f)
    print('# running at ' + time.ctime(), file=f)
    f.flush()
    start_time = time.time()
    ret = subprocess.call(command, shell=True, stderr=f,
                          universal_newlines=True, executable='/bin/bash')
    end_time = time.time()
    print('# exited with return code {0} after {1} seconds'.format(
            ret, '%.1f' % (end_time - start_time)), file=f)
    f.close()
    if ret != 0:
        ExitProgram('command {0} exited with status {1}, output is in {2}'.format(
                command, ret, log_file))


def GetCommandStdout(command, log_file, verbose=False):
    if verbose:
        print("{0}: running command '{1}', log in {2}".format(
                os.path.basename(sys.argv[0]), command, log_file),
              file=sys.stderr)

    try:
        f = open(log_file, 'w')
    except:
        ExitProgram('error opening log file {0} for writing'.format(log_file))

    # print the command to the log file.
    print('# ' + command, file=f)
    print('# running at ' + time.ctime(), file=f)
    start_time = time.time()
    try:
        output = subprocess.check_output(command, shell=True, stderr=f,
                                         universal_newlines=True, executable='/bin/bash')
    except CalledProcessError as e:
        end_time = time.time()
        print(e.output, file=f)
        print('# exited with return code {0} after {1} seconds'.format(
            e.returncode, '%.1f' % (end_time - start_time)), file=f)
        f.close()
        ExitProgram('command {0} exited with status {1}, stderr is in {2} (output is: {3})'.format(
                command, e.returncode, log_file, e.output))

    print(output, file=f)
    end_time = time.time()
    print('# exited with return code 0 after {0} seconds'.format(
            '%.1f' % (end_time - start_time)), file=f)
    f.close()
    return output


def TouchFile(fname):
    if os.path.exists(fname):
        os.utime(fname, None)
    else:
        open(fname, 'a').close()


def LogMessage(message):
    print(os.path.basename(sys.argv[0]) + ": " + message, file=sys.stderr)


def DivideMemory(total, n):
    (value, unit) = ParseMemoryString(total)
    sub_memory = value // n
    if sub_memory != float(value) / n:
        if unit in ['K', 'k', '']:
            sub_memory = value * 1024 / n
            unit = 'b'
        elif unit in ['M', 'm']:
            sub_memory = value * 1024 / n
            unit = 'K'
        elif unit in ['G', 'g']:
            sub_memory = value * 1024 / n
            unit = 'M'
        elif (unit in ['B', 'b', '%']) and (sub_memory == 0):
            ExitProgram("max_memory for each of the {0} train sets is {1}{2}."
                        "Please reset a larger max_memory value".format(
                            n, float(value)/n, unit))
        else:
            ExitProgram("Invalid format for max_memory. "
                        "Please 'man sort' to see how to set buffer size.")
    return str(int(sub_memory)) + unit


# this function returns the value and unit of the max_memory
# if max_memory is in format of "integer + letter/%", like  "10G", it returns (10, 'G')
# if max_memory contains no letter, like "10000", it returns (10000, '')
# we assume the input string is not empty since when it is empty we never call this function
def ParseMemoryString(s):
    if not s[-1].isdigit():
        return (int(s[:-1]), s[-1])
    else:
        return (int(s), '')


class EnvironmentContext(object):
    """
    Context manager which sets the environment variables and unsets them once the context is finished.

    Usage:
        with EnvironmentContext(ENVVAR="x", ANOTHER_ENVVAR="y"):
            print(os.environ["ENVVAR"])
    """
    def __init__(self, **kwargs):
        self.envs = kwargs

    def __enter__(self):
        self.old_envs = {}
        for k, v in self.envs.items():
            self.old_envs[k] = os.environ.get(k)
            os.environ[k] = v

    def __exit__(self, *args):
        for k, v in self.old_envs.items():
            if v:
                os.environ[k] = v
            else:
		del os.environ[k]

