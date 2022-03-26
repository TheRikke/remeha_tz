import locale
import json
import os


def byte_to_bit(input_value):
    return list(map(int, bin(input_value).lstrip('0b').rjust(8, '0')))


class Translator:
    def __init__(self):
        self.translations = {}
        script_directory = os.path.dirname(__file__)
        with open(os.path.join(script_directory, "config/translations.json"), "r", encoding='utf8') as read_file:
            json_data = json.load(read_file)
            self.translations = json_data['en']
            locales = locale.getdefaultlocale()
            if locales and locales[0]:
                two_letter_language = locales[0][:2]
                if two_letter_language in json_data:
                    self.translations = json_data[two_letter_language]

    def translate(self, to_translate, default=None):
        if to_translate in self.translations:
            return self.translations[to_translate]
        elif default:
            return default
        else:
            return to_translate

    def has_translation(self, to_check):
        return True if to_check in self.translations else False


datamap = [
    #  unpack format, int to value transl., variable name, variable unit group, unit
    ['h', lambda x: x * 0.01, 'flow_temp', "temps", 'ms'],
    ['h', lambda x: x * 0.01, 'return_temp', "temps", 'ms'],
    ['h', lambda x: x * 0.01, 'dhw_in_temp',  "temps_off", 'ms'],
    ['h', lambda x: x * 0.01, 'outside_temp',  "temps", 'ms'],
    ['h', lambda x: x * 0.01, 'calorifier_temp', "temps", 'ms'],
    ['h', lambda x: x       , 'unknown10', "unknowns", 'ms'],
    ['h', lambda x: x * 0.01, 'boiler_control_temp', "temps", 'ms'],
    ['h', lambda x: x * 0.01, 'room_temp', "temps", 'ms'],
    ['h', lambda x: x * 0.01, 'cv_setpoint', "temps", 'ms'],
    ['h', lambda x: x * 0.01, 'dhw_setpoint', "temps", 'ms'],
    ['h', lambda x: x * 0.01, 'room_setpoint', "temps", 'ms'],
    ['h', lambda x: x       , 'airflow_setpoint', "flow", 'ms'],
    ['h', lambda x: x       , 'airflow_actual', "flow", 'ms'],  # 24
    ['b', lambda x: x * 0.1 , 'ionisation_current', "current", 'ms'],  # 26
    ['h', lambda x: x * 0.01, 'intern_setpoint', "temps", 'ms'],  # 27
    ['b', lambda x: x       , 'output', "flow", 'ms'],  # 29
    ['b', lambda x: x       , 'pump_speed', "flow", 'ms'],
    ['b', lambda x: x       , 'unknown31', "unknown", 'ms'],   # 31
    ['b', lambda x: x       , 'setpoint_power', "flow", 'ms'],
    ['b', lambda x: x       , 'actual_power', "flow", 'ms'],
    ['b', lambda x: x       , 'unknown34', "unknown", 'ms'],
    ['b', lambda x: x       , 'unknown35', "unknown", 'ms'],   # 35
    ['B', lambda x: byte_to_bit(x ^ 0b00010000),
     ['dwh_heat_demand', 'anti_legionella', 'dhw_blocking', 'dhw_eco_boiler_not_kept_warm', 'frost_protection',
      'heat_demand', 'modulating_controller_demand', 'modulating_controller'],
     ["switch", "switch", "switch", "switch", "switch", "switch", "switch", "switch"],
     ['g', 'g', 'g', 'g', 'g', 'g', 'g', 'g'],
     ],  # 36
    ['B', lambda x: byte_to_bit(x ^ 0b00000011),
     ['dhw_enabled', 'ch_enabled', 'min_gas_pressure', 'unknown37.4', 'flow_switch_for_detecting_dhw', 'ionisation',
      'release_input', 'shutdown_input'],
     ["switch", "switch", "switch", "switch", "switch", "switch", "switch", "switch"],
     ['g', 'g', 'g', 'g', 'g', 'g', 'g', 'g'],
     ],  # 37
    ['B', lambda x: byte_to_bit(x ^ 0b00000001),
     ['unknown38.7', 'ext_gas_valve', 'unknown38.5', 'ext_three_way_valve', 'three_way_valve', 'ignition',
      'unknown38.1', 'gas_valve'],
     ["switch", "switch", "switch", "switch", "switch", "switch", "switch", "switch"],
     ['g', 'g', 'g', 'g', 'g', 'g', 'g', 'g'],
     ],  # 38
    ['B', lambda x: byte_to_bit(x),
     ['opentherm_smart_power', 'unknown39.6', 'unknown39.5', 'status_report', 'unknown39.3', 'ext_ch_pump',
      'calorifier_pump', 'pump'],
     ["switch", "switch", "switch", "switch", "switch", "switch", "switch", "switch"],
     ['g', 'g', 'g', 'g', 'g', 'g', 'g', 'g'],
     ],
    ['B', lambda x: x, 'status', "mapped", {0: 'Standby',
                                            1: 'boiler_start',
                                            2: 'burner_start',
                                            3: 'burning_ch',
                                            4: 'burning_dhw',
                                            5: 'burner_stop',
                                            6: 'boiler_stop',
                                            8: 'controlled_stop',
                                            9: 'blocking_mode',
                                            10: 'locking_mode',
                                            11: 'chimney_mode_1',
                                            12: 'chimney_mode_2',
                                            13: 'chimney_mode_3',
                                            15: 'manual_heat_demand',
                                            16: 'boiler_frost_protection',
                                            17: 'de_aeration',
                                            18: 'controller_temp_protection',
                                            }],  # 40
    ['B', lambda x: x, 'locking', "mapped", {
        0: "psu_not_connected",
        1: "su_parameter_fault",
        2: "t_heatexchanger_closed",
        3: "t_heatexchanger_open",
        4: "t_heatexchanger_lt_min",
        5: "t_heatexchanger_gt_max",
        6: "t_return_closed",
        7: "t_return_open",
        8: "t_return_lt_min",
        9: "t_return_gt_max",
        10: "dt_heatexchanger_return_gt_max",
        11: "dt_return_heatexchanger_gt_max",
        12: "stb_activated",
        14: "five_unsuccessful_starts",
        15: "five_vps_test_failures",
        16: "false_flame",
        17: "su_gasvalve_driver_error",
        32: "t_flow_closed",
        33: "t_flow_open",
        34: "fan_range_error",
        35: "return_over_flow_temp",
        36: "five_flame_loss_failures",
        37: "su_communication",
        38: "scu_s_communication",
        39: "bl_input_as_lockout",
        41: "pcb_temperature",
        42: "low_water_pressure",
        43: "no_gradient",
        45: "deair_test_failed",
        50: "external_psu_timeout",
        51: "onboard_psu_timeout",
        52: "gvc_lockout",
        255: "no_locking"

    }],
    ['B', lambda x: x, 'blocking', "mapped", {
        0: "pcu_wrong_param",
        1: "t_flow_gt_max",
        2: "dts_flow_gt_max",
        3: "t_heatexchanger_gt_max",
        4: "dts_heatexchanger_gt_max",
        5: "dt_heatexchanger_return_gt_max",
        6: "dt_flow_heatexchanger_gt_max",
        7: "dt_flow_return_gt_max",
        8: "no_release_signal",
        9: "pn_swept",
        10: "blocking_sig_without_frost",
        11: "blocking_sig_with_frost",
        12: "hmi_not_connected",
        13: "scu_communication",
        14: "min_water_pressure",
        15: "min_gas_pressure",
        16: "ident_su_mismatch",
        17: "ident_dfdu_table_error",
        18: "ident_psu_mismatch",
        19: "ident_dfdu_needed",
        20: "identification_running",
        21: "su_communication_lost",
        22: "flame_lost",
        24: "vps_test_failed",
        25: "internal_su_error",
        26: "calorifier_sensor_error",
        27: "dhw_sensor_error",
        28: "reset_in_progress",
        29: "gvc_parameter_changed",
        255: "no_blocking"
    }],  # 42
    ['B', lambda x: x, 'substatus', "mapped", {0: "Standby",
                                               1: "anti_cycling",
                                               2: "hydraulic_valve_open",
                                               3: "pump_start",
                                               4: "wait_for_burner_start",
                                               10: "ext_gasvalve_open",
                                               11: "fluegasvalve_fan_speed",
                                               12: "fluegasvalve_open",
                                               13: "pre_purge",
                                               14: "wait_for_release",
                                               15: "burner_start",
                                               16: "vps_test",
                                               17: "pre_ignition",
                                               18: "ignition",
                                               19: "flame_check",
                                               20: "inter_purge",
                                               30: "normal_internal_setpoint",
                                               31: "limit_internal_setpoint",
                                               32: "powercontrol_normal",
                                               33: "gradient_control_lvl1",
                                               34: "gradient_control_lvl2",
                                               35: "gradient_control_lvl3",
                                               36: "flame_protection",
                                               37: "stabilization_time",
                                               38: "cold_start",
                                               39: "limited_power_tfg",
                                               40: "burner_stop",
                                               41: "post_purge",
                                               42: "fluegasvalve_fan_speed",
                                               43: "fluegasvalve_close",
                                               44: "fan_stop",
                                               45: "ext_gasvalve_close",
                                               60: "pump_post_running",
                                               61: "pump_stop",
                                               62: "hydraulic_valve_close",
                                               63: "start_wait_timer",
                                               255: "wait_time_reset",
                                               }],
    ['h', lambda x: x, 'fan_speed', "flow", 'ms'],
    ['b', lambda x: x, 'su_state', "unkown46", 'ms'],
    ['b', lambda x: x, 'su_locking', "unkown47", 'ms'],
    ['b', lambda x: x, 'su_blocking', "unkown48", 'ms'],
    ['b', lambda x: x * 0.1, 'hydr_pressure', "flow", 'ms'],
    ['B', lambda x: byte_to_bit(x),
     ['dhw_timer_enable', 'ch_timer_enable', 'unknown50.5', 'unknown50.4', 'unknown50.3', 'unknown50.2', 'hru_active',
      'unknown50.0'],
     ["switch", "switch", "switch", "switch", "switch", "switch", "switch", "switch"],
     ['g', 'g', 'g', 'g', 'g', 'g', 'g', 'g'],  # 50
     ],
    ['h', lambda x: x * 0.01, 'control_temp', "temps", 'ms'],
    ['h', lambda x: x * 0.01, 'dhw_flow', "flow", 'ms'],  # 53
    ['b', lambda x: x, 'unknown55', "unkown", 'ms'],  # 55
    ['h', lambda x: x * 0.1, 'solar_temp', "unkown", 'ms'],
    ['h', lambda x: x, 'hmi_active', "unkown", 'ms'],
    ['b', lambda x: x, 'ch_setpoint_hmi', "temps", 'ms'],  # 60
    ['b', lambda x: x, 'dhw_setpoint_hmi', "temps", 'ms'],
    ['b', lambda x: x, 'service_mode', "value", 'ms'],  # 62
    ['b', lambda x: x, 'serial_mode', "value", 'ms'],
]

datamap_identification = [
    #  Byte, int to value transl., variable name,
    ['b', lambda x: x, 'unknown00', "unknown00", "", ""],
    ['b', lambda x: x, 'df_code', "dF-code", "", ''],
    ['b', lambda x: x, 'du_code', "dU-code", "", ''],
    ['b', lambda x: x, 'unknown03', "unknown03", "", ""],
    ['b', lambda x: x, 'unknown04', "unknown04", "", ""],
    ['b', lambda x: x, 'software_version', "Software Version", "", ''],
    ['b', lambda x: x, 'parameter_version', "parameter_version", "", ''],
    ['b', lambda x: x, 'parameter_type', "parameter_type", "", ''],
    ['b', lambda x: x, 'unknown08', "unknown08", "", ""],
    ['b', lambda x: x, 'unknown09', "unknown09", "", ""],
    ['b', lambda x: x, 'next_service_code', "Next Service Code", "", ''],
    ['21s', lambda x: x, 'unknown11_31', "Unknown 11-31", "", ''],
    ['16s', lambda x: x.decode('UTF-8').strip(), 'serial_number', "Serial Number", "", ''],
    ['16s', lambda x: x.decode('UTF-8').strip(), 'boiler_name', "Boiler Name", "", ''],

]


def get_type_names():
    for n, x in enumerate(datamap):
        if isinstance(datamap[n][2], list):
            for sub_index, sub_value in enumerate(datamap[n][2]):
                type_name = datamap[n][2][sub_index]
                if type_name.startswith('unknown'):
                    continue
                yield type_name
        else:
            type_name = datamap[n][2]
            if type_name.startswith('unknown'):
                continue
            yield type_name
