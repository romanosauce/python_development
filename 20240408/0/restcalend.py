import calendar
import sys

cur_calend = calendar.month(int(sys.argv[1]), int(sys.argv[2])).split('\n')
re_calend = f".. table:: {cur_calend[0].strip()}\n\n"
re_calend += f'    {"== "*7}\n    {cur_calend[1]}\n'
re_calend += f'    {"== "*7}\n'
for i in range(2, 7):
    re_calend += f'    {cur_calend[i]}\n'
re_calend += f'    {"== "*7}'
print(re_calend)
