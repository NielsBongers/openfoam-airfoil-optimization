# OpenFOAM airfoil optimization 

<img src="figures/Pretty airfoil, Cl_Cd 39.151.png" width="800" alt="ParaView visualization for an example airfoil the code optimized.">

## Overview 

This is a simple set of code that automatically finds airfoils, optimizing for the lift-to-drag ratio $C_l / C_d$. It does this by generating an airfoil shape based on six CST-parameters (courtesy of [this repo](https://github.com/Ry10/Kulfan_CST/)). An initial attempt to create a variable meshing code myself with `blockMesh` turned out to be very painful, so the meshing is handled by [curiosityFluids' excellent mesher](https://github.com/curiosityFluids/curiosityFluidsAirfoilMesher) ([blog post](https://curiosityfluids.com/2019/04/22/automatic-airfoil-cmesh-generation-for-openfoam-rev-1/)) 

SciPy's [differential evolution](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.differential_evolution.html) is taken as an optimization algorithm. It's far slower than other methods, but using a global optimizer here seems like the better choice. Other gradient-free algorithms like Nelder-Mead also found reasonable airfoils and were much faster, however. 

The simulation is then ran. If any issues are encountered with the meshing, `blockMesh`, or `simpleFoam`, the code returns $+\infty$. For $C_l / C_d$, any value is considered feasible, even negative ones - that turns out to generally be the code inventing upside-down airfoils. The case is essentially symmetric at $0^\circ$ angle-of-attack, so this is not penalized. The value to optimize is taken as $|C_l / C_d|$. 

The result is a CSV containing airfoil parameters and their performance. These can be further post-processed with ParaView. 

Overall, I'm surprised at how smoothly this project went. The existing repos helped a lot, especially with meshing. I found it an interesting introduction into coupling optimization methods and non-trivial simulations. I'm still impressed at how effective differential evolution was - with a previous meshing-template, it was able to find and exploit flaws with ease. 

## Installation 

This assumes you already have OpenFOAM installed - I am using the [OpenFOAM.com/ESI](https://www.openfoam.com/about-esi-opencfd) version. You can clone the repo. Source the OpenFOAM functions first. For the ESI-version, this can be done with 

```bash 
source /usr/lib/openfoam/openfoam2406/etc/bashrc
``` 

This exposes functions like `blockMesh` and `simpleFoam`. Dependencies were kept to a minimum: `pandas`, `numpy`, `matplotlib`, `scipy`, and optionally `sklearn`. Once these are installed, run ```python main.py```. 

## Getting started 

The code is quite minimal. This is partially on purpose. If you are using OpenFOAM, you are used to editing code files. It's also quite difficult to create a sufficiently flexible way of working with these things without oversimplifying. The intended way of using the code is to look through everything and try to understand it. Everything should be quite straight-forward and readable. 

## Features 

### Parallel-processing 

The code uses an OpenFOAM template folder, which is repeatedly copied into several directories, depending on the number of workers specified, using UUIDs as names. Relevant parameters are then entered into these templates (such as the adjusted `blockMesh`, and `U`) As soon as a case completes (either because of errors, or because it correctly finished), the folder is deleted. Since OpenFOAM requires its folders in a particular structure, differential evolution can easily be parallelized, and because each individual case runs fast, this seemed like a better choice than decomposing the domain across multiple cores. With the current method, there should be almost no overhead from parallelization. 

### Automatic top-n selection and rendering  

The code can post-process the top-n highest scoring airfoils so far, simulating each of them. The results can subsequently be rendered with a ParaView Python macro. First, run 

```python main.py --custom```

This places the top-n runs under `custom_runs`. Follow this by 

```python src/post_processing/post_process.py``` 

If all goes well, this places all the results under `results/renders`. 

<img src="figures/cl_cd_35.177_render.png" width="400" alt="ParaView visualization for an example airfoil the code optimized.">

The latter isn't entirely reliable: ParaView includes its own Python-distribution based on Python 3.10. If you encounter errors here, it's best to either look at the code, or open each `.foam` under `custom_runs` individually. 

### Analysis 

The repo includes an analysis-notebook. This tracks performance over time, and allows for selection of the best-performing airfoils. 

<img src="figures/27122024 - OpenFOAM - Lift-drag ratio over time.png" width="600" alt="Lift-drag ratio over time with differential evolution.">

## Updates and adjustments 

### Turbulence modelling 

I started off with the default parameters from a case I found, which used $\tilde \nu = 0.14$. That seemed high, also compared to other OpenFOAM examples I found, but I assumed it was acceptable - up until I started getting $C_l/C_d$ values of over 900. Reducing the layer thickness close to the mesh to fix $y+$ did not improve the situation. 

It turns out, $\tilde \nu$ was probably far too high. There are different sources here. [CFD-Online](https://www.cfd-online.com/Wiki/Turbulence_free-stream_boundary_conditions) argues $\tilde \nu$ should be 0 for the Spalart-Allmaras model (which I'm using), but can also be set to $\tilde \nu \leq \nu / 2$ if that causes problems with solvers. Since $\nu \approx 14.88 \cdot 10^{-6}$ at ambient temperatures and pressures, this is certainly a far lower value than I was using before. A [NASA source](https://turbmodels.larc.nasa.gov/spalart.html) gives different values still. (Note that this page uses $\hat \nu$ rather than $\tilde \nu$; the latter apparently didn't show up properly on screens when this page was created.) It says to use $\tilde \nu_\text{far-field}$ between $3 \nu_\infty$ and $5 \nu_\infty$, so between $4.5$ and $7.5 \cdot 10^{-5}$. 

I tested some of these for one of the airfoils that previously messed up, and it appears there is almost no difference between the smaller values. 

| Case              | $\tilde \nu$      | $C_l$      | $C_d$        | $C_l/C_d$    |
|-------------------|-------------------|------------|--------------|--------------|
| Original          | $0.14$           | 0.516667   | -0.000555    | -931.013514  |
| OpenFOAM default  | $4.0 \cdot 10^{-5}$ | 1.13645    | -0.0742927   | -15.295453   |
| Lower NASA-bound  | $4.5 \cdot 10^{-5}$ | 1.1369     | -0.0743574   | -15.287780   |
| Far lower value   | $7.0 \cdot 10^{-6}$ | 1.13665    | -0.0743269   | -15.290234   |

I will continue to use $4.5 \cdot 10^{-5}$ for now. If anyone has better suggestions, I would love to hear them! 

## Future steps 

### $C_l/C_d$ curves 

I have added some basic angle-of-attack (AoA) formats already to the OpenFOAM templates. The next step will be to pick the best-performing airfoils, and simulate a range of angles for them, then analyze the lift and drag performance. The same can then be done for different velocities, to obtain estimates of the window of operation per airfoil before stall etc. occurs. 

### Model reduction 

I am curious about potential model reduction: by predicting performance based on the six inputs, a lot of time could be saved. If a rough prediction on which airfoils perform best is accurate, a simple machine learning model like random forests could be used for an initial optimization stage. I doubt a simple model like this would be sufficient, but it's an interesting avenue to explore. 

<img src="figures/27122024 - OpenFOAM - random forest model reduction.png" width="400" alt="Random forest model reduction idea">