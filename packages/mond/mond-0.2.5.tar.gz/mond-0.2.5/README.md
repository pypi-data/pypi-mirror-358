# monte-solver


[![Downloads](https://static.pepy.tech/personalized-badge/mond?period=total&units=international_system&left_color=orange&right_color=blue&left_text=Downloads)](https://pepy.tech/project/mond)
[![License: GPL v3](https://img.shields.io/badge/License-GPL_v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
![Python Versions](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C-blue)
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
[![PyPI - Version](https://img.shields.io/pypi/v/mond.svg)](https://pypi.org/project/mond)

Monte Carlo dissolver.

## Why

Studying molecules in solution is super interesting. 

## What

It is a module to automatically prepare sample mixtures for solutions in e.g. gas phase or liquid phase
from multiple molecules according to defined concentration

## Converting pdb files is not trivial

I guess MS chose their native file format as pdb. 
What does not work now. It is insane. 

* openbabel (not working from package man, or uncompilable) 
* Chimera (uninstallable on free systems), now Meta
* rdkit (can't output proper pdb files)
* PDBFixer (can't fix broken rdkit files)
* No idea how MDAnalysis might do it 
* openff is not compilable

### What could work 

* mol files?
* using sdf and https://cactus.nci.nih.gov/translate/
* da muss irgendwo ein Leerzeichen rein und nicht bei 1 anfangen we HETATM ist somehow logisch

## Periodic

Muss periodische Boundaries selbst reinmachen



## Set up notebook visualization

In your environment run


```bash
pip install jupyterlab jupyter_contrib_nbextensions nglview
jupyter-nbextension enable --py --sys-prefix widgetsnbextension and jupyter-nbextension enable nglview --py --sys-prefix
```

## XTB

Dringend installieren um MC-search auf die Moleküle zu machen: 

Download and add to path
```bash 
export PATH=/home/your_home/xtb-dist/bin:$PATH
```

## OpenMM 

Installing OpenMM from PyPi is nice to avoid conda, but you need to have numpy<2 installed. In case
of errors, you may run: 

```bash
pip install "numpy<2"
```