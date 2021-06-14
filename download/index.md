<h1 id="overview">Overview</h1>

The **Pano3D** 360<sup>o</sup> depth estimation benchmark provides a standard <a href="https://niessner.github.io/Matterport/">Matterport3D</a> train and test split, as well as a secondary <a href="http://gibsonenv.stanford.edu/database/">GibsonV2</a> partioning for testing and training as well.

The latter is used for zero-shot cross dataset transfer performance assessment and decomposes it into 3 different splits, each one ablating a specific generalization trait.

<h1> Data Description </h1>

<h2> Modalities </h2>

The dataset offers `3` different modalities as indicated below:

| __Image Type__        | __Data Format__           | __Invalid Value__  |
| ------------- |:-------------:|:-----:|
| `Color` | `.png` | true black, <br/> _i.e._ `(0, 0, 0)` |
| `Depth` | single channel, <br/> floating point `.exr` | `(inf)` |
| `Normal` | 3-channel (_x, y, z_),<br/> floating point `.exr` | `(0.0f, 0.0f, 0.0f)` <br/> & `(nan, nan, nan)` |

Each modality has a corresponding data format and invalid values (due to imperfect scanning, holes manifest during rendering).


<h2> Splits </h2>
  
  <style type="text/css">
.tg  {border:none;border-collapse:collapse;border-spacing:0;margin:0px auto;}
.tg td{border-style:solid;border-width:0px;font-family:Arial, sans-serif;font-size:14px;overflow:hidden;
  padding:10px 5px;word-break:normal;}
.tg th{border-style:solid;border-width:0px;font-family:Arial, sans-serif;font-size:14px;font-weight:normal;
  overflow:hidden;padding:10px 5px;word-break:normal;}
.tg .tg-290e{background-color:#1f78b4;border-color:inherit;color:#efefef;
  font-family:"Lucida Console", Monaco, monospace !important;;font-weight:bold;text-align:center;vertical-align:top}
.tg .tg-baqh{text-align:center;vertical-align:top}
.tg .tg-7c40{background-color:#986536;border-color:inherit;font-family:"Lucida Console", Monaco, monospace !important;;
  font-weight:bold;text-align:center;vertical-align:top;color:#efefef}
.tg .tg-kzsc{background-color:#e7298a;color:#efefef;font-weight:bold;text-align:center;vertical-align:top}
.tg .tg-xhg5{border-color:inherit;font-family:"Lucida Console", Monaco, monospace !important;;text-align:center;vertical-align:top}
.tg .tg-9cbo{background-color:#b3de69;border-color:inherit;font-family:"Lucida Console", Monaco, monospace !important;;
  font-weight:bold;text-align:center;vertical-align:top}
.tg .tg-yz71{background-color:#1b9e77;border-color:inherit;color:#efefef;
  font-family:"Lucida Console", Monaco, monospace !important;;font-weight:bold;text-align:center;vertical-align:top}
</style>
<table class="tg">
<tbody>
  <tr style="padding: 0px;">
    <td class="tg-yz71" style="padding: 0px;">GibsonV2 Tiny</td>
    <td class="tg-290e" style="padding: 0px;">GibsonV2 Medium</td>
  </tr>
  <tr>
    <td class="tg-xhg5" style="padding: 0px;"> <img src="../assets/data_gifs/gv2_tiny.gif" width="100%" style="float:center; margin-right:1%;"></td>
    <td class="tg-xhg5" style="padding: 0px;"> <img src="../assets/data_gifs/gv2_tiny.gif" width="100%" style="float:center; margin-right:1%;"></td>
  </tr>
  <tr>
    <td class="tg-9cbo" style="padding: 0px;">GibsonV2 Fullplus</td>
    <td class="tg-7c40" style="padding: 0px;">GibsonV2 Full</td>
  </tr>
  <tr>
    <td class="tg-xhg5" style="padding: 0px;"> <img src="../assets/data_gifs/gv2_tiny.gif" width="100%" style="float:center; margin-right:1%;"></td>
    <td class="tg-xhg5" style="padding: 0px;"> <img src="../assets/data_gifs/gv2_tiny.gif" width="100%" style="float:center; margin-right:1%;"></td>
  </tr>
  <tr>
    <td class="tg-kzsc" style="padding: 0px;">GibsonV2 Tiny Filmic</td>
    <td class="tg-kzsc" style="padding: 0px;">GibsonV2 Fullplus Filmic</td>
  </tr>
  <tr>
    <td class="tg-baqh" style="padding: 0px;"> <img src="../assets/data_gifs/gv2_tiny.gif" width="100%" style="float:center; margin-right:1%;"></td>
    <td class="tg-baqh" style="padding: 0px;"> <img src="../assets/data_gifs/gv2_tiny.gif" width="100%" style="float:center; margin-right:1%;"></td>
  </tr>
</tbody>
</table>
  
  When training on Matterport3D the above splits offer:
  - <b><span style="color: #1b9e77;">Tiny</span></b>: <b>Same</b> context (residential buildings) but <b>different</b> depth distribution
  - <b><span style="color: #1f78b4;">Medium</span></b>: <b>Same</b> context (residential buildings) but <b>different</b> depth distribution
  - <b><span style="color: #b3de69;">Fullplus</span></b>: <b>Different</b> context (non exclusively residential buildings) but of the <b>same</b> depth distribution
  - <b><span style="color: #e7298a;">Filmic</span></b>: <b>Same</b> as the original splits but with a <b>shifted</b> camera (color) domain
  - <b><span style="color: #986536;">Full</span></b>: An <b>expanded</b> (`~ x3` compared to Matterport3D) training set

 <h1> Download Data </h1><a href="#Download"/>

<p style="text-align: justify;">
  To download the <b>Pano3D</b> dataset a two-step process is employed as the rendered dataset is a derivative of third party 3D datasets. To get access to download the dataset two **parallel** steps are required:
                        <ol>
                            <li>
                                First, to agree with the terms and conditions for each of the 3D datasets that were used to create (i.e. render) it, and more specifically, Matterport3D [<a href="#Matterport3D"><b>1</b></a>] and GibsonV2 [<a href="#GibsonV2"><b>2</b></a>]. This is accomplished by filling in this <a href="" >request form</a>.
                            </li>
                            <li>
                                Second, a request for access to the respective Zenodo repositories where the data are hosted is required, one for each split/part.
                                Due to Zenodo's quota limitations, the dataset is split into eight (8) repositories grouped in resolutions and splits/parts as follows:
                              <ol>
                                <li>`1024 x 512` Resolution
                                    <ul>
                                      <li>Matterport3D Train & Test</li>
                                      <li>GibsonV2 Full (<b>w/o normals</b>)</li>
                                      <li>GibsonV2 Tiny, Medium & Fullplus (<b>w/o normals</b>)</li>
                                      <li>GibsonV2 Full <b>normals only</b></li>
                                      <li>GibsonV2 Tiny, Medium & Fullplus <b>normals only</b></li>
                                  </ul>
                                </li>
                                <li>`512 x 256` Resolution
                                    <ul>
                                      <li>Matterport3D Train & Test</li>
                                      <li>GibsonV2 Full</li>
                                      <li>GibsonV2 Tiny, Medium & Fullplus</li>
                                  </ul>
                                </li>
                              </ol>
                               
                            </li>
                        </ol>
                        Therefore, a separate request for access needs to be made to each repository in order to download 
                                the corresponding data. 
</p>
<p style="text-align: justify;">
  <b>Note</b> that only completing one step of the two (<i>i.e.</i> only filling out the form, or only requesting access from the Zenodo repositories <b>will not</b> be enough to get access to the data. We will do our best to contact you in such cases and notify you to complete all steps as needed, but our mails may be lost (e.g. spam filters/folders). 
  The only exception to this, is if you have already filled in the form and need access to another Zenodo repository (for example you need extra viewpoint renders which are hosted on different Zenodo repositories), then you only need to fill in the Zenodo request but please, make sure to mention that the form has already been filled in so that we can verify it.
</p>

<p style="text-align: justify;">
Each volume is broken down in several <code>.zip</code> files (2GB each) for more convinient downloading on low bandwidth connections. You need all the <code>.zip</code> archives of each volume in order to extract the containing files, recommendably with <a href="https://www.7-zip.org/">7zip's GUI</a>.
</p>

 <h2> Data splits </h2>
 We follow the same data-split logic as defined in Matterport3D. 
 The GV2 subgroups are used as distinct splits with only the full variant used for training.

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
 <br>

 <a href="https://atlantis-ar.eu/"><img align="middle" src="../assets/images/atlantis_logo.png" alt="atlantis" width="75%" ></a><img src="../assets/images/eu_logo.png" alt="eu" width="25%" class="center">
