# SpikES
Companion code to Confavreux, Agnes, Zenke, Sprekeler and Vogels, arXiv 2023, Balancing complexity, performance and plausibility to meta learn plasticity rules in recurrent spiking networks.

### Required packages
- python part: numpy, pytorch, matplotlib
- C++ part: Auryn

### Installing Auryn:
All spiking network simulations in this repo use Auryn, a fast, C++ simulator developped by Friedemann Zenke.
To install, please refer to https://fzenke.net/auryn/doku.php?id=start  
Note that installing Auryn with MPI support is not required for the tutorial.

### Compile Auryn simulations:
- Compile the auryn simulation `sim_innerloop_bg_TIF_IE_6pPol.cpp` located in `Innerloop/cpp_innerloops/`. First, edit the `Makefile` in the same directory, you should only need to change AURYNPATH there.  
For troubleshooting, refer to https://fzenke.net/auryn/doku.php?id=manual:compileandrunaurynsimulations
- Go to tasks_configs/ and update `auryn_sim_dir` and `workdir` inside the 2 yaml files (these variables control where Auryn will write output spike trains).

