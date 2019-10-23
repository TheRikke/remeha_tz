import paho.mqtt.client as mqttClient

from datamap import Translator
from remeha_core import FrameDecoder


def get_human_readable_duration_and_unit(timediff):
    total_seconds = timediff.total_seconds()
    if total_seconds <= 90:
        return total_seconds, 's'
    elif total_seconds <= (90 * 60):
        return total_seconds / 60, 'min'
    elif total_seconds <= (90 * 60 * 60):
        return total_seconds / (60 * 60), 'h'
    return total_seconds / (60 * 60 * 24), 'd'


class LogToMQtt:
    def __init__(self, update_freq_in_s):
        self.update_freq_in_s = update_freq_in_s
        self.client = mqttClient.Client("Python")
        self.translator = Translator()
        try:
            self.client.connect("localhost")
        except Exception as e:
            self.client = None

        self.frame_decoder = None
        if self.client:
            self.frame_decoder = FrameDecoder()
            self.client.loop_start()
        self.previous_values = {}
        self.last_known_duration = {}

    def log(self, frame, runtime_seconds):
        if runtime_seconds % self.update_freq_in_s == 0:
            unpacked_data = frame.get_parseddata()
            if self.client:
                self.log_single_value('outside_temp', unpacked_data)
                self.log_single_value('flow_temp', unpacked_data)
                self.log_single_value('return_temp', unpacked_data)
                self.log_single_value('status', unpacked_data, frame.timestamp)
                self.log_single_value('substatus', unpacked_data, frame.timestamp)
                self.log_single_value('locking', unpacked_data, frame.timestamp)
                self.log_single_value('blocking', unpacked_data, frame.timestamp)
                self.log_duration_of_value('status', 'burning_dhw', unpacked_data, frame.timestamp)
            else:
                print("Temp: %d" % self.frame_decoder.decode(unpacked_data, 'outside_temp'))

    def log_single_value(self, value_name, unpacked_data, current_time=None):
        value = self.frame_decoder.decode(unpacked_data, value_name)
        mqtt_topic = "boiler/" + value_name
        if current_time:
            if value_name not in self.previous_values:
                self.previous_values[value_name] = [current_time, '-']
            previous_value = self.previous_values[value_name]
            if previous_value[1] != value:
                previous_value[1] = value
                previous_value[0] = current_time

            value_format = '{:1.1f}'
            if isinstance(value, str):
                value_format = '{}'
                value = self.translator.translate(value)
            time_delta, unit = get_human_readable_duration_and_unit(current_time - previous_value[0])
            self.client.publish(mqtt_topic,
                                (value_format + ' ({:0.3g}{})').format(
                                    value,
                                    time_delta,
                                    unit
                                ),
                                retain=True)
        else:
            self.client.publish(mqtt_topic, '{:1.1f}'.format(value), retain=True)

    def log_duration_of_value(self, value_name, expected_value, unpacked_data, current_time):
        value = self.frame_decoder.decode(unpacked_data, value_name)
        if value_name not in self.last_known_duration:
            self.last_known_duration[value_name] = None
        last_known_duration = self.last_known_duration[value_name]
        if expected_value == value:
            if last_known_duration is None:
                # start measurement
                self.last_known_duration[value_name] = current_time
        elif last_known_duration is not None:
            # end measurement
            time_delta, unit = get_human_readable_duration_and_unit(current_time - last_known_duration)
            self.client.publish("boiler/" + value_name + '_' + expected_value + '_duration',
                                '{:0.3g}{}'.format(time_delta, unit),
                                retain=True)
            self.last_known_duration[value_name] = None
