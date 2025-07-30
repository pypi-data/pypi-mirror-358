from adaptive_harmony import StringThread, DataSet, CosineScheduler, TrainingModel, Logger, TokenizedThread
from adaptive_harmony.core.utils import async_map_batch, async_map, get_minibatches
from typing import Callable, Awaitable
import numpy as np
from dataclasses import dataclass
from adaptive_harmony.core.utils import log_args


@dataclass
class Batch:
    samples: list[TokenizedThread]
    logprobs: list[list[float]]
    ref_logprobs: list[list[float]]
    advantages: list[float]
    score: float
    kl_div: list[float]
    gen_len: float


class GRPO:

    @log_args
    def __init__(
        self,
        data_set: list[StringThread],  # (positive_sample, negative_sample)
        model: TrainingModel,
        scoring_fn: Callable[[StringThread], Awaitable[float]],
        logger: Logger,
        lr: float = 7.5e-7,
        num_samples_per_batch=128,
        num_samples_per_mini_batch=128,
        max_grad_norm=1.0,
        clip_range=0.1,
        kl_beta=0.1,
        mini_epochs_per_batch=1,
        max_num_grpo_steps: int | None = None,
        completions_per_sample=8,
    ):
        self.dataset = DataSet(data_set, allow_looping=True)

        self.completions_per_sample = completions_per_sample
        self.lr_schedule = CosineScheduler(lr)

        self.model = model
        self.samples_per_batch = num_samples_per_batch // completions_per_sample
        self.num_mini_epochs_per_batch = mini_epochs_per_batch

        self.logger = logger
        self.max_grad_norm = max_grad_norm
        self.scoring_fn = scoring_fn
        self.clip_range = clip_range
        self.kl_beta = kl_beta
        self.num_samples_per_mini_batch = num_samples_per_mini_batch
        self.max_num_batches = max_num_grpo_steps

    async def gen_data(self, sample: StringThread):
        assert self.model_ref is not None, "Calling `process_sample_grpo` before reference model has been set"

        all_samples = await async_map(self.model.generate_tokens, [sample] * self.completions_per_sample)
        string_samples = await async_map(self.model.detokenize_thread, all_samples)
        all_scores = np.array(await async_map(self.scoring_fn, string_samples))

        advantages = all_scores - all_scores.mean()
        advantages /= advantages.std() + 1e-8

        logprobs = await async_map(self.model.logprobs_per_token, all_samples)
        ref_logprobs = await async_map(self.model_ref.logprobs_per_token, all_samples)
        kl = np.array(np.concatenate(logprobs), dtype=np.float32) - np.array(
            np.concatenate(ref_logprobs), dtype=np.float32
        )

        return Batch(
            samples=all_samples,
            logprobs=logprobs,
            ref_logprobs=ref_logprobs,
            advantages=advantages,
            score=np.mean(all_scores).item(),
            kl_div=kl.tolist(),
            gen_len=np.mean([sample.len_last_turn() for sample in all_samples]),
        )

    async def train_mini_batch(self, data: Batch):
        for i in range(len(data.samples)):
            await self.model.train_grpo(
                data.samples[i],
                data.logprobs[i],
                data.ref_logprobs[i],
                [data.advantages[i]] * len(data.logprobs[i]),
                self.clip_range,
                self.kl_beta,
            )

    async def run(self):
        self.model_ref = await self.model.clone_inf()

        completion_percentage = 0.0
        num_batches_processed = 0

        while completion_percentage < 1.0:
            num_batches_processed += 1

            data = await async_map_batch(self.gen_data, self.dataset, self.samples_per_batch)

            completion_percentage = (
                self.dataset.completion_percentage()
                if self.max_num_batches is None
                else min(num_batches_processed / self.max_num_batches, 1.0)
            )
            current_lr = self.lr_schedule(completion_percentage)

            batch_logs = dict(
                completion_percentage=completion_percentage,
                score_mean=np.mean([batch.score for batch in data]).item(),
                score_std=np.std([batch.score for batch in data]).item(),
                kl_div=np.mean(np.concatenate([batch.kl_div for batch in data])),
                advantages=np.mean(np.concatenate([batch.advantages for batch in data])),
                generation_length=np.mean([batch.gen_len for batch in data]),
                logprobs=np.mean(np.concatenate([np.concatenate(batch.logprobs) for batch in data])),
                ref_logprobs=np.mean(np.concatenate([np.concatenate(batch.ref_logprobs) for batch in data])),
            )
            batch_logs["training/completion_percentage"] = (
                completion_percentage  # to have an comparable axis with prior runs
            )
            for mini_batch in get_minibatches(
                data, self.num_samples_per_mini_batch // self.completions_per_sample, self.num_mini_epochs_per_batch
            ):
                total_num_samples = sum([len(batch.samples) for batch in mini_batch])
                print(f"training on {total_num_samples} samples")
                await async_map(self.train_mini_batch, mini_batch)
                try:
                    logs = await self.model.optim_step(current_lr, wd=0, max_grad_norm=self.max_grad_norm)
                    self.logger(logs | batch_logs)
                except Exception as e:
                    # print(mini_batch, flush=True)
                    raise e
