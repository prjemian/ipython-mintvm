print(__file__)

# see: https://github.com/stuwilkins/nsls-ii-tools/blob/add_csx_config/nsls2tools/csx1/startup/tardis.py
# see: https://github.com/NSLS-II-CSX/xf23id1_profiles/blob/master/profile_collection/startup/98-tardis-mu.py
# see: https://github.com/sardana-org/sardana/blob/develop/doc/source/sep/SEP4.md
# see: https://github.com/sardana-org/sardana/blob/develop/doc/source/index.rst
# see: https://github.com/sardana-org/sardana/blob/develop/doc/source/users/spock.rst
# see: https://github.com/sardana-org/sardana/blob/develop/doc/source/sep/SEP4.md
# e4c (fourc) see: https://github.com/picca/hkl/blob/next/Documentation/sphinx/source/diffractometers/e4cv.rst
# e6c (sixc) see: https://github.com/picca/hkl/blob/next/Documentation/sphinx/source/diffractometers/e6c.rst
# k6c see: https://github.com/picca/hkl/blob/next/Documentation/sphinx/source/diffractometers/k6c.rst
# see: https://github.com/picca/hkl/blob/next/Documentation/sphinx/source/diffractometers/soleil_sirius_kappa.rst
# see: https://github.com/picca/hkl/blob/next/Documentation/sphinx/source/
# see: https://github.com/picca/hkl/blob/next/Documentation/sphinx/source/bindings/bindings.rst
# see: https://github.com/picca/hkl/blob/next/Documentation/sphinx/source/introduction.rst (half-English, half-French)


from ophyd import (PseudoSingle, EpicsMotor, SoftPositioner, Signal)
import gi
gi.require_version('Hkl', '5.0')
from hkl.diffract import E6C, E4CH, E4CV
from ophyd.pseudopos import (pseudo_position_argument, real_position_argument)
