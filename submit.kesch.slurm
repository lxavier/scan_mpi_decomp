#!/bin/bash
#SBATCH --job-name=cosmo-1
#SBATCH --ntasks=?NTASKS?
#SBATCH --ntasks-per-node=16
#SBATCH --ntasks-per-socket=8
#SBATCH --output=test.out
#SBATCH --partition=normal
#SBATCH --time=03:00:00
#SBATCH --gres=gpu:16

echo "print =========================================="
echo "print SLURM_JOB_ID = $SLURM_JOB_ID"
echo "print SLURM_NODELIST = $SLURM_NODELIST"
echo "print =========================================="


source /etc/bashrc
source ./modules_fortran_kesch.env

export LD_LIBRARY_PATH=${CRAY_LD_LIBRARY_PATH}:${LD_LIBRARY_PATH}:/opt/cray/lib64:/usr/lib64:/opt/local/slurm/default/lib64:/opt/cray/netcdf/4.3.2/CRAY/83/lib



# Set this to avoid segmentation faults
ulimit -s unlimited

# set environmental parameters
#export STELLA_DEBUG=42
export OMP_NUM_THREADS=1
export MV2_ENABLE_AFFINITY=0
export MV2_USE_CUDA=1
export MALLOC_MMAP_MAX_=0
export MALLOC_TRIM_THRESHOLD_=536870912
export G2G=1
export COSMO_NPROC_NODEVICE=?NPROCIO?

# cleanup
rm -f lm_fine_10min/* output/*
mkdir -p lm_fine_10min/ output/

# delete old YU files (required if job is requeued by scheduler)
rm -f YU*

echo '********** Start Run ********* '
echo "StartTime: `date +%s` s"
srun -K -u --ntasks=?NTASKS? ./cosmo_gpu >& exe.log
echo "EndTime: `date +%s` s"
echo '********** End Run ********* '

