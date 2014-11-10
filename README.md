# Pl
Taking the "OO" out of Pool.

## Install instructions

Download the pygame2d source from https://code.google.com/p/pybox2d/ and unzip. 
Change velocity_threshold in Box2d/Common/b2_setting.h to 0.0f.
Run `python setup.py build` then `sudo python setup.py install --force` in the Box2d-* dir.
You're all good! (yay)