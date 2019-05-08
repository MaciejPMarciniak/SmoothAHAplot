# Building population data from individual cases
Statistical models rely on the sets of samples to infer the behaviour of similar samples, classifiy them and build
predictions based on them. In general, the more samples are gathered, the more robust and reliable the model is and more
features of a sample can be explored. This project builds a data set from individual samples, to provide the user with 
a tidy, easily applicable set to explore, and hypothesize.

In explicit, from a number of raw .xml files exported from the EchoPAC software, a single table is generated. With cases
as rows and features as columns, it is in good shape to be used for quick analysis with modules such as pandas, 
scikit-learn or matplotlib, as well as off-the-shelf statistical tools.

Among the features there are strain measurements and myocardial work indices for available triplane views, as well as 
global indices and basic patient data (valve opening times, blood pressure, ejection fraction). In addition to the raw
indices, processed features are included, such as the post-systolic index and frame rate, to provide the user with 
information relevant for results publication. 

# Motivation


# Screenshots
Examples of differences in septal curvature among 3 patients: healthy, hypertensive and hypertensive with septal bulge:
![curvature examples](images/Curvature_healthy_htn_bsh.png "Curvature differences among patient groups")

# How2use

### class Cohort (bsh.py)

**Call**
```python
class Cohort(source_path='path_to_data', view='4C', output_path='path_to_store_results', 
output='name_of_output_file.csv')
```

**Input**

*source_path*: path to the .csv files containing the myocardial trace obtained with speckle tracing in EchoPAC. 
 

*view*: the view in which the image was taken; 4-chamber ('4C'), 3-chamber ('3C'), or 2-chamber ('2C') 

 
*output_path*: path to a folder where the results of computation and plots will be stored 

 
**Output** 


---
**Methods**


# Credits
Abstract

# License