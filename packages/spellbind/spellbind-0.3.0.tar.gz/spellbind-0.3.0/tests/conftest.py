from unittest.mock import Mock


class Observer(Mock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class NoParametersObserver(Observer):
    def __call__(self):
        super().__call__()


class OneParameterObserver(Observer):
    def __call__(self, param0):
        super().__call__(param0)


class OneDefaultParameterObserver(Observer):
    def __call__(self, param0="default"):
        super().__call__(param0)


class TwoParametersObserver(Observer):
    def __call__(self, param0, param1):
        super().__call__(param0, param1)


class OneRequiredOneDefaultParameterObserver(Observer):
    def __call__(self, param0, param1="default"):
        super().__call__(param0, param1)


class TwoDefaultParametersObserver(Observer):
    def __call__(self, param0="default0", param1="default1"):
        super().__call__(param0, param1)


class ThreeParametersObserver(Observer):
    def __call__(self, param0, param1, param2):
        super().__call__(param0, param1, param2)


class ThreeDefaultParametersObserver(Observer):
    def __call__(self, param0="default0", param1="default1", param2="default2"):
        super().__call__(param0=param0, param1=param1, param2=param2)


class TwoRequiredOneDefaultParameterObserver(Observer):
    def __call__(self, param0, param1, param2="default2"):
        super().__call__(param0, param1, param2)
