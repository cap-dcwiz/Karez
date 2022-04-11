from karez.aggregator.base import AggregatorBase
from rich import print


class EchoAggregator(AggregatorBase):
    @classmethod
    def role_description(cls) -> str:
        return "Simple aggregator that echos all received data."

    def process(self, payload):
        print(f"[bold]{self.name}[/bold]:")
        print(payload)
        print()
