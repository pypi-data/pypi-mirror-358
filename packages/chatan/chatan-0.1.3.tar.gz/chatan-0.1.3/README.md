# Chatan

Create diverse, synthetic datasets. Start from scratch or augment an existing dataset. Simple define your dataset schema as a set of generators, typically being LLMs with a prompt describing what kind of examples you want.

## Installation

```
pip install chatan
```

## Getting Started

```
import chatan

# Create a generator
gen = chatan.generator("openai", "YOUR_API_KEY")

# Define a dataset schema
ds = chatan.dataset({
    "topic": chatan.sample.choice(["Python", "JavaScript", "Rust"]),
    "prompt": gen("write a programming question about {topic}"),
    "response": gen("answer this question: {prompt}")
})

# Generate the data with a progress bar
df = ds.generate(n=10)
```

## Examples

Create Data Mixes

```
from chatan import dataset, generator, sample
import uuid

gen = generator("openai", "YOUR_API_KEY")

mix = [
    "san antonio, tx",
    "marfa, tx",
    "paris, fr"
]

ds = dataset({
    "id": sample.uuid(),
    "topic": sample.choice(mix),
    "prompt": gen("write an example question about the history of {topic}"),
    "response": gen("respond to: {prompt}"),
})
```

Augment datasets

```
from chatan import generator, dataset, sample
from datasets import load_dataset

gen = generator("openai", "YOUR_API_KEY")
hf_data = load_dataset("some/dataset")

ds = dataset({
    "original_prompt": sample.from_dataset(hf_data, "prompt"),
    "variation": gen("rewrite this prompt: {original_prompt}"),
    "response": gen("respond to: {variation}")
})

```

## Citation

If you use this code in your research, please cite:

```
@software{reetz2025chatan,
  author = {Reetz, Christian},
  title = {chatan: Create synthetic datasets with LLM generators.},
  url = {https://github.com/cdreetz/chatan},
  year = {2025}
}
```

## Contributing

Community contributions are more than welcome, bug reports, bug fixes, feature requests, feature additions, please refer to the Issues tab.
