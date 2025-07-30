NcpSemApi is a python interface to access the REST-API of the NCP Secure Enterprise Management Server (SEM).

To use this API you need a running SEM (at least Version 6.0) accessable via network from the machine running this Python-API.

To activate the REST-API of your SEM, edit ```[sem-install-dir]/etc/sentinel.conf``` and set ```sem-nginx = true;```.

You may configure the ports in ```[sem-install-dir]/etc/nginx/admmgm.conf```.

You may want to restart the SEM-Service after doing that configuration.

The documentation of the SEM-REST-API and this python-API-bindings can be viewed by a webbroser accessing the previously configurated port.

