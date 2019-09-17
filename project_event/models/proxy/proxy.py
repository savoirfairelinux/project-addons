class Proxy:
    def __init__(self, state):
        self._state = state
        self._is_new_proxy = True

class ProxyState(Proxy):
    def confirm_state_change(self):
        if self._is_new_proxy:
            self._proxy_sate = False
            return (Wizard, self)