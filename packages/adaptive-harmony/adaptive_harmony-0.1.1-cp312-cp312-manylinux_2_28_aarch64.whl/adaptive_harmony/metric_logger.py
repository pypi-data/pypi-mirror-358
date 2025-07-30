from numbers import Number
from typing import Callable, Any

Logger = Callable[[dict[str, Any]], None]
import wandb
from tensorboardX import SummaryWriter

from rich.pretty import pprint


class WandbLogger:
    def __init__(
        self,
        project_name: str,
        run_name: str,
        entity: str,
    ):
        self.run = wandb.init(project=project_name, name=run_name, entity=entity)
        self.step = 0

    def __call__(self, logs: dict[str, Any]):
        wandb.log(logs, step=self.step, commit=True)
        self.step += 1
        
    @property
    def training_monitoring_link(self) -> str:
        return self.run.get_url()  # type: ignore

    def close(self):
        wandb.finish()


class TBMetricsLogger:
    def __init__(self, logging_dir: str):
        self.logging_dir = logging_dir
        self.writer = SummaryWriter(str(logging_dir), flush_secs=15)
        self.step = 0

    @property
    def training_monitoring_link(self) -> str:
        return self.logging_dir

    def __call__(self, logs: dict[str, Any]):
        for entry, data in logs.items():
            if isinstance(data, Number):
                self.writer.add_scalar(entry, data, global_step=self.step)
            else:
                print(f"Unsupported type: {type(data)}")
        self.step += 1
        self.writer.flush()

    def close(self):
        self.writer.close()


class StdoutLogger:
    def __init__(self): ...

    def __call__(self, logs: dict[str, Any]):
        pprint(logs)
