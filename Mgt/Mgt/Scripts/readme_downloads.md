1. Creating downloadable allelic prifiles for all public isolates for each species:
```sh
python3 createDump_PuAllelicProf.py --mgtBasePath ../ --settingFn Mgt.settings_sklocal > outfile
```

2. Creating dump of alleles (all)
```sh
python3 createDump_alleles.py --mgtBasePath ../ --settingFn Mgt.settings_sklocal > outfile
```

3. Creating allelic profiles of each project
```sh
python3 createDump_ProjAllelicProf.py --mgtBasePath ../ --settingFn Mgt.settings_sklocal > outfile
```
