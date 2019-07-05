# splash-ui
User interface web app for M-WET splash application

# Description
This application demonstrates capabilities of a web application that serves MWET data. It consists of 
several parts:

* A Flask server processing REST requests.
* A Vue-based Single Page Application (SPA). The SPA gets all of its data from the Flask REST service.
* A MongoDB for persistence.

# Installation
To install the application, run pip to install dependencies:

## Server

### Install dependencies
```
pip install pymongo flask flask_cors
```

### Configure database location
By default, the REST service reads and writes to a MongoDB started up at localhost:27107. The URL can be modified by changing the server_config.ini file.

# Startup

## UI
Currently, the UI layer is served by a NPM. In the future, it will be built and distributed with the product. But for now, to start it up by navigating to the splash-app/ui folder and typing:
```
npm run serve
````

To build a production release of the UI code (pack up javascript and CSS, minify, etc.), run:
```
npm run build
```

## Flask server
To start the flask RESTful service, create a python environmnet in the splas-app folder. Call it "env" to match the command in .gitignore. Then, type:

```
python rest_service.py
```


