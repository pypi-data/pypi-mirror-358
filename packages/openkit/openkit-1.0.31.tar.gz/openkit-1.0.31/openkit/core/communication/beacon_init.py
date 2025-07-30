from typing import TYPE_CHECKING

import openkit.core.communication as comm
from .state_utils import send_status_request

if TYPE_CHECKING:
    from ...core.beacon_sender import BeaconSendingContext


class BeaconSendingInitState(comm.AbstractBeaconSendingState):
    STATUS_CHECK_INTERVAL = 2 * 60 * 60 * 1000
    MAX_INITIAL_STATUS_REQUEST_RETRIES = 5
    INITIAL_RETRY_SLEEP_TIME_MILLISECONDS = 1000
    REINIT_DELAY_MILLISECONDS = [
        1 * 60 * 1000,  # 1 minute
        5 * 60 * 1000,  # 5 minutes
        15 * 60 * 1000,  # 15 minutes
        1 * 60 * 60 * 1000,  # 1 hour
        2 * 60 * 60 * 1000,  # 2 hours
    ]

    def __init__(self):
        super().__init__()
        self.terminal = False
        self.reinitialize_delay_index = 0

    def do_execute(self, context: "BeaconSendingContext"):
        r = self.execute_status_request(context)

        if context.shutdown_requested:
            context.init_completed(False)
        elif r.is_ok_response():
            context.handle_response(r)
            context.next_state = comm.BeaconSendingCaptureOnState() if context.capture_on else comm.BeaconSendingCaptureOffState()
            context.init_completed(True)

    def execute_status_request(self, context: "BeaconSendingContext"):
        try:

            while True:
                current_timestamp = context.current_timestamp()
                context.last_open_session_beacon_send_time = current_timestamp
                context.last_status_check_time = current_timestamp

                r = send_status_request(context,
                                        self.MAX_INITIAL_STATUS_REQUEST_RETRIES,
                                        self.INITIAL_RETRY_SLEEP_TIME_MILLISECONDS)
                if context.shutdown_requested or r.is_ok_response():
                    break

                sleep_time = self.REINIT_DELAY_MILLISECONDS[self.reinitialize_delay_index]
                if r.is_too_many_requests():
                    if "retry-after" in r.headers:
                        sleep_time = int(r.headers.get("retry-after")) * 1000
                        context.disable_capture_and_clear()

                context.sleep(sleep_time)
                self.reinitialize_delay_index = min(self.reinitialize_delay_index + 1,
                                                    len(self.REINIT_DELAY_MILLISECONDS) - 1)

            return r
        except Exception as e:
            context.logger.error(f"Error while trying to initialize OpenKit: {e}")

    def get_shutdown_state(self):
        return comm.BeaconSendingTerminalState()

    def __repr__(self):
        return "Init"
