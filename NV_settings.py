damper_closed={
    "status": "CLOSED",
    "line_color_v": '#000000',
    "line_color_f": 'THEMEGUARD(RGB(0,0,0))'
}
damper_open={
    "status": "OPEN",
    "line_color_v": '#ffffff',
    "line_color_f": 'THEMEGUARD(RGB(255,255,255))'
}
damper_unknown={
    "status": "STATUS?",
    "line_color_v": '#ffff00',
    "line_color_f": 'THEMEGUARD(RGB(255,255,0))'
}
damper_settings={
    "CLOSED": damper_closed,
    "OPEN": damper_open,
    None: damper_unknown
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
fan_settings={
    "on": fan_on,
    "off": fan_off,
    "unknown":fan_unknown,
    1:  fan_exhaust,
    -1: fan_supply
}
