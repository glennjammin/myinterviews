setup:
	python2.7 3rdParty/virtualenv.py pyenv
	pyenv/bin/pip install requests
	pyenv/bin/pip install django
	pyenv/bin/python tv.py syncdb --noinput
	pyenv/bin/python tv.py loaddata admin-fixture.json
