import struct
import locale
import json


def byte_to_bit(input_value):
    return list(map(int, bin(input_value).lstrip('0b').rjust(8, '0')))


class Translator:
    def __init__(self):
        self.translations = {}
        with open("translations.json", "r") as read_file:
            json_data = json.load(read_file)
            self.translations = json_data['en']
            if locale.getlocale():
                two_letter_language = locale.getlocale()[0][:2]
                if two_letter_language in json_data:
                    self.translations = json_data[two_letter_language]

    def translate(self, to_translate, default=None):
        print(self.translations)
        print("trying to translate {}".format(to_translate))
        if to_translate in self.translations:
            print("Found translation {}".format(self.translations[to_translate]))
            return self.translations[to_translate]
        elif default:
            return default
        else:
            return to_translate


datamap = [
    #  Byte, int to value transl., variable name,
    ['h', lambda x: x * 0.01, 'flow_temp', "Flow temp.", "temps", 'ms'],
    ['h', lambda x: x * 0.01, 'return_temp', "Return temp.", "temps", 'ms'],
    ['h', lambda x: x * 0.01, 'dhw_in_temp', "Domestic hot water -in temp.", "temps_off", 'ms'],
    ['h', lambda x: x * 0.01, 'outside_temp', "Temperature outside", "temps", 'ms'],
    ['h', lambda x: x * 0.01, 'calorifier_temp', "Calorifier temp.", "temps", 'ms'],
    ['h', lambda x: x, 'dunno1', "dunno1", "unknowns", 'ms'],
    ['h', lambda x: x * 0.01, 'boiler_control_temp', "Boiler control temp.", "temps", 'ms'],
    ['h', lambda x: x * 0.01, 'room_temp', "Room temp.", "temps", 'ms'],  #
    ['h', lambda x: x * 0.01, 'cv_setpoint', "CV Setpoint", "temps", 'ms'],  # Vorlauftemperatursollwert Heizung
    ['h', lambda x: x * 0.01, 'dhw_setpoint', "Domestic hot water Setpoint", "temps", 'ms'],
    ['h', lambda x: x * 0.01, 'room_setpoint', "room temp. Setpoint", "temps", 'ms'],
    ['h', lambda x: x, 'airflow_setpoint', "Airflow setpoint", "flow", 'ms'],
    ['h', lambda x: x, 'airflow_actual', "Airflow actual", "flow", 'ms'],  # 24
    ['b', lambda x: x * 0.1, 'ionisation_current', "Ionisation Current", "current", 'ms'],  # 26
    ['h', lambda x: x * 0.01, 'intern_setpoint', "Internal Setpoint", "temps", 'ms'],  # 27
    ['b', lambda x: x, 'output', "output", "flow", 'ms'],  # 29
    ['b', lambda x: x, 'pump_speed', "Pump Speed", "flow", 'ms'],
    ['b', lambda x: x, 'dunno2', "dunno2", "unknown", 'ms'],  # 31
    ['b', lambda x: x, 'setpoint_power', "Setpoint power", "flow", 'ms'],
    ['b', lambda x: x, 'actual_power', "Actual Power", "flow", 'ms'],
    ['b', lambda x: x, 'dunno3', "dunno3", "unknown", 'ms'],
    ['b', lambda x: x, 'dunno4', "dunno4", "unknown", 'ms'],
    ['B', lambda x: byte_to_bit(x ^ 0b00010000),
     ['dwh_heat_demand', 'anti_legionella', 'dhw_blocking', 'DHW eco, boiler not kept warm', 'frost_protection',
      'heat_demand', 'modulating_controller_demand', 'modulating_controller'],
     ['DHW heat demand', 'Anti Legionella', 'DHW blocking', 'DHW eco', 'Frost protection', 'A/U warmtevraag',
      'On/off heat demand', 'Modulating Controller'],
     ["switch", "switch", "switch", "switch", "switch", "switch", "switch", "switch"],
     ['g', 'g', 'g', 'g', 'g', 'g', 'g', 'g'],
     ],
    ['B', lambda x: byte_to_bit(x ^ 0b00000011),
     ['dhw_enabled', 'ch_enabled', 'min_gas_pressure', 'unknown37.4', 'Flow switch for detecting DHW', 'ionisation',
      'release_input', 'shutdown_input'],
     ['dhw_enabled', 'ch_enabled', 'min_gas_pressure', 'unknown37.4', 'Flow switch for detecting DHW', 'ionisation',
      'release_input', 'shutdown_input'],
     ["switch", "switch", "switch", "switch", "switch", "switch", "switch", "switch"],
     ['g', 'g', 'g', 'g', 'g', 'g', 'g', 'g'],
     ],
    ['B', lambda x: byte_to_bit(x ^ 0b00000001),
     ['unknown38.7', 'ext_gas_valve', 'unknown38.5', 'ext_three_way_valve', 'three_way_valve', 'ignition',
      'unknown38.1', 'gas_valve'],
     ['unknown38.7', 'Extern. gas valve', 'unknown38.5', 'Extern. 3-way valve', 'Three way valve', 'ignition',
      'unknown38.1', 'gas_valve'],
     ["switch", "switch", "switch", "switch", "switch", "switch", "switch", "switch"],
     ['g', 'g', 'g', 'g', 'g', 'g', 'g', 'g'],
     ],
    ['B', lambda x: byte_to_bit(x),
     ['opentherm_smart_power', 'unknown39.6', 'unknown39.5', 'status_report', 'unknown39.3', 'ext_ch_pump',
      'calorifier_pump', 'pump'],
     ['OpenTherm Smart power', 'unknown39.6', 'unknown39.5', 'Status report', 'unknown39.3', 'Extern. CH pump',
      'Calorifier Pump', 'Pump'],
     ["switch", "switch", "switch", "switch", "switch", "switch", "switch", "switch"],
     ['g', 'g', 'g', 'g', 'g', 'g', 'g', 'g'],
     ],
    ['B', lambda x: x, 'status', "Status", "mapped", {0: 'Standby',
                                                      1: 'Kesselstart',
                                                      2: 'Brennerstart',
                                                      3: 'Brennen ZH',
                                                      4: 'Brennen BW',
                                                      5: 'Brennerstopp',
                                                      6: 'Kesselstopp',
                                                      7: '-',
                                                      8: 'Kontroll. Stopp',
                                                      9: 'Sperrmodus',
                                                      10: ' Störungsmod.',
                                                      11: 'Schornstein Modus N',
                                                      12: 'Schornstein Modus h',
                                                      13: 'Schornstein Modus H',
                                                      14: '-',
                                                      15: 'Manuelle Wärmeanforderung',
                                                      16: 'Kessel-Frostschutz',
                                                      17: 'Entlüften',
                                                      18: 'Temperaturschutz-Regler',
                                                      }],  # 40
    ['B', lambda x: x, 'locking', "Locking", "mapped", {
        0: "PSU nicht angeschlossen",
        1: "SU Parameter falsch",
        2: "T Wärmet. geschlossen",
        3: "T Wärmet. geöffnet",
        4: "T Wärmet. &lt; min.",
        5: "T Wärmet. &gt; max.",
        6: "T Rücklauf geschlossen",
        7: "T Rücklauf geöffnet",
        8: "T Rücklauf &lt; min.",
        9: "T Rücklauf &gt; max.",
        10: "dT(Wärmet.,Rückl.) &gt; max",
        11: "dT(Rückl.Wärmet.) &gt; max",
        12: "STB aktiviert",
        13: "-",
        14: "Start 5x erfolglos",
        15: "5x Fehler VPS-Test",
        16: "Falschflamme",
        17: "Fehler SU Gasv. Treiber",
        32: "T Vorlauf geschlossen",
        33: "T Vorlauf geöffnet",
        34: "Gebläse aus Regelbereich",
        35: "Rückl. über Vorl.Temp.",
        36: "5x Flamme aus",
        37: "SU Kommunikation",
        38: "SCU-S Kommunikation",
        39: "BL-Eingang als Störung",
        40: "-",
        41: "E11: Airbox temp. &gt; max.",
        42: "Low water pressure",
        43: "No gradient",
        45: "De-air test failed",
        50: "External PSU timeout",
        51: "Onboard PSU timeout",
        52: "GVC lockout",
        255: "Keine Störung"

    }],
    ['B', lambda x: x, 'blocking', "Blocking", "mapped", {
        0: "PCU Param. falsch",
        1: "T Vorlauf &gt; max.",
        2: "dT/s Vorlauf &gt;max.",
        3: "T Wärmet. &gt; max.",
        4: "dT/s Wärmet. &gt; max.",
        5: "dT(Wärmet.,Rückl.) &gt; max.",
        6: "dT(Vorl.,Wärmet.) &gt; max.",
        7: "dT(Vorl.,Rückl.) &gt; max.",
        8: "Kein Freigabesignal",
        9: "P-N gepr.",
        10: "Sperrsignal o. Frost",
        11: "Sperrsignal m. Frost",
        12: "HMI nicht verbunden",
        13: "SCU Kommunikation",
        14: "Min. Wasserdruck",
        15: "Min. Gasdruck",
        16: "Ident. SU falsch",
        17: "Ident. dF/dU Tab.-Fehler",
        18: "Ident. PSU falsch",
        19: "Ident. notw. dF/dU",
        20: "Identifikation läuft",
        21: "SU Kommunik. verloren",
        22: "Keine Flamme",
        23: "-",
        24: "Fehler bei VPS-Test",
        25: "Interner SU-Fehler",
        26: "Störung Bw tank - Fühler",
        27: "Störung BW in - Fühler",
        28: "Zurücksetzen...",
        29: "GVC parameter changed",
        30: "-",
        31: "-",
        32: "-",
        33: "-",
        34: "-",
        35: "-",
        36: "-",
        41: "-",
        43: "-",
        44: "-",
        45: "-",
        255: "Keine Sperre"
    }],  # 42
    ['B', lambda x: x, 'substatus', "Sub Status", "mapped", {0: "Standby",
                                                             1: "Wartezeit",
                                                             2: "Hydraulikventil öffnen",
                                                             3: "Pumpenstart",
                                                             4: "Warten auf Brennerstart",
                                                             5: "-",
                                                             6: "-",
                                                             7: "-",
                                                             8: "-",
                                                             9: "-",
                                                             10: "Externes Gasventil öffnen",
                                                             11: "Drehz. Gebl. zu Abg.vent.",
                                                             12: "Abgasvent. öffnen",
                                                             13: "Vorbelüften",
                                                             14: "Auf Freigabe warten",
                                                             15: "Brennerstart",
                                                             16: "VPS-Test",
                                                             17: "Vorzündung",
                                                             18: "Zündung",
                                                             19: "Kontrolle Flamme",
                                                             20: "Zwischenlüftung",
                                                             30: "Normal. intern. Sollwert",
                                                             31: "Begrenzt. intern. Sollw.",
                                                             32: "Normale Leistungsregelung",
                                                             33: "Gradient Regelstufe 1",
                                                             34: "Gradient Regelstufe 2",
                                                             35: "Gradient Regelstufe 3",
                                                             36: "Flammenschutz",
                                                             37: "Stabilisationszeit",
                                                             38: "Kaltstart",
                                                             39: "-",
                                                             40: "Brennerstop",
                                                             41: "Nachbelüftung",
                                                             42: "Drehz. Gebl. zu Abg.vent.",
                                                             43: "Abgasventil schließen",
                                                             44: "Gebläse stoppen",
                                                             45: "Ext. Gasventil schließen",
                                                             46: "-",
                                                             47: "-",
                                                             48: "-",
                                                             49: "-",
                                                             39: "-",
                                                             60: "Nachlauf Pumpe",
                                                             61: "Pumpe stoppen",
                                                             62: "Hydraulikventil schließen",
                                                             63: "Wartezeit starten",
                                                             255: "Wartezeit rücksetzen",
                                                             }],
    ['h', lambda x: x, 'fan_speed', "Fan speed", "flow", 'ms'],
    ['b', lambda x: x, 'su_state', "SU state", "unkown", 'ms'],
    ['b', lambda x: x, 'su_locking', "SU locking", "unkown", 'ms'],
    ['b', lambda x: x, 'su_blocking', "SU blocking", "unkown", 'ms'],
    ['b', lambda x: x * 0.1, 'hydr_pressure', "Hydr pressure", "flow", 'ms'],
    ['B', lambda x: byte_to_bit(x),
     ['dhw_timer_enable', 'ch_timer_enable', 'unknown50.5', 'unknown50.4', 'unknown50.3', 'unknown50.2', 'hru_active',
      'unknown50.0'],
     ['DHW Timer enable', 'CH Timer enable', 'unknown50.5', 'unknown50.4', 'unknown50.3', 'unknown50.2', 'HRU active',
      'unknown50.0'],
     ["switch", "switch", "switch", "switch", "switch", "switch", "switch", "switch"],
     ['g', 'g', 'g', 'g', 'g', 'g', 'g', 'g'],  # 50
     ],
    ['h', lambda x: x * 0.01, 'control_temp', "Control temp.", "temps", 'ms'],
    ['h', lambda x: x * 0.01, 'dhw_flow', "DHW flow", "flow", 'ms'],  # 53
    ['b', lambda x: x, 'dunno19', "dunno19", "unkown", 'ms'],  # 55
    ['h', lambda x: x * 0.1, 'solar_temp', "Solar temp.", "unkown", 'ms'],
    ['h', lambda x: x, 'HMI active', "HMI active", "unkown", 'ms'],
    ['b', lambda x: x, 'ch_setpoint_hmi', "CH setpoint HMI", "temps", 'ms'],  # 60
    ['b', lambda x: x, 'dhw_setpoint_hmi', "DHW setpoint HMI", "temps", 'ms'],
    ['b', lambda x: x, 'service_mode', "service_mode", "value", 'ms'],  # 62
    ['b', lambda x: x, 'serial_mode', "serial mode", "value", 'ms'],
    #    [00, lambda x: x, None, 'crc', 0, 'g'],
    #    [00, lambda x: x, None, 'stop', 0, 'g'],
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
    ['16s', lambda x: x, 'serial_number', "Serial Number", "", ''],
    ['16s', lambda x: x, 'boiler_name', "Boiler Name", "", ''],

]
