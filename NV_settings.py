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
