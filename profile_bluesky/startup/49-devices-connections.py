print(__file__)


def simulate_peak(swait, motor, profile=None, start=-1.5, stop=-0.5):
    if profile is not None:
        simulator = dict(
            gaussian = swait_setup_gaussian,
            lorentzian = swait_setup_lorentzian,
        )[profile]
        kw = dict(
            center = start + np.random.uniform()*(stop-start), 
            width = 0.002 + 0.1*np.random.uniform(), 
            scale = 100000 * np.random.uniform(), 
            noise = 0.05 + 0.1*np.random.uniform())
        simulator(swait, motor, **kw)
    else:
        swait_setup_random_number(swait)

def both_peaks(calc=None, dets=None, motor=None):
    calc = calc or calc1
    dets = dets or [noisy,]
    motor = motor or m1
    start, stop = -1.5, -0.5
    simulate_peak(calc, motor, profile="gaussian")
    yield from bp.scan(dets, motor, start, stop, 219)
    simulate_peak(calc, motor, profile="lorentzian")
    yield from bp.scan(dets, motor, start, stop, 219)
