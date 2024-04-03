# CHANGE Database name 
DB_NAME='clawclip'

# CHANGE App name (usually the database name with a captial letter)
APPNAME='Clawclip'

# CHANGE Species name that you want displayed with the page.
SPECIES = '<i> Cute Beige Claw Clip </i>'

# CHANGE full path of the reference genome 
REF_GENOME = '/home/vandana/MGT-local/setup/example_inputs/genome.fasta'

# CHANGE full path of the lociLocations file 
LOCI_LOC = '/home/vandana/MGT-local/setup/example_inputs/lociLocationsInRef.txt'

# CHANGE full path to folder of schemes 
SCHEME_ACCESSIONS = '/home/vandana/MGT-local/setup/example_inputs/Schemes'

# CHANGE number of schemes 
SCHEME_NO = 3

# CHANGE to list of ODCSLS, which is a string of numbers separated by ',' (i.e. "1,2,5,10")
ODCLS = "1,2,5,10"

# CHANGE full path to store the reference files (typically have the App name as the last part of the path)
REF_FILES = 'data/tmp_setup_files/Clawclip/'

# CHANGE username for the database
DB_USER='blankuser'

# CHANGE full path of the settings_template
SETTING_FILE="/home/vandana/MGT-local/Mgt/Mgt/Mgt/settings_template.py"

# CHANGE full path of the root to MGT-local project 
PATH_MGT="/home/vandana/MGT-local/"

# CHANGE to settings prefix (relative path separated by dots)
SETTINGS_PREFIX="Mgt.settings_template"

# CHANGE full path of where you want to store species specific alleles that are generated. 
REFALLELES="data/species_specific_alleles/"

# CHANGE name of the conda environment.
CONDAENV="mgtenv"

# CHANGE superusername of the django application 
SUPERUSERNAME="blank2blank2"

# CHANGE superuseremail of the django application 
SUPERUSEREMAIL="blank2@blank2.blank2"
