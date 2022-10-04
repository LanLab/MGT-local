amkdir /srv/scratch/z3521839/shovill/shovill_runs/mathers1

FP="/srv/scratch/z3521839/fastq_files/PRJEB2189/*/*_1.fastq.gz";FILES=($FP);arrayno=${#FILES[@]};let arrayno=$arrayno-1;qsub -v FILES=$FP,OUTPUT=/srv/scratch/z3521839/shovill/shovill_runs/mathers1 -t 0-$arrayno""%20 /srv/scratch/z3521839/shovill/shovill_runs/run_shovill_array_15cov.pbs

mkdir /srv/scratch/z3521839/shovill/shovill_runs/mathers2

FP="/srv/scratch/z3521839/fastq_files/stm/mathers_r2/*_1.fastq.gz";FILES=($FP);arrayno=${#FILES[@]};let arrayno=$arrayno-1;qsub -v FILES=$FP,OUTPUT=/srv/scratch/z3521839/shovill/shovill_runs/mathers2 -t 0-$arrayno""%20 /srv/scratch/z3521839/shovill/shovill_runs/run_shovill_array_15cov.pbs

mkdir /srv/scratch/z3521839/shovill/shovill_runs/salty

FP="/srv/scratch/z3521839/fastq_files/stm/saltykova_dataset/*_1.fastq.gz";FILES=($FP);arrayno=${#FILES[@]};let arrayno=$arrayno-1;qsub -v FILES=$FP,OUTPUT=/srv/scratch/z3521839/shovill/shovill_runs/salty -t 0-$arrayno""%20 /srv/scratch/z3521839/shovill/shovill_runs/run_shovill_array_15cov.pbs

mkdir /srv/scratch/z3521839/shovill/shovill_runs/NZ

FP="/srv/scratch/z3521839/fastq_files/stm/NZ_fastq/*_1.fastq.gz";FILES=($FP);arrayno=${#FILES[@]};let arrayno=$arrayno-1;qsub -v FILES=$FP,OUTPUT=/srv/scratch/z3521839/shovill/shovill_runs/NZ -t 0-$arrayno""%20 /srv/scratch/z3521839/shovill/shovill_runs/run_shovill_array_15cov.pbs

mkdir /srv/scratch/z3521839/shovill/shovill_runs/leekit

FP="/srv/scratch/z3521839/fastq_files/stm/dt104_fastqs/*_1.fastq.gz";FILES=($FP);arrayno=${#FILES[@]};let arrayno=$arrayno-1;qsub -v FILES=$FP,OUTPUT=/srv/scratch/z3521839/shovill/shovill_runs/leekit -t 0-$arrayno""%20 /srv/scratch/z3521839/shovill/shovill_runs/run_shovill_array_15cov.pbs

mkdir /srv/scratch/z3521839/shovill/shovill_runs/Westmead

FP="/srv/scratch/z3521839/Westmead_data/fastq_only/*_1.fastq.gz";FILES=($FP);arrayno=${#FILES[@]};let arrayno=$arrayno-1;qsub -v FILES=$FP,OUTPUT=/srv/scratch/z3521839/shovill/shovill_runs/Westmead -t 0-$arrayno""%20 /srv/scratch/z3521839/shovill/shovill_runs/run_shovill_array_15cov.pbs

mkdir /srv/scratch/z3521839/shovill/shovill_runs/Anast

FP="/srv/scratch/lanlab/Anastasia_fastqs/*_1.fastq.gz";FILES=($FP);arrayno=${#FILES[@]};let arrayno=$arrayno-1;qsub -v FILES=$FP,OUTPUT=/srv/scratch/z3521839/shovill/shovill_runs/Anast -t 0-$arrayno""%20 /srv/scratch/z3521839/shovill/shovill_runs/run_shovill_array_15cov.pbs


