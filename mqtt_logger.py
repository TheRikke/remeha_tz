import paho.mqtt.client as mqttClient

from remeha_core import FrameDecoder


class LogToMQtt:
    def __init__(self, update_freq_in_s, ):
        self.update_freq_in_s = update_freq_in_s
        self.client = mqttClient.Client("Python")
        try:
            self.client.connect("localhost")
        except Exception as e:
            self.client = None

        self.frame_decoder = None
        if self.client:
            self.frame_decoder = FrameDecoder()
            self.client.loop_start()
        self.previous_values = {}

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
            else:
                print("Temp: %d" % self.frame_decoder.decode(unpacked_data, 'outside_temp'))

    def log_single_value(self, value_name, unpacked_data, current_time=None):
        value = self.frame_decoder.decode(unpacked_data, value_name)
        mqtt_topic = "boiler/" + value_name
        if current_time:
            if not value_name in self.previous_values:
                self.previous_values[value_name] = [current_time, '-']
            previous_value = self.previous_values[value_name]
            if previous_value[1] != value:
                previous_value[1] = value
                previous_value[0] = current_time

            value_format = '{}'
            if isinstance(value, int):
                value_format = '{:1.1f}'

            self.client.publish(mqtt_topic,
                                (value_format + ' ({:0.3g}min)').format(
                                    value,
                                    (current_time - previous_value[0]).total_seconds() / 60
                                ),
                                retain=True)
        else:
            self.client.publish(mqtt_topic, '{:1.1f}'.format(value), retain=True)
