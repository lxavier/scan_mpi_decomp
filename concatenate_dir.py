#!/usr/bin/env python2

"""
Concatenate dir
"""

# built-in modules
import os, sys, glob


def main(dir1,dir2,newdir):
    
    #def run dir pattern
    rundirpattern="run_"

    # check dir existence and create new dir
    if not(os.path.exists(dir1)):
        print 'Error: File '+dir1+' does not exist'
        return -1
    if not(os.path.exists(dir2)):
        print 'Error: File '+dir2+' does not exist'
        return -1
    if (os.path.exists(newdir)):
        print 'Error:  File '+newdir+' already exists'
        return -1
    else:
        os.mkdir(newdir)
    

    list_dir=glob.glob(dir1+"/"+rundirpattern+"*")
    list_dir+=glob.glob(dir2+"/"+rundirpattern+"*")

    for i in range(len(list_dir)):
        os.rename(list_dir[i],newdir+"/"+rundirpattern+str(i+1))

    

    
#-----------------------------------
#execute as a script 
if __name__ == "__main__":

    if len(sys.argv)==4:
        main(sys.argv[1],sys.argv[2],sys.argv[3])
    else:
        print '''USAGE : ./concatenate_dir.py dir1 dir2 newdir '''
    

