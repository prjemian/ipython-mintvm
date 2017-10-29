print(__file__)

# Bluesky plans (scans)

from bluesky.utils import Msg, separate_devices


def tune_centroid(
        detectors, signal, motor, 
        start, stop, min_step, 
        num_points = 10, 
        step_factor = 2,
        snake = False,
        *, md=None):
    """
    plan: tune a motor to the centroid of signal(motor)
    
    Initially, traverse the range from start to stop with
    the number of points specified.  Repeat with progressively
    smaller step size until the minimum step size is reached.
    Rescans will be centered on the signal centroid
    (for $I(x)$, centroid$= \sum{I}/\sum{x*I}$)
    with a scan range of 2*step_factor*step of current scan.
    
    Set `snake=True` if your positions are reproducible
    moving from either direction.  This will not necessarily
    decrease the number of steps required to reach convergence.
    Snake motion reduces the total time spent on motion
    to reset the positioner.  For some positioners, such as 
    those with hysteresis, snake scanning may not be appropriate.  
    For such positioners, always approach the positions from the 
    same direction.

    Parameters
    ----------
    detectors : Signal
        list of 'readable' objects
    signal : string
        detector field whose output is to maximize
    motor : object
        any 'setable' object (motor, temp controller, etc.)
    start : float
        start of range
    stop : float
        end of range, note: start < stop
    min_step : float
        smallest step size to use.
        note: For EpicsMotors, ``min_step=min(min_step,motor.MRES)``
        is used.
    num_points : int, optional
        number of points with each step size, default = 10
    step_factor : float, optional
        used in calculating range when 
        maximum is found, note: step_factor > 0, default = 2
    snake : bool, optional
        if False (default), always scan from start to stop

    Example
    -------
    motor = Mover('motor', {'motor': lambda x: x}, {'x': 0})
    det = SynGauss('det', motor, 'motor', center=-1.3, Imax=1e5, sigma=0.021)
    RE(tune_centroid([det], "det", motor, -1.5, -0.5, 0.01, 10))

    m1 = EpicsMotor('xxx:m1', name='m1')
    synthetic_pseudovoigt = SynPseudoVoigt(
            'synthetic_pseudovoigt', m1, 'm1',
            center=-1.5 + 0.5*np.random.uniform(),
            eta=0.3 + 0.5*np.random.uniform(),
            sigma=0.001 + 0.05*np.random.uniform(),
            scale=1e5)
    RE(
        tune_centroid(
            [synthetic_pseudovoigt], "synthetic_pseudovoigt", 
            motor, 
            -2, 0, 0.001, 10
        )
    )
    """
    if step_factor <= 0:
        raise ValueError("step_factor must be positive")
    if (num_points - 1) <= 2*step_factor:
        raise ValueError(
            "Increase num_points and/or decrease step_factor"
            " or tune_centroid will never converge to a solution"
        )
    if isinstance(motor, EpicsMotor):
        min_step = max(min_step, epics.caget(motor.prefix+".MRES"))
    try:
        motor_name, = motor.hints['fields']
    except (AttributeError, ValueError):
        motor_name = motor.name
    _md = {'detectors': [det.name for det in detectors],
           'motors': [motor_name],
           'plan_args': {'detectors': list(map(repr, detectors)),
                         'motor': repr(motor),
                         'start': start,
                         'stop': stop,
                         'num_points': num_points,
                         'min_step': min_step,},
           'plan_name': 'tune_centroid',
           'hints': {},
          }
    _md.update(md or {})
    try:
        dimensions = [(motor.hints['fields'], 'primary')]
    except (AttributeError, KeyError):
        pass
    else:
        _md['hints'].setdefault('dimensions', dimensions)

    @bp.stage_decorator(list(detectors) + [motor])
    @bp.run_decorator(md=_md)
    def _tune_core(start, stop, num_points, signal):
        next_pos = start
        step = (stop - start) / (num_points - 1)
        peak_position = None
        cur_I = None
        cur_det = {}
        sum_I = 0       # for peak centroid calculation, I(x)
        sum_xI = 0

        while abs(step) >= min_step:
            yield Msg('checkpoint')
            yield from bp.mv(motor, next_pos)
            #yield Msg('create', None, name='primary')
            #for det in detectors:
            #    yield Msg('trigger', det, group='B')
            #yield Msg('wait', None, 'B')
            #for det in separate_devices(detectors + [motor]):
            #    cur_det = yield Msg('read', det)
            #    if signal in cur_det:
            #        cur_I = cur_det[signal]['value']
            #        sum_I += cur_I
            #        position = motor.read()[motor_name]["value"]
            #        sum_xI += position * cur_I
            #yield Msg('save')

            ret = (yield from bp.trigger_and_read(detectors + [motor]))
            cur_I = ret[signal]['value']
            sum_I += cur_I
            position = ret[motor_name]['value']
            sum_xI += position * cur_I

            if (stop - start) < abs(stop - start):
                in_range = start >= next_pos >= stop  # negative motion
            else:
                in_range = start <= next_pos <= stop  # positive motion
            
            if in_range:
                next_pos += step
            else:
                if sum_I == 0:
                    return
                peak_position = sum_xI / sum_I  # centroid
                # TODO: report current peak_position in metadata
                RE.md["peak_position"] = str(peak_position)
                start = peak_position - step_factor*step
                stop = peak_position + step_factor*step
                if snake:
                    start, stop = stop, start
                step = (stop - start) / (num_points - 1)
                next_pos = start

        # finally, move to peak position
        if peak_position is not None:
            RE.md["peak_position"] = peak_position
            yield from bp.mv(motor, peak_position)

    results = (yield from _tune_core(start, stop, num_points, signal))
    print("Peak at ", motor.read()[motor_name]['value'])
    return results


if False:       # demo & testing code
    simulate_peak(calc1, m1, profile="lorentzian")
    RE(tune_centroid([noisy], "noisy", m1, -2, 0, 0.00001, 10))
    
    RE(
        tune_centroid(
            [synthetic_pseudovoigt], "synthetic_pseudovoigt", m1, 
            -2, 0, 0.00001, 10
        )
    )
    RE(
        bp.adaptive_scan(
            [synthetic_pseudovoigt], 'synthetic_pseudovoigt', m1, 
            start=-2, stop=0, min_step=0.01, max_step=1, 
            target_delta=500, backstep=True
        )
    )
