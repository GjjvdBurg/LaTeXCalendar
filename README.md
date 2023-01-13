# LaTeX Calendar

This script generates a nice year calendar using 
[LaTeX](https://www.latex-project.org/).

## Installation

Install the [dateutil](https://pypi.org/project/python-dateutil/) package 
using:
```
$ pip install python-dateutil
```

If you want to automatically fill in the bank holidays for the UK, install the 
following dependency:
```
$ pip install govuk-bank-holidays>=0.12
```
Note that in that case the script defaults to England & Wales.

## Usage

The script can generate an A3 calendar for the full year, or a A4 calendar for 
the first or second half of the year.
```
$ python generate_calendar.py --mode a3-year calendar.tex
```

Optionally you can provide a JSON file with holidays to mark on the calendar.
```
$ python generate_calendar.py --holidays ./holidays/2023_netherlands.json calendar_nl.tex
```

Then compile the resulting TeX file with pdfLaTeX:
```
$ pdflatex calendar.tex
```

To get help on the available options, run:
```
$ python generate_calendar.py -h
```

## Notes

Written by [Gertjan van den Burg](https://gertjan.dev). See the LICENSE file 
for licensing information. Copyright (c) 2023 G.J.J. van den Burg.
