from requests.models import Response

from thsr_ticket.controller.confirm_train_flow import ConfirmTrainFlow
from thsr_ticket.controller.confirm_ticket_flow import ConfirmTicketFlow
from thsr_ticket.controller.first_page_flow import FirstPageFlow
from thsr_ticket.view_model.error_feedback import ErrorFeedback
from thsr_ticket.view_model.booking_result import BookingResult
from thsr_ticket.view.web.show_error_msg import ShowErrorMsg
from thsr_ticket.view.web.show_booking_result import ShowBookingResult
from thsr_ticket.view.common import history_info
from thsr_ticket.model.db import ParamDB, Record
from thsr_ticket.remote.http_request import HTTPRequest


class BookingFlow:
    def __init__(self, db_path: str = None, record_idx: int = 0, OCR: bool = False) -> None:
        self.client = HTTPRequest()
        self.db = ParamDB(db_path)
        self.record = Record()
        self.record_idx = record_idx
        self.config = True if db_path else False
        self.OCR = OCR

        self.error_feedback = ErrorFeedback()
        self.show_error_msg = ShowErrorMsg()

    def run(self) -> Response:
        self.show_history(self.record_idx)

        # First page. Booking options
        book_resp, book_model = FirstPageFlow(self.client, self.record, self.config, self.OCR).run()
        if self.show_error(book_resp.content):
            return book_resp

        # Second page. Train confirmation
        train_resp, train_model = ConfirmTrainFlow(self.client, book_resp, self.record).run()
        if self.show_error(train_resp.content):
            return train_resp
        
        # Final page. Ticket confirmation
        ticket_resp, ticket_model = ConfirmTicketFlow(self.client, train_resp, self.record).run()
        if self.show_error(ticket_resp.content):
            return ticket_resp

        # Result page.
        result_model = BookingResult().parse(ticket_resp.content)
        book = ShowBookingResult()
        book.show(result_model)
        print("\n請使用官方提供的管道完成後續付款以及取票!!")

        self.db.save(book_model, train_model, ticket_model)
        return ticket_resp

    def show_history(self, record_idx: int = 0) -> None:
        hist = self.db.get_history()
        if not hist:
            return
        h_idx = history_info(hist, select=record_idx)
        if h_idx is not None:
            self.record = hist[h_idx]

    def show_error(self, html: bytes) -> bool:
        errors = self.error_feedback.parse(html)
        if len(errors) == 0:
            return False

        self.show_error_msg.show(errors)
        return True
