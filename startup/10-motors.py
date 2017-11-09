print(__file__)

from ophyd import (PVPositioner, EpicsMotor, EpicsSignal, EpicsSignalRO,
                   PVPositionerPC, Device)
from ophyd import Component as Cpt
import ophyd.sim        # simulated hardware
from ophyd.flyers import FlyerInterface

from bluesky.preprocessors import (
   fly_during_wrapper, 
   fly_during_decorator,
   monitor_during_wrapper,
   monitor_during_decorator
   )

class MotorDialValues(Device):
	value = Cpt(EpicsSignalRO, ".DRBV")
	setpoint = Cpt(EpicsSignal, ".DVAL")

class MyEpicsMotorWithDial(EpicsMotor):
	dial = Cpt(MotorDialValues, "")

class EpicsMotorFlyer(EpicsMotor, FlyerInterface):
    # TODO: this may not be the right idea

    def kickoff(self) -> StatusBase:
        '''Start a flyer

        The status object return is marked as done once flying
        has started.

        Returns
        -------
        kickoff_status : StatusBase
            Indicate when flying has started.

        '''

    def complete(self) -> StatusBase:
        '''Wait for flying to be complete.

        This can either be a question ("are you done yet") or a
        command ("please wrap up") to accommodate flyers that have a
        fixed trajectory (ex. high-speed raster scans) or that are
        passive collectors (ex MAIA or a hardware buffer).

        In either case, the returned status object should indicate when
        the device is actually finished flying.

        Returns
        -------
        complete_status : StatusBase
            Indicate when flying has completed
        '''

    def collect(self) -> Generator[Dict, None, None]:
        '''Retrieve data from the flyer as proto-events

        The events can be from a mixture of event streams, it is
        the responsibility of the consumer (ei the RunEngine) to sort
        them out.

        Yields
        ------
        event_data : dict
            Must have the keys {'time', 'timestamps', 'data'}.

        '''

    def collect_tables(self) -> Iterable[Any]:
        '''Retrieve data from flyer as tables

        PROPOSED


        Yields
        ------
        time : Iterable[Float]

        data : dict

        timestamps : dict
        '''

    def describe_collect(self) -> Dict[str, Dict]:
        '''Provide schema & meta-data from :meth:`collect`

        This is analogous to :meth:`describe`, but nested by stream name.

        This provides schema related information, (ex shape, dtype), the
        source (ex PV name), and if available, units, limits, precision etc.

        The data_keys are mapped to events from `collect` by matching the
        keys.

        Returns
        -------
        data_keys_by_stream : dict
            The keys must be strings and the values must be dict-like
            with keys that are str and the inner values are dict-like
            with the ``event_model.event_descriptor.data_key`` schema.
        '''


# m1 = MyEpicsMotorWithDial('prj:m1', name='m1')
m1 = EpicsMotor('prj:m1', name='m1')
m2 = EpicsMotor('prj:m2', name='m2')
m3 = EpicsMotor('prj:m3', name='m3')
m4 = EpicsMotor('prj:m4', name='m4')
m5 = EpicsMotor('prj:m5', name='m5')
m6 = EpicsMotor('prj:m6', name='m6')
m7 = EpicsMotor('prj:m7', name='m7')
m8 = EpicsMotor('prj:m8', name='m8')

m1flyer = EpicsMotorFlyer('prj:m1', name='m1flyer')
