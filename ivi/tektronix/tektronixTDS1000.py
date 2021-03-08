
from .tektronixBaseScope import *

class tektronixTDS1000(tektronixBaseScope):

    def __init__(self, *args, **kwargs):
        #self.__dict__.setdefault('_instrument_id', 'MDO3022')

        super(tektronixTDS1000, self).__init__(*args, **kwargs)

        self._analog_channel_count = 2
        self._digital_channel_count = 0
        self._bandwidth = 60e6

        self._vertical_divisions = 8

        self._init_channels()
    
    def _get_channel_probe_attenuation(self, index):
        index = ivi.get_index(self._analog_channel_name, index)
        if not self._driver_operation_simulate and not self._get_cache_valid(index=index):
            self._channel_probe_attenuation[index] = 1/float(self._ask(":%s:probe?" % self._channel_name[index]))
            self._set_cache_valid(index=index)
        return self._channel_probe_attenuation[index]

    def _set_channel_probe_attenuation(self, index, value):
        index = ivi.get_index(self._analog_channel_name, index)
        value = 1/float(value)
        if not self._driver_operation_simulate:
            self._write(":%s:probe %e" % (self._channel_name[index], value))
        self._channel_probe_attenuation[index] = value
        self._set_cache_valid(index=index)
        self._set_cache_valid(False, 'channel_offset', index)
        self._set_cache_valid(False, 'channel_scale', index)

    def _measurement_fetch_waveform_measurement(self, index, measurement_function, ref_channel = None):
        index = ivi.get_index(self._channel_name, index)
        if index < self._analog_channel_count:
            if measurement_function not in MeasurementFunctionMapping:
                raise ivi.ValueNotSupportedException()
            func = MeasurementFunctionMapping[measurement_function]
        else:
            if measurement_function not in MeasurementFunctionMappingDigital:
                raise ivi.ValueNotSupportedException()
            func = MeasurementFunctionMappingDigital[measurement_function]
        if not self._driver_operation_simulate:
            self._write(":measurement:immed:type %s" % func)
            self._write(":measurement:immed:source1 %s" % self._channel_name[index])
            if measurement_function in ['ratio', 'phase', 'delay']:
                if hasattr(ref_channel, 'name'):
                    ref_channel = ref_channel.name
                ref_index = ivi.get_index(self._channel_name, ref_channel)
                self._write(":measurement:immed:source2 %s" % self._channel_name[ref_index])
            return float(self._ask(":measurement:immed:value?"))
        return 0
