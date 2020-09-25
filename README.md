# splash-server
Server for the Splash application. 

This project contains a service layer for running the Splash experimental database service. It includes a RESTFul interface served by a Flask container.

There is a companion project [splash-deploy](https://github.com/als-computing/splash-deploy) which provides an easy-to-use method for running the full splash system in containers. That project for more information on installation. Nothing stops you from installation or running on your own outside of containers, but that is probably your easiest path.

# fits datahandler plugin
This application needs to use the fits datahandler plugin for databroker which you can install by cloning the pip package into the root directory with: `git clone https://github.com/als-computing/datahandler_fits.git` 

