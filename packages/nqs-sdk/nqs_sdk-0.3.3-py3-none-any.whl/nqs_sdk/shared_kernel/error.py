class BaseApplicationError(Exception):
    ERROR_CODE = "0001"

    def __init__(self, message: str):
        super().__init__(f"[{self.ERROR_CODE}] {message}")


class MessageDispatcherValidationError(BaseApplicationError):
    ERROR_CODE = "0002"


class MessageDispatcherStartWhenAlreadyStartedError(BaseApplicationError):
    ERROR_CODE = "0003"


class MessageDispatcherUnRegistredProducerError(BaseApplicationError):
    ERROR_CODE = "0004"


class MessageDispatcherRegisterOnStartedSimualtionError(BaseApplicationError):
    ERROR_CODE = "0005"


class MessageDispatcherMessageTryToTimeTravelError(BaseApplicationError):
    ERROR_CODE = "0006"
