# Lyra - Static Analyzer for Data Science Applications

<p align="center">
  <img src ="https://raw.githubusercontent.com/caterinaurban/Lyra/master/lyra.png" width="25%"/>
</p>

Lyra is a prototype static analyzer for data science applications written in **Python**. 
The purpose of Lyra is to provide confidence in the behavior of these applications,
which nowadays play an increasingly important role 
in critical decision making in our social, economic, and civic lives.

At the moment, Lyra includes the following static program analyses:

### Input Data Usage Analysis
 
Lyra automatically detects *unused input data*. For example, consider this program:

```
english: bool = bool(input())
math: bool = bool(input())
science: bool = bool(input())
bonus: bool = bool(input())
passing: bool = True
if not english:
    english: bool = False         # error: *english* should be *passing*
if not math:
    passing: bool = False or bonus
if not math:
    passing: bool = False or bonus   # error: *math* should be *science*
print(passing)
```

Due to the indicated errors, 
the input data stored in the variables ``english`` and ``science`` remains unused.

Lyra automatically detects these problems using an input data usage analysis
based on *syntactic dependencies between variables*.
Lyra additionally supports a less precise input data usage analysis 
based on the *strongly live variant of live variable analysis*.
Both analyses use *summarization* to reason about 
input data stored in compound data structures such as lists.
A more precise input data usage analysis detects 
unused chunks of lists containing input data by *partitioning*.

### Interval Analysis

Lyra automatically computes the *range of possible value of the program variables*. For example:

```
a: int = int(input())
if 1 <= a <= 9:
    b: int = a
else:
    b: int = 0
print(b)
```

The range of possible values printed by the program is ``[0, 9]``.

## Getting Started 

### Prerequisites

* Install **Git**

* Install [**Python 3.6**](http://www.python.org/)

* Install ``virtualenv``:

    | Linux or Mac OS X                     |
    | ------------------------------------- |
    | `python3.6 -m pip install virtualenv` |


### Installation

* Create a virtual Python environment:

    | Linux or Mac OS X                     |
    | ------------------------------------- |
    | `virtualenv --python=python3.6 <env>` |

* Install Lyra in the virtual environment:

    | Linux or Mac OS X                                                       |
    | ----------------------------------------------------------------------- |
    | `./<env>/bin/pip install git+https://github.com/caterinaurban/Lyra.git` | 
    
### Command Line Usage

To analyze a specific Python program run:

   | Linux or Mac OS X                            |
   | ---------------------------------------------|
   | `./<env>/bin/lyra [OPTIONS] path-to-file.py` | 
   
The following command line options are recognized:

    --analysis [ANALYSIS]   
    
                Sets the static analysis to be performed. Possible analysis options are:
                * ``usage`` (input data usage analysis based on syntactic variable dependencies)
                * ``liveness`` (input data usage analysis based on strongly live variable analysis)
                * ``interval`` (interval analysis)
                Default: ``usage``.

After the analysis, Lyra generates a PDF file showing the control flow graph of the program
annotated with the result of the analysis before and after each statement in the program.

## Documentation

Lyra's documentation is available online: http://caterinaurban.github.io/Lyra/

## Authors

* **Caterina Urban**, ETH Zurich, Switzerland
* **Simon Wehrli**, ETH Zurich, Switzerland
