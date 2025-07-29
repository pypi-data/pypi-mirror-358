# MeDIC
Metabolomic Dashboard for Interpretable Classification

## Description
The MeDIC is a tool to apply machine learning algorithms to untargeted metabolomics datasets acquired by liquid-chromatography mass spectrometry. The goal is to extract the most important features because they are potential novel biomarkers.
The interface is made to be easy to use and intuitive even for those with small to nonexistant experience in programming and AI.

## The documentation
You can find the documentation [here](https://elinaff.github.io/MeDIC/).
It explains how to use MeDIC but also how it works.

## Authors and contributors
 - [Élina Francovic-Fontaine](https://github.com/ElinaFF)
 - [Vincent Primpied](https://github.com/le-smog)
 - [Vincent Vilain](https://github.com/VincentVilain)

## Disclaimer
MeDIC is still in development. If you encounter any issue or have any suggestion, feel free to contact us at [elina.francovic-fontaine.1@ulaval.ca](mailto:elina.francovic-fontaine.1@ulaval.ca). Or you can leave an issue [here](https://github.com/ElinaFF/MeDIC/issues) with the tag "bug".

## Development

### Setup

Clone the project with :
```shell
git clone https://github.com/ElinaFF/MeDIC.git
```

It is recommanded to setup a virtual environment. When it's done, use your isolated python and install `medic` package locally and in editable mode with :
```shell
python -m pip install -e ".[dev]"
```

### Trigger a release

Let's say you want to update to version `1.3.2`.
   1.  Make sure the main branch is working fine, either run `pytest` locally or trigger a tests workflow manually.
   1.  Set the version to `__version__ = "1.3.2"` in [medic/__init__.py](./medic/__init__.py) (you can edit a file from GitHub by clicking on the key `.` on your keyboard)
   2.  Commit the new version change with `git add medic/__init__.py` and `git commit -m "Bump version`
   3.  Push the commit with `git push`
   4.  Go to https://github.com/ElinaFF/MeDIC/releases/new, choose a tag, create new tag with name `1.3.2`
   5.  Document what have changed since the last release (you can try the `Generate release notes` button)
   6.  Click `Publish release`!