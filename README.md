# Pano3D
## A Holistic Benchmark and a Solid Baseline for 360<sup>o</sup> Depth Estimation

[![](https://img.shields.io/badge/CVPR21-OmniCV-blueviolet)](https://sites.google.com/view/omnicv2021/home)
[![](https://img.shields.io/badge/Project-Page-blue)](https://vcl3d.github.io/Pano3D/)
[![](https://img.shields.io/badge/Download-Data-ff69b4)](https://vcl3d.github.io/Pano3D/download/)
[![](https://img.shields.io/badge/H2020-ATLANTIS-2e324d)](https://atlantis-ar.eu/)

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Maintaner](https://img.shields.io/badge/maintainer-Giorgos_Albanis-blue)](http://tzole1155.github.io)
[![Maintaner](https://img.shields.io/badge/maintainer-Nikolaos_Zioulis-lightblue)](http://zokin.github.io)


<!-- https://academia.stackexchange.com/questions/27341/flair-badge-for-arxiv-paper -->
<!-- https://zenodo.org/badge/doi/10.5281/zenodo.4018965.svg?color=yellow -->
<!-- https://github.com/bionanoimaging/UC2-GIT/issues/44
-->

> Pano3D  is a new benchmark for depth estimation from spherical panoramas. 
We generate a dataset (using GibsonV2) and provide baselines for holistic performance assessment, offering:
1. Primary and secondary traits metrics:
     - Direct **depth** performance:
        - (w)RMSE
        - (w)RMSLE
        - AbsRel
        - SqRel
        - (w)Relative accuracy (`\delta`) @ `{1.05, 1.1, 1.25, 1.25^2, 1.25^3}`
    - Boundary **discontinuity** preservation:
        - Precision @ `{0.25, 0.5, 1.0}m`
        - Recall @ `{0.25, 0.5, 1.0}m`
        - Depth boundary errors of accuracy and completeness
    - Surface **smoothness**:
        - RMSE<sup>o</sup>
        - Relative accuracy (`\alpha`) @ `{11.25`<sup>o</sup>`, 22.5`<sup>o</sup>`, 30`<sup>o</sup>`}`
2. Out-of-distribution & Zero-shot cross dataset transfer:
    - Different depth distribution test set
    - Varying scene context test set
    - Shifted camera domain test set
> By disentangling generalization and assessing all depth properties, Pano3D aspires to drive progress benchmarking for 360<sup>o</sup> depth estimation.

> Using Pano3D to search for a solid baseline results in an acknowledgement of exploiting complementary error terms, adding encoder-decoder skip connections and using photometric augmentations.

### TODO

- [ ] Data & Loader
- [ ] Models Weights & Code
- [ ] Metrics Code

### Data

#### Download

#### Loader

#### Splits


### Models

#### Download

#### Inference

#### Serve


### Metrics

#### Direct

#### Boundary

#### Smoothness


### Results

