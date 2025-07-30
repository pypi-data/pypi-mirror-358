import yaml
from wizlib.parser import WizParser

from kwark.command import KwarkCommand
from kwark.ai import AI


class ModelsCommand(KwarkCommand):
    """List available Anthropic AI models."""

    name = 'models'

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
        ai = AI(self.api_key)
        models = ai.available_models

        if not models:
            self.status = "Retrieved available models (none found)"
            return yaml.dump([], default_flow_style=False)

        # Create YAML output as array of hashes
        yaml_models = []
        for model in models:
            yaml_models.append({
                'id': model['id'],
                'display_name': model.get('display_name', model['id']),
                'created_at': model.get('created_at', 'Unknown')
            })

        self.status = f"Retrieved available models"
        return yaml.dump(yaml_models, default_flow_style=False)
