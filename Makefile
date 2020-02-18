PYTHON ?= python3
PIP ?= pip3

# directory for virtual Python environment
# (but re-use if already active):
VIRTUAL_ENV ?= $(CURDIR)/.venv
ACTIVATE_VENV := $(VIRTUAL_ENV)/bin/activate

.DEFAULT_GOAL = help

define WGET
$(if $(shell which wget),wget -nv -O $(1) $(2),$(if $(shell which curl),curl -L -o $(1) $(2),$(error "found no cmdline downloader (wget/curl)")))
endef

.PHONY: help deps-ubuntu install download convert all clean clean-xml

define HELP
cat <<"EOF"
Rules to install ocrd-import-mscoco, and to use it on
PubLayNet (by downloading, extracting and converting).

Targets:
	help: this message
	deps-ubuntu: install system dependencies for Ubuntu
	all: alias for `install download convert`
	install: alias for `pip install .`
	download: alias for `publaynet.tar.gz`
	convert: alias for `publaynet/val/mets.xml publaynet/train/mets.xml`
	uninstall: alias for `pip uninstall ocrd_publaynet`
	clean-xml: remove results of conversion (METS and PAGE files in `publaynet`)
	clean: remove `publaynet` altogether

Variables:
	VIRTUAL_ENV: absolute path to (re-)use for the virtual environment
	PYTHON: name of the Python binary
	PIP: name of the Python packaging binary
EOF
endef
export HELP
help: ;	@eval "$$HELP"

deps-ubuntu:
	apt-get install -y python3 python3-pip python3-venv wget make

$(ACTIVATE_VENV) $(VIRTUAL_ENV):
	$(PYTHON) -m venv $(VIRTUAL_ENV)
	. $(ACTIVATE_VENV) && $(PIP) install --upgrade pip

install: $(ACTIVATE_VENV)
	. $(ACTIVATE_VENV) && $(PIP) install .

uninstall: $(ACTIVATE_VENV)
	. $(ACTIVATE_VENV) && $(PIP) uninstall ocrd_publaynet

.SECONDARY: publaynet.tar.gz
publaynet.tar.gz:
	$(call WGET,$@,https://dax.cdn.appdomain.cloud/dax-publaynet/1.0.0/publaynet.tar.gz)

download: publaynet

publaynet: publaynet.tar.gz
	tar zxvf $<

publaynet/val.json publaynet/train.json: publaynet

publaynet/val/mets.xml: publaynet/val.json $(ACTIVATE_VENV)
	. $(ACTIVATE_VENV) && ocrd-import-mscoco $< $(@D)

publaynet/train/mets.xml: publaynet/train.json $(ACTIVATE_VENV)
	. $(ACTIVATE_VENV) && ocrd-import-mscoco $< $(@D)

convert: publaynet/val/mets.xml publaynet/train/mets.xml

all: install download convert

clean-xml:
	$(RM) publaynet/val/*.xml publaynet/train/*.xml

clean:
	$(RM) -r publaynet publaynet.tar.gz
