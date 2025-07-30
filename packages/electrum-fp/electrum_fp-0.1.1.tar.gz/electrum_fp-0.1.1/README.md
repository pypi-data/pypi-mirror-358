# electrum-fp

**Metal-aware molecular fingerprinting tools for transition metal complexes.**  
`electrum-fp` provides vector representations that combine ligand topology with metal identity, enabling downstream tasks like classification, regression, and visualization.

## Installation

```bash
pip install electrum-fp
```

## Usage

```python
from electrum_fp.electrum import calculate_fingerprint

ligands = "Cc1c(C)c(C)c(c2cccc3cccnc32)c1C.Cl.Cl"        # Ligand SMILES
metal = "Rh"                                             # Corresponding metal

fps = calculate_fingerprint(ligands, metal, radius=2, n_bits=512)
print(fps) 
``` 