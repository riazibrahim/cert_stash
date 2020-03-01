# Cert Stash

A tool for downloading certificate log data from cert.sh, parse it based on domains and store into a database or export as excel.

Feel free to hit me up with suggestions.

### Installing


Download the latest version from Git Repo

```
git clone git@github.com:riazibrahim/cert_stash.git

```

Change to the source code folder

```
cd cert_stash

```
Start a new virtual environment

```
python -m venv venv

source venv/bin/activate

```

Install all the requirements

```
pip install -r requirements.txt

```

## Running the tool


##### Usage 1: To obtain certs of a single domain:
```
python cert_stash.py -d/ --domain digg.com
```
##### Usage 2: To obtain certs of domains list in a file
```
python cert_stash.py -f/ --file domain.lst
```
##### Usage 3: To output current results to an excel sheet
```
python cert_stash.py -d <domain_name> -e/ --export
```
##### Usage 4: To output entire local sqlite database (i.e. results of all previous and/ or current searches) with all historic search results to an excel sheet (can be used without any other argument)
```
python cert_stash.py -eA/ --export_all 

or

python cert_stash.py -d <domain_name> -eA/ --export_all
```
##### Usage 5: Export only results pertaining to specific previous searches (all queries gets saved as search tag in database)
```
python cert_stash.py -eA --tag <search tag>
```
##### Usage 6: Process domains/ subdomains in database to resolve IP and CNAME. Also produces 3 files which splits the records into external domain, internal domain and others
```
python cert_stash.py --process filter -if INT_TLD_LOC.lst -ef EXT_TLD_LOC.lst --tag <previous_search>(optional) 

```

## Built With

* [Python3](https://www.python.org/download/releases/3.0/) 


## Authors

* **Riaz Ibrahim** - [riazibrahim](https://github.com/https://github.com/riazibrahim/)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE) file for details

## Acknowledgments

* Cert.Sh : https://cert.sh
* Certificate Transparency : https://www.certificate-transparency.org/