# covert-scope-jobs
Run tifconvert.sh.  
tiffix.py extracts metadata and performs shading correction on images.

When you collect a new reference for shading correction, push it to `data/`.


## Data Flow
The scope compter uploads new tif files to ResearchNAS every 2 hours. The list of uploaded files is appended to `robocopy.log`.


This program first reads `robocopy.log`, extract a list of tif files as `tifffiles.txt` and remove the `robocopy.log`.

Each image in tifffiles.txt goes through `tiffix.py` for the following process.
- shading correction if there is a proper reference for the corresponding channel, magnification and binning.
- tif compression.


#### TODO: 
- truncate to the odd size image to even size.
- make metadata compatible with imageJ `Show Info`
- logs for tifconvert.sh
- collect more shading correction references.
- write a function for estimating the reference from 1x1 binning image if 2-4 binning does not exist (imresize?)
- (extract time points?)



