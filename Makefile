build-package:
	pipenv run python setup.py sdist

upload-package:
	pipenv run python -m twine upload dist/*




_dev-install-virtualenv:
	virtualenv _dev-install-virtualenv
	. _dev-install-virtualenv/bin/activate && pip install pytest cram pexpect
	. _dev-install-virtualenv/bin/activate && pip install -e .

dev-install: _dev-install-virtualenv

run-unit_tests:
	. _dev-install-virtualenv/bin/activate && cd testing && time python -m pytest -s

run-cli_tests:
	. _dev-install-virtualenv/bin/activate && cd testing && time cram *.t




_test-install-virtualenv:
	virtualenv _test-install-virtualenv
	. _test-install-virtualenv/bin/activate && pip install pytest cram pexpect
	. _test-install-virtualenv/bin/activate && pip install .

test-install: _test-install-virtualenv

test:
	make test-install
	. _test-install-virtualenv/bin/activate && cd testing && time python -m pytest -s
	. _test-install-virtualenv/bin/activate && cd testing && time cram *.t

