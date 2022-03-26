import logging
import paho.mqtt.client as mqttClient
from datamap import Translator, get_type_names
from remeha_core import FrameDecoder

log = logging.getLogger(__name__)


def get_human_readable_duration_and_unit(timediff):
    total_seconds = timediff.total_seconds()
    if total_seconds <= 90:
        return total_seconds, 's'
    elif total_seconds <= (90 * 60):
        return total_seconds / 60, 'min'
    elif total_seconds <= (90 * 60 * 60):
        return total_seconds / (60 * 60), 'h'
    return total_seconds / (60 * 60 * 24), 'd'


def on_message(client, update_function, message):
    if update_function:
        update_function(message.payload.decode('UTF-8'))


def on_connect(client, userdata, flags, rc):
    if rc !=0:
        log.error("MQTT connection returned result: " + mqttClient.connack_string(rc))


def on_disconnect(client, userdata, rc):
    if rc != 0:
        log.error(f"MQTT Unexpected disconnection ({rc}): {mqttClient.connack_string(rc)}")


class LogToMQtt:
    def __init__(self, config, update_freq_in_s, function_callback=None):
        self.client = None
        if config and 'mqtt_logger' in config:
            if self.process_config(config['mqtt_logger']) and self.config['enabled']:
                self.update_freq_in_s = update_freq_in_s
                self.client = mqttClient.Client("remeha logger")
                self.client.on_connect = on_connect
                self.client.on_disconnect = on_disconnect
                self.client.enable_logger(log)
                self.translator = Translator()
                host = self.config['host']
                port = self.config['port']
                try:
                    if 'user_name' in self.config and self.config['user_name'] is not None:
                        password = None if 'password' not in self.config else self.config['password']
                        self.client.username_pw_set(self.config['user_name'], password=password)
                    if 'tls_enabled' in self.config and self.config['tls_enabled']:
                        self.client.tls_set()
                    self.client.connect(host=host, port=port)
                except Exception as ex:
                    log.error(f"Could not connect to MQTT at {host}:{port}. Reason: {ex}")
                    self.client = None

                self.frame_decoder = None
                if self.client:
                    self.frame_decoder = FrameDecoder()
                    self.client.on_message = on_message
                    self.client.user_data_set(function_callback)
                    self.client.subscribe("{}/manual_log".format(self.topic))

                    self.client.loop_start()

                self.previous_values = {}
                self.last_known_duration = {}
            else:
                log.info("mqtt_logger disabled in config")
                self.client = None
        else:
            log.error('"mqtt_logger" section in config missing')

    def process_config(self, config):
        self.config = config
        self.log_single_value_list = []
        self.log_with_timestamp_list = []
        self.log_duration_list = []
        self.scaled_values = {}
        self.log_extended = []
        possible_value_names = list(get_type_names())
        if 'enabled' not in config:
            self.config = None
            log.error('missing "enabled" in "mqtt_logger" config section')
        if 'host' not in config:
            self.config = None
            log.error('missing "host" in "mqtt_logger" config section')
        if 'port' not in config:
            self.config = None
            log.error('missing "port" in "mqtt_logger" config section')
        if 'password' in config and config['password'] is not None and ('user_name' not in config or config['user_name'] is None):
            self.config = None
            log.error('missing "user_name" in "mqtt_logger" config section')
        if 'topic' not in config:
            self.topic = 'boiler'
            log.warning('missing "port" in "mqtt_logger" config section. Using "boiler/"')
        else:
            self.topic = config['topic']

        if 'log_values' in config:
            self.log_single_value_list = config['log_values']
        if 'log_values_with_duration' in config:
            self.log_duration_list = config['log_values_with_duration']
        if 'log_values_with_timestamp' in config:
            self.log_with_timestamp_list = config['log_values_with_timestamp']
        if 'log' in config:
            for current_log_entry in config['log']:
                if 'value_name' in current_log_entry:
                    if current_log_entry['value_name'] not in possible_value_names:
                        log.warning(f'Unknown name "{current_log_entry["value_name"]}". Possible names are:')
                        for possible_value_name in possible_value_names:
                            log.warning(f'   {possible_value_name}')
                if 'value_name' in current_log_entry and 'payload' in current_log_entry:
                    log.error(f"Don't know what to do if 'value_name' and 'payload' are both specified in one log entity. (value_name: {config['log']['value_name']}, payload: {config['log']['payload']})")
                    return None
                if 'topic' not in current_log_entry and 'value_name' in current_log_entry:
                    current_log_entry['topic'] = current_log_entry['value_name']
                if not current_log_entry['topic'].startswith('/'):
                    current_log_entry['topic'] = f"{self.topic}/{current_log_entry['topic']}"
                else:
                    current_log_entry['topic'] = current_log_entry['topic'][1:]
                if 'mapping' in current_log_entry or 'payload' in current_log_entry:
                    self.log_extended += [current_log_entry]
                else:
                    log.error('Missing "value_name" in "log" entry. Please specify with "value_name" the source for the mapping.')
        if 'scale_to_percent' in config:
            for scales in config['scale_to_percent']:
                self.scaled_values[scales['value_name']] = [scales['lower_limit'], scales['upper_limit']]
        if not self.log_duration_list and not self.log_single_value_list and not self.log_with_timestamp_list and not self.log_extended:
            self.config = None
            log.error('Nothing to log. Specified "log_values", "log_values_with_timestamp", "log_mapped" or "log_values_with_duration" to "mqtt_logger" config section')
        return self.config

    def log(self, frame, runtime_seconds):
        if self.client and runtime_seconds % self.update_freq_in_s == 0:
            unpacked_data = frame.get_parseddata()
            for value_name in self.log_single_value_list:
                if value_name in self.scaled_values:
                    self.log_single_value(value_name, unpacked_data, scale_to_percent=[self.scaled_values[value_name][0], self.scaled_values[value_name][1]])
                else:
                    self.log_single_value(value_name, unpacked_data)
            for value_name in self.log_with_timestamp_list:
                self.log_single_value(value_name, unpacked_data, frame.timestamp)
            for entry in self.log_duration_list:
                self.log_duration_of_value(entry['value_name'], entry['expected_value'], unpacked_data, frame.timestamp)
            for entry_config in self.log_extended:
                self.log_extended_values(entry_config, unpacked_data)

    def log_extended_values(self, mapping_config, unpacked_data):
        retained = mapping_config.get('retained', False)

        if 'mapping' in mapping_config:
            value = self.frame_decoder.decode(unpacked_data, mapping_config['value_name'])
            self.client.publish(mapping_config['topic'], mapping_config['mapping'].get(value, f'unknown({value})'), retain=retained)
        elif 'payload' in mapping_config:
            self.client.publish(mapping_config['topic'], mapping_config['payload'], retain=retained)

    def log_single_value(self, value_name, unpacked_data, current_time=None, scale_to_percent=None):
        value = self.frame_decoder.decode(unpacked_data, value_name)
        mqtt_topic = self.topic + "/" + value_name
        if scale_to_percent:
            value = ((value - scale_to_percent[0]) / (scale_to_percent[1] - scale_to_percent[0])) * 100
        value_format = '{:1.1f}'
        if isinstance(value, str):
            value_format = '{}'
            value = self.translator.translate(value)
        if current_time:
            if value_name not in self.previous_values:
                self.previous_values[value_name] = [current_time, '-']
            previous_value = self.previous_values[value_name]
            if previous_value[1] != value:
                previous_value[1] = value
                previous_value[0] = current_time

            time_delta, unit = get_human_readable_duration_and_unit(current_time - previous_value[0])
            self.client.publish(mqtt_topic,
                                (value_format + ' ({:0.3g}{})').format(
                                    value,
                                    time_delta,
                                    unit
                                ),
                                retain=True)
        else:
            self.client.publish(mqtt_topic, value_format.format(value), retain=True)

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

    def close(self):
        pass
