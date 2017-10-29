print(__file__)

from collections import OrderedDict
from ophyd.device import (
    DynamicDeviceComponent as DDC,
    FormattedComponent as FC)


class EpicsSscanPositioner(Device):
    """positioner of an EPICS sscan record"""
    
    readback_pv = FC(EpicsSignal, '{self.prefix}.R{self._ch_num}PV')
    readback_value = FC(EpicsSignalRO, '{self.prefix}.R{self._ch_num}CV')
    setpoint_pv = FC(EpicsSignal, '{self.prefix}.P{self._ch_num}PV')
    setpoint_value = FC(EpicsSignalRO, '{self.prefix}.P{self._ch_num}DV')
    start = FC(EpicsSignal, '{self.prefix}.P{self._ch_num}SP')
    center = FC(EpicsSignal, '{self.prefix}.P{self._ch_num}CP')
    end = FC(EpicsSignal, '{self.prefix}.P{self._ch_num}EP')
    step_size = FC(EpicsSignal, '{self.prefix}.P{self._ch_num}SI')
    width = FC(EpicsSignal, '{self.prefix}.P{self._ch_num}WD')
    abs_rel = FC(EpicsSignal, '{self.prefix}.P{self._ch_num}AR')
    mode = FC(EpicsSignal, '{self.prefix}.P{self._ch_num}SM')
    
    def __init__(self, prefix, num, **kwargs):
        self._ch_num = num
        super().__init__(prefix, **kwargs)
    
    def reset(self):
        """set all fields to default values"""
        self.readback_pv.put("")
        self.setpoint_pv.put("")
        self.start.put(0)
        self.center.put(0)
        self.end.put(0)
        self.step_size.put(0)
        self.width.put(0)
        self.abs_rel.put("ABSOLUTE")
        self.mode.put("LINEAR")


class EpicsSscanDetector(Device):
    """detector of an EPICS sscan record"""
    
    input_pv = FC(EpicsSignal, '{self.prefix}.D{self._ch_num}PV')
    current_value = FC(EpicsSignal, '{self.prefix}.D{self._ch_num}CV')
    # TODO: triggers
    
    def __init__(self, prefix, num, **kwargs):
        self._ch_num = num
        super().__init__(prefix, **kwargs)
    
    def reset(self):
        """set all fields to default values"""
        self.input_pv.put("")


def _sscan_positioners(channel_list):
    defn = OrderedDict()
    for chan in channel_list:
        attr = 'p{}'.format(chan)
        defn[attr] = (EpicsSscanPositioner, '', {'num': chan})
    return defn


def _sscan_detectors(channel_list):
    defn = OrderedDict()
    for chan in channel_list:
        attr = 'd{}'.format(chan)
        defn[attr] = (EpicsSscanDetector, '', {'num': chan})
    return defn


class EpicsSscanRecord(Device):
    """EPICS synApps sscan record: used as $(P):userCalc$(N)"""
    
    desc = Cpt(EpicsSignal, '.DESC')
    faze = Cpt(EpicsSignal, '.FAZE')
    data_state = Cpt(EpicsSignal, '.DSTATE')
    npts = Cpt(EpicsSignal, '.NPTS')
    cpt = Cpt(EpicsSignalRO, '.CPT')
    pasm = Cpt(EpicsSignal, '.PASM')
    exsc = Cpt(EpicsSignal, '.EXSC')

    positioners = DDC(
        _sscan_positioners(
            "1 2 3 4".split()
        )
    )
    detectors = DDC(
        _sscan_detectors(
            ["%02d" % k for k in range(1,71)]
        )
    )
    
    def reset(self):
        """set all fields to default values"""
        self.npts.put(0)
        for part in (self.positioners, self.detectors):
            for ch_name in part.read_attrs:
                channel = part.__getattr__(ch_name)
                channel.reset()
        # TODO: what else?


class EpicsSynAppsSscanDevice(Device):
    """synApps XXX IOC setup of sscan records: $(P):scan$(N)"""

    scan_dimension = Cpt(EpicsSignalRO, 'ScanDim')
    scan_pause = Cpt(EpicsSignal, 'scanPause')
    abort_scans = Cpt(EpicsSignal, 'AbortScans')
    scan1 = Cpt(EpicsSscanRecord, 'scan1')
    scan2 = Cpt(EpicsSscanRecord, 'scan2')
    scan3 = Cpt(EpicsSscanRecord, 'scan3')
    scan4 = Cpt(EpicsSscanRecord, 'scan4')
    scanH = Cpt(EpicsSscanRecord, 'scanH')

    def reset(self):
        """set all fields to default values"""
        self.scan1.reset()
        self.scan2.reset()
        self.scan3.reset()
        self.scan4.reset()
        self.scanH.reset()
        # TODO: what else?
