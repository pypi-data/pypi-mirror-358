# CellECTION: An Attention-Based Multiple Instance Learning Approach to Predict Emergent Phenotypes from Single Cell Populations

developed by Hongru Hu: hrhu@ucdavis.edu

![alt text](https://github.com/quon-titative-biology/CELLECTION/blob/main/img/cellection.png)

Biological systems exhibit emergent phenotypes that arise from the collective behavior of individual components, such as whole-organ functions that arise from the coordinated activity of its individual cells, or organism-level phenotypes that result from the functional interplay of collections of genes in the genome. We present CELLECTION, a deep learning framework that learns to associate subgroups of instances with different emergent phenotypes. We show CELLECTION enables interpretable predictions for heterogeneous tasks, including disease classification, identification of disease-associated cell subtypes, alignment of developmental stages between human model systems, and even predicting relative hand-wing indices across the avian lineage. CELLECTION therefore provides a scalable and flexible framework for identifying key cellular or genetic signatures underlying complex traits in development, disease, and evolution.

---
## Installation

You can install CELLECTION from PyPI:

```bash
pip install cellection
```

For full functionality including additional bioinformatics tools:

```bash
pip install cellection[full]
```

Or install from source:

```bash
git clone https://github.com/quon-titative-biology/CELLECTION.git
cd CELLECTION
pip install -e .
```

---
### Package requirements
scPair is implemented using `torch 2.4.1`, `anndata 0.10.9`, and `scanpy 1.10.3`  under `Python 3.10.15`. 

Users can choose to create the environment provided under this repository [(env file)](https://github.com/quon-titative-biology/CELLECTION/blob/main/environment.yml):
```command line
conda env create --file=environment.yml
```



## Quick Start

```python
import cellection
import scanpy as sc

# Load your single-cell data
adata = sc.read_h5ad("your_data.h5ad")

# Initialize CELLECTION object
cellection_obj = cellection.cellectiion_object(
    adata=adata,
    task_type='classification', 
    task_key='disease_cov', 
    sample_key='ind_cov', 
    batch_key=None, 
    model_type='classification', 
    input_type='measurement', 
    sparse_input=True, 
    InstanceEncoder=True, 
    val_size=0.2, 
    aggregator='gated_attention', 
    global_features=128, 
    attention_dim=32, 
    max_epochs=200, 
    learning_rate=1e-4, 
    batch_size=15, 
    seed=2, 
    device=torch.device("cuda" if torch.cuda.is_available() else "cpu"), 
    hidden_layer=[256, 32], 
    activation=nn.ReLU(), 
    layernorm=True, 
    batchnorm=False, 
    dropout_rate=0.1, 
    save_model=True, 
    save_path=None)

# Prepare the data and initialize the model
cellection_obj.prepare()

# Train the model
cellection_obj.train()

# Perform inference
sample_meta, true_labels, pred_labels, sample_embeddings, sample_global_features, attention_scores = cellection_obj.inference()
```


## Features

- **Multiple Instance Learning (MIL)**: Framework for learning from bags of instances
- **PointNet Architecture**: Implementation of PointNet for point cloud classification
- **Cell Classification**: Specialized for biological cell classification tasks
- **Attention Mechanisms**: Multiple aggregation methods including gated attention
- **Batch Effect Correction**: Built-in support for batch effect handling
- **Flexible Input**: Support for both measurement data and pre-computed features


## Citation

If you use CELLECTION in your research, please cite:

```bibtex
@software{cellection2025,
  title={Predicting emergent phenotypes from single cell populations using CELLECTION},
  author={Hongru Hu},
  year={2025},
  url={https://github.com/quon-titative-biology/CELLECTION}
}
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
