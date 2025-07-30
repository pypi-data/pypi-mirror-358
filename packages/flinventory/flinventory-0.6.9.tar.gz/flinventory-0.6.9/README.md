# Inventory

Python module and scripts for inventory software.

Also look at the data in the subdirectory `sample-data` or a real-life [data set](https://flugit.hilsky.de/flukx/things-data) (unfortunately private due to not owned images)
and the corresponding [GUI](https://flugit.hilsky.de/flukx/flinventory-gui).

## Motivation

In a community-run workshop, e.g. a self-help bike repair workshop, there are a lot of different things stored, a lot more than a newcomer — or a long-time user as well — can memorize. That's why a good sorting system is very helpful.
There are limitations to a good physical sorting though:
1. things can belong to different categories
2. available space restrictions force us putting small things to each other, breaking association by topic
3. if you look for the correct place for a thing, you might not know what it is called or what it is good for. Than categories and signs help less.
4. Newcomers are not able to sort things and clean up the workshop. This tedious task is usually restricted to the people that have been involved for a long time while they are also a bottleneck for a lot of other activity.

There this inventory should help.
1. Each thing is listed with many names and an "official" name. That way you have higher chances to find your thing and its place if the alternative name you would use intuitively is also listed. This should enable newcomers to independently clean up and learn about the existing things at the same time.
2. Each label (that is big enough) contains a picture to identify things from outside (intransparent) boxes as well.
3. Each thing can be found by one of its names alphabetically, by several categories, by English or German name, by looking at pictures in the storage. Not a single categorization to be limited to.

## Data
For example data see the directory `sample-data` or [branch Rad i.O. in the data repository](https://codeberg.org/flukx/flings/src/branch/rad-i-o) or the [private data repository](https://flugit.hilsky.de/flukx/things-data) if you have access.
The data format is a specific directory structure with specific file names:
- `schema.yaml`: describes how locations in this workshop are defined. See `sample_data` for details.
- `preferences.yaml`: general options for this data. See `sample_data` for details.
- directory `things`: directory with the actual data. Includes one directory per thing.
- `things/someID/thing.yaml`: name, description, ... about one thing. This should be (largely) workshop-independent.
- `things/someID/location.yaml`: where this thing is stored in this workshop
- `things/someID/sign.yaml`: how the sign on the box for this thing looks in this workshop
- `things/someID/image.*`: an image for this thing. Usually workshop-independent.

No keys in `things/someID/*yaml` are mandatory. Therefore, code that uses the data has to handle missing data.

## Install
`pip install flinventory`

or 
```
git clone https://codeberg.org/flukx/flinventory
# install requirements listed in pyproject.toml
# e.g. with
nix-shell
```

## Usage
flinventory is mainly intended as a python module used
in the [flinventory-GUI](https://codeberg.org/flukx/flinventory-gui).
But by installing this module, also the command-line interface `flinventory-cli` is installed.
(It can also be run with the repo and `python -m flinventory`.)

This command-line interface includes
- `flinventory-cli label` for creating signs that can be printed and glued to the boxes. The size and formatting of the signs happens in `things/*/sign.json`. Also, it creates a list of all names of all things with a reference to their location. This list is in markdown and can be converted with pandoc to a printable (multiple page) list. For details see the help messages.
- `flinventory-cli {normalize,printed,shortcut,unprinted,useIDs,locationsFile}` for various tasks for reformatting the yaml files. This is helpful to have a bit of standardisation to avoid big git diffs when the yaml files are read and written again. For details see the help messages.
