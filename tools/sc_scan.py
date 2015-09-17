#!/usr/bin/env python2

"""


This module implements the scan baseclass which can be used to setup, run scan
"""

# built-in modules
import os, sys, copy, math, re, glob

# private modules
from ts_fortran_nl import get_param, replace_param
from ts_error import StopError, SkipError
from ts_utilities import dir_path, system_command, change_dir

# information
__author__     = "Xavier Lapillonne"
__date__       = "10.08.2015"
__maintainer__ = "xavier.lapillonne@meteoswiss.ch"


class Scan:
    """Class representing a scan element. Perpare and launch job"""

    def __init__(self, scanid, np, npx, npy, npio, options, conf, logger):
        
        # store private information for this test
        self.scanid = scanid
        self.name = options.data_dir      # ref input
        self.np  = np
        self.npx = npx
        self.npy = npy
        self.npio= npio 
        self.options = copy.copy(options) # test options
        self.conf = copy.copy(conf)       # storage of the auxiliary parameters
        self.logger = logger              # store logger
        self.executable = options.exe        

        # setup of directory paths
        self.basedir = dir_path(conf.basedir)
        self.inputdir = dir_path(self.basedir + options.data_dir) # set path for input directory
        self.rundir = dir_path(self.basedir) + dir_path(options.workdir) + dir_path(self.name) + dir_path("run_%i" %scanid)
        

    def run_test(self):
        """ check whether this test should be carried out in case "only" option is used"""
        if self.options.only is not None:
            if self.options.only=='%s,%s' %(self.type,self.name):
                return True
            else:
                return False
        else:
            return True


    def prepare(self):
        """prepare test directory and namelists for this test"""

        # log messages        
        self.__setup_directory()

        self.__setup_executable()

        self.__set_parallelization()

        self.__setup_submit_script()

        



    def launch(self):
        """launch test"""

        self.logger.info('Launching Job')

        # change to run directory for this test
        status = change_dir(self.rundir, self.logger)
        
        cmd=self.options.submitcmd+' '+self.options.submitscript
        self.logger.info(cmd)
        # executes the run command
        status = system_command(cmd, self.logger, False)       
       


    def __setup_directory(self):
        """generate test directory including all required links and sub-directories"""

        self.logger.info('Creating directory for '+self.name)

        # create run directory and move there
        status = system_command('/bin/mkdir -p '+self.rundir, self.logger)
        status = change_dir(self.rundir, self.logger)

        # removal of all the possible pre-existing files
        status = system_command('/bin/rm -r -f *', self.logger)
        
        # explicit copy of the namelists (copy is required since we will apply the change_par)
        status = system_command('/bin/cp -f '+self.inputdir+'INPUT_* .', self.logger)

        # copy of the auxiliary input parameters if exists (non compulsory)
        try:
            status = system_command('/bin/cp -f '+self.inputdir+'*.dat .', self.logger)
        except:
            pass

        # linking input binary fields
        status = system_command('/bin/ln -s '+dir_path(self.inputdir)+'input .', self.logger)

        # generation of the output folder
        status = system_command('/bin/mkdir -p output', self.logger)


    def __setup_executable(self):

        self.logger.info('Fetching executable '+self.basedir+self.executable)

        # copy of the executable
        if not os.path.exists(self.basedir+self.executable):
            raise SkipError('Executable '+self.basedir+self.executable+' does not exist')
        status = system_command('/bin/cp '+self.basedir+self.executable+' .', self.logger)
        


    def __set_parallelization(self):

        self.logger.info('Set domain decomposition')
        replace_param(self.conf.par_file, 'nprocx', ' nprocx= %i' %self.npx)
        replace_param(self.conf.par_file, 'nprocy', ' nprocy= %i' %self.npy)
                                 

    def __setup_submit_script(self):

        self.logger.info('Fetching/adapt submit script '+self.basedir+self.options.submitscript)

        # copy of script
        if not os.path.exists(self.basedir+self.options.submitscript):
            raise StopError('Script '+self.basedir+self.options.submitscript+' does not exist')
        status = system_command('/bin/cp '+self.basedir+self.options.submitscript+' .', self.logger)
        # Copy module file if exists (assumes module*)
        status = system_command('/bin/cp '+self.basedir+'/modules*'+' .', self.logger)

        #TODO : implement a better solution with proper handling of the submit script
        #set number of tasks
        status = system_command('/bin/grep ?NTASKS? %s' %(self.options.submitscript), self.logger,False)
        if (status!=0):
            raise StopError('No keyword ?NTASKS? in %s' %(self.basedir+self.options.submitscript))
        status = system_command('/bin/sed -i s/?NTASKS?/%i/g %s' %(self.np,self.options.submitscript), \
                                self.logger)
        #set id to job name
        status = system_command('/bin/sed -i s/?ID?/%i/g %s' %(self.scanid,self.options.submitscript), \
                                self.logger)
        #set env variable for IO procs
        status = system_command('/bin/sed -i s/?NPROCIO?/%i/g %s' %(self.npio,self.options.submitscript), \
                                self.logger)
        

