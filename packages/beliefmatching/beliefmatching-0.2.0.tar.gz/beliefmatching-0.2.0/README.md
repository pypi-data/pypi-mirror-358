# BeliefMatching

[![PyPI version](https://badge.fury.io/py/beliefmatching.svg)](https://badge.fury.io/py/beliefmatching)

An implementation of the [belief-matching](https://arxiv.org/abs/2203.04948) decoder, using 
[pymatching](https://github.com/oscarhiggott/PyMatching) for the minimum-weight perfect matching (MWPM) subroutine and 
the [ldpc](https://pypi.org/project/ldpc/) library for the belief propagation (BP) subroutine.
Belief-matching is more accurate than the MWPM decoder alone when hyperedge error mechanisms are present in the error 
model.
Belief-matching has the same worst-case complexity as minimum-weight perfect matching, and the expected running time is roughly linear in the size of the decoding problem (Tanner graph).
See the [paper](https://journals.aps.org/prx/abstract/10.1103/PhysRevX.13.031007) for more details.

However, note that this implementation is much (>100x) slower than just using the pymatching (v2) 
decoder alone, since it has not been optimised for performance.
For example, for each shot, belief propagation is run on the full Tanner graph (stim `DetectorErrorModel`) with 
the output used to construct a new instance of a pymatching `Matching` object.
This implementation uses the [ldpc](https://pypi.org/project/ldpc/) library for BP, which uses a 
parallel BP schedule, and does not support the serial BP schedule shown to have slightly improved accuracy 
for belief-matching in the appendix of [this paper](https://arxiv.org/abs/2207.06431).

## Installation

To install beliefmatching, run:
```shell
pip install beliefmatching
```
To install from source, run:
```shell
pip install -e .
```
from the root directory.

## Usage

Here is an example of how the decoder can be used directly with Stim:

```python
import stim
import numpy as np
from beliefmatching import BeliefMatching

num_shots = 100
d = 5
p = 0.007
circuit = stim.Circuit.generated(
    "surface_code:rotated_memory_x",
    rounds=d,
    distance=d,
    before_round_data_depolarization=p,
    before_measure_flip_probability=p,
    after_reset_flip_probability=p,
    after_clifford_depolarization=p
)

sampler = circuit.compile_detector_sampler()
shots, observables = sampler.sample(num_shots, separate_observables=True)

bm = BeliefMatching(circuit, max_bp_iters=20)

predicted_observables = bm.decode_batch(shots)
num_mistakes = np.sum(np.any(predicted_observables != observables, axis=1))

print(f"{num_mistakes}/{num_shots}")  # prints 4/100
```

Note that, as well as loading directly from a `stim.Circuit` as above, you can also 
load from a `stim.DetectorErrorModel`. When using this option it is important that 
`decompose_errors=True` is set when calling `circuit.detector_error_model`. E.g.:
```python
dem = circuit.detector_error_model(decompose_errors=True)
bm = BeliefMatching(dem, max_bp_iters=20)
```

### Sinter integration

To integrate with [sinter](https://github.com/quantumlib/Stim/tree/main/glue/sample), you can use the 
`beliefmatching.BeliefMatchingSinterDecoder` class, which inherits from `sinter.Decoder`.
To use it, you can use the `custom_decoders` argument when using `sinter.collect`:

```python
import sinter
from beliefmatching import BeliefMatchingSinterDecoder

samples = sinter.collect(
    num_workers=4,
    max_shots=1_000_000,
    max_errors=1000,
    tasks=generate_example_tasks(),
    decoders=['beliefmatching'],
    custom_decoders={'beliefmatching': BeliefMatchingSinterDecoder()}
)
```

A complete example using sinter to compare beliefmatching with pymatching
can be found in the `examples/surface_code_threshold.py` file (this file also 
includes a definition of `generate_example_tasks()` used above).


## Tests

Tests can be run by installing pytest with 
```shell
pip install pytest
```

and running 
```shell
pytest tests
```

## Attribution

When using `beliefmatching` for research, please cite 
the [paper](https://journals.aps.org/prx/abstract/10.1103/PhysRevX.13.031007):
```
@article{PhysRevX.13.031007,
  title = {Improved Decoding of Circuit Noise and Fragile Boundaries of Tailored Surface Codes},
  author = {Higgott, Oscar and Bohdanowicz, Thomas C. and Kubica, Aleksander and Flammia, Steven T. and Campbell, Earl T.},
  journal = {Phys. Rev. X},
  volume = {13},
  issue = {3},
  pages = {031007},
  numpages = {20},
  year = {2023},
  month = {Jul},
  publisher = {American Physical Society},
  doi = {10.1103/PhysRevX.13.031007},
  url = {https://link.aps.org/doi/10.1103/PhysRevX.13.031007}
}

```
