mkdir /srv/scratch/z3521839/shovill/shovill_runs/sophie2

FP="/srv/scratch/z3521839/fastq_files/stm/rem_sophie_strains_fq/*_1.fastq.gz";FILES=($FP);arrayno=${#FILES[@]};let arrayno=$arrayno-1;qsub -v FILES=$FP,OUTPUT=/srv/scratch/z3521839/shovill/shovill_runs/sophie2 -t 0-$arrayno""%20 /srv/scratch/z3521839/shovill/shovill_runs/run_shovill_array_15cov.pbs

mkdir /srv/scratch/z3521839/shovill/shovill_runs/saltykova

FP="/srv/scratch/z3521839/fastq_files/stm/saltykova_dataset/*_1.fastq.gz";FILES=($FP);arrayno=${#FILES[@]};let arrayno=$arrayno-1;qsub -v FILES=$FP,OUTPUT=/srv/scratch/z3521839/shovill/shovill_runs/saltykova -t 0-$arrayno""%20 /srv/scratch/z3521839/shovill/shovill_runs/run_shovill_array_15cov.pbs