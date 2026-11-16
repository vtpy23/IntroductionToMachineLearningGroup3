# Dataset preparation

Implemented: Hugging Face `uoft-cs/cifar100`, pinned revision
`aadb3af77e9048adbea6b47c21a81e47dd092ae5`. Run `python -m scripts.run --stage data`.
See [provenance and preprocessing](../docs/DATA.md).

Datasets must be downloaded by the experiment code from Hugging Face or Kaggle, not added manually to this Git repository. If the paper dataset does not already exist on either site, prepare and publish an appropriate copy there, then download it programmatically.

Document dataset identifier, license, version, split and processing in the root README after paper selection.
