from __future__ import annotations

import logging
import time
from logging import Formatter
from logging import LogRecord
from logging.handlers import SMTPHandler

from flask import Flask
from flask import has_request_context
from flask import request


def remote_addr() -> str | None:
    # try CloudFlare
    addr = request.headers.get("CF-Connecting-IP")
    if addr:
        return addr
    addr = request.headers.get("X-Forwarded-For")
    if addr:
        return addr
    return request.remote_addr


def escapeit(url: str) -> str:
    # because microsoft mangles urls
    if not url:
        return ""
    return url.replace("https://", "").replace("http://", "")


class RequestFormatter(Formatter):
    def format(self, record: LogRecord) -> str:
        ret = super().format(record)
        if not has_request_context():
            return ret

        extra = """
Remote Address:       {remote_addr}
Request Path:         {req.path}
Request Values:       {req.values}
Request User-Agent:   {req.user_agent}
Original Referrer:    {oref}
Request Referrer:     {req.referrer}

""".format(
            req=request,
            remote_addr=remote_addr(),
            oref=(
                escapeit(request.referrer)
                if request.referrer is not None
                else "<unknown>"
            ),
        )
        return extra + ret


class LimitFilter(logging.Filter):
    def __init__(self, delay: int = 60 * 5):
        super().__init__("delay")
        self.start = time.time()
        self.delay = delay

    def filter(self, record: LogRecord) -> bool:
        t = time.time()
        if (t - self.start) > self.delay:
            self.start = t
            return True
        return False


def init_email_logger(
    app: Flask,
    Cls: type[SMTPHandler] = SMTPHandler,
    level: int = logging.ERROR,
) -> None:

    admins: str | list[str] | None = app.config.get("ADMINS")
    if not admins:
        return
    if isinstance(admins, str):
        admins = [admins]

    frm = admins[0].split("@")[-1]
    name = app.config.get("MAIL_SUBJECT", app.name)
    mailhost = app.config.get("MAIL_SERVER", "mailhost")
    if not mailhost:
        return
    if isinstance(mailhost, str) and ":" in mailhost:
        mailhost = mailhost.split(":")
        mailhost = (mailhost[0], int(mailhost[1]))
    mail_handler = Cls(
        mailhost,
        app.name + f"-server-error@{frm}",
        admins,
        subject=name + " Failed",
    )

    mail_handler.setLevel(level)

    delay = app.config.get("LOG_ERROR_DELAY")

    if delay is not None and delay > 0:
        mail_handler.addFilter(LimitFilter(delay=delay))

    mail_handler.setFormatter(
        RequestFormatter(
            """
Message type:       %(levelname)s
Location:           %(pathname)s:%(lineno)d
Module:             %(module)s
Function:           %(funcName)s
Time:               %(asctime)s

Message:

%(message)s
""",
        ),
    )

    app.logger.addHandler(mail_handler)
