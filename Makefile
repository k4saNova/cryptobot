PYTHON = python3.7
VENV_DIR = venv
VPYTHON = $(VENV_DIR)/bin/python
PIP = $(VENV_DIR)/bin/pip
PYINSTALLER = $(VENV_DIR)/bin/pyinstaller

.PHONY: venv
venv:
	@ $(PYTHON) -m venv $(VENV_DIR)

clean:
	@ rm $(PWD)/build/ $(PWD)/__pycache__/ *.spec -rf 

install:
	@ $(PYINSTALLER) -D --onefile stew.py


run:
	nohup $(PYTHON) run.py 
