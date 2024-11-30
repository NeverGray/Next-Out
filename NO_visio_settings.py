# Project Name: Next-Out
# Description: List of different settings to display Visio templates.
# Copyright (c) 2024 Justin Edenbaum, Never Gray
#
# This file is licensed under the MIT License.
# You may obtain a copy of the license at https://opensource.org/licenses/MIT

damper_closed={
    "LineColor_V": '#000000',
    "LineColor_F": 'THEMEGUARD(RGB(0,0,0))'
}
damper_open={
    "LineColor_V": '#ffffff',
    "LineColor_F": 'THEMEGUARD(RGB(255,255,255))'
}
damper_unknown={
    "LineColor_V": '#ffff00',
    "LineColor_F": 'THEMEGUARD(RGB(255,255,0))'
}
damper_settings={
    "CLOSED": damper_closed,
    "OPEN": damper_open,
    "STATUS?": damper_unknown
}
fan_on={
    "FillPattern_V":'1',
    "FillForegnd_V":'#00b050',
    "FillForegnd_F":'THEMEGUARD(RGB(0,176,80))'
}
fan_unknown={
    "FillPattern_V":'1',
    "FillForegnd_V":'#ffffff',
    "FillForegnd_F":'THEMEGUARD(RGB(255,255,255))'
}
fan_off={
    "FillPattern_V":'0',
    "FillForegnd_V":'#ffffff',
    "FillForegnd_F":'THEMEGUARD(RGB(255,255,255))'
}
fan_exhaust={
    "BeginArrow_V":'1',
    "EndArrow_V"  :'0'
}
fan_supply={
    "BeginArrow_V":'0',
    "EndArrow_V"  :'1'
}
fan_arrow_off={
    "BeginArrow_V":'0',
    "EndArrow_V"  :'0'
}
fan_settings={
    "on": fan_on,
    "off": fan_off,
    "unknown":fan_unknown,
    1:  fan_exhaust,
    -1: fan_supply,
    "fan_arrow_off" : fan_arrow_off
}
jet_fan_on={
    'FillForegnd_V': '#00b050',
    'fillForegnd_F': 'THEMEGUARD(RGB(0,176,80))'
}
jet_fan_off={
    'FillForegnd_V': '#ffffff',
    'fillForegnd_F': 'THEMEGUARD(RGB(255,255,255))'
}
jet_fan_power={
    'on':jet_fan_on,
    'off':jet_fan_off
}

line_black={
    'LineColor_V': '#000000',
    'LineColor_F': 'THEMEGUARD(RGB(0,0,0)'
}

line_white={
    'LineColor_V': '#ffffff',
    'LineColor_F': 'THEMEGUARD(RGB(255,255,255)'
}
train_fire_values={
    True : '0',
    False : '1', 
    'unknown': '0.75'
}
train_fire_settings ={
    "FillForegndTrans": 'V',
    "FillBkgndTrans": 'V'
}

train_fire_names = [".//Visio:Shape[@Name='Fire']",".//Visio:Shape[@Name='Train']"]
