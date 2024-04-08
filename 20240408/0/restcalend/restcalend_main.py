"""it is useless module"""

import calendar


def calend_to_rst(year, month):
    cur_calend = calendar.month(year, month).split('\n')
    re_calend = f".. table:: {cur_calend[0].strip()}\n\n"
    re_calend += f'    {"== "*7}\n    {cur_calend[1]}\n'
    re_calend += f'    {"== "*7}\n'
    for i in range(2, 7):
        re_calend += f'    {cur_calend[i]}\n'
    re_calend += f'    {"== "*7}'
    return re_calend

print(1)
