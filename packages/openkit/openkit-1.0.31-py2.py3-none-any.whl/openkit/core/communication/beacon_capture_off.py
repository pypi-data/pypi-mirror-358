from typing import TYPE_CHECKING

import openkit.core.communication as comm
from . import AbstractBeaconSendingState
from ..communication.state_utils import send_status_request
from ...protocol.status_response import StatusResponse

if TYPE_CHECKING:
    from ..beacon_sender import BeaconSendingContext


class BeaconSendingCaptureOffState(AbstractBeaconSendingState):
    STATUS_CHECK_INTERVAL = 2 * 60 * 60 * 1000
    STATUS_REQUEST_RETRIES = 5
    INITIAL_RETRY_SLEEP_TIME_MILLISECONDS = 1000

    def __init__(self, sleep_time = None):
        super().__init__()
        if sleep_time is None:
            sleep_time = self.STATUS_CHECK_INTERVAL
        self.sleep_time = sleep_time
        self.terminal = False

    def do_execute(self, context: "BeaconSendingContext"):
        context.disable_capture()
        context.clear_all_session_data()

        current_time = context.current_timestamp()

        delta = self.sleep_time if self.sleep_time > 0 else self.STATUS_CHECK_INTERVAL - (
                current_time - context.last_status_check_time)
        if delta > 0 and not context.shutdown_requested:
            context.sleep(delta)

        response = send_status_request(context, self.STATUS_REQUEST_RETRIES, self.INITIAL_RETRY_SLEEP_TIME_MILLISECONDS)
        self.handle_status_response(context, response)
        context.last_status_check_time = current_time

    def get_shutdown_state(self):
        return comm.BeaconSendingFlushSessionsState()

    def handle_status_response(self, context: "BeaconSendingContext", response: StatusResponse):
        if response is not None:
            context.handle_response(response)

            if response.is_error_response():
                context.next_state = BeaconSendingCaptureOffState(10 * 60 * 1000)
            elif response.is_ok_response() and context.capture_on:
                context.next_state = comm.BeaconSendingCaptureOnState()

    def __repr__(self):
        return "Capture OFF"
