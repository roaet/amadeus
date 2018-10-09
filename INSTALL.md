# Installation Notes

The versions are pinned because random package upgrades tend to break the
code.

## Installation Ubuntu (WSL):

Packages known to fail without packages installed first:
- matplotlib==1.4.3
- pyodbc

### TLDR:
`sudo apt install libfreetype6-dev pkg-config unixodbc unixodbc-dev tdsodbc`
`sudo apt install freetds-bin freetds-common freetds-dev libct4 libsybdb5`
Read the FreeTDS section

### Mark sure you install in a virtualenv

Packages that need to be installed first:
- virtualenv

### Can't open lib 'FreeTDS' : file not found

FreeTDS is the connection driver used to access the DB. 

You need to install packages:
- tdsodbc freetds-bin freetds-common freetds-dev libct4 libsybdb5

And then you need to configure the following files:

`sudo vi /etc/odbcinst.ini`

```
[ODBC]
Trace = No
TraceFile = /tmp/odbc.log

[FreeTDS]
Description = FreeTDS
Driver = /usr/lib/x86_64-linux-gnu/odbc/libtdsodbc.so
Setup = /usr/lib/x86_64-linux-gnu/odbc/libtdsS.so
UsageCount = 1
```

Below, the [dbserverdsn] is optional and only if you want to have named
connections configured.

`sudo vi /etc/odbc.ini`

```
[dbserverdsn]
Driver = FreeTDS
Server = <server_name>.database.windows.net
Port = 1433
Database = <database_name>
Driver=/usr/local/lib/libtdsodbc.so
UsageCount = 1

[Default]
Driver = /usr/lib/x86_64-linux-gnu/odbc/libtdsodbc.so


```

Only do the below if the file doesn't already exist (it should):

`sudo vi /etc/freetds/freetds.conf`

```
#   $Id: freetds.conf,v 1.12 2007/12/25 06:02:36 jklowden Exp $
#
# This file is installed by FreeTDS if no file by the same 
# name is found in the installation directory.  
#
# For information about the layout of this file and its settings, 
# see the freetds.conf manpage "man freetds.conf".  

# Global settings are overridden by those in a database
# server specific section
[global]
  # TDS protocol version
  tds version = 7.2
  port = 1433

  # Whether to write a TDSDUMP file for diagnostic purposes
  # (setting this to /tmp is insecure on a multi-user system)
; dump file = /tmp/freetds.log
; debug flags = 0xffff

  # Command and connection timeouts
; timeout = 10
; connect timeout = 10
  
  # If you get out-of-memory errors, it may mean that your client
  # is trying to allocate a huge buffer for a TEXT field.  
  # Try setting 'text size' to a more reasonable limit 
; text size = 64512

# A typical Microsoft server
[dbserverdsn]
  database = <database_name>
  host = <server_name>.database.windows.net
  port = 1433
  tds version = 7.2
  client charset = UTF-8
```

### Debugging installation errors

Note:
- to install packages one at a time (to discover what packages are needed
  cat requirements.txt | xargs -n 1 pip install
- pip sometimes looks like it isn't doing anything, use the argument -vvv

### Required Packages:

Ubuntu Packages that need to be installed to fix matplotlib==1.4.3
- libfreetype6-dev pkg-config

Ubuntu Packages that need to be installed to fix pyodbc
- unixodbc unixodbc-dev

### Sources for install:

- https://stackoverflow.com/questions/9829175/pip-install-matplotlib-error-with-virtualenv
- https://stackoverflow.com/questions/21530577/fatal-error-python-h-no-such-file-or-directory
- https://stackoverflow.com/questions/31353137/sql-h-not-found-when-installing-pyodbc-on-heroku
- http://help.interfaceware.com/kb/904


