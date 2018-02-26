print(__file__)

"""
work out the per-axis tuning support
"""

from ophyd.sim import motor1, motor2, motor3
from ophyd.sim import det1, det2 
from bluesky.callbacks.fitting import PeakStats
from ophyd.sim import SynGauss
from ophyd.sim import SynAxis

append_wa_motor_list(motor1, motor2, motor3)


# this code will go into APS_BlueSky_tools.devices
#------------------------------------------------------

class AxisTunerException(ValueError): 
    """Exception during execution of `AxisTunerBase` subclass"""
    pass


class AxisTunerBase(object):
    """
    base class for AxisTuner implementations

    .. autosummary::
       
        ~tune
        ~peak_detected
        ~get_param
        ~set_params

    """
    axis = None
    det = None
    params = dict()         # terms needed by the `tune()` method
    pretune_position = None # position before `tune()` is called
    ok = False              # was `tune()` successful? 
    tune_position = None    # position to use if self.ok

    def tune(self, md={}, **kwargs):
        raise NotImplementedError("must define in subclass")

    def peak_detected(self, *args, **kwargs):
        raise NotImplementedError("must define in subclass")

    def get_param(self, key):
        """get tuner parameter by keyword"""
        if key == "axis":
            return self.axis
        elif key == "det":
            return self.det
        return self.params[key]

    def set_params(self, **kwargs):
        """
        set tuner parameters by keyword
        """
        for key, value in kwargs.items():
            if key == "axis":
                self.axis = value
            elif key == "det":
                self.det = value
            elif key in self.params:
                # only accept known keys
                # each tuner will define all recognized members of self.params
                self.params[key] = value
            else:
                msg = "{} = {}".format(key, value)
                raise KeyError(msg)


class PeakAxisTuner(AxisTunerBase):
    """
    scan y v. x, then set x = x@max(y), iff max(y) >= 4*min(y), raise `AxisTunerException` as needed
    """
    # implement algorithm from SPEC here (tune to signal peak)
    # see example: https://github.com/prjemian/ipython_ookhd/blob/master/profile_bluesky/startup/11-bs_sim_motors.py#L29
    params = dict(
        start = -1,
        finish = 1,
        num = 11,
        time_s = 1
        )
    std_stage_sigs = OrderedDict()
    tune_stage_sigs = OrderedDict()     # contents defined by caller
    peak_stats = None

    def tune(self, start=None, finish=None, num=None, time_s=None, md=None):
        """
        tune this axis with the named detector in a single pass
        
        uses `bp.rel_scan()` and `PeakStats`
        
        PARAMETERS
        det : obj
            detector object (must be provided on first use)
        start : float
            axis starting position *relative* to pretune axis position
        finish : float
            axis ending position *relative* to pretune axis position
        num : int
            number of points (number of steps + 1)
        time_s : float
            counting time (s) at each step
        md : dict
            scan metadata dictionary
        
        RAISES
        
            `AxisTunerException` if cannot tune

        """
        if self.axis is None:
            msg = "Must define an axis, none specified."
            raise AxisTunerException(msg)
        
        if self.det is None:
            msg = "Must define a detector, none specified."
            raise AxisTunerException(msg)
        
        self.params["start"] = start or self.params["start"]
        self.params["finish"] = finish or self.params["finish"]
        self.params["num"] = num or self.params["num"]
        self.params["time_s"] = time_s or self.params["time_s"]
        self.pretune_position = self.axis.position
        
        # additional metadata
        if md is None:
            md = OrderedDict()
        
        sub_md = OrderedDict()
        sub_md["name"] = "PeakAxisTuner.tune"
        sub_md["det"] = self.det.name
        sub_md["axis"] = self.axis.name
        for k, v in self.params.items():
            sub_md[k] = v
        sub_md["pretune_position"] = self.pretune_position
        md["tuner"] = sub_md

        # additional staging for tuning
        # use a class attribute as fallback in case restore is missed
        self.std_stage_sigs = self.axis.stage_sigs
        self.axis.stage_sigs.update(self.tune_stage_sigs)

        # stage the counting time
        det_time = self.params["time_s"]    # RHS should be current detector counting time
        if False:
            # TODO: stage or set?
            yield from bps.mv(self.det.exposure_time, self.params["time_s"])  # FIXME: fails
        
        # prepare to get pl_MAX, pl_MIN, and PL_COM
        self.peak_stats = PeakStats(x=self.axis.name, y=self.det.name)
        
        yield from bpp.subs_wrapper(
            bp.rel_scan(
                [self.det], 
                self.axis, 
                self.params["start"], 
                self.params["finish"], 
                self.params["num"], 
                md=md),
            self.peak_stats
        )

        # restore standard staging
        self.axis.stage_sigs = self.std_stage_sigs
        self.params["time_s"] = det_time
        
        if self.peak_detected(peak_stats=self.peak_stats):
            self.ok = True
            self.tune_position = self.peak_stats.cen
            yield from bps.mv(self.axis, self.tune_position)
        else:
            self.ok = False
            self.tune_position = None
            yield from bps.mv(self.axis, self.pretune_position)
            msg = "tune {} v. {}: no tunable peak found"
            raise AxisTunerException(msg.format(self.det.name, self.axis.name))

    def peak_detected(self, peak_stats=None):
        """
        returns True if a peak was detected, otherwise False
        
        detected means:
            There must be a maximum in Y and it must be 4* the minimum Y.
        
        Parameters
        
        peak_stats : obj
            Instance of bluesky.callbacks.fitting.PeakStats()
            with data from tuning scan.
        
        The default algorithm identifies a peak when the maximum
        value is four times the minimum value.  Change this routine
        by subclassing :class:`TuneAxis` and override :meth:`peak_detected`.
        """
        if peak_stats is None:
            return False
        peak_stats.compute()
        if peak_stats.max is None:
            return False
        
        ymax = peak_stats.max[-1]
        ymin = peak_stats.min[-1]
        return ymax > 4*ymin        # this works for USAXS


class AxisTunerMixin(object):
    """
    docstring needed
    
    USAGE::
    
        class myTunableAxis(EpicsMotor, AxisTunerMixin):
            pass
        
        a2r = myTunableAxis("xxx:m1", name="a2r")
        a2r.tuner.config(det=det1, start=-0.01, finish=0.01, num=21, time=0.2)
        RE(a2r.tune())
        
        def tune_usaxs():
            # tune four of the USAXS axes
            yield from mr.tune()
            yield from m2r.tune()
            yield from ar.tune()
            yield from a2r.tune()

        RE(tune_usaxs())

    Hook functions
    
    There are two hook functions (`pre_tune_function()`, and `post_tune_function()`)
    for callers to add additional plan parts, such as opening or closing shutters, 
    setting detector parameters, or other actions.
    
    Each hook function must accept one argument: 
    axis object such as `EpicsMotor` or `SynAxis`,
    such as::
    
        def my_pre_tune_hook(axis):
            yield from bps.mv(shutter, "open")
        def my_post_tune_hook(axis):
            yield from bps.mv(shutter, "close")
        
        class myAxis(SynAxis, AxisTunerMixin):
            pass

        myaxis = myAxis(name="myaxis")
        mydet = SynGauss('mydet', myaxis, 'myaxis', center=0.21, Imax=0.98e5, sigma=0.127)
        
        myaxis.pre_tune_function = my_pre_tune_hook
        myaxis.post_tune_function = my_post_tune_hook
        myaxis.tuner.set_params(axis=myaxis, det=mydet, num=81)
        
        RE(myaxis.tune())

    """

    tuner = PeakAxisTuner()
    
    # Hook functions for callers to add additional plan parts
    # Each must accept one argument: axis object such as `EpicsMotor` or `SynAxis`
    pre_tune_function = None        # called before `tune()`
    post_tune_function = None       # called after `tune()`

    # Mixin MUST not provide __init__() method, instead use self.tuner.config()
    
    def tune(self, md=None, **kwargs):
        if self.tuner.axis is None:
            msg = "Must define an axis, none specified."
            raise AxisTunerException(msg)
        
        if self.tuner.det is None:
            msg = "Must define a detector, none specified."
            raise AxisTunerException(msg)

        if md is None:
            md = OrderedDict()
        md["purpose"] = "tuner"
        md["datetime"] = str(datetime.now())

        if self.pre_tune_function is not None:
            self.pre_tune_function(self)

        # TODO: prep
        if self.tuner is not None:
            yield from self.tuner.tune(md=md, **kwargs)
        # TODO: restore

        if self.post_tune_function is not None:
            self.post_tune_function(self)


#------------------------------------------------------


def my_pre_tune_hook(axis):
    print("#"*40 + " my_pre_tune_hook")
def my_post_tune_hook(axis):
    print("#"*40 + " my_post_tune_hook")

class myAxis(SynAxis, AxisTunerMixin):
    pass


myaxis = myAxis(name="myaxis")
mydet = SynGauss('mydet', myaxis, 'myaxis', center=0.21, Imax=0.98e5, sigma=0.127)

myaxis.pre_tune_function = my_pre_tune_hook
myaxis.post_tune_function = my_post_tune_hook
myaxis.tuner.set_params(axis=myaxis, det=mydet, num=71)
