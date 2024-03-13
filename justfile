default:
  just --list

test:
  cd {{ justfile_directory()/"testing" }} && poetry run pytest -s

test-on-changes:
  cd {{ justfile_directory() }} && watchexec -e py just test

build-package:
  cd {{ justfile_directory()/"testing" }} && poetry build

upload-package:
  cd {{ justfile_directory()/"testing" }} && poetry publish
