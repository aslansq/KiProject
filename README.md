# KiProject
KiCAD Project Generator Script  
This project takes csv file and converts to KiCAD project.  
It will take information from csv file; generate symbol and global labels in a KiCAD project.  
It can be also used for just generating KiCAD libraries.  
  
![MicrochipProject](./doc/img/schEditMicrochipProject.PNG "MicrochipProject")  
Figure 1. Simple Generated KiCAD Project example. [Click to see this example](./examples/microchip.csv)
  
![ShowcaseProject](./doc/img/showcase.svg "ShowcaseProject")  
Figure 2. Showcase Generated KiCAD Project's Plot. [Click to see this example](./examples/showcase.py)
  
## Setup
Open terminal follow below instructions:  
```bash
$ git clone https://github.com/aslansq/KiProject.git
$ cd KiProject
$ ./configure.sh # it will test your environment and suggest solution
# after configure successful, you can continue with examples
$ ./examples/gen.sh
```
  
## Interface
There are two ways to interface with KiProject.  
  
### [kicli](./doc/kicli.md)

### [kiapi](./doc/kiapi.md)

