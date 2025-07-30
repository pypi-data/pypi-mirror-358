from wizlib.command import WizCommand


class KwarkCommand(WizCommand):

    default = 'null'


class NullCommand(KwarkCommand):

    name = 'null'
