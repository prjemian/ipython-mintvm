print(__file__)

"""
setup a fourc 4-circle diffractometer

see: https://github.com/picca/hkl/blob/next/Documentation/sphinx/source/diffractometers/e4cv.rst
"""

from hkl.util import Lattice
import bluesky.magics


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
    
    # ipython:
    # wa(list(fourc.real_positioners) + list(fourc.pseudo_positioners))


fourc = Fourc('', name='fourc')

fourc.calc.engine.mode = 'bissector'    # constrain tth = 2 * omega


def fourc_example():
    """
    epitaxial thin film of Mn3O4 on MgO substrate
    
    see: http://www.rigaku.com/downloads/journal/Vol16.1.1999/cguide.pdf
    """
    
    fourc.calc.new_sample('Mn3O4/MgO thin film', 
        lattice=Lattice(
            a=5.72, b=5.72, c=9.5, 
            alpha=90.0, beta=90.0, gamma=90.0))
    
    fourc.calc.wavelength = 12.3984244 / 8.04   # Cu Kalpha
    
    r1 = fourc.calc.sample.add_reflection(
        -1.998, -1.994, 4.011,
        position=fourc.calc.Position(
            tth=80.8769, omega=40.6148, chi=0.647, phi=-121.717))
    r2 = fourc.calc.sample.add_reflection(
        -0.997, -0.997, 2.009,
        position=fourc.calc.Position(
            tth=28.695, omega=14.4651, chi=-48.8860, phi=-88.758))
    fourc.calc.sample.compute_UB(r1, r2)
    
    print(fourc.calc.forward((0, 0, 8)))
    print(fourc.calc.forward((-2, -2, 4)))
    print("(hkl) now=", fourc.position)
    print("motors now=", fourc.real_position)
    print("motors at (-2 1 1)", fourc.calc.forward((-2, 1, 1)))
    print("motors at (-3 0 5)", fourc.calc.forward((-3, 0, 5)))
    
    fourc.move(0, 3, 1)

    scaler.channels.read_attrs = ['chan1', 'chan2', 'chan3', 'chan6']
    RE(bp.scan([scaler, fourc.h, fourc.k, fourc.l, ], fourc.l, 0.5, 1.5, 11))
    
    wa(list(fourc.real_positioners) + list(fourc.pseudo_positioners))
