<div align="center">

![Banner_Image](./example_data/images/banner.png)

</div>

---

<div align="center">

# BED-BPP: Benchmark Dataset for Robotic Bin Packing Problems

</div>

>
> ℹ️ To take a look at the actual paper implementation, please use the branch 
> [paper-implementation](https://github.com/floriankagerer/bed-bpp-env/tree/paper-implementation).
>

<!-- -------------------------------------------------------------- -->
## <div align="center">Paper Accepted</div>
I am happy to announce that our paper "BED-BPP: Benchmarking Dataset for Robotic Bin Packing" has been accepted for publication in the <a href="https://journals.sagepub.com/home/ijr" target="_blank">International Journal of Robotics Research (IJJR)</a>.


Whenever you use the dataset, please cite our publication:

>
> Kagerer F, Beinhofer M, Stricker S, Nüchter A. BED-BPP: Benchmarking dataset for robotic bin packing problems. The International Journal of Robotics Research. 2023;42(11):1007-1014. doi:10.1177/02783649231193048
> <br>
> <a href="https://floriankagerer.github.io/assets/publications/Kagereretal2023-ijrr.bib" target="_blank">[BibTeX]</a>
<a href="https://doi.org/10.1177/02783649231193048" target="_blank">[DOI]</a>
>


<!-- -------------------------------------------------------------- -->
## <div align="center">Getting Started</div>

### <div align="center"> 🚧 Work in progress 🚧</div>


Please find below the instructions on how to setup and use the code in this repository.

<!-- Preliminaries -->
<details open>
<summary><u>Preliminaries (Python and Blender)</u></summary>

To use all features and functions in this repository, make sure that you have installed Python and Blender on your system.

**Blender.** Download and install [Blender](https://www.blender.org/download/). If [script_evaluate_packing_plan.py](./code/script_evaluate_packing_plan.py) does not find the location of Blender, add the [Blender path to bed-bpp_env.conf](./code/bed-bpp_env.conf#L16).

**Python.** We manage our Python environments with [Anaconda](https://www.anaconda.com/download). The dependencies of this project are managed with [Poetry](https://python-poetry.org/).

</details> <!-- end preliminaries-->
<br>

<!-- Install Requirements -->
<details open>
<summary><u>Install (Requirements in virtual Python environment)</u></summary>

1. Create and activate a virtual Python environment
    
    (a) Create a virtual environment with Anaconda by running
    ```powershell
    (base) dev@nb:~$ conda create -n bed-bpp-env python=3.12
    ```

    <br>

    (b) Activate the created environment with
    ```powershell
    (base) dev@nb:~$ conda activate bed-bpp-env
    ```
    This should update your terminal to
    ```powershell
    (bed-bpp-env) dev@nb:~$
    ```
    <br>

    (c) Install the dependencies with
    ```powershell
    (bed-bpp-env) dev@nb:~$ poetry install
    ```

</details> <!-- end install-->
<br>


<!-- usage -->
<details open>
<summary><u>Usage</u></summary>

Check whether the setup was successful by running
```powershell
(bed-bpp-env) dev@nb:~$ python demo_gym_pal_env.py -v
```
After a few seconds you should see an image that is similar to the following

<div align="center">

![test_image](./example_data/images/example_render_image.png)

**😀 Happy Coding 😀**
</div>
</details> <!-- end usage-->
<br>

<!-- -------------------------------------------------------------- -->
## <div align="center">Scripts</div>
Here is an overview about the scripts in this repo.

<!-- -->
<details><summary>demo_gym_palenv.py</summary>
This script demonstrates the use of this repository and the palletizing environment. 

</details><br>


<!-- -->
<details><summary>script_evaluate_packing_plan.py</summary>
This script evaluates packing plans and stores the results. 

</details><br>


<!-- -->
<details><summary>run_heuristic_O3DBP_3_2.py</summary>
The script which we used to create the packing plan for the task Online 3D bin packing with preview `p=3` and selection `s=2`.

</details><br>


<!-- -->
<details><summary>script_visualize_packing_plan.py</summary>
This script visualizes a packing plan, which is given as dict with order ids as key and a list of actions as values, and finally creates a video of the palletization for each order.  

</details><br>


<!-- -->
<details><summary>run_your_solver.py</summary>
This script can be used for your solver.
</details><br>


<!-- -------------------------------------------------------------- -->
## <div align="center">Participation</div>

We encourage you to develop solvers for the three-dimensional bin packing problem and submit your results to the [leaderboard](https://floriankagerer.github.io/leaderboard/).

For details, visit https://floriankagerer.github.io/dataset and https://floriankagerer.github.io/leaderboard.

<div align="center">
    
![Leaderboardr_Image](./example_data/images/leaderboard.png)

</div>

Till now, we integrated the following solvers in this repo and used `BED-BPP` as benchmark:  

- [alexfrom0815/sisyphus](./alexfrom0815_O3D-BPP-PCT/readme_Online-3D-BPP-PCT_integration.md)

- [floriankagerer/heuristic_O3DBP-3-2](./code/heuristics/O3DBP_3_2.md)

- [hschneid/xflp](./hschneid_xflp/readme_xflp_integration.md)

- [josch/sisyphus](./josch_sisyphus/readme_sisyphus_integration.md)






