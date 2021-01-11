class NotInteractiveError(Exception):
    pass


class Connection:
    def __init__(self, server, http_request, websocket=None):
        self.server = server
        self.http_request = http_request
        self.websocket = websocket

    @property
    def is_interactive(self):
        return self.websocket is not None

    @property
    def user(self):
        return getattr(self, '_user', None)

    @user.setter
    def user(self, value):
        self._user = value

    def send_str(self, string, priority=None, sync=True):
        priority = priority or self.server.settings.DEFAULT_VIEW_PRIORITY

        if not self.is_interactive:
            raise NotInteractiveError

        try:
            return self.server.schedule(
                self.websocket.send_str(string),
                sync=sync,
                priority=priority,
            )

        except ConnectionResetError:
            # this exception gets handled by aiohttp internally and
            # can be ignored

            pass
