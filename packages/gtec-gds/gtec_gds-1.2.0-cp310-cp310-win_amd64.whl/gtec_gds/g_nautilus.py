import threading
import numpy as np
from enum import Enum


class GNautilus:

    class Sensitivities(Enum):
        SENS_2250000 = 2250000,
        SENS_1125000 = 1125000,
        SENS_750000 = 750000,
        SENS_562500 = 562500,
        SENS_375000 = 375000,
        SENS_187500 = 187500

    _serial: str
    _sampling_rate: float
    _channel_count: int
    _device: None
    _data_callback: callable
    _running: bool

    @staticmethod
    def register(key: str):
        from .lib.gtec_gds_wrapper import GDS
        GDS.register(key=key)

    def __init__(self,
                 serial: str = None,
                 sampling_rate: float = None,
                 channel_count: int = None,
                 frame_size: int = None,
                 sensitivity: float = None,
                 enable_di: bool = None,
                 **kwargs):
        self._serial = serial
        self._sampling_rate = None
        self._channel_count = None
        self._frame_size = None
        self._sensitivity = None
        self._enable_di = None
        self._device = None
        self._data_callback = None
        self._running = False

        from .lib.gtec_gds_wrapper import GDS, ConnectedDevices
        GDS._check_key()

        if sampling_rate is None:
            raise ValueError("Sampling rate not set.")

        cd = ConnectedDevices()
        if len(cd) == 0:
            raise Exception("No GDS devices found.")
        self._device = GDS(gds_device=cd[0][0])
        if channel_count is None:
            channel_count = len(self._device.Channels)

        supported_sampling_rates = self._device.GetSupportedSamplingRates()[0]
        ssr = [*supported_sampling_rates.keys()]
        if sampling_rate not in ssr:
            raise ValueError(f"Sampling rate {sampling_rate} Hz not supported."
                             f" Please use {format(ssr)} Hz.")

        sfsz = supported_sampling_rates[sampling_rate]
        if type(sfsz) is not list:
            sfsz = [sfsz]

        if frame_size is None:
            frame_size = 1
        if frame_size != 1:
            if frame_size not in sfsz:
                raise ValueError(f"Frame size {frame_size} not supported. "
                                 f"Please use {format(sfsz)}.")

        supported_sens = self._device.GetSupportedSensitivities()[0]
        if sensitivity is None:
            sensitivity = supported_sens[0]  # lowest sensitivity per default
        if sensitivity not in supported_sens:
            raise ValueError("Sensitivity not supported. Please use one "
                             "of {}.".format(supported_sens))

        if enable_di is None:
            enable_di = False

        for i in range(len(self._device.Channels)):
            self._device.Channels[i].Enabled = i < channel_count
            self._device.Channels[i].Sensitivity = sensitivity

        self._device.Trigger = 1 if enable_di else 0
        self._device.SamplingRate = sampling_rate
        self._device.NumberOfScans = frame_size

        self._device.SetConfiguration()
        self._sampling_rate = sampling_rate
        self._channel_count = channel_count
        self._frame_size = frame_size
        self._sensitivity = sensitivity
        self._enable_di = enable_di

    def __del__(self):
        if self._device is not None:
            del self._device
            self._device = None

    def start(self):
        if self._data_callback is None:
            raise ValueError("No data callback set.")
        self._running = True
        self._data_thread = threading.Thread(target=self._data_thread_fun)
        self._data_thread.daemon = True
        self._data_thread.start()

    def stop(self):
        self._running = False
        if self._data_thread:
            self._data_thread.join()

    def set_data_callback(self, callback):
        self._data_callback = callback

    def _data_thread_fun(self):
        self._device.GetData(scanCount=self._frame_size,
                             more=self._callback_wrapper)

    def get_impedance(self, first: bool = True):
        z = self._device.GetImpedanceEx(electrodeType=0,  # passive electrodes
                                        tmsBoxCorrection=False,
                                        firstMeasurementOfSession=first)
        return np.array(z[0][:self._channel_count])

    def _callback_wrapper(self, data: np.ndarray) -> bool:
        self._data_callback(data.copy())
        return self._running

    @property
    def serial_number(self):
        return self._serial

    @property
    def sampling_rate(self):
        return self._sampling_rate

    @property
    def channel_count(self):
        return self._channel_count

    @property
    def sensitivity(self):
        return self._sensitivity
