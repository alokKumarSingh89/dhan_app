from dhanhq import dhanhq
import cred as _cred
class Login:
    def __init__(self ):
        self.client_id = _cred.client_id
        self.access_token = _cred.access_token
        self._dhan = None
    def get_dhan(self):
        if self._dhan is None:
            self._dhan = dhanhq(self.client_id, self.access_token)
        return self._dhan