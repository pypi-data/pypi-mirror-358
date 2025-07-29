# Direct Connect ++ client

## Install
On Ubuntu from PPA.
```sh
sudo add-apt-repository ppa:colin-i/ppa
```
Or the *manual installation step* from this link *https://gist.github.com/colin-i/e324e85e0438ed71219673fbcc661da6* \
Install:
```sh
sudo apt-get install dicopp
```
Will also install eiskaltdcpp-daemon/libgtk-4-1 if are not already installed.\
\
\
On openSUSE, run the following as __root__:\
For openSUSE Tumbleweed:
```sh
zypper addrepo https://download.opensuse.org/repositories/home:costin/openSUSE_Tumbleweed/home:costin.repo
```
For openSUSE Leap:
```sh
zypper addrepo https://download.opensuse.org/repositories/home:costin/openSUSE_Leap_16.0/home:costin.repo
```
And:
```sh
zypper refresh
zypper install python313-dicopp
```
Replace *python313* with *python312* or *python311* if needed.\
Will also install eiskaltdcpp-daemon/libgtk-4-1 if are not already installed.\
\
\
On Fedora, run the following as __root__:
```sh
dnf copr enable colin/project
dnf install python3-dicopp
```
And having eiskaltdcpp/gtk4.\
\
\
From [PyPI](https://pypi.org/project/dicopp):
```sh
pip3 install dicopp
```
And having eiskaltdcpp/gtk4. Also working on Windows MinGW64 MSys2 with eiskaltdcpp from official installer and the daemon to be in PATH.\
\
\
On othern linux distributions, <i>.AppImage</i> file from [releases](https://github.com/colin-i/dico/releases).

## From source
Using gtk4 bound with PyGObject and eiskaltdcpp through json rpc.\
More info at setup.pre.py.

## [Info](https://github.com/colin-i/dico/blob/master/info.md)

## Donations
The *donations* section is here
*https://gist.github.com/colin-i/e324e85e0438ed71219673fbcc661da6*
