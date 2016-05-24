#!/bin/bash
#SBATCH --job-name=cosmo-7
#SBATCH --ntasks=?NTASKS?
#SBATCH --ntasks-per-node=18
#SBATCH --ntasks-per-socket=9
#SBATCH --output=test.out
#SBATCH --gres=gpu:16
#SBATCH --partition=dev
#SBATCH --account=s83                                            
#SBATCH --time=00:20:00                                            
#SBATCH --distribution=cyclic

echo "print =========================================="
echo "print SLURM_JOB_ID = $SLURM_JOB_ID"
echo "print SLURM_NODELIST = $SLURM_NODELIST"
echo "print =========================================="


source /etc/bashrc
module purge
source ./modules_fortran_kesch.env

# Set this to avoid segmentation faults
ulimit -s unlimited

# set environmental parameters

#export STELLA_DEBUG=42
export OMP_NUM_THREADS=1
export MALLOC_MMAP_MAX_=0
export MALLOC_TRIM_THRESHOLD_=536870912
export G2G=1
export MV2_USE_GPUDIRECT=0 #with this perf are ok
export COSMO_NPROC_NODEVICE=?NPROCIO?
export DYCORE_JSON_PERFORMANCE_REPORT=1


# cleanup
rm -f lm_fine_10min/* output/* lm_cnmet/*  lm_coarse_10min/*
mkdir -p lm_fine_10min/ output/ lm_cnmet/ lm_coarse_10min/

# delete old YU files (required if job is requeued by scheduler)
rm -f YU*

echo '********** Start Run ********* '
echo "StartTime: `date +%s` s"
srun -K -u --ntasks=?NTASKS? ./cosmo_gpu_float >& exe.log
echo "EndTime: `date +%s` s"
echo '********** End Run ********* '

