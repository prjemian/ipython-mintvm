print(__file__)

"""
work out the per-axis tuning support
"""

from ophyd.sim import motor1, motor2, motor3
from ophyd.sim import det1, det2 
from bluesky.callbacks.fitting import PeakStats
from ophyd.sim import SynGauss
from ophyd.sim import SynAxis
from ophyd.sim import SynSignal
from ophyd import areadetector
from ophyd.device import BlueskyInterface
from APS_BlueSky_tools.plans import TuneAxis


append_wa_motor_list(motor1, motor2, motor3)


# this code will go into APS_BlueSky_tools.devices
#------------------------------------------------------


class AxisTunerException(ValueError): 
    """Exception during execution of `AxisTunerBase` subclass"""
    pass


# class AxisTunerBase(BlueskyInterface):
#     """
#     base class for AxisTuner implementations
# 
#     .. autosummary::
#        
#         ~tune
#         ~peak_detected
#         ~get_param
#         ~set_params
# 
#     """
#     
#     def __init__(self):
#         self.axis = None
#         self.det = None
#         self.params = dict()         # terms needed by the `tune()` method
#         self.pretune_position = None # position before `tune()` is called
#         self.ok = False              # was `tune()` successful? 
#         self.tune_position = None    # position to use if self.ok
# 
#     def tune(self, md={}, **kwargs):
#         raise NotImplementedError("must define in subclass")
# 
#     def peak_detected(self, *args, **kwargs):
#         raise NotImplementedError("must define in subclass")
# 
#     def get_param(self, key):
#         """get tuner parameter by keyword"""
#         if key == "axis":
#             return self.axis
#         elif key == "det":
#             return self.det
#         return self.params[key]
# 
#     def set_params(self, **kwargs):
#         """
#         set tuner parameters by keyword
#         """
#         for key, value in kwargs.items():
#             if key == "axis":
#                 self.axis = value
#             elif key == "det":
#                 self.det = value
#             elif key in self.params:
#                 # only accept known keys
#                 # each tuner will define all recognized members of self.params
#                 self.params[key] = value
#             else:
#                 msg = "{} = {}".format(key, value)
#                 raise KeyError(msg)


# class PeakAxisTuner(AxisTunerBase):
#     """
#     scan y v. x, then set x = x@max(y), iff max(y) >= 4*min(y), raise `AxisTunerException` as needed
#     """
#     
#     def __init__(self):
#         # self.
#         super().__init__() 
# 
#         # implement algorithm from SPEC here (tune to signal peak)
#         # see example: https://github.com/prjemian/ipython_ookhd/blob/master/profile_bluesky/startup/11-bs_sim_motors.py#L29
#         self.params = dict(
#             start = -1,
#             finish = 1,
#             num = 11,
#             time_s = 1
#             )
#         self.std_stage_sigs = OrderedDict()
#         self.tune_stage_sigs = OrderedDict()     # contents defined by caller
#         self.peak_stats = None
# 
#     def tune(self, start=None, finish=None, num=None, time_s=None, md=None):
#         """
#         tune this axis with the named detector in a single pass
#         
#         uses `bp.rel_scan()` and `PeakStats`
#         
#         PARAMETERS
#         det : obj
#             detector object (must be provided on first use)
#         start : float
#             axis starting position *relative* to pretune axis position
#         finish : float
#             axis ending position *relative* to pretune axis position
#         num : int
#             number of points (number of steps + 1)
#         time_s : float
#             counting time (s) at each step
#         md : dict
#             scan metadata dictionary
#         
#         RAISES
#         
#             `AxisTunerException` if cannot tune
# 
#         """
#         def set_detector_count_time(det_list, time_s):
#             """set detector counting time (s)"""
#             for det in det_list:
#                 if isinstance(det, SynSignal):
#                     det.exposure_time = time_s  # no stage_sigs here
#          
#                 elif isinstance(det, (EpicsScaler, ScalerCH)):
#                     det.stage_sigs["preset_time"] = time_s
#          
#                 elif isinstance(det, areadetector.DetectorBase):
#                     det.cam.stage_sigs["acquire_time"] = time_s
# 
#         if self.axis is None:
#             msg = "Must define an axis, none specified."
#             raise AxisTunerException(msg)
#         
#         if self.det is None:
#             msg = "Must define a detector, none specified."
#             raise AxisTunerException(msg)
#         
#         self.params["start"] = start or self.params["start"]
#         self.params["finish"] = finish or self.params["finish"]
#         self.params["num"] = num or self.params["num"]
#         self.params["time_s"] = time_s or self.params["time_s"]
#         self.pretune_position = self.axis.position
#         
#         # additional metadata
#         if md is None:
#             md = OrderedDict()
#         
#         sub_md = OrderedDict()
#         sub_md["name"] = "PeakAxisTuner.tune"
#         sub_md["det"] = self.det.name
#         sub_md["axis"] = self.axis.name
#         for k, v in self.params.items():
#             sub_md[k] = v
#         sub_md["pretune_position"] = self.pretune_position
#         md["tuner"] = sub_md
# 
#         # additional staging for tuning
#         # use a class attribute as fallback in case restore is missed
#         self.std_stage_sigs = self.axis.stage_sigs
#         self.axis.stage_sigs.update(self.tune_stage_sigs)
# 
#         set_detector_count_time([self.det], self.params["time_s"])
# 
#         # prepare to get pl_MAX, pl_MIN, and PL_COM
#         # TODO: allow to override signal names for complex devices such as swait record
#         self.peak_stats = PeakStats(x=self.axis.name, y=self.det.name)
#         
#         yield from bpp.subs_wrapper(
#             bp.rel_scan(
#                 [self.det], 
#                 self.axis, 
#                 self.params["start"], 
#                 self.params["finish"], 
#                 self.params["num"], 
#                 md=md),
#             self.peak_stats
#         )
# 
#         # restore standard staging
#         self.axis.stage_sigs = self.std_stage_sigs
#         # self.params["time_s"] = det_time
#         
#         if self.peak_detected(peak_stats=self.peak_stats):
#             self.ok = True
#             self.tune_position = self.peak_stats.cen
#             yield from bps.mv(self.axis, self.tune_position)
#         else:
#             self.ok = False
#             self.tune_position = None
#             yield from bps.mv(self.axis, self.pretune_position)
#             msg = "tune {} v. {}: no tunable peak found"
#             raise AxisTunerException(msg.format(self.det.name, self.axis.name))
# 
#     def peak_detected(self, peak_stats=None):
#         """
#         returns True if a peak was detected, otherwise False
#         
#         detected means:
#             There must be a maximum in Y and it must be 4* the minimum Y.
#         
#         Parameters
#         
#         peak_stats : obj
#             Instance of bluesky.callbacks.fitting.PeakStats()
#             with data from tuning scan.
#         
#         The default algorithm identifies a peak when the maximum
#         value is four times the minimum value.  Change this routine
#         by subclassing :class:`TuneAxis` and override :meth:`peak_detected`.
#         """
#         if peak_stats is None:
#             return False
#         peak_stats.compute()
#         if peak_stats.max is None:
#             return False
#         
#         ymax = peak_stats.max[-1]
#         ymin = peak_stats.min[-1]
#         return ymax > 4*ymin        # this works for USAXS


class AxisTunerMixin(object):
    """
    Mixin class to provide tuning capabilities for an axis
    
    USAGE::
    
        class TunableEpicsMotor(EpicsMotor, AxisTunerMixin):
            pass
        
        def a2r_pretune_hook():
            # set the counting time for *this* tune
            yield from bps.abs_set(scaler.preset_time, 0.2)
            
        a2r = TunableEpicsMotor("xxx:m1", name="a2r")
        a2r.tuner = TuneAxis([scaler], a2r, signal_name=scaler.channels.chan2.name)
        a2r.tuner.width = 0.02
        a2r.tuner.num = 21
        a2r.pre_tune_method = a2r_pretune_hook
        RE(a2r.tune())
        
        # tune four of the USAXS axes (using preconfigured parameters for each)
        RE(tune_axes([mr, m2r, ar, a2r])

    HOOK METHODS
    
    There are two hook methods (`pre_tune_method()`, and `post_tune_method()`)
    for callers to add additional plan parts, such as opening or closing shutters, 
    setting detector parameters, or other actions.
    
    Each hook method must accept one argument: 
    axis object such as `EpicsMotor` or `SynAxis`,
    such as::
    
        def my_pre_tune_hook(axis):
            yield from bps.mv(shutter, "open")
        def my_post_tune_hook(axis):
            yield from bps.mv(shutter, "close")
        
        class TunableSynAxis(SynAxis, AxisTunerMixin):
            pass

        myaxis = TunableSynAxis(name="myaxis")
        mydet = SynGauss('mydet', myaxis, 'myaxis', center=0.21, Imax=0.98e5, sigma=0.127)
        myaxis.tuner = TuneAxis([mydet], myaxis)
        myaxis.pre_tune_method = my_pre_tune_hook
        myaxis.post_tune_method = my_post_tune_hook
        
        RE(myaxis.tune())

    """
    
    def __init__(self):
        # self.tuner = PeakAxisTuner()
        self.tuner = None   # such as: APS_BlueSky_tools.plans.TuneAxis
        
        # Hook functions for callers to add additional plan parts
        # Each must accept one argument: axis object such as `EpicsMotor` or `SynAxis`
        self.pre_tune_method = self._default_pre_tune_method
        self.post_tune_method = self._default_post_tune_method
    
    def _default_pre_tune_method(self):
        """called before `tune()`"""
        print("{} position before tuning: {}".format(self.name, self.position))

    def _default_post_tune_method(self):
        """called after `tune()`"""
        print("{} position after tuning: {}".format(self.name, self.position))

    def tune(self, md=None, **kwargs):
        if self.tuner is None:
            msg = "Must define an axis tuner, none specified."
            msg += "  Consider using APS_BlueSky_tools.plans.TuneAxis()"
            raise AxisTunerException(msg)
        
        if self.tuner.axis is None:
            msg = "Must define an axis, none specified."
            raise AxisTunerException(msg)

        if md is None:
            md = OrderedDict()
        md["purpose"] = "tuner"
        md["datetime"] = str(datetime.now())

        if self.pre_tune_method is not None:
            self.pre_tune_method()

        if self.tuner is not None:
            yield from self.tuner.tune(md=md, **kwargs)

        if self.post_tune_method is not None:
            self.post_tune_method()


# this code will go into APS_BlueSky_tools.plans
#------------------------------------------------------


def tune_axes(axes):
    """
    BlueSky plan to tune a list of axes in sequence
    """
    for axis in axes:
        yield from axis.tune()

#------------------------------------------------------


# myaxis = TunableSynAxis(name="myaxis")
# mydet = SynGauss('mydet', myaxis, 'myaxis', center=0.21, Imax=0.98e5, sigma=0.127)
# 
# myaxis.pre_tune_method = my_pre_tune_hook
# myaxis.post_tune_method = my_post_tune_hook
# myaxis.tuner.set_params(axis=myaxis, det=mydet, num=71, time_s=0.05)
# 
# m1 = TunableEpicsMotor('prj:m1', name='m1')
# spvoigt = SynPseudoVoigt(
#     'spvoigt', m1, 'm1', 
#     center=-1.5 + 0.5*np.random.uniform(), 
#     eta=0.2 + 0.5*np.random.uniform(), 
#     sigma=0.001 + 0.05*np.random.uniform(), 
#     scale=0.95e5,
#     bkg=0.01*np.random.uniform())
# # m1.tuner.set_params(axis=m1, det=spvoigt, num=71, time_s=0.1)
# # m1.pre_tune_method = my_pre_tune_hook
# # m1.post_tune_method = my_post_tune_hook
# 
# m2 = TunableEpicsMotor('prj:m2', name='m2')
# # m2.tuner.set_params(axis=m2, det=scaler, num=31, time_s=0.15)
# 
# m3 = TunableEpicsMotor('prj:m3', name='m3')
# swait_setup_lorentzian(calcs.calc3, m3, center=-0.15, width=0.025, scale=12345, noise=0.05)
# # m3.tuner.set_params(axis=m3, det=calcs.calc3, num=61, time_s=0.015, start=-.5, finish=.5)


#------------------------------------------------------


class TunableSynAxis(SynAxis, AxisTunerMixin):
    pass


class TunableEpicsMotor(EpicsMotor, AxisTunerMixin):
    pass

def myaxis_pretune_hook():
    # set the counting time for *this* tune
    mydet.exposure_time = 0.02      # can't yield this one


myaxis = TunableSynAxis(name="myaxis")
mydet = SynGauss('mydet', myaxis, 'myaxis', center=0.21, Imax=0.98e5, sigma=0.127)
myaxis.tuner = TuneAxis([mydet], myaxis)
myaxis.tuner.width = 2
myaxis.tuner.num = 81

m1 = TunableEpicsMotor('prj:m1', name='m1')
spvoigt = SynPseudoVoigt(
    'spvoigt', m1, 'm1', 
    center=-1.5 + 0.5*np.random.uniform(), 
    eta=0.2 + 0.5*np.random.uniform(), 
    sigma=0.001 + 0.05*np.random.uniform(), 
    scale=0.95e5,
    bkg=0.01*np.random.uniform())
m1.tuner = TuneAxis([spvoigt], m1)
m1.tuner.width = 2
m1.tuner.num = 41

m2 = TunableEpicsMotor('prj:m2', name='m2')
m2.tuner = TuneAxis([scaler], m2, signal_name=scaler.channels.chan2.name)
m2.tuner.width = 2
m2.tuner.num = 10
scaler.channels.read_attrs = "chan1 chan2 chan3 chan4".split()

m3 = TunableEpicsMotor('prj:m3', name='m3')
m3.tuner = TuneAxis([calcs.calc3], m3, signal_name=calcs.calc3.val.name)
m3.tuner.width = 0.5
m3.tuner.num = 31
swait_setup_lorentzian(calcs.calc3, m3, center=-0.15, width=0.025, scale=12345, noise=0.05)
calcs.calc3.read_attrs = ["val",]

append_wa_motor_list(myaxis)
