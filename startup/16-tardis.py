print(__file__)

"""
setup the tardis 6-circle diffractometer

Direct copy from NSLS-II CSX Tardis 6-circle setup

https://github.com/NSLS-II-CSX/xf23id1_profiles/blob/master/profile_collection/startup/98-tardis-mu.py

"""


MOTOR_PV_MU = "prj:m3"
MOTOR_PV_MUR = "prj:m4"     # instead of omega
#MOTOR_PV_OMEGA = "prj:m4"
MOTOR_PV_GAMMA = "prj:m5"
MOTOR_PV_DELTA = "prj:m6"


muR = EpicsMotor(MOTOR_PV_MUR, name='muR')


class Tardis(E6C):
    h = Cpt(PseudoSingle, '')
    k = Cpt(PseudoSingle, '')
    l = Cpt(PseudoSingle, '')

    mu    = Cpt(EpicsMotor, MOTOR_PV_MU)
    omega = Cpt(NullMotor)
    #omega = Cpt(EpicsSignal,'prj:m4.RBV')
    chi =   Cpt(NullMotor)
    phi =   Cpt(NullMotor)
    gamma = Cpt(EpicsMotor, MOTOR_PV_GAMMA)
    delta = Cpt(EpicsMotor, MOTOR_PV_DELTA)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # prime the 3 null-motors with initial values
        # otherwise, position == None --> describe, etc gets borked
        self.omega.move(muR.user_readback.value)
        self.chi.move(0.0)
        self.phi.move(0.0)

    @pseudo_position_argument
    def set(self, position):
        return super().set([float(_) for _ in position])


tardis = Tardis('', name='tardis')

# re-map Tardis' axis names onto what an E6C expects
tardis.calc.physical_axis_names = {
    # Tardis : E6C
    'mu': 'theta', 
    'omega': 'omega', 
    'chi': 'chi', 
    'phi': 'phi', 
    'gamma': 'delta', 
    'delta': 'gamma'
}

tardis.calc.engine.mode = 'lifting_detector_mu'

# from this point, we can configure the Tardis instance
from hkl.util import Lattice


# apply some constraints

tardis_constraints = {
    # axis: [limits, value, fit]
    "theta": [(-181, 181), 0, True],
    
    # we don't have these axes. Fix them to 0
    "phi": [(0, 0), 0, False],
    "chi": [(0, 0), 0, False],
    "omega": [(0, 0), 0, False],    #tardis.omega.position.real
    
    # Attention naming convention inverted at the detector stages!
    "delta": [(-5, 180), 0, True],
    "gamma": [(-5, 180), 0, True],
}
for axis, constraints in tardis_constraints.items():
    limits, value, fit = constraints
    tardis.calc[axis].limits = limits
    tardis.calc[axis].value = value
    tardis.calc[axis].fit = fit



"""
See https://github.com/NSLS-II/hklpy/tree/master/examples
for jupyter notebooks with tardis in the E6C geometry.

add a sample to the calculation engine (lengths are 
in angstroms, angles are in degrees)::

    tardis.calc.new_sample('esrf_sample', 
        lattice=Lattice(
            a=9.069, b=9.069, c=10.390, 
            alpha=90.0, beta=90.0, gamma=120.0))

define the wavelength (angstrom)::

    tardis.calc.wavelength = 1.61198


alternatively, set the energy on the Tardis instance::

    # tardis.energy.put(12.3984244 / 1.61198)


test computed real positions against the table below

===========  ==========  == == == ======== ======== ===  ===  =====  =========
basis        wavelength  h  k  l  delta    theta    chi  phi  omega  gamma
===========  ==========  == == == ======== ======== ===  ===  =====  =========
known        1.61198     3  3  0  64.449   25.285   0    0    0      -0.871
known        1.61198     5  2  0  79.712   46.816   0    0    0      -1.374
experiment   1.61198     4  4  0  90.628   38.373   0    0    0      -1.156
experiment   1.61198     4  1  0  56.100   40.220   0    0    0      -1.091
experiment   1.60911     6  0  0  75.900   61.000   0    0    0      -1.637
experiment   1.60954     3  2  0  53.090   26.144   0    0    0      -.933
experiment   1.60954     5  4  0  106.415  49.900   0    0    0      -1.535
experiment   1.60954     4  5  0  106.403  42.586   0    0    0      -1.183
===========  ==========  == == == ======== ======== ===  ===  =====  =========


Orient the sample on the diffractometer (set up the UB matrix)::

    r1 = tardis.calc.sample.add_reflection(
        3, 3, 0,
        position=tardis.calc.Position(
            delta=64.449, theta=25.285, 
            chi=0.0, phi=0.0, omega=0.0, 
            gamma=-0.871))
    r2 = tardis.calc.sample.add_reflection(
        5, 2, 0,
        position=tardis.calc.Position(
            delta=79.712, theta=46.816, 
            chi=0.0, phi=0.0, omega=0.0, 
            gamma=-1.374))
    tardis.calc.sample.compute_UB(r1, r2)

Test the orientation::

    print(tardis.calc.forward((4,4,0)))
    print(tardis.calc.forward((4,1,0)))
    print("(hkl) now=", tardis.position)
    print("motors now=", tardis.real_position)
    print("motors at (330)", tardis.calc.forward((3, 3, 0)))
    print("motors at (520)", tardis.calc.forward((5, 2, 0)))

Move to (hkl) (note: the first solution if multiple are found)::

    tardis.move(3, 3, 0)

Scan by mu::

    RE(bp.scan([scaler, tardis.h, tardis.k, tardis.l, ], tardis.mu, 5, 35, 51))

Scan by h::

    RE(bp.scan([scaler, tardis.h, tardis.k, tardis.l, ], tardis.h, 3, 5, 11))


    >>> wa(list(tardis.real_positioners) + list(tardis.pseudo_positioners))

"""
