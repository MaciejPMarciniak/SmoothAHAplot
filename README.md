# Smooth 17 and 18 segment AHA bullseye plots
When assessing the function of the left ventricle (LV), American Society of Echocardiography and European Association of 
Cardiovascular Imaging recommends the segmentation of the LV into 16, 17 or 18 elements:

* The left ventricle is divided into equal thirds perpendicular to the long axis of the heart. This generates three 
circular sections of the left ventricle named basal, mid-cavity, and apical. Only slices containing myocardium 
in all 360° are included.
* The basal part is divided into six segments of 60° each. The segment nomenclature along the circumference is: 
basal anterior, basal anteroseptal, basal inferoseptal, basal inferior, basal inferolateral, and basal anterolateral. 
The attachment of the right ventricular wall to the left ventricle can be used to identify the septum.
* Similarly the mid-cavity part is divided into six 60° segments called mid anterior, mid anteroseptal, 
mid inferoseptal, mid inferior, mid inferolateral, and mid anterolateral.
* In case of 17 segments:
    * Only four segments of 90° each are used for the apex because of the myocardial tapering. The segment names are 
apical anterior, apical septal, apical inferior, and apical lateral.
    * The apical cap represents the true muscle at the extreme tip of the ventricle where there is no longer cavity present.
 This segment is called the apex.
* In case of 18 segments, the apical part is also divided into six 60° segments called apical anterior, apical 
anteroseptal, apical inferoseptal, apical inferior, apical inferolateral, and apical anterolateral.
 
Using novel techonlogies and software, it is 
now possible to calculate the segmental values of the relevant parameters, such as strain or myocardial work.


In this project, the segmental values are visualized using the 17 and 18 segment bullseye plots, to provide insights
into the function of the LV in a palpable way. Proposed plots are smoothed, to increase the readability and enhance the
value of the provided medical data. Examples of strain and myocardial work (with random, probable values) are provided. 
The plots can be generated in two versions: as described in the recommendations, and as provided within the EchoPAC 
software (GE, Horten, Norway).

# Motivation
### Left Ventricle Segmentation Procedure

The muscle and cavity of the left ventricle can be divided into a variable number of segments. Based on autopsy data 
the AHA recommends a division into 17 or 18 segments for the regional analysis of left ventricular function or 
myocardial perfusion. These segmentation schemes result in segments with comparable myocardial mass, which are
also related (with some varibility) to the coronary perfusion. The proposed segmentations enable standardized 
communication within echocardiography and across other imaging modalities.

---
# Screenshots
## 17 AHA plot of Myocardial Work
![smooth plots](images/17_AHA_MW.png "17 AHA plot of Myocardial Work")

## Myocardial Work - EchoPAC version
![smooth plots](images/17_AHA_Echo_MW.png "Myocardial Work - Echopac version")

## 17 AHA plot of Segmental Strain
![smooth plots](images/17_AHA_strain.png "17 AHA plot of Segmental Strain")

## Segmental Strain - EchoPAC version
![smooth plots](images/17_AHA_Echo_strain.png "Segmental Strain - Echopac version")

---
# How2use

### class

**Call**
```python
```

---
**Input**

---
**Output** 

---
**Methods**


# Credits
Abstract

---
# License
