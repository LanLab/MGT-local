Generating alleles file locally
-------------------------------

In order reduce the amount of data to be uploaded to the [MGT database](http://mgtdb.unsw.edu.au) some of the MGT pipeline processing can be performed locally.

These steps include:

**1 - Species, serovar checking with [kraken](https://ccb.jhu.edu/software/kraken/) and [SISTR](https://github.com/phac-nml/sistr_cmd)**

**2 - Genome assembly with [shovill](https://github.com/tseemann/shovill) and [skesa](https://github.com/ncbi/SKESA)**

**3 - Genome QC**

**4 - Extraction of alleles from genome using known allele fasta file**

**5 - Assignment of 7 gene MLST sequence type**

The resulting file is often several orders of magnitude smaller than the raw reads, facilitating rapid upload and analysis.

Install
-----------
**1. Download this repo:**

	git clone https://github.com/LanLab/MGT_reads2alleles.git

**2. Download latest miniKraken Database:**

Before setting up the pipeline for processing raw data reads into alleles, firstly download a minikraken database (warning is 2.9GB).

The MiniKraken DB can be accessed at https://ccb.jhu.edu/software/kraken/,

OR

	wget https://ccb.jhu.edu/software/kraken/dl/minikraken_20171019_4GB.tgz

	unzip archive


**3. Add database folder variable with:**

    export KRAKEN_DEFAULT_DB="/home/user/minikraken_db_folder"


**4. Install miniconda3:**

This pipeline requires you already have a miniconda3 installed.  
install miniconda3 -> https://conda.io/miniconda.html


**5. Create miniconda3 environment:**

Next a Miniconda3 environment will be created and will contain all the required dependencies for this pipeline.
The "fq_to_allele.yml" has been provided to creating an environment named "fq_to_allele".

	conda env create -f /path_to_MGT_reads2alleles/fq_to_allele.yml -n fq_to_allele

**6. Users Permission**

Lastly, the user permissions for the shovill_15cov file must be adjusted to allow execution

	chmod 755 /path_to_MGT_reads2alleles/shovill_cmd/bin/shovill_15cov

Run
---


**Activate conda environment**

    conda activate fq_to_allele

**For usage**

    python /path/to/reads_to_alleles.py -h

	usage: reads_to_alleles.py [-h] -i INPUTREADS -r REFALLELES -o OUTPATH
                           [-s SPECIES] [--no_serotyping NO_SEROTYPING]
                           [-y SEROTYPE] [-t THREADS] [-m MEMORY] [-f]
                           [--min_largest_contig MIN_LARGEST_CONTIG]
                           [--max_contig_no MAX_CONTIG_NO]
                           [--genome_min GENOME_MIN] [--genome_max GENOME_MAX]
                           [--n50_min N50_MIN] [--kraken_db KRAKEN_DB]
                           [--hspident HSPIDENT] [--locusnlimit LOCUSNLIMIT]
                           [--snpwindow SNPWINDOW] [--densitylim DENSITYLIM]
                           [--refsize REFSIZE] [--blastident BLASTIDENT]
                           [--strainid STRAINID]

    optional arguments:
      -h, --help            show this help message and exit
      -i INPUTREADS, --inputreads INPUTREADS
                            Input paired fastq(.gz) files, comma separated (i.e.
                            name_1.fastq,name_2.fastq ) (default: None)
      -r REFALLELES, --refalleles REFALLELES
                            File path to MGT reference allele file. (default:
                            None)
      -o OUTPATH, --outpath OUTPATH
                            Path to ouput file name,required=True (default: None)
      -s SPECIES, --species SPECIES
                            String to find in kraken species confirmation test
                            (default: Salmonella enterica)
      --strainid STRAINID
                            Specify strain name instead of extracting from read file name
                            (default: None)
      --no_serotyping NO_SEROTYPING
                            Do not run Serotyping of Salmonella using SISTR (ON by
                            default) (default: None)
      -y SEROTYPE, --serotype SEROTYPE
                            Serotype to match in SISTR, semicolon separated
                            (default: Typhimurium;I 4,[5],12:i:-)
      -t THREADS, --threads THREADS
                            number of computing threads (default: 4)
      -m MEMORY, --memory MEMORY
                            memory available in GB (default: 8)
      -f, --force           overwrite output files with same strain name?
                            (default: False)
      --min_largest_contig MIN_LARGEST_CONTIG
                            Assembly quality filter: minimum allowable length of
                            the largest contig in the assembly in bp (default:
                            60000)
      --max_contig_no MAX_CONTIG_NO
                            Assembly quality filter: maximum allowable number of
                            contigs allowed for assembly (default: 700)
      --genome_min GENOME_MIN
                            Assembly quality filter: minimum allowable total
                            assembly length in bp (default: 4500000)
      --genome_max GENOME_MAX
                            Assembly quality filter: maximum allowable total
                            assembly length in bp (default: 5500000)
      --n50_min N50_MIN     Assembly quality filter: minimum allowable n50 value
                            in bp (default for salmonella) (default: 20000)
      --kraken_db KRAKEN_DB
                            path for kraken db (if KRAKEN_DEFAULT_DB variable has
                            already been set then ignore) (default:
                            /srv/scratch/lanlab/kraken_dir/minikraken_20141208)
      --hspident HSPIDENT   BLAST percentage identity needed for hsp to be
                            returned (default: 0.98)
      --locusnlimit LOCUSNLIMIT
                            minimum proportion of the locus length that must be
                            present (not masked with Ns) (default: 0.8)
      --snpwindow SNPWINDOW
                            Size of sliding window to screen for overly dense SNPs
                            (default: 40)
      --densitylim DENSITYLIM
                            maximum number of SNPs allowed to be present in window
                            before window is masked (default: 4)
      --refsize REFSIZE     Approx size of genome for shovill input in megabases
                            i.e. 5.0 or 2.9 (default: 5.0)
      --blastident BLASTIDENT
                            BLAST percentage identity needed for entire alignment to be returned (default: 90)
      --strainid STRAINID   specify a strain name (overrides default extraction
                            from read names) (default: False)


Examples
--------

**example1:**

running strain 1234 against salmonella typhimurium MGT with 8 cores and 30gb RAM

    python /path/to/reads_to_alleles.py -i 1234_1.fastq.gz,1234_2.fastq.gz -r MGT_alleles_file -o output_file_name --serotype "Typhimurium;I 4,[5],12:i:-" --species "Salmonella enterica" -t 8 -m 30

**example2:**

running strain abcd against vibrio cholerae MGT with 4 cores and 50gb RAM
(serotyping is currently only for Salmonella)

    python /path/to/reads_to_alleles.py -i abcd_1.fastq.gz,abcd_2.fastq.gz -r MGT_alleles_file -o output_file_name --no_serotyping --species "Vibrio cholerae" -t 4 -m 50