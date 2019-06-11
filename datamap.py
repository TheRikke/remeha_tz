import struct

#fmt = '<13hbh7b4B11bhh9b'

byte_to_bit = lambda x: list(map(int, bin(x).lstrip('0b').rjust(8,'0')))

datamap = [
#  Byte, int to value transl., variable name,
    [ 'h', lambda x: x*0.01, 'flow_temp', "Flow temp.", "temps", 'ms'],
    [ 'h', lambda x: x*0.01, 'return_temp', "Return temp.", "temps", 'ms'],
    [ 'h', lambda x: x*0.01, 'dhw_in_temp', "Domestic hot water -in temp.", "temps", 'ms'],
    [ 'h', lambda x: x*0.01, 'outside_temp', "outside temp.", "temps", 'ms'],
    [ 'h', lambda x: x*0.01, 'calorifier_temp', "Calorifier temp.", "temps", 'ms'],
    [ 'h', lambda x: x, 'dunno1', "dunno1", "unknowns", 'ms'],
    [ 'h', lambda x: x*0.01, 'boiler_control_temp', "Boiler control temp.", "temps", 'ms'],
    [ 'h', lambda x: x*0.01, 'room_temp', "Room temp.", "temps", 'ms'],                #
    [ 'h', lambda x: x*0.01, 'cv_setpoint', "CV Setpoint", "temps", 'ms'],             # Vorlauftemperatursollwert Heizung
    [ 'h', lambda x: x*0.01, 'dhw_setpoint', "Domestic hot water Setpoint", "temps", 'ms'],
    [ 'h', lambda x: x*0.01, 'room_setpoint', "room temp. Setpoint", "temps", 'ms'],
    [ 'h', lambda x: x, 'airflow_setpoint', "Airflow setpoint", "flow", 'ms'],
    [ 'h', lambda x: x, 'airflow_actual', "Airflow actual", "flow", 'ms'],                                                          #24
    [ 'b', lambda x: x*0.1, 'ionisation_current', "Ionisation Current", "current", 'ms'],                                           #26
    [ 'h', lambda x: x*0.01, 'intern_setpoint', "Internal Setpoint", "temps", 'ms'],                                                #27
    [ 'b', lambda x: x, 'output', "output", "flow", 'ms'],                                                                          #29
    [ 'b', lambda x: x, 'pump_speed', "Pump Speed", "flow", 'ms'],
    [ 'b', lambda x: x, 'dunno2', "dunno2", "unknown", 'ms'],                                                                       #31
    [ 'b', lambda x: x, 'setpoint_power', "Setpoint power", "flow", 'ms'],
    [ 'b', lambda x: x, 'actual_power', "Actual Power", "flow", 'ms'],
    [ 'b', lambda x: x, 'dunno3', "dunno3", "unknown", 'ms'],
    [ 'b', lambda x: x, 'dunno4', "dunno4", "unknown", 'ms'],
    [ 'B', lambda x: byte_to_bit(x ^ 0b00010000),
        ['DHW heat demand', 'anti_legionella', 'DHW blocking', 'DHW eco, boiler not kept warm', 'Frost protection', 'On/off heat demand', 'modulating_controller_demand', 'modulating_controller'],
        ['WW warmtevraag', 'Anti Legionella', 'WW blokkering', 'WW eco', 'Vorstbeveiliging', 'A/U warmtevraag', 'Mod. warmtevraag', 'Mod. regelaar'],
        ["switch", "switch", "switch", "switch", "switch", "switch", "switch", "switch"],
        ['g', 'g', 'g', 'g', 'g', 'g', 'g', 'g'],
    ],
    [ 'B', lambda x: byte_to_bit(x ^ 0b00000011),
        ['dhw_enabled', 'ch_enabled', 'min_gas_pressure', 'unknown37.4', 'Flow switch for detecting DHW', 'ionisation', 'release_input', 'shutdown_input'],
        ['dhw_enabled', 'ch_enabled', 'min_gas_pressure', 'unknown37.4', 'Flow switch for detecting DHW', 'ionisation', 'release_input', 'shutdown_input'],
        ["switch", "switch", "switch", "switch", "switch", "switch", "switch", "switch"],
        ['g', 'g', 'g', 'g', 'g', 'g', 'g', 'g'],
    ],
    ['B', lambda x: byte_to_bit(x ^ 0b00000001),
        ['unknown38.7', 'ext_gas_valve', 'unknown38.5', 'ext_three_way_valve', 'three_way_valve', 'ignition', 'unknown38.1', 'gas_valve'],
        ['unknown38.7', 'Extern. gas valve', 'unknown38.5', 'Extern. 3-way valve', 'Three way valve', 'ignition', 'unknown38.1', 'gas_valve'],
        ["switch", "switch", "switch", "switch", "switch", "switch", "switch", "switch"],
        ['g', 'g', 'g', 'g', 'g', 'g', 'g', 'g'],
    ],
    ['B', lambda x: byte_to_bit(x),
        ['opentherm_smart_power', 'unknown39.6', 'unknown39.5', 'status_report', 'unknown39.3', 'ext_ch_pump', 'calorifier_pump', 'pump'],
        ['OpenTherm Smart power', 'unknown39.6', 'unknown39.5', 'Status report', 'unknown39.3', 'Extern. CH pump', 'Calorifier Pump', 'Pump'],
        ["switch", "switch", "switch", "switch", "switch", "switch", "switch", "switch"],
        ['g', 'g', 'g', 'g', 'g', 'g', 'g', 'g'],
    ],
    [ 'b', lambda x: x, 'status', "Status", "mapped", 'g'],                                    #40
    [ 'b', lambda x: x, 'locking', "Locking", "mapped", 'g'],
    [ 'b', lambda x: x, 'blocking', "Blocking", "mapped", 'g'],                        #42
    [ 'b', lambda x: x, 'substatus', "Sub Status", "mapped", 'g'],
    [ 'h', lambda x: x, 'fan_speed', "Fan speed", "flow", 'ms'],
    [ 'b', lambda x: x, 'su_state', "SU state", "unkown", 'ms'],
    [ 'b', lambda x: x, 'su_locking', "SU locking", "unkown", 'ms'],
    [ 'b', lambda x: x, 'su_blocking', "SU blocking", "unkown", 'ms'],
    [ 'b', lambda x: x*0.1, 'hydr_pressure' ,"Hydr pressure", "flow", 'ms'],
    [ 'B', lambda x: byte_to_bit(x),
        ['dhw_timer_enable', 'ch_timer_enable', 'unknown50.5', 'unknown50.4', 'unknown50.3', 'unknown50.2', 'hru_active', 'unknown50.0'],
        ['DHW Timer enable', 'CH Timer enable', 'unknown50.5', 'unknown50.4', 'unknown50.3', 'unknown50.2', 'HRU active', 'unknown50.0'],
        ["switch", "switch", "switch", "switch", "switch", "switch", "switch", "switch"],
        ['g', 'g', 'g', 'g', 'g', 'g', 'g', 'g'],                                               #50
    ],
    [ 'h', lambda x: x*0.01, 'control_temp', "Control temp.", "temps", 'ms'],
    [ 'h', lambda x: x*0.01, 'dhw_flow', "DHW flow", "flow", 'ms'],                       #53
    [ 'b', lambda x: x, 'dunno19', "dunno19", "unkown", 'ms'],                           #55
    [ 'h', lambda x: x*0.1, 'solar_temp', "Solar temp.", "unkown", 'ms'],
    [ 'h', lambda x: x, 'HMI active', "HMI active", "unkown", 'ms'],
    [ 'b', lambda x: x, 'ch_setpoint_hmi', "CH setpoint HMI", "temps", 'ms'],                                  #60
    [ 'b', lambda x: x, 'dhw_setpoint_hmi', "DHW setpoint HMI", "temps", 'ms'],
    [ 'b', lambda x: x, 'service_mode', "service_mode", "value", 'ms'],                              #62
    [ 'b', lambda x: x, 'serial_mode', "serial mode", "value", 'ms'],
#    [00, lambda x: x, None, 'crc', 0, 'g'],
#    [00, lambda x: x, None, 'stop', 0, 'g'],
]
