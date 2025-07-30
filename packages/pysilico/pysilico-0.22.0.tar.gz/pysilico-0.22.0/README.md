# PYSILICO: Prosilica AVT camera controller for Plico

 ![Python package](https://img.shields.io/github/actions/workflow/status/ArcetriAdaptiveOptics/pysilico/pythontest.yml)
 [![codecov](https://codecov.io/gh/ArcetriAdaptiveOptics/pysilico/branch/master/graph/badge.svg?token=GTDOW6IWDE)](https://codecov.io/gh/ArcetriAdaptiveOptics/pysilico)
 [![Documentation Status](https://readthedocs.org/projects/pysilico/badge/?version=latest)](https://pysilico.readthedocs.io/en/latest/?badge=latest)
 [![PyPI version][pypiversion]][pypiversionlink]



pysilico is an application to control [Allied AVT/Prosilica][allied] cameras (and possibly other GigE cameras) under the [plico][plico] environment.

[plico]: https://github.com/ArcetriAdaptiveOptics/plico
[travis]: https://travis-ci.com/ArcetriAdaptiveOptics/pysilico.svg?branch=master "go to travis"
[travislink]: https://travis-ci.com/ArcetriAdaptiveOptics/pysilico
[coveralls]: https://coveralls.io/repos/github/ArcetriAdaptiveOptics/pysilico/badge.svg?branch=master "go to coveralls"
[coverallslink]: https://coveralls.io/github/ArcetriAdaptiveOptics/pysilico
[allied]: https://www.alliedvision.com
[pypiversion]: https://badge.fury.io/py/pysilico.svg
[pypiversionlink]: https://badge.fury.io/py/pysilico



## Installation

### On client

On the client machine

```
pip install pysilico
```

### On the server

On the server machine install the proprietary driver for the camera you want to control. Currently only AVT/Prosilica camera are supported through Vimba

#### For AVT / Prosilica

First install Vimba (that comes with the camera, or download Vimba SDK from AVT website). Assuming you have downloaded and unpacked Vimba6 in the Downloads folder on a Linux machine:

```
cd ~/Downloads/Vimba_6_0/VimbaGigETL/
sudo ./Install.sh
```

Check that the Vimba installation is successful (you may need to log out and log in) and that the camera is accessible by the server using VimbaViewer, the standalone application provided in Vimba SDK. You should be able to see the cameras reachable in the network and you should be able to stream images.

```
cd ~/Downloads/Vimba_6_0/Tools/Viewer/Bin/x86_64bit
./VimbaViewer
```

Then install the Vimba python wrapper. It is suggested to use a dedicated python virtual environment, like conda (check elsewhere how to install Anaconda and create a virtual environment). 

Now you can install the Vimba python wrapper in the 

```
cd ~/Downloads/Vimba_6_0/VimbaPython/
./Install.sh
```

The script `Install.sh` is to date not working with conda virtual envs. If you are using conda and the command above fails, the following should do the work :

```
cd ~/Downloads/Vimba_6_0/VimbaPython/Source
pip install .
```

Check that the installation is successfull by running the provided example, like the one below:

```
cd ~/Downloads/Vimba_6_0/VimbaPython/Examples
python list_cameras.py
```

The ouput shows that camera(s) has been properly detected.

```
(pysilico) lbusoni@argos:~/Downloads/Vimba_6_0/VimbaPython/Examples$ python list_cameras.py 
//////////////////////////////////////
/// Vimba API List Cameras Example ///
//////////////////////////////////////

Cameras found: 1
/// Camera Name   : GC1350M
/// Model Name    : GC1350M (02-2130A)
/// Camera ID     : DEV_000F3101C686
/// Serial Number : 02-2130A-06774
/// Interface ID  : eno2
```


#### Install server
As a last step you always have to install the package `pysilico-server`

```
pip install pysilico-server
```


## Usage

### Edit config file

The config file location depends on the operating system. In Ubuntu is `/home/labot/.config/inaf.arcetri.ao.pysilico_server/pysilico_server.conf`. When the server is started, it prints the config file location on standard output.
Open the file and adapt it to your case.

In this example we want `pysilico_server` to control 2 cameras: a Manta 419 whose IP address is 192.168.29.189 used for a SH WFS, and a GC1350 (IP 192.168.29.194) used as PSF monitor. We reduce the streaming rate to 20MB/s in such a way that no packet will be lost during transfer to the server PC. 

Every `[cameraN]` entry in the config file correspond to a pysilico server; you may add as many as you want. Every `[cameraN]` entry must have a `camera=` key linking to a `[deviceX]` entry that specifies the camera model, IP, etc. 

```
[deviceManta419]
name= AVT Manta G-419B 5CA8
model= avt
ip_address= 192.168.29.189
streambytespersecond= 20000000
binning= 1

[deviceGC1350M]
name= AVT GC 1350M C686
model= avt
ip_address= 192.168.29.194
streambytespersecond= 20000000
binning= 1

[camera1]
name= SH WFS Ibis
log_level= info
camera= deviceManta419
host= localhost
port= 7100

[camera2]
name= PSF Ibis
log_level= info
camera= deviceGC1350M
host= localhost
port= 7110
```


### Starting Servers

Start the servers with 

```
pysilico_start
```

The servers are logging info in a dedicate log file. The log file name is printed on the standard output when the server is started. 

On Ubuntu it can be in `/home/labot/.cache/inaf.arcetri.ao.pysilico_server/log/camera1.log` (and camera2.log and so on for the other servers)

Check in the log file that the server is properly running and communicating with the camera; it should periodically dump a line like "Stepping at xx Hz"  

  

### Using the client module 

We assume that `pysilico_server` runs on '192.168.29.132'.  

In a python terminal on a client computer on which `pysilico` has been installed:

```
In [1]: import pysilico

In [2]: cam_sh= pysilico.camera('192.168.29.132', 7100)

In [3]: cam_psf= pysilico.camera('192.168.29.132', 7110)

In [4]: frames= cam_sh.getFutureFrames(10)
```

### Using the GUI

Run `pysilico_gui`

### Stopping pysilico

To kill the servers run

```
pysilico_stop
```

More hard:

```
pysilico_kill_all
```




## Administration Tool

For developers.


### Testing
Never commit before tests are OK!
To run the unittest and integration test suite cd in pysilico source dir

```
python setup.py test
```


### Creating a Conda environment
Use the Anaconda GUI or in terminal

```
conda create --name pysilico
```

To create an environment with a specific python version (you need > 3.7 for Vimba)

```
conda create --name pysilico python=3.8
```


It is better to install available packages from conda instead of pip. 

```
conda install --name pysilico matplotlib scipy ipython numpy
```

### Packaging and distributing

1. Update the version in version.py and commit
2. Create a new release
3. If you have the proper rights (see PYPI_API_TOKEN in Settings/Secrets), the Action automatically builds and uploads the wheel on pypi

