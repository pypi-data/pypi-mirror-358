from adaptive_harmony import StringThread, DataSet, CosineScheduler, TrainingModel, Logger
from adaptive_harmony.core.utils import async_map_batch
from tqdm.auto import tqdm


class SFT:
    def __init__(
        self,
        data_set: list[StringThread],
        model: TrainingModel,
        logger: Logger,
        lr: float = 1e-5,
        samples_per_batch=512,  # axel magic number: "pretty well validated across different scales"
        max_grad_norm=1.0,
    ):
        self.dataset = DataSet(data_set)
        self.lr_schedule = CosineScheduler(lr)
        self.model = model
        self.samples_per_batch = samples_per_batch
        self.logger = logger
        self.max_grad_norm = max_grad_norm

    async def run(self):
        with tqdm(total=100) as pbar:

            while self.dataset.completion_percentage() < 1.0:
                await async_map_batch(self.model.train_language_modelling, self.dataset, self.samples_per_batch)
                cp = self.dataset.completion_percentage()
                current_lr = self.lr_schedule(cp)
                pbar.update(cp * 100.0 - pbar.n)

                logs = await self.model.optim_step(current_lr, wd=0, max_grad_norm=self.max_grad_norm)
                self.logger(logs | dict(completion_percentage=cp))
