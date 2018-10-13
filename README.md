HWMake
============================
> This is essentially an enhanced python3 make file for your assignment. 

The is created to help ensure productivity is spent on development of the project rather than the writeup. This project is currently "patchy", as development has only been for short spurts of time and it hasn't been fully consolidated yet. The lifecycle of the project will generate the required "environment" to write code and write the "body" (body.tex) in, generate several report types, add files to be ignored in the auto comment in the cut option, and finally cut the source folder and all of its contents into a "release". There is swapping between file operation/raw commands in Linux and Python3, which will need to be ported to Python3.

### How to run post download
```
./?/make.py ./?/Info.json (switch)
 switch
    ├── gen    : Used to generate the 'body.tex','Info.json', as well as the directories 'Imgs','Source'.
    ├── draft  : Used to set the make type for latex as draft.
    ├── make   : Used to set the make type for latex as conference.
    ├── note   : Used to set the make type for latex as technote.
    ├── cut    : Used to create "cut" the Source directory with a two digit pattern into a zip file with recursive sha512sums and auto commented headers in configured source code file types.
    └── clean  : Used to clean empty directories (untested and likely be removed).
    
./?/make.py -i (file): Used to ignore a file from the auto commenting of the sha zipping.
```

### Flag Notes
- draft/make/note
```
These stages move the Imgs folder, the body.tex file, and the Info.json file to the specified assignmentTemplate folder.
Next it runs a make command in the set folder to generate the report, then it moves the report into the local dir.
It finally runs a make clean command to clean the template folder.

The template folder must have a structure as follows:
    ├── (OverheadFile).tex    : Sets up the Latex document and properties, while importing the body.tex in the document. 
    └──Makefile               : Used to build the specified report and clean the folder
```

- cut
```
This stage will 
  1) Copy Source to a temp folder
  2) Recursively create a sha of every file after inserting header comments into source code
  3) Zip the folder
  4) Create a sha of the folder
  5) move all of this into a "Release folder": Cut_##
```

### Running Requirements

- OS
```
Currently hard set on Linux
```

- Run
```
Using Python3.
```

- Assignment Word Processor
```
Using Latex (any form).
```
