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
    "FillForegnd_V":'#000000',
    "FillForegnd_F":'THEMEGUARD(RGB(0,0,0))'
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
