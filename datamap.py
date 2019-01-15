import struct

fmt = '<bhbbh'+'13hbh7b4B11bhh9b'+'hb'

byte_to_bit = lambda x: map(int, bin(x).lstrip('0b').rjust(8,'0'))

datamap = [
    [00, lambda x: x, None, 'start', 0, 'g'],
    [00, lambda x: x, None, '', 0, 'g'],
    [00, lambda x: x, None, '', 0, 'g'],
    [00, lambda x: x, None, '', 0, 'g'],
    [00, lambda x: x, None, '', 0, 'g'],
    [ 0, lambda x: x*0.01, 'aanvoer_temp', "Aanvoer temp.", 0, 'ms'],
    [ 2, lambda x: x*0.01, 'retour_temp', "Retour temp.", 0, 'ms'],
    [ 4, lambda x: x*0.01, 'zonneboiler_temp', "Zonneboiler temp.", 0, 'ms'],
    [ 6, lambda x: x*0.01, 'buiten_temp', "Buiten temp.", 0, 'ms'],
    [ 8, lambda x: x*0.01, 'boiler_temp', "Boiler temp.", 0, 'ms'],
    [10, lambda x: x, 'dunno1', "?", 0, 'ms'],
    [12, lambda x: x*0.01, 'automaat_temp', "Automaat temp.", 0, 'ms'],
    [14, lambda x: x*0.01, 'ruimte_temp', "Ruimte temp.", 0, 'ms'],
    [16, lambda x: x*0.01, 'cv_setpoint', "CV Setpunt", 0, 'ms'],
    [18, lambda x: x*0.01, 'ww_setpoint', "WW Setpunt", 0, 'ms'],
    [20, lambda x: x*0.01, 'ruimte_setpoint', "Ruimte setpunt", 0, 'ms'],
    [22, lambda x: x, 'ventilator_setpoint', "Ventilator setpunt", 0, 'ms'],
    [24, lambda x: x, 'ventilator_toeren', "Ventilator toeren", 0, 'ms'],
    [26, lambda x: x*0.1, 'ionisatie_stroom', "Ionisatie stroom", 0, 'ms'],
    [27, lambda x: x*0.01, 'intern_setpoint', "Intern setpunt", 0, 'ms'],
    [29, lambda x: x, 'beschikbaar_vermogen', "Beschikb. vermogen", 0, 'ms'],
    [30, lambda x: x, 'pomp', "Pomp", 0, 'ms'],
    [31, lambda x: x, 'dunno2', "?", 0, 'ms'],
    [32, lambda x: x, 'gewenst_vermogen', "Gewenst vermogen", 0, 'ms'],
    [33, lambda x: x, 'geleverd_vermogen', "Geleverd vermogen", 0, 'ms'],
    [34, lambda x: x, 'dunno3', "?", 0, 'ms'],
    [35, lambda x: x, 'dunno4', "?", 0, 'ms'],
    [36, 
        lambda x: byte_to_bit(x ^ 0b00010000),
        ['ww_warmtevraag', 'anti_legionella', 'ww_blokkering', 'ww_eco', 'vorstbeveiliging', 'au_warmtevraag', 'mod_warmtevraag', 'mod_regelaar'],
        ['WW warmtevraag', 'Anti Legionella', 'WW blokkering', 'WW eco', 'Vorstbeveiliging', 'A/U warmtevraag', 'Mod. warmtevraag', 'Mod. regelaar'],
        [0,0,0,0,0,0,0,0], 
        ['g', 'g', 'g', 'g', 'g', 'g', 'g', 'g'], 
    ],
    [37, 
        lambda x: byte_to_bit(x ^ 0b00000011),
        ['ww_vrijgave', 'cv_vrijgave', 'min_gasdruk', 'tapschakelaar', '', 'ionisatie', 'vrijgave_ingang', 'blokkerende_ingang'],
        ['', '', '', '', '', '', '', ''],
        [0,0,0,0,0,0,0,0], 
        ['g', 'g', 'g', 'g', 'g', 'g', 'g', 'g'], 
    ],
#byte="37" bit="0" expression="A" invert="true" id="open.closed.code" "Blokkerende ingang"
#byte="37" bit="1" expression="A" invert="true" id="open.closed.code" "Vrijgave ingang"
#byte="37" bit="2" expression="A" invert="false" id="no.yes.code" "Ionisatie"
#byte="37" bit="3" expression="A" invert="false" id="open.closed.code" "Tapschakelaar"
#byte="37" bit="5" expression="A" invert="false" id="open.closed.code" "Min. gasdruk"
#byte="37" bit="6" expression="A" invert="false" id="no.yes.code" "CV vrijgave"
#byte="37" bit="7" expression="A" invert="false" id="no.yes.code" "WW vrijgave"
    [38, lambda x: x, 'bitmap3', "bitmap", 0, 'g'],
#byte="38" bit="0" expression="A" invert="true" id="closed.open.code" "Gasklep"
#byte="38" bit="2" expression="A" invert="false" id="off.on.code" "Ontsteking"
#byte="38" bit="3" expression="A" invert="false" value="0" result.nr="CV" selection value="1" result.nr="WW" "Driewegklep"
#byte="38" bit="4" expression="A" invert="false" id="open.closed.code" "Externe driewegklep"
#byte="38" bit="6" expression="A" invert="false" id="open.closed.code" "Externe gasklep"
    [39, lambda x: x, 'bitmap4', "bitmap", 0, 'g'],
#byte="39" bit="0" expression="A" invert="false" id="off.on.code" "Pomp"
#byte="39" bit="1" expression="A" invert="false" id="open.closed.code" "Boilerpomp"
#byte="39" bit="2" expression="A" invert="false" id="off.on.code" "Externe CV pomp"
#byte="39" bit="4" expression="A" invert="false" id="open.closed.code" "Status melding"
#byte="39" bit="7" expression="A" invert="false" id="off.on.code" "OT Smart power"
    [40, lambda x: x, 'status', "Status", 0, 'g'],
    [41, lambda x: x, 'vergrendeling_e', "Vergrendeling E", 0, 'g'],
    [42, lambda x: x, 'blokkering_b', "Blokkering b", 0, 'g'],
    [43, lambda x: x, 'substatus', "Sub-Status", 0, 'g'],
    [44, lambda x: x, 'dunno5', "?", 0, 'ms'],
    [45, lambda x: x, 'dunno6', "?", 0, 'ms'],
    [46, lambda x: x, 'dunno7', "?", 0, 'ms'],
    [47, lambda x: x, 'dunno8', "?", 0, 'ms'],
    [48, lambda x: x, 'dunno9', "?", 0, 'ms'],
    [49, lambda x: x*0.1, 'waterdruk' ,"Waterdruk", 0, 'ms'],
    [50, lambda x: x, 'bitmap5', "bitmap", 0, 'g'],
    [51, lambda x: x*0.01, 'regel_temp', "Regel temp.", 0, 'ms'],
    [53, lambda x: x*0.01, 'tapdebiet', "Tapdebiet", 0, 'ms'],
    [00, lambda x: x, 'dunno19', "?", 0, 'ms'],
    [00, lambda x: x, 'dunno29', "?", 0, 'ms'],
    [00, lambda x: x, 'dunno39', "?", 0, 'ms'],
    [00, lambda x: x, 'dunno49', "?", 0, 'ms'],
    [00, lambda x: x, 'dunno59', "?", 0, 'ms'],
    [00, lambda x: x, 'dunno59', "?", 0, 'ms'],
    [00, lambda x: x, 'dunno59', "?", 0, 'ms'],
    [00, lambda x: x, 'dunno59', "?", 0, 'ms'],
    [00, lambda x: x, 'dunno59', "?", 0, 'ms'],
    [00, lambda x: x, None, 'crc', 0, 'g'],
    [00, lambda x: x, None, 'stop', 0, 'g'],
]
