init:
	test -d .env || virtualenv .env
	. .env/bin/activate; pip install -r requirements.txt
	touch .env/bin/activate

console:
	. .env/bin/activate; python

test:
	. .env/bin/activate; nosetests -s $(TESTS)

lint:
	. .env/bin/activate; flake8 crust/ tests/ 

release: test lint
