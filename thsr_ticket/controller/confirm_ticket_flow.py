import json
from typing import Tuple

from bs4 import BeautifulSoup
from requests.models import Response
from thsr_ticket.configs.web.param_schema import ConfirmTicketModel

from thsr_ticket.model.db import Record
from thsr_ticket.remote.http_request import HTTPRequest


class ConfirmTicketFlow:
    def __init__(self, client: HTTPRequest, train_resp: Response, record: Record = None):
        self.client = client
        self.train_resp = train_resp
        self.record = record
        self.personal_id = ''
        self.member_radio = 0

    def run(self) -> Tuple[Response]:
        page = BeautifulSoup(self.train_resp.content, features='html.parser')
        ticket_model = ConfirmTicketModel(
            personal_id=self.set_personal_id(),
            phone_num=self.set_phone_num(),
            passenger_id=self.set_passenger_id(page),
            member_radio=self.set_member_radio(page),
            member_id=self.set_member_id(),
        )

        json_params = ticket_model.json(by_alias=True)
        dict_params = json.loads(json_params)
        resp = self.client.submit_ticket(dict_params)
        return resp, ticket_model

    def set_personal_id(self) -> str:
        if self.record and (personal_id := self.record.personal_id):
            self.personal_id = personal_id
        else:
            self.personal_id = input(f'輸入身分證字號：\n')
        return self.personal_id

    def set_phone_num(self) -> str:
        if self.record and (phone_num := self.record.phone):
            return phone_num

        if phone_num := input('輸入手機號碼：\n'):
            return phone_num
        return ''
    
    def set_passenger_id(self, page: BeautifulSoup) -> str:
        passenger_ids = page.find(
            'input',
            attrs={
                'name': lambda x: x in [
                    'TicketMemberSystemInputPanel:TakerMemberSystemDataView:memberSystemRadioGroup:memberShipNumber',  # general
                    'TicketPassengerInfoInputPanel:passengerDataView:0:passengerDataView2:passengerDataIdNumber'  # discount
                    ]
            },
        )
        if passenger_ids is None:
            return ''
        if self.record and (passenger_id := self.record.passenger_id):
            return passenger_id
        if passenger_id := input(f'輸入乘客身分證字號（預設：{self.personal_id}）：\n'):
            return passenger_id
        return self.personal_id

    def set_member_radio(self, page: BeautifulSoup, default_value: int = 1) -> str:
        candidates = page.find_all(
            'input',
            attrs={
                'name': 'TicketMemberSystemInputPanel:TakerMemberSystemDataView:memberSystemRadioGroup'
            },
        )
        if candidates is None:
            return 0
        if self.record and (member_radio := self.record.member_radio):
            radio_table = {1: 0, 2: 2, 3: 5}
            if member_radio in radio_table.keys():
                self.member_radio = member_radio
                base_num = int(candidates[0].attrs['value'].replace('radio',''))
                return f'radio{base_num + radio_table[member_radio]}'
            else:
                print('會員選項須為 1 (非會員)、2 (TGo 會員)、3 (企業會員)，請重新選擇。')
        
        print('選擇高鐵會員資訊：')
        print('1. 非高鐵會員 TGo／企業會員')
        print('2. 高鐵會員 TGo 帳號')
        print('3. 企業會員統編（暫不支援）')
        self.member_radio = int(input(f'輸入選擇（預設：{default_value}）：') or default_value)
        return candidates[self.member_radio-1].attrs['value']
    
    def set_member_id(self) -> str:
        if self.member_radio != 2:
            return ''
        if self.record and (member_id := self.record.member_id):
            return member_id
        if member_id := input(f'輸入身分證字號/會員卡號/手機號碼(已認證)（預設：{self.personal_id}）：\n'):
            return member_id
        return self.personal_id
