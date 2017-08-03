import web

from . import logger


# TODO - does not handle attachments
class DebugMailer:
    def __init__(self):
        self.messages = []

    def __call__(self, from_address, to_address, subject, message,
                 headers=None, **kw):
        mail = web.storage({'to': to_address,
                            'to_address': to_address,
                            'from': from_address,
                            'from_address': from_address,
                            'subject': subject,
                            'message': message})
        mail.update(kw)
        logger.debug("Sending message: %s" % mail)
        self.messages.append(mail)
        return mail

sendmail = web.sendmail

debugmail = DebugMailer()
