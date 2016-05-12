class DefaultValues:
    """Datacontainer for the default values of the command line options"""
    
    nprocio  = None
    v_level  = 1
    mpicmd   = "aprun -n"
    submitcmd = "sbatch"
    submitscript = "submit.kesch.slurm"
    exe      = "cosmo_gpu"
    stdout   = ""
    np_s     = 8
    np_e     = 10
    npxy_min = 2
    ncomp_mult=1
    data_dir = "cosmo1"
    ngpu_nodes=16
