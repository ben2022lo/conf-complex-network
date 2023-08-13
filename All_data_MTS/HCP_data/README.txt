The data of these folders include preprocessed data considering resting-state fMRI signals of the 100 unrelated subjects from the Human Connectome Project (HCP, http://www.humanconnectome.org/).

All the time series are in .mat format. Each time series has been processed using the preprocessing pipeling described in Enrico Amico's papers(i.e. https://www.science.org/doi/10.1126/sciadv.abj0751 ;  https://www.sciencedirect.com/science/article/pii/S1053811917300204?via%3Dihub).  This is just a standard general linear model (GLM) processing, which included: detrending, removal of motion regressors and their first derivatives, removal of WM, CSF signals and their first derivatives.
For each subject, there are four fMRI recordings that were acquired over 2 different days (REST1 and REST2), while  LR/RL refers to the left-right (LR) and right-left (RL) phase-encoding of the magnetic field during the scans.


In the Misc folder there are also information about:
- Subcortical_labels subfolder: the list of subcortical regions appended in the time series files: “Atlas_ROIs.2_LUT_ordered.txt”
- In the Cortical_labels subfolder: the label list for the parcellations provided (cortical regionsonly).
- In the YeoOrder folder: the yeo_RS7_* files, containing yeoOrder and yeoROIs matlab variables. yeoROIs: label assignment of the overlap between a specific Parcellation and Yeo 7 resting state networks (+ an 8th subcortical). YeoOrder: in case you want to visualize functional connectomes ordered according to the “7 Yeo resting-state networks” + 8 th subcortical

