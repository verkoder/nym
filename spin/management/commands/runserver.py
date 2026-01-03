import platform

import django.core.servers.basehttp
from django.conf import settings
from django.contrib.staticfiles.management.commands.runserver import Command as RunserverCommand
from django.core.servers.basehttp import ServerHandler


def handle_one_request(self):
    """
    Exact copy of django.core.servers.WSGIRequestHandler.handle_one_request except it
    Completely ignores "ConnectionResetError: [Errno 54] Connection reset by peer"
    Which seems to be only noise on MacOS.
    """
    try:
        self.raw_requestline = self.rfile.readline(65537)
    except ConnectionResetError:
        return
    if len(self.raw_requestline) > 65536:
        self.requestline = ""
        self.request_version = ""
        self.command = ""
        self.send_error(414)
        return

    if not self.parse_request():  # An error code has been sent, just exit
        return

    handler = ServerHandler(self.rfile, self.wfile, self.get_stderr(), self.get_environ())
    handler.request_handler = self  # backpointer for logging & connection closing
    handler.run(self.server.get_app())


class Command(RunserverCommand):
    def get_handler(self, *args, **options):
        if settings.DEBUG and platform.platform().upper().startswith("DARWIN"):
            # patch the offending code
            django.core.servers.basehttp.WSGIRequestHandler.handle_one_request.__code__ = handle_one_request.__code__

        return super().get_handler(*args, **options)
