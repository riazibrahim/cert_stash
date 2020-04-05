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

Install and configure Tor for threading

```
1. Install Tor on your system 

2. Setup Password

$ tor --hash-password MyStr0n9P#D
16:160103B8D7BA7CFA605C9E99E5BB515D9AE71D33B3D01CE0E7747AD0DC
$ sudo vi /etc/tor/torrc
HashedControlPassword 16:160103B8D7BA7CFA605C9E99E5BB515D9AE71D33B3D01CE0E7747AD0DC


3. Uncomment the below ControlPort line

$ sudo vi /etc/tor/torrc
ControlPort 9051

4. Restart Tor service

```

## Running the tool


##### Usage 1: To obtain certs of a single domain:
```
python cert_stash.py -d/--domain -i/--input digg.com
```
##### Usage 2: To obtain certs of a single organisation name:
```
python cert_stash.py -o/--org -i/--input digg.com
```
##### Usage 3: To obtain certs of domains list in a file (will skip entries if domains are not in right format)
```
python cert_stash.py -d/--domain -f/--file <domain.lst>
```
##### Usage 4: To obtain certs of organisation names list in a file
```
python cert_stash.py -o/--org -f/--file <orgs.lst>
```
##### Usage 5: To output current results to an excel sheet
```
python cert_stash.py -d <domain_name> -e/ --export
```
##### Usage 6: To output entire local sqlite database (i.e. results of all previous and/ or current searches) with all historic search results to an excel sheet (can be used without any other argument)
```
python cert_stash.py -eA/ --export_all 

or

python cert_stash.py -d <domain_name> -eA/ --export_all
```
##### Usage 7: Export only results pertaining to specific previous searches (all queries gets saved as search tag in database)
```
python cert_stash.py -eA --tag <search tag>
```
##### Usage 8: Process domains/ subdomains in database to resolve IP and CNAME. Also produces 3 files which splits the records into external domain, internal domain and others
```
python cert_stash.py --process filter -if <internal_tlds>.lst -ef <external_tlds>.lst --tag <previous_search>(optional) 

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