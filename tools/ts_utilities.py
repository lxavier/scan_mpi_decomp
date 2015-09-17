#!/usr/bin/env python2

"""
COSMO TECHNICAL TESTSUITE

Collection of general purpose utility functions
"""

# built-in modules
import re, os, subprocess

# private modules
from ts_error import StopError

# information
__author__     = "Oliver Fuhrer, Xavier Lapillonne, Nicolo Lardelli"
__copyright__  = "Copyright 2012, COSMO Consortium"
__license__    = "GPL"
__version__    = "1.0"
__date__       = "Mon Oct  8 15:37:57 CEST 2012"
__email__      = "cosmo-wg6@cosmo.org"
__maintainer__ = "xavier.lapillonne@meteoswiss.ch"

class TimeoutExpired(Exception):
    pass

if not hasattr(subprocess,'TimeoutExpired'):
    timeout_supported = False
    subprocess.TimeoutExpired = TimeoutExpired
else:
    timeout_supported = True

def dir_path(path):
    """decorate a path with a trailing slash if not present"""
    pattern='^(.*)[/]$'
    matchobj=re.match(pattern,path)
    if matchobj:
        return path
    else:
        return path+'/'


def change_dir(dir, logger, throw_exception=True):
    """wrapper to issue a change of working directory and handle errors"""

    logger.debug('ChgDir: '+dir+' (from '+str(os.getcwd())+')')

    status = os.chdir(dir)

    if status:
        if throw_exception:
            raise StopError('Problem changing to directory '+dir)
        else:
            logger.error('Problem changing to directory '+dir)


def system_command(cmd, logger, throw_exception=True, return_output=False, issue_error=True, timeout=None):
    """wrapper to launch systems commands and handle stdout/stderr and exit status correctly"""

    # launch command
    status = 0
    try:
        logger.debug('SysCmd: '+cmd)
        s = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    except Exception as e:
        if issue_error:
            logger.error(e)
            logger.error('Problem with launching system command: '+cmd)
        status = -1

    # wait for command termination
    if not status:
        try:
            if timeout_supported and timeout:
                s.wait(timeout=int(timeout))
            else:
                s.wait()
        except subprocess.TimeoutExpired:
            logger.error('Timeout for system command: '+cmd)
            s.kill()
            s.wait()
            status = -2
        except Exception as e:
            logger.error(e)
            logger.error('Problem with waiting for system command: '+cmd)
            status = -3

    # wait for command termination and log output to logger
    lines=''
    if status != -1:
        while True:
            line = s.stdout.readline()
            if not line:
                break
            lines += line
            if not return_output:
                logger.debug('   Out: '+line.rstrip())
    if not status:
        status = s.returncode

    # trow exception if requested
    if status: 
        if throw_exception:
            raise StopError('Error with system command: '+cmd)
        else:
            if issue_error:
                logger.error('Error with system command: '+cmd)

    if return_output:
        return (status,lines)
    else:
        return status
    

def status_str(status):
    """return status string from status code"""

    status_map = {
      0: 'MATCH',
     10: 'OK',
     15: 'SKIP',
     20: 'FAIL',
     30: 'CRASH'
    }
    return status_map.get(status, 'UNKNOWN')


def pretty_status_str(status,color,bold):
    """return pretty status string from status code"""

    if bold:
        bold_str='1'
    else:
        bold_str='0'

    color_map = {
      0: 32, # green
     10: 32, # green
     15: 37, # white
     20: 31, # red
     30: 31, # red
    }
    color_code=color_map.get(status,41)

    if color:
        COL_ON='\033['+bold_str+';'+str(color_code)+'m'
        COL_OFF='\033[0m'
    else:
        COL_ON=''
        COL_OFF=''

    return COL_ON+status_str(status)+COL_OFF


def write_environ(test):
    """write environment variables for checkers"""

    os.environ['TS_BASEDIR'] = test.basedir
    os.environ['TS_REFOUTDIR'] = test.refoutdir
    os.environ['TS_VERBOSE'] = str(test.options.v_level)
    os.environ['TS_RUNDIR'] = test.rundir
    os.environ['TS_LOGFILE'] = test.log_file
    os.environ['TS_NAMELISTDIR'] = test.namelistdir
    os.environ['TS_TOLERANCE'] = test.tolerance
    os.environ['TS_FORCEMATCH'] = str(test.options.forcematch)

def read_environ():
    """read environment variables and store into local map"""

    environ = {}
    environ['BASEDIR'] = os.environ['TS_BASEDIR']
    environ['REFOUTDIR'] = os.environ['TS_REFOUTDIR']
    environ['VERBOSE'] = os.environ['TS_VERBOSE']
    environ['RUNDIR'] = os.environ['TS_RUNDIR']
    environ['LOGFILE'] = os.environ['TS_LOGFILE']
    environ['NAMELISTDIR'] = os.environ['TS_NAMELISTDIR']
    environ['TOLERANCE'] = os.environ['TS_TOLERANCE']
    environ['FORCEMATCH'] = os.environ['TS_FORCEMATCH']

    return environ

