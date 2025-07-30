from wizlib.parser import WizParser

from kwark.command import KwarkCommand
from kwark.util import load_prompt
from kwark.ai import AI


class DocCommand(KwarkCommand):
    """Summarize observations and conclusions from random text such as a
    thread, email, or notes"""

    name = 'doc'
    prompt = load_prompt(name)

    @classmethod
    def add_args(cls, parser: WizParser):
        super().add_args(parser)
        parser.add_argument('--api-key', '-k')

    def handle_vals(self):
        super().handle_vals()
        if not self.provided('api-key'):
            if key := self.app.config.get('kwark-api-anthropic-key'):
                self.api_key = key

    @KwarkCommand.wrap
    def execute(self):
        input = self.app.stream.text
        prompt = self.prompt.format(text=input)
        response = AI(self.api_key).query(prompt)
        return response
        # return f"Hello, {input}!"
