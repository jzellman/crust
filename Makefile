init:
	test -d .env || virtualenv .env
	. .env/bin/activate; pip install -r requirements.txt
	touch .env/bin/activate

console:
	. .env/bin/activate; python

test:
	. .env/bin/activate; nosetests -s $(TESTS)

lint:
	. .env/bin/activate; flake8 --exclude=crust/__init__.py crust/ tests/

release: test lint
