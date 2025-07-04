import io
import json
from PIL import Image
from typing import Tuple
from datetime import date, timedelta

from bs4 import BeautifulSoup
from requests.models import Response

from thsr_ticket.view_model.error_feedback import ErrorFeedback
from thsr_ticket.ml.captcha import preprocess, predict

from thsr_ticket.model.db import Record
from thsr_ticket.remote.http_request import HTTPRequest
from thsr_ticket.configs.web.param_schema import BookingModel
from thsr_ticket.configs.web.parse_html_element import BOOKING_PAGE
from thsr_ticket.configs.web.enums import StationMapping, TicketType
from thsr_ticket.configs.common import (
    AVAILABLE_TIME_TABLE,
    DAYS_BEFORE_BOOKING_AVAILABLE,
    MAX_TICKET_NUM,
    MAX_TRIES,
)


class FirstPageFlow:
    def __init__(self, client: HTTPRequest, record: Record = None, config: bool = False, OCR: bool = False) -> None:
        self.client = client
        self.record = record
        self.config = config
        self.OCR = OCR
        self.error_feedback = ErrorFeedback()
        self.book_model = None
        self.retries = 1
    
    def _prepare_form(self) -> None:
        print('請稍等...')
        book_page = self.client.request_booking_page().content
        img_resp = self.client.request_security_code_img(book_page).content
        page = BeautifulSoup(book_page, features='html.parser')
        self.book_model = BookingModel(
            start_station=self.select_station('啟程'),
            dest_station=self.select_station('到達', default_value=StationMapping.Zuouing.value),
            outbound_date=self.select_date('出發'),
            outbound_time=self.select_time('啟程'),
            adult_ticket_num=self.select_ticket_num(TicketType.ADULT),
            seat_prefer=_parse_seat_prefer_value(page),
            types_of_trip=_parse_types_of_trip_value(page),
            search_by=_parse_search_by(page),
            security_code=_input_security_code(img_resp, self.OCR),
        )

    def run(self) -> Tuple[Response, BookingModel]:
        # First page. Booking options
        self._prepare_form()

        json_params = self.book_model.json(by_alias=True)
        dict_params = json.loads(json_params)
        self.resp = self.client.submit_booking_form(dict_params)

        while not self.valid_security_code(self.resp.content):
            if self.retries == MAX_TRIES:
                print(f'驗證碼輸入錯誤達上限{MAX_TRIES}次')
                break
            print('驗證碼輸入錯誤，重新嘗試...')
            self.OCR = False
            self.retry_submission()
            self.retries += 1

        return self.resp, self.book_model

    def select_station(self, travel_type: str, default_value: int = StationMapping.Taipei.value) -> int:
        if (
            self.record
            and (
                station := {
                    '啟程': self.record.start_station,
                    '到達': self.record.dest_station,
                }.get(travel_type)
            )
        ):
            return station

        print(f'選擇{travel_type}站：')
        for station in StationMapping:
            print(f'{station.value}. {station.name}')

        return int(
            input(f'輸入選擇(預設: {default_value})：')
            or default_value
        )

    def select_date(self, date_type: str) -> str:
        if self.config and self.record and (date_str := self.record.date):
            return date_str
        
        today = date.today()
        weekday = today.strftime('%A')
        if weekday == 'Friday':
            shift = 2
        elif weekday == 'Saturday':
            shift = 1
        else:
            shift = 0
        last_avail_date = today + timedelta(days=DAYS_BEFORE_BOOKING_AVAILABLE+shift)
        print(f'選擇{date_type}日期（{today}~{last_avail_date}）（預設為今日）：')
        return input() or str(today)

    def select_time(self, time_type: str, default_value: int = 17) -> str:
        if self.record and (
            time_str := {
                '啟程': self.record.outbound_time,
                '回程': None,
            }.get(time_type)
        ):
            return time_str

        print('選擇出發時間：')
        for idx, t_str in enumerate(AVAILABLE_TIME_TABLE):
            t_int = int(t_str[:-1])
            if t_str[-1] == "A" and (t_int // 100) == 12:
                t_int = "{:04d}".format(t_int % 1200)  # type: ignore
            elif t_int != 1230 and t_str[-1] == "P":
                t_int += 1200
            t_str = str(t_int)
            print(f'{idx+1}. {t_str[:-2]}:{t_str[-2:]}')

        selected_opt = int(input(f'輸入選擇（預設：{default_value}）：') or default_value)
        return AVAILABLE_TIME_TABLE[selected_opt-1]

    def select_ticket_num(self, ticket_type: TicketType, default_ticket_num: int = 1) -> str:
        if self.record and (
            ticket_num_str := {
                TicketType.ADULT: self.record.adult_num,
                TicketType.CHILD: None,
                TicketType.DISABLED: None,
                TicketType.ELDER: None,
                TicketType.COLLEGE: None,
            }.get(ticket_type)
        ):
            return ticket_num_str

        ticket_type_name = {
            TicketType.ADULT: '成人',
            TicketType.CHILD: '孩童',
            TicketType.DISABLED: '愛心',
            TicketType.ELDER: '敬老',
            TicketType.COLLEGE: '大學生',
        }.get(ticket_type)

        print(f'選擇{ticket_type_name}票數（0~{MAX_TICKET_NUM}）（預設：{default_ticket_num}）')
        ticket_num = int(input() or default_ticket_num)
        return f'{ticket_num}{ticket_type.value}'
    
    def valid_security_code(self, html: bytes) -> bool:
        errors = self.error_feedback.parse(html)
        if len(errors) == 0:
            return True
        return False
    
    def retry_submission(self):
        self._prepare_form()
        json_params = self.book_model.json(by_alias=True)
        dict_params = json.loads(json_params)
        self.resp = self.client.submit_booking_form(dict_params)


def _parse_seat_prefer_value(page: BeautifulSoup) -> str:
    options = page.find(**BOOKING_PAGE["seat_prefer_radio"])
    preferred_seat = options.find_next(selected='selected')
    return preferred_seat.attrs['value']


def _parse_types_of_trip_value(page: BeautifulSoup) -> int:
    options = page.find(**BOOKING_PAGE["types_of_trip"])
    tag = options.find_next(selected='selected')
    return int(tag.attrs['value'])


def _parse_search_by(page: BeautifulSoup) -> str:
    candidates = page.find_all('input', {'name': 'bookingMethod'})
    tag = next((cand for cand in candidates if 'checked' in cand.attrs))
    return tag.attrs['value']


def _input_security_code(img_resp: bytes, OCR: bool = False) -> str:
    image = Image.open(io.BytesIO(img_resp))
    if OCR:
        image = preprocess(image)
        text = predict(image)
        print(f'自動輸入驗證碼：{text}')
        return text
    else:
        print('輸入驗證碼：')
        image.show()
        return input()
