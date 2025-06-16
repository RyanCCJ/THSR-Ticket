import sys
import argparse
sys.path.append("./")

from thsr_ticket.remote.endpoint_client import EndpointClient
from thsr_ticket.model.json.v1.train import Train
from thsr_ticket.controller.booking_flow import BookingFlow

def parse_arguments():
    parser = argparse.ArgumentParser(description="THSR Ticket Booking System")
    parser.add_argument(
        "--config", "-C",
        type=str,
        help="Path to the configuration file"
    )
    parser.add_argument(
        "--record", "-R",
        type=int,
        help="Index of the record to use for booking",
        default=0,
    )
    parser.add_argument(
        "--OCR", "-O",
        action='store_true',
        help="Use OCR model to predict captcha"
    )
    return parser.parse_args()

def main(config_path=None, record_idx=None, OCR=False):
    if config_path:
        print(f"Using configuration file: {config_path}")
    else:
        print("No configuration file provided. Using default settings.")
    
    flow = BookingFlow(db_path=config_path, record_idx=record_idx, OCR=OCR)
    flow.run()


if __name__ == "__main__":
    #client = EndpointClient()
    #resp = client.get_trains_by_date("2020-01-25")
    #train = Train().from_json(resp[0])

    args = parse_arguments()
    main(args.config, args.record, args.OCR)
