[![Docker Build](https://github.com/LeoIV/bencher/actions/workflows/docker_build.yml/badge.svg)](https://github.com/LeoIV/bencher/actions/workflows/docker_build.yml)

# Docker Container

The Docker container can be pulled from the [Docker Hub](https://hub.docker.com/r/gaunab/bencher) or built locally.
It contains all benchmarks and dependencies and exposes the benchmark server via port 50051.

We give an exemplary usage of the Docker container in the [bencherclient](https://github.com/LeoIV/bencherclient)
repository.

```shell
pwd # /path/to/bencher
docker build -t bencher .
# always keep the container running, can be stopped with docker stop <container-id>
docker run -p 50051:50051 --restart always -d gaunab/bencher:latest
```

**or**

```shell
docker pull gaunab/bencher:latest
# always keep the container running, can be stopped with docker stop <container-id>
docker run -p 50051:50051 --restart always -d gaunab/bencher:latest
```

# Apptainer / Singularity Container

You can build an Apptainer container from the Docker image:

```shell
Bootstrap: docker
From: gaunab/bencher:latest
Namespace:
Stage: build

%environment
    export LANG=C.UTF-8
    export PATH="/root/.local/bin:$PATH"

%post
    cd /opt
    git clone your-repo
    cd your-repo
    pip install bencherscaffold # you'll need bencherscaffold to call bencher
    pip install your-dependencies

%startscript
    bash -c "/docker-entrypoint.sh"

%runscript
    bash -c "your-command-to-run-your-app"
```

This will create an Apptainer container with the Docker image `gaunab/bencher:latest` and the repository `your-repo`
with the dependencies `your-dependencies` installed.

## Usage

### Starting the instance

```shell
apptainer build container.sif your-apptainer-file
```

### Start the Apptainer instance

This starts all the benchmarks in the container (as defined in the `startscript` of the Apptainer file).

```shell
apptainer instance start container.sif your-instance-name
```

### Run your command that depends on the benchmarks

This runs your command in the instance `your-instance-name` as defined in the `runscript` of the Apptainer file.

```shell
apptainer run instance://your-instance-name
```

### Evaluating a benchmark

We show how to run all benchmarks in the [`bencherclient`](https://github.com/LeoIV/bencherclient) repository.
You don't need to use this repository, it is mainly used to test the benchmarks.
The general setup to evaluate a benchmark is as follows.
First, install the [`bencherscaffold`](https://github.com/LeoIV/BencherScaffold) package:

```shell
pip install git+https://github.com/LeoIV/BencherScaffold
```

Then, you can use the following code to evaluate a benchmark:

```python
from bencherscaffold.client import BencherClient
from bencherscaffold.protoclasses.bencher_pb2 import Value, ValueType

# Create a client to communicate with the Bencher server
# By default, it connects to 127.0.0.1:50051
client = BencherClient()

# Create a list of values to evaluate
values = [Value(type=ValueType.CONTINUOUS, value=0.5) for _ in range(180)]
# The benchmark name is the name of the benchmark you want to evaluate
benchmark_name = 'lasso-dna'

# Evaluate the benchmark with the given values
# This will send the values to the server and return the result
# If the server is not running, it will raise an error
result = client.evaluate_point(
    benchmark_name=benchmark_name,
    point=values,
)
print(f"Result: {result}")
```

### Available Benchmarks

The following benchmarks are available:

| Benchmark Name             | # Dimensions | Type        | Source(s)      | Noisy    |
|----------------------------|--------------|-------------|----------------|----------|
| lasso-dna                  | 180          | continuous  | [^1],[^5]      | &#x2612; |
| lasso-simple               | 60           | continuous  | [^1]           | &#x2612; |
| lasso-medium               | 100          | continuous  | [^1]           | &#x2612; |
| lasso-high                 | 300          | continuous  | [^1],[^5]      | &#x2612; |
| lasso-hard                 | 1000         | continuous  | [^1],[^5]      | &#x2612; |
| lasso-leukemia             | 7129         | continuous  | [^1]           | &#x2612; |
| lasso-rcv1                 | 47236        | continuous  | [^1],[^2]      | &#x2612; |
| lasso-diabetes             | 8            | continuous  | [^1]           | &#x2612; |
| lasso-breastcancer         | 10           | continuous  | [^1]           | &#x2612; |
| mopta08                    | 124          | continuous  | [^4],[^5]      | &#x2612; |
| maxsat60                   | 60           | binary      | [^6],[^7]      | &#x2612; |
| maxsat125                  | 125          | binary      | [^7]           | &#x2612; |
| robotpushing               | 14           | continuous  | [^3]           | &#x2611; |
| lunarlander                | 12           | continuous  | [^3]           | &#x2611; |
| rover                      | 60           | continuous  | [^3]           | &#x2612; |
| mujoco-ant                 | 888          | continuous  | [^9],[^5]      | &#x2611; |
| mujoco-hopper              | 33           | continuous  | [^9],[^5]      | &#x2611; |
| mujoco-walker              | 102          | continuous  | [^9],[^5]      | &#x2611; |
| mujoco-halfcheetah         | 102          | continuous  | [^9],[^5]      | &#x2611; |
| mujoco-swimmer             | 16           | continuous  | [^9],[^5]      | &#x2611; |
| mujoco-humanoid            | 6392         | continuous  | [^9],[^5]      | &#x2611; |
| svm                        | 388          | continuous  | [^4],[^5],[^8] | &#x2612; |
| svmmixed                   | 53           | mixed       | [^6],[^7]      | &#x2612; |
| pestcontrol                | 25           | categorical | [^10],[^13]    | &#x2612; |
| bbob-sphere                | any          | continuous  | [^11],[^12]    | &#x2612; |
| bbob-ellipsoid             | any          | continuous  | [^11],[^12]    | &#x2612; |
| bbob-rastrigin             | any          | continuous  | [^11],[^12]    | &#x2612; |
| bbob-buecherastrigin       | any          | continuous  | [^11],[^12]    | &#x2612; |
| bbob-linearslope           | any          | continuous  | [^11],[^12]    | &#x2612; |
| bbob-attractivesector      | any          | continuous  | [^11],[^12]    | &#x2612; |
| bbob-stepellipsoid         | any          | continuous  | [^11],[^12]    | &#x2612; |
| bbob-rosenbrock            | any          | continuous  | [^11],[^12]    | &#x2612; |
| bbob-rosenbrockrotated     | any          | continuous  | [^11],[^12]    | &#x2612; |
| bbob-ellipsoidrotated      | any          | continuous  | [^11],[^12]    | &#x2612; |
| bbob-discus                | any          | continuous  | [^11],[^12]    | &#x2612; |
| bbob-bentcigar             | any          | continuous  | [^11],[^12]    | &#x2612; |
| bbob-sharpridge            | any          | continuous  | [^11],[^12]    | &#x2612; |
| bbob-differentpowers       | any          | continuous  | [^11],[^12]    | &#x2612; |
| bbob-rastriginrotated      | any          | continuous  | [^11],[^12]    | &#x2612; |
| bbob-weierstrass           | any          | continuous  | [^11],[^12]    | &#x2612; |
| bbob-schaffers10           | any          | continuous  | [^11],[^12]    | &#x2612; |
| bbob-schaffers1000         | any          | continuous  | [^11],[^12]    | &#x2612; |
| bbob-griewankrosenbrock    | any          | continuous  | [^11],[^12]    | &#x2612; |
| bbob-schwefel              | any          | continuous  | [^11],[^12]    | &#x2612; |
| bbob-gallagher101          | any          | continuous  | [^11],[^12]    | &#x2612; |
| bbob-gallagher21           | any          | continuous  | [^11],[^12]    | &#x2612; |
| bbob-katsuura              | any          | continuous  | [^11],[^12]    | &#x2612; |
| bbob-lunacekbirastrigin    | any          | continuous  | [^11],[^12]    | &#x2612; |
| pbo-onemax                 | any          | binary      | [^11]          | &#x2612; |
| pbo-leadingones            | any          | binary      | [^11]          | &#x2612; |
| pbo-linear                 | any          | binary      | [^11]          | &#x2612; |
| pbo-onemaxdummy1           | any          | binary      | [^11]          | &#x2612; |
| pbo-onemaxdummy2           | any          | binary      | [^11]          | &#x2612; |
| pbo-onemaxneutrality       | any          | binary      | [^11]          | &#x2612; |
| pbo-onemaxepistasis        | any          | binary      | [^11]          | &#x2612; |
| pbo-onemaxruggedness1      | any          | binary      | [^11]          | &#x2612; |
| pbo-onemaxruggedness2      | any          | binary      | [^11]          | &#x2612; |
| pbo-onemaxruggedness3      | any          | binary      | [^11]          | &#x2612; |
| pbo-leadingonesdummy1      | any          | binary      | [^11]          | &#x2612; |
| pbo-leadingonesdummy2      | any          | binary      | [^11]          | &#x2612; |
| pbo-leadingonesneutrality  | any          | binary      | [^11]          | &#x2612; |
| pbo-leadingonesepistasis   | any          | binary      | [^11]          | &#x2612; |
| pbo-leadingonesruggedness1 | any          | binary      | [^11]          | &#x2612; |
| pbo-leadingonesruggedness2 | any          | binary      | [^11]          | &#x2612; |
| pbo-leadingonesruggedness3 | any          | binary      | [^11]          | &#x2612; |
| pbo-labs                   | any          | binary      | [^11]          | &#x2612; |
| pbo-isingring              | any          | binary      | [^11]          | &#x2612; |
| pbo-isingtorus             | any          | binary      | [^11]          | &#x2612; |
| pbo-isingtriangular        | any          | binary      | [^11]          | &#x2612; |
| pbo-mis                    | any          | binary      | [^11]          | &#x2612; |
| pbo-nqueens                | any          | binary      | [^11]          | &#x2612; |
| pbo-concatenatedtrap       | any          | binary      | [^11]          | &#x2612; |
| pbo-nklandscapes           | any          | binary      | [^11]          | &#x2612; |
| graph-maxcut2000           | 800          | binary      | [^11]          | &#x2612; |
| graph-maxcut2001           | 800          | binary      | [^11]          | &#x2612; |
| graph-maxcut2002           | 800          | binary      | [^11]          | &#x2612; |
| graph-maxcut2003           | 800          | binary      | [^11]          | &#x2612; |
| graph-maxcut2004           | 800          | binary      | [^11]          | &#x2612; |
| graph-maxcoverage2100      | 800          | binary      | [^11]          | &#x2612; |
| graph-maxcoverage2101      | 800          | binary      | [^11]          | &#x2612; |

# Citation
If you use this repository or the benchmarks in your research, please cite the following [paper](https://arxiv.org/abs/2505.21321):

```bibtex
@misc{papenmeier2025bencher,
      title={Bencher: Simple and Reproducible Benchmarking for Black-Box Optimization}, 
      author={Leonard Papenmeier and Luigi Nardi},
      year={2025},
      eprint={2505.21321},
      archivePrefix={arXiv},
      primaryClass={cs.LG},
      url={https://arxiv.org/abs/2505.21321}, 
}
```

[^1]: [`LassoBench`](https://github.com/ksehic/LassoBench) (`
Šehić Kenan, Gramfort Alexandre, Salmon Joseph and Nardi Luigi, "LassoBench: A High-Dimensional Hyperparameter Optimization Benchmark Suite for Lasso", AutoML conference, 2022.`)
[^2]: The LassoBench paper states 19,959 features, but the number of features in the RCV1 dataset is 47,236.
[^3]: [`TurBO`](https://github.com/uber-research/TuRBO) (
`David Eriksson, Michael Pearce, Jacob Gardner, Ryan D Turner and Matthias Poloczek, "Scalable Global Optimization via Local Bayesian Optimization." NeurIPS 2019`)
[^4]: [`SAASBO`](https://github.com/martinjankowiak/saasbo)
`David Eriksson and Martin Jankowiak, "High-dimensional Bayesian optimization with sparse axis-aligned subspaces", UAI 2021`
[^5]: [`BAxUS`](https://github.com/LeoIV/BAxUS)
`Leonard Papenmeier, Luigi Nardi, and Matthias Poloczek, "Increasing the Scope as You Learn: Adaptive Bayesian Optimization in Nested Subspaces", NeurIPS 2022`
[^6]: [`BODi`](https://github.com/aryandeshwal/BODi)
`Aryan Deshwal, Sebastian Ament, Maximilian Balandat, Eytan Bakshy, Janardhan Rao Doppa, and David Eriksson, "Bayesian Optimization over High-Dimensional Combinatorial Spaces via Dictionary-based Embeddings", AISTATS 2023`
[^7]: [`Bounce`](https://github.com/LeoIV/bounce)
`Leonard Papenmeier, Luigi Nardi and Matthias Poloczek, "Bounce: Reliable High-Dimensional Bayesian Optimization for Combinatorial and Mixed Spaces", NeurIPS 2023`
[^8]: The SVM benchmark is not included in the repository and was obtained by corresponding with the authors of the
paper.
[^9]: [`LA-MCTS`](https://github.com/facebookresearch/LA-MCTS)
`Linnan Wang, Rodrigo Fonseca, and Yuandong Tian, "Learning Search Space Partition for Black-box Optimization using Monte Carlo Tree Search", NeurIPS 2020`
[^10]: Oh, Changyong, et al. "Combinatorial bayesian optimization using the graph cartesian product." Advances in Neural
Information Processing Systems 32 (2019).
[^11]: de Nobel, Jacob, et al. "Iohexperimenter: Benchmarking platform for iterative optimization heuristics."
Evolutionary Computation 32.3 (2024): 205-210.
[^12]: Hansen, Nikolaus, et al. "COCO: A platform for comparing continuous optimizers in a black-box setting."
Optimization Methods and Software 36.1 (2021): 114-144.
[^13]: Each category has 5 possible values. The benchmark expects an integer between 0 and 4 for each category.