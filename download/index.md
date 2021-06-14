<h1 id="overview">Overview</h1>
The <i>Pano3D</i>, dataset is specifically designed for fostering 360 based applications.
We employ two real-world 3D scanned datasets (<a href="https://niessner.github.io/Matterport/">Matterport3D</a>) and  (<a href="http://gibsonenv.stanford.edu/database/">GibsonV2</a>), and physically-based rendering, to generate realistic multimodal data.
 <!-- <p>
 <img src="./assets/images/dataset_concept.png" alt="DatasetConcept">
 </p> -->

 <h1 id="motivation">Motivation</h1>
Even though great progress has been achieved during the last years in the 360 domain, there is still a gap regarding data availability, which permits evaluating the generalization ability of the developed algorithms. To that end, Pano3d aims at filling this gap by providing a large corpus of data, varying in terms of domain, lighting conditions, and  <a href="https://docs.blender.org/manual/en/latest/render/color_management.html">color spaces</a>. 

<h1> Modalities </h1>
We offer 3 different modalities as indicated below, with the corresponding data formats following and the invalid values (due to imperfect scanning, holes manifest during rendering) denoted in brackets.

| __Image Type__        | __Data Format__           | __Invalid Value__  |
| ------------- |:-------------:|:-----:|
| `Color` images | <code>.png</code> | gray, _i.e._ `(64, 64, 64)` |
| `Depth` maps | single channel, floating point <code>.exr</code> | `(inf)` |
| `Normal` maps | 3-channel (_x, y, z_), floating point <code>.exr</code> | `(0.0f, 0.0f, 0.0f)` & `(nan, nan, nan)` |
<h2> Samples </h2>
<p align="center">
  <div> 
    <img src=".assets/images/data_gifs/gv2_tiny.gif" width="100%" style="float:left; margin-right:1%;">
  </div>
  <!-- <div> 
    <img src="./assets/img/data_gifs/DatasetGifStanford.gif" width="32%" style="float:left; margin-right:1%;">
  </div>
  <div> 
    <img src="./assets/img/data_gifs/DatasetGifSunCG.gif" width="32%" style="float:left; margin-right:1%;">
  </div> -->
  <p style="clear:both;"/>
</p>

 <h1> Usage </h1>

 <h2> Download </h2>
<p>We follow a <b>two-step</b> procedure to download the <b>UAVA</b> dataset.</p>

<p style="text-align: justify;">
                To download the \(\textbf{Pano3D}\) dataset we follow a two-step process:
                        <ol>
                            <li>
                                Access to the \(\textbf{Pano3D}\) dataset requires agreement with the terms and conditions for each of the 3D datasets
                                that were used to create (i.e. render) it, and more specifically, Matterport3D [<a href="#Matterport3D"><b>1</b></a>] and GibsonV2 [<a href="#GibsonV2"><b>2</b></a>]. 
                                Therefore, in order to grant you access to this dataset, we need you to first fill <a href="" >request form</a>.
                            </li>
                            <li>
                                Then, you need to perform a request for access to the respective Zenodo repositories, 
                                where the data are hosted (more information can be found in our <a href="" >download page</a>). 
                                Due to data-size limitations, the dataset is split into six (6) repositories, 
                                which respectively contain the color image, depth and normal map renders for each image. 
                                The repositories are split into the two resolutions, with each subgroup of 3 repositories 
                                containing the entire Matterport3D dataset renders, the entire GibsonV2 test split renders, 
                                and the remainder of GibsonV2 which is used as additional training data. 
                                Therefore, a separate request for access needs to be made to each repository in order to download 
                                the corresponding data. 
                            </li>
                        </ol>
                        <b>Note</b> that only completing one step of the two (i.e. only filling out the form, or only requesting access 
                        from the Zenodo repositories) <b>will not</b> be enough to get access to the data. 
                        We will do our best to contact you in such cases and notify you to complete all steps as needed, 
                        but our mails may be lost (e.g. spam filters/folders). 
                        The only exception to this, is if you have already filled in the form and need access to another Zenodo repository 
                        (for example you need extra dataset/splits which are hosted on different Zenodo repositories), then you only need 
                        to fill in the Zenodo request but please, make sure to mention that the form has already been filled in so that 
                        we can verify it. <br>

                        Each volume is broken down in several .zip files (2GB each) for more convenient downloading on low 
                        bandwidth connections. You need all the .zip archives of each volume in order to extract the containing files.
</p>
<p style="text-align: justify;">
  <b>Note</b> that only completing one step of the two (<i>i.e.</i> only filling out the form, or only requesting access from the Zenodo repositories <b>will not</b> be enough to get access to the data. We will do our best to contact you in such cases and notify you to complete all steps as needed, but our mails may be lost (e.g. spam filters/folders). 
  The only exception to this, is if you have already filled in the form and need access to another Zenodo repository (for example you need extra viewpoint renders which are hosted on different Zenodo repositories), then you only need to fill in the Zenodo request but please, make sure to mention that the form has already been filled in so that we can verify it.
</p>

<p style="text-align: justify;">
Each volume is broken down in several <code>.zip</code> files (2GB each) for more convinient downloading on low bandwidth connections. You need all the <code>.zip</code> archives of each volume in order to extract the containing files.
</p>

 <h2> Data splits </h2>
 We follow the same data-split logic as defined in Matterport3D. We use GV2 splits for testing only.

<!-- <h2> Data organisation</h2>
<table>
<tr>
<td>
<img src="./images/data_organisation.png" height="450" alt="datatree">
</td>
</tr>
</table> -->
 <h1> Acknowledgements </h1>
 This dataset has been generated within the European Union’s Horizon 2020 innovation programme [ATLANTIS](https://atlantis-ar.eu/) under grant agreement No 951900.

 <table>
<tr>
<td>
<img src="./assets/images/eu_logo.png" alt="eu">
</td>
<td>
<img src="./assets/images/atlantis_logo.png" alt="atlantis">
</td>
</tr>
</table>
