
class Mail(object):

    def __init__(self, to, sender, m, subject=None, cc=None, bcc=None):

        super().__init__()

        from itertools import chain as _chain
        from email import charset as _charset
        from email.mime.multipart import MIMEMultipart as _MIMEMultipart
        from email.utils import formatdate as _formatdate
        from photon import __ident__
        from ..util.structures import to_list
        from ..util.system import get_timestamp

        if callable(m): self.m = m
        else: raise Exception('wrong m(')

        to = to_list(to)
        cc = to_list(cc)
        bcc = to_list(bcc)
        if not subject: subject = __ident__
        subject = '%s - %s' %(subject, get_timestamp())

        self.__sender = sender
        self.__recipients = list(_chain(to, cc, bcc))

        _charset.add_charset('utf-8', _charset.QP, _charset.QP, 'UTF-8')

        self.__message = _MIMEMultipart()
        self.__message.add_header('To', ', '.join(to))
        if cc: self.__message.add_header('CC', ', '.join(cc))
        self.__message.add_header('From', sender)
        self.__message.add_header('Subject', subject)
        self.__message.add_header('Date', _formatdate())
        self.__message.add_header('X-Mailer', 'Postbote Willy')

        self.m(
            'mail tool startup done',
            more=dict(to=to, cc=cc, bcc=bcc, sender=sender, subject=subject),
            verbose=False
        )

    @property
    def text(self):

        return self.__message.as_string()

    @text.setter
    def text(self, elem):

        from email.mime.text import MIMEText as _MIMEText
        from pprint import pformat as _pformat

        if elem:
            if not isinstance(elem, str): elem = _pformat(elem)
            self.m(
                'add text to mail',
                more=dict(len=len(elem))
            )
            return self.__message.attach(_MIMEText(elem, 'plain', 'UTF-8'))

    def send(self):

        from smtplib import SMTP as _SMTP, SMTPException as _SMTPException
        from socket import error as _error

        if self.__message:
            try:
                s = _SMTP()
                s.connect('localhost')
                r = s.sendmail(self.__sender, self.__recipients, self.__message.as_string().encode('UTF-8'))
                self.m(
                    'mail sent',
                    more=dict(sender=self.__sender, recipients=self.__recipients, result=str(r))
                )
            except (_SMTPException, _error) as ex:
                self.m(
                    'error sending mail',
                    state=True,
                    more=dict(sender=self.__sender, recipients=self.__recipients, exception=str(ex))
                )



