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

![Pano3D Intro](./assets/img/intro.png)

> Pano3D  is a new benchmark for depth estimation from spherical panoramas. 
We generate a dataset (using GibsonV2) and provide baselines for holistic performance assessment, offering:
1. Primary and secondary traits metrics:
     - Direct **depth** performance:
        - (w)RMSE
        - (w)RMSLE
        - AbsRel
        - SqRel
        - (w)Relative accuracy (`\delta`) @ {`1.05`, `1.1`, `1.25`, `1.25`<sup>2</sup>, `1.25`<sup>3</sup> }
    - Boundary **discontinuity** preservation:
        - Precision @ {`0.25`, `0.5`, `1.0`}m
        - Recall @ {`0.25`, `0.5`, `1.0`}m
        - Depth boundary errors of accuracy and completeness
    - Surface **smoothness**:
        - RMSE<sup>o</sup>
        - Relative accuracy (`\alpha`) @ {`11.25`<sup>o</sup>, `22.5`<sup>o</sup>, `30`<sup>o</sup>}
2. Out-of-distribution & Zero-shot cross dataset transfer:
    - Different depth distribution test set
    - Varying scene context test set
    - Shifted camera domain test set
> By disentangling generalization and assessing all depth properties, Pano3D aspires to drive progress benchmarking for 360<sup>o</sup> depth estimation.

> Using Pano3D to search for a solid baseline results in an acknowledgement of exploiting complementary error terms, adding encoder-decoder skip connections and using photometric augmentations.

### TODO
- [x] Data Download
- [ ] Loader & Splits
- [ ] Models Weights Download
- [ ] Model Serve Code
- [ ] Model Hub Code
- [ ] Metrics Code

### Data

#### Download
To download the data, follow the instructions at [vcl3d.github.io/Pano3D/download/](https://vcl3d.github.io/Pano3D/download/).
> Please note that getting access to the data download links is a **two** step process as the dataset is a derivative and compliance with the original dataset's terms and usage agreements is required. Therefore:
1. You first need to fill in this [Google Form](https://forms.gle/SJUqLZYmu8sogwrAA).
2. And, then, you need to perform an access request at each one of the Zenodo repositories (depending on which dataset partition you need):
    - [Matterport3D Train & Test (/w Filmic) High Resolution (`1024 x 512`)](https://zenodo.org/record/4957413#.YM9GRfkzaUk)
    - [GibsonV2 Full (w/o normals) High Resolution (`1024 x 512`)](https://zenodo.org/record/4986012#.YM9K1fkzaUl)
    - [GibsonV2 Tiny, Medium & Fullplus (w/o normals) High Resolution (`1024 x 512`)](https://zenodo.org/record/4991961#.YM9K3fkzaUl)
    - [Matterport3D Train & Test (/w Filmic) Low Resolution (`512 x 256`)](https://zenodo.org/record/4957305#.YM9K6PkzaUl)
    - [GibsonV2 Full Low Resolution (`512 x 256`)](https://zenodo.org/record/4966769#.YM9K6fkzaUl)
    - [GibsonV2 Tiny, Medium & Fullplus (/w Filmic) Low Resolution (`512 x 256`)](https://zenodo.org/record/4966684#.YM9K6fkzaUl)

After both these steps are completed, you will soon receive the download links for each dataset partition.

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

