#!/usr/bin/env python2

"""
Scritp to get scan results
"""

# built-in modules
import os, sys, string, struct,glob
import optparse as OP
import subprocess

# private modules
sys.path.append("./tools") # this is the generic folder for subroutines
from ts_fortran_nl import get_param, replace_param
from sc_utilities import get_line

# information
__author__     = "Xavier Lapillonne"
__license__    = "GPL"
__version__    = "1.0"
__date__       = "10.08.2015"
__maintainer__ = "xavier.lapillonne@meteoswiss.ch"



def parse_cmdline():
    """parse command line options"""

    # the parser is initialized with its description and its epilog
    parser = OP.OptionParser(description=
                "Description: this script get timing generated from scanscript",
              epilog=
                "Example: ./get_timing --scan_dir=./work/cosmo1")
            

    # Scan directory
    parser.set_defaults(scan_dir='.')
    parser.add_option("--scan_dir",dest="scan_dir",type="string",action="store",
               help="Scan directory (where the run_* are) [.]")

    # Sort timing
    parser.set_defaults(sort=False)
    parser.add_option("--sort",dest="sort",action="store_true",
               help="Sort by time [False]")

    # Filter ntot
    parser.set_defaults(filter_ntot=False)
    parser.add_option("--filter_ntot",dest="filter_ntot",action="store_true",
               help="Filter only one timing per ntot (should be use with --sort) [False]")

    # parse
    try:
        (options,args)=parser.parse_args()
    except (OP.OptionError,TypeError):
        sys.exit("problem parsing command line arguments (check ./get_scan_timing -h for valid arguments)")

    return options


def main():
    """read configuration and then execute scan"""
    # Aux
    CLOG="exe.log"       #cosmo LOG
    SLOG="test.out"      #scheduler log
    PARFILE="INPUT_ORG"  #file containing decomp. info
    
    # parse command line arguments
    opt = parse_cmdline()
        
    # cd to main scan dirt
    try:        
        os.chdir(opt.scan_dir)        
    except:
        print "Error : scan_dir %s does not exist" %(opt.scan_dir)
    
    # List run dir
    list_run=sorted(glob.glob("run_*"))

    #print header
    print '#  runid    ntot       npx       npy        npio        timeloop(s)   tot_run_time(s)'

    #init lists
    l_runid =[]
    l_npx=[]
    l_npy=[]
    l_npio=[]
    l_nptot=[]
    l_timeloop=[]
    l_tot_time=[]

    #get all infos
    for run_dir in list_run:
        os.chdir(run_dir)
        #get id from dir name
        l_runid.append(int(run_dir.split('run_')[1]))
   
        #check run success
        res=get_line(CLOG,"CLEAN UP")        
        if (len(res)==0):
            print "!! Warning :  %s file missing or run failed, skipping this run" %(os.getcwd()+'/'+CLOG)
            #back to scandir
            os.chdir('..')            
            continue
            
        #get config
        npx=int(get_param('INPUT_ORG','nprocx'))
        npy=int(get_param('INPUT_ORG','nprocy'))
        npio=int(get_param('INPUT_ORG','nprocio'))
        nptot=npx*npy+npio
        l_npx.append(npx)
        l_npy.append(npy)
        l_npio.append(npio)
        l_nptot.append(nptot)

        #get timing (last column in line containing time loop
        res=get_line(CLOG,"timeloop")
        if not res:
            print "!!Warning :  No timeloop keyword in log in %s, skipping this run" %(os.getcwd()+'/'+CLOG)
            #back to scandir
            os.chdir('..')            
            continue

        timeloop=res[0].split()
        timeloop=float(timeloop[5]) # assumes mean time on column 5     
        l_timeloop.append(timeloop)

        #get global timing (keyword Startime and EndTime) for slurm output
        if os.path.exists(SLOG):
            res=get_line(SLOG,"StartTime")
            if not res:
                sys.exit("Error :  No StartTime keyword in log in %s" %(os.getcwd()+'/'+SLOG))
            stime=res[0].split()
            stime=int(stime[1])
            res=get_line(SLOG,"EndTime")
            if not res:
                sys.exit("Error :  No EndTime keyword in log in %s" %(os.getcwd()+'/'+SLOG))
            etime=res[0].split()
            etime=int(etime[1])
            tot_time=etime-stime
        else:
            print "!!Warning : missing %s, total time set to 0" %(os.getcwd()+'/'+SLOG)
            tot_time=0
        l_tot_time.append(tot_time)
        #back to scandir
        os.chdir('..')


    # default id ordere    
    l_index=range(len(l_timeloop))
    
    #oder list y timeloop time if required
    if opt.sort:
        l_index=[i[0] for i in sorted(enumerate(l_timeloop), key=lambda x:x[1])]                


    #only get the fastet time per encountered nptot
    if opt.filter_ntot:
            l_filter=[]
            l_ntot_filter=[]
            #for i in l_index:

    #print res
    for i in l_index:        
        print ' %4i   %6i    %6i    %6i       %6i           %6.2f      %6i' %(l_runid[i],l_nptot[i],l_npx[i],l_npy[i],l_npio[i],l_timeloop[i],l_tot_time[i])
        

        
        


if __name__ == "__main__":
    main()


