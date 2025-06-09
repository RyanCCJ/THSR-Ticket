from typing import Iterable

from thsr_ticket.model.db import Record
from thsr_ticket.model.web.booking_form.station_mapping import StationMapping


def history_info(hists: Iterable[Record], select: bool = True) -> int:
    for idx, r in enumerate(hists, 1):
        print("第{}筆紀錄".format(idx))
        if r.passenger_id != '':
            print("  乘客身分證字號(早鳥限定): " + r.passenger_id)
        print("  訂票人身分證字號: " + r.personal_id)
        print("  訂票人手機號碼: " + r.phone)
        if r.member_radio == 'radio56':
            print("  高鐵會員帳號: " + r.member_id)
        print("  起程站: " + StationMapping(r.start_station).name)
        print("  到達站: " + StationMapping(r.dest_station).name)
        t_str = r.outbound_time  # A:上午 P:下午 N:中午
        t_int = int(t_str[:-1])
        if t_str[-1] == "A" and (t_int // 100) == 12:
            t_int = "{:04d}".format(t_int % 1200)  # type: ignore
        elif t_int != 1230 and t_str[-1] == "P":
            t_int += 1200
        t_str = str(t_int)
        print("  出發時間: {}:{}".format(t_str[:-2], t_str[-2:]))
        print("  班次: " + r.train)
        print("  大人票數: " + r.adult_num[:-1])

    if select:
        sel = input("請選擇紀錄或是 Enter 跳過: ")
        return int(sel)-1 if sel != "" else None
    return None
