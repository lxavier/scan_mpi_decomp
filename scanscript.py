#!/usr/bin/env python2

"""
Scritp to scan over MPI decomposion (adapt from testsuite)
"""

# built-in modules
import os, sys, string, struct
import optparse as OP

# private modules
sys.path.append("./tools") # this is the generic folder for subroutines
from sc_scan import Scan
from ts_error import StopError
from ts_fortran_nl import get_param, replace_param
from ts_utilities import system_command, change_dir, dir_path
import ts_logger as LG
from default_values import DefaultValues

# information
__author__     = "Xavier Lapillonne"
__license__    = "GPL"
__version__    = "1.0"
__date__       = "10.08.2015"
__maintainer__ = "xavier.lapillonne@meteoswiss.ch"


def setup_configuration():
    """setup an object to carry some global configuration parameters"""

    # construct empty structure
    class Empty:
        pass
    conf = Empty()

    # save base directory where scansuite is executed
    conf.basedir = dir_path(os.getcwd())

    # list of all namelist files which will copied
    conf.l_files = ['INPUT_ORG','INPUT_ASS','INPUT_DIA','INPUT_DYN','INPUT_INI',\
                    'INPUT_IO','INPUT_PHY','INPUT_SAT','INPUT_POL','INPUT_IDEAL']

    # namelist file which contains nprocx, nprocy and nprocio
    conf.par_file = 'INPUT_ORG'

    # namelist file which contains the timestep (dt)
    conf.dt_file = 'INPUT_ORG'

    # name of file to which scan info are being written
    conf.scaninfo = 'scaninfo.txt'

    # name of the main file containing output for testing
    conf.yufile = 'YUPRTEST'

    # dual namelist parameters (relevant to the testsuite)
    conf.dual_params = []
    conf.dual_params.append(('nstop','hstop'))
    conf.dual_params.append(('hincrad','nincrad'))

    conf.scheduler_ntasks_key='ntasks'

    return conf


def parse_cmdline():
    """parse command line options"""

    # the parser is initialized with its description and its epilog
    parser = OP.OptionParser(description=
                "Description: this script run cosmo for different MPI configuration",
              epilog=
                "Example: ./scansuite.py --exe=cosmo_gpu --submitscript=submit.kesch.slurm --np_s=120 --np_e=128 --data_dir=cosmo1")
            
    # set the level of verbosity of the standard output
    parser.set_defaults(v_level=DefaultValues.v_level)
    parser.add_option("-v",type="int",dest="v_level",help=("verbosity level 0 to 3 [default=%d]" % DefaultValues.v_level))

    # start scan
    parser.set_defaults(np_s=DefaultValues.np_s)
    parser.add_option("--np_s",type="int",dest="np_s",help=("Start number of tasks [default=%d]" % DefaultValues.np_s))

    # end scan
    parser.set_defaults(np_e=DefaultValues.np_e)
    parser.add_option("--np_e",type="int",dest="np_e",help=("End number of tasks [default=%d]" % DefaultValues.np_e))

    # min npx npy
    parser.set_defaults(npxy_min=DefaultValues.npxy_min)
    parser.add_option("--npxy_min",type="int",dest="npxy_min",help=("Min  [default=%d]" % DefaultValues.npxy_min))

    # npx*npy mult
    parser.set_defaults(ncomp_mult=DefaultValues.ncomp_mult)
    parser.add_option("--ncomp_mult",type="int",dest="ncomp_mult",help=("Min  [default=%d]" % DefaultValues.ncomp_mult))


    # specifies the syntax of the mpi command
    parser.set_defaults(mpicmd=DefaultValues.mpicmd)
    parser.add_option("--mpicmd",dest="mpicmd",type="string",
               help=("MPI run command (e.g. \"mpirun -n\") [default=\"%s\"]" % DefaultValues.mpicmd))

    # specifies the syntax of the submit command
    parser.set_defaults(submitcmd=DefaultValues.submitcmd)
    parser.add_option("--submitcmd",dest="submitcmd",type="string",
               help=("submit command [default=\"%s\"]" % DefaultValues.submitcmd))

    # specifies submit script
    parser.set_defaults(submitscript=DefaultValues.submitscript)
    parser.add_option("--submitscript",dest="submitscript",type="string",
               help=("submit script [default=\"%s\"]" % DefaultValues.submitscript))

    # defines the executable name, this overides the definition in testlist.xml if any
    parser.set_defaults(exe=DefaultValues.exe)
    parser.add_option("--exe",dest="exe",type="string",
               help="Executable file, [default=\"%s\"]" % DefaultValues.exe )

    # defines the filename for the redirected standard output
    parser.set_defaults(stdout=DefaultValues.stdout)
    parser.add_option("-o",dest="stdout",type="string",action="store",
               help="Redirect standard output to selected file [default=<stdout>]")
    
    # defines the behaviour of the redirected standard output, if appended or overwritten
    parser.add_option("-a","--append",action="store_true",default=False,dest="outappend",
               help="Appends standard output if redirection selected [default=False]")

    # Ref data directory
    parser.set_defaults(data_dir=DefaultValues.data_dir)
    parser.add_option("--data_dir",dest="data_dir",type="string",action="store",
               help="Working directory [default=\"%s\"]" % DefaultValues.data_dir)

    # working directory
    parser.add_option("--workdir",dest="workdir",type="string",action="store",default="./work",
               help="Working directory [default=./work]")

    # No run option (only create folders)
    parser.set_defaults(norun=False)
    parser.add_option("--norun",dest="norun",action="store_true",
               help="No run option only creates folders")

    # parse
    try:
        (options,args)=parser.parse_args()
    except (OP.OptionError,TypeError):
        sys.exit("problem parsing command line arguments (check ./testsuite.py -h for valid arguments)")

    return options


def setup_logger(options):

    # instantiate logger class
    logger = LG.Logger(options.stdout, options.outappend, False)

    # set verbosity level
    if options.v_level <= 0:
      logger.setLevel(LG.ERROR)
    elif options.v_level == 1:
      logger.setLevel(LG.WARNING)
    elif options.v_level == 2:
      logger.setLevel(LG.INFO)
    elif options.v_level >= 3:
      logger.setLevel(LG.DEBUG)

    return logger

def get_parallelization(nprocs,nprocio):
    """return a list of possible tuples of domain decompositions"""

    nxy = int(nprocs)-int(nprocio)
    if nxy < 1:
        raise ValueError('*** ERROR: The number of total processor'\
                                 ' is smaller equal the number of I\O processors')
    parlist = []

    for i in range(nxy,0,-1):
        if nxy%i == 0:
            parlist.append([i,nxy/i])
        
    # sort parlist by aspect ratio of solutions
    parlist = sorted(parlist, key=lambda tuple: aspect_ratio(tuple[0],tuple[1]))


    return parlist    
    

def aspect_ratio(nprocx,nprocy):
    """compute aspect ratio of decomposition"""
    nprocx = abs(float(nprocx))
    nprocy = abs(float(nprocy))
    if (nprocx > nprocy):
        return nprocx/nprocy
    else:
        return nprocy/nprocx    

def main():
    """read configuration and then execute scan"""

    # definition of structure carrying global configuration
    conf = setup_configuration()
    
    # parse command line arguments
    opt = parse_cmdline()
        
    # redirect standard output (if required)
    logger = setup_logger(opt)

    # hello world!
    logger.important('SCANSCRIPT ')

    # generate work directory
    status = system_command('/bin/mkdir -p '+opt.workdir+'/', logger, throw_exception=False)
    if status:
      exit(status)

    # Set ref data path
    data_path=dir_path(conf.basedir + opt.data_dir)
    if not os.path.exists(data_path):
        sys.exit("Missing folder %s" %data_path)

    #get nprocio
    nprocio=int(get_param(data_path+conf.par_file,"nprocio"))

    #init scan_id
    scan_id=0

    #---------------------------------------------------------
    # scan over np
    for np in range(opt.np_s,opt.np_e+1):
        #check if ncompute is a modulo of opt.ncomp_mult
        if ((np-nprocio)%opt.ncomp_mult==0):
            parlist=get_parallelization(np,nprocio)
        else:
            parlist=[]
        for pardecomp in parlist:
            #only considerf if both npx and npy > min
            npx=pardecomp[0]
            npy=pardecomp[1]
            if (npx >= opt.npxy_min) and (npy >= opt.npxy_min):
                scan_id+=1
                logger.important("%s, scanid %s : nproc=%i, npx=%i, npy=%i" %(opt.data_dir,scan_id,np,npx,npy))
                scan=Scan(scan_id, np, npx, npy, nprocio, opt, conf, logger)

                #Prepare rundir
                scan.prepare()

                #Launch
                if not opt.norun:
                    scan.launch()
    
        

    # end of testsuite std output
    logger.important('FINISHED')


if __name__ == "__main__":
    main()


