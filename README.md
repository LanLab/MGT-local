# MGT-local
Install a local blank version of the MGT database

The MGT database and associated scripts are presented here in a format that should make them installable on a local machine. 
The MGT was written as a website and associated database so the setup of a local version is more complex than a normal command line program.

# Installation:
## 1. input file generation
1. reference genome (fasta format)
2. lociLocationsInRef.txt - a tab delimited file with a row for each locus with columns:
   1. locus id
   2. reference genome start
   3. reference genome end
   4. \+ or - strand
   5. chromosome number (1 for all loci for most bacteria)
3. folder named "Schemes" -  with one file for each MGT level named MGTN_gene_accessions.txt where N is the level number. Each file lists the loci to be used in each level.

examples are in the setup/example_inputs folder

## 2. install dependencies
1. install [postgres](https://www.postgresql.org/download/)
2. [miniconda](https://docs.conda.io/en/latest/miniconda.html) or [mamba](https://mamba.readthedocs.io/en/latest/installation.html)(recommended) for environment management
3. create an environment within conda/mamba using the included yaml file (/setup/mgt_conda_env.yaml). Default name is mgtenv.
    ````
    conda env create --file=/path/to/MGT-local/setup/mgt_conda_env.yaml
    or
    mamba env create --file=/path/to/MGT-local/setup/mgt_conda_env.yaml
    ````

## 3. modify settings and urls files
In the /Mgt/Mgt/Mgt folder find the settings_template.py file and rename any lines with #CHANGE comments as per comment instructions. You can also make a copy of this file and update the changes in the copy. 
## 4. run /setup/setup_new_database.ssh
in command line use postgres password when prompted
## 5. access local mgt database site 
run `python manage.py runserver --settings Mgt.settings_template` and access the website locally using host in settings file (http://localhost:8000/ by default)
## 6. typing isolates
Typing of isolates is in three stages:
1. Run reads_to_alleles.py script to generate an alleles file from reads or genomes following the readme in the /MGT-local/Mgt/Mgt/MGT_processing/Reads2MGTAlleles folder
2. Upload the alleles files along with associated metadata to the local site (via a project page)
3. run the /MGT-local/Mgt/Mgt/Scripts/cron_pipeline.py script to call final alleles and MGT types

   ````
   conda activate mgt_env
   
   cd /path/to/MGT-local/Mgt/Mgt/Scripts
   
   python cron_pipeline.py -s /path/to/settings_file.py -d Blankdb --allele_to_db --local
   ````
