# Dish Digital RS-Cloud Team Interview Stuff

Hi - this is a prebuilt homework assignment used in RS-Cloud team interviews. It
provides a mini-django app contained in one file called tv.py that deals with tv
channels and shows.

tv.py runs on either OS X or Ubuntu Linux using python 2.7. To get started, do
the following:

        $ make setup
        $ . pyenv/bin/activate

This will setup a python virtual environment, install some dependencies, create
a admin account named "admin" with the password "admin" and initialize a sqlite
database called tvdata.db that will hold the tv.py data.

You can now run django management commands to run the server, look at the
database, etc.  To initialize the database with channels, run the custom django
management command called load_channels as follows:

        $ ./tv.py load_channels

This will perform an http request against a Dish Digital content management
system (cms) server and get a list of available channels, and will then create
django model instances and save them to the database.

You can run the django server with the following:

        $ ./tv.py runserver

and then visit http://localhost:8000 with your browser. Login with the
admin:admin credentials and you can view the existing channels.
