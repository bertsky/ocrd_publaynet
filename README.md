# ocrd_publaynet

    convert PubLayNet data into METS/PAGE-XML
    
## Introduction

This offers [OCR-D](https://ocr-d.github.io) compliant (i.e. [METS-XML](https://ocr-d.github.io/en/spec/mets)/[PAGE-XML](https://ocr-d.github.io/en/spec/page) based) conversion for [PubLayNet](https://github.com/ibm-aur-nlp/PubLayNet) or similar, [MS-COCO](http://cocodataset.org/#format-data)-based, ground-truth data.

## Installation

### System packages

Install GNU `make` and `wget` if you wish to use the Makefile.

    # on Debian / Ubuntu:
    sudo apt install make wget

Install Python3 regardless:

    # on Debian / Ubuntu:
    sudo apt install python3 python3-pip python3-venv

Equivalently:

    # on Debian / Ubuntu:
    sudo make deps-ubuntu

### Python packages

It is strongly recommended to use [venv](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/). You can create and install a virtual environment of your own (which the Makefile will re-use when activated), or have the Makefile do that for you.

    pip install -r requirements.txt
    pip install .
    
Equivalently:

    make install

## Usage

### command-line interface `ocrd-import-mscoco`

Once installed, the following executable becomes available:

```
Usage: ocrd-import-mscoco [OPTIONS] COCOFILE DIRECTORY

  Convert MS-COCO JSON to METS/PAGE XML files.

  Load JSON ``cocofile`` (in MS-COCO format) and chdir to ``directory``
  (which it refers to).

  Start a METS file mets.xml with references to the image files (under
  fileGrp ``OCR-D-IMG``) and their corresponding PAGE-XML annotations (under
  fileGrp ``OCR-D-GT-SEG-BLOCK``), as parsed from ``cocofile`` and written
  using the same basename.

Options:
  --help  Show this message and exit.
```

### apply on `PubLayNet`

To apply on the validation subsection:

    ocrd-import-mscoco publaynet/val.json publaynet/val

This will create a METS `publaynet/val/mets.xml` and PAGE files `publaynet/val/*.xml` for all image files.

To apply on the training subsection:

    ocrd-import-mscoco publaynet/train.json publaynet/train

This will create a METS `publaynet/train/mets.xml` and PAGE files `publaynet/train/*.xml` for all image files.

Equivalently (including download/extraction if necessary):

    make convert

> **Note**: PubLayNet itself requires approximately 103 GB of disk space. If you already have it (elsewhere), but still wish to use the Makefile to convert the files, make sure to symlink it here, so it does not get downloaded twice: `ln -s your/path/to/publaynet publaynet`


### all Makefile targets

```
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
```
