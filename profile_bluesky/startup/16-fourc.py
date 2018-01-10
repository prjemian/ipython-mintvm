print(__file__)

"""
setup a fourc 4-circle diffractometer

see: https://github.com/picca/hkl/blob/next/Documentation/sphinx/source/diffractometers/e4cv.rst
"""

import bluesky.magics
from hkl.util import Lattice


MOTOR_PV_OMEGA = "prj:m9"
MOTOR_PV_CHI = "prj:m10"
MOTOR_PV_PHI = "prj:m11"
MOTOR_PV_TTH = "prj:m12"


class Fourc(E4CV):
    h = Cpt(PseudoSingle, '')
    k = Cpt(PseudoSingle, '')
    l = Cpt(PseudoSingle, '')

    omega = Cpt(EpicsMotor, MOTOR_PV_OMEGA)
    chi =   Cpt(EpicsMotor, MOTOR_PV_CHI)
    phi =   Cpt(EpicsMotor, MOTOR_PV_PHI)
    tth =   Cpt(EpicsMotor, MOTOR_PV_TTH)


fourc = Fourc('', name='fourc')
fourc.calc.engine.mode = 'bissector'    # constrain tth = 2 * omega

mn3o4_lattice = Lattice(
            a=5.72, b=5.72, c=9.5, 
            alpha=90.0, beta=90.0, gamma=90.0)
mgo_lattice = Lattice(
            a=4.2112, b=4.2112, c=4.2112, 
            alpha=90.0, beta=90.0, gamma=90.0)

def fourc_example():
    """
    epitaxial thin film of Mn3O4 on MgO substrate
    
    see: http://www.rigaku.com/downloads/journal/Vol16.1.1999/cguide.pdf
    """
    
    BlueskyMagics.positioners += list(fourc.real_positioners)
    BlueskyMagics.positioners += list(fourc.pseudo_positioners)
    
    fourc.calc.new_sample('Mn3O4 thin film', mn3o4_lattice)
    
    # define the wavelength (angstrom)
    fourc.calc.wavelength = 1.5418   # Cu Kalpha
    
    r1 = fourc.calc.sample.add_reflection(
        -1.998, -1.994, 4.011,
        position=fourc.calc.Position(
            tth=60.0324, omega=29.9988, chi=-48.962, phi=-88.824))
    r2 = fourc.calc.sample.add_reflection(
        -0.009, -0.007, 4,
        position=fourc.calc.Position(
            tth=37.8482, omega=19.1174, chi=0.3980, phi=-121.717))
    fourc.calc.sample.compute_UB(r1, r2)
    
    print(fourc.calc.forward((0, 0, 8)))
    print(fourc.calc.forward((-2, -2, 4)))
    print("Where all?")
    wa
    # print("(hkl) now=", fourc.position)
    # print("motors now=", fourc.real_position)
    print("motors at (-2 -2 4)", fourc.calc.forward((-2, -2, 4)))
    print("motors at (-2 1 1)", fourc.calc.forward((-2, 1, 1)))
    print("motors at (-3 0 5)", fourc.calc.forward((-3, 0, 5)))
    
    fourc.move(0, 3, 1)

    scaler.channels.read_attrs = ['chan1', 'chan2', 'chan3', 'chan6']
    RE(bp.scan([scaler, fourc.h, fourc.k, fourc.l, ], fourc.l, 0.5, 1.5, 11))
    
    # TODO: test the UB against known & expected reflections


    
    fourc.calc.new_sample('MgO substrate', mgo_lattice)
    
    # define the wavelength (angstrom)
    fourc.calc.wavelength = 1.5418   # Cu Kalpha
    
    r1 = fourc.calc.sample.add_reflection(
        0.019, -0.009, 2,
        position=fourc.calc.Position(
            tth=42.9149, omega=21.5175, chi=0.786, phi=-166.717))
    r2 = fourc.calc.sample.add_reflection(
        -1.982, -2.009, 2.009,
        position=fourc.calc.Position(
            tth=78.6327, omega=39.3029, chi=-54.127, phi=-133.8))
    fourc.calc.sample.compute_UB(r1, r2)
    
    print("Where all?")
    wa
    
    fourc.calc.forward((0, -2, 2))
    fourc.move(0, -2, 2)

    scaler.channels.read_attrs = ['chan1', 'chan2', 'chan3', 'chan6']
    RE(bp.scan([scaler, fourc.h, fourc.k, fourc.l, ], fourc.l, 0.5, 1.5, 11))
    
    # TODO: test the UB against known & expected 
