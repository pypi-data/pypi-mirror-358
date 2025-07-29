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
