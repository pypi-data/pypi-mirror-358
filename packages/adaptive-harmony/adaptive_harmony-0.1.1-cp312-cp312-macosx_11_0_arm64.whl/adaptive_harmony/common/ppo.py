import numpy as np
from dataclasses import dataclass
from typing import Callable, Coroutine, Any

from adaptive_harmony import (
    StringThread,
    DataSet,
    CosineScheduler,
    TrainingModel,
    Logger,
    TokenizedThread,
    CombinedSchedule,
)
from adaptive_harmony.core import rl_utils
from adaptive_harmony.core.utils import async_map_batch, get_minibatches, async_map


@dataclass
class Sample:
    sample: TokenizedThread
    string_sample: StringThread
    logprobs: list[float]
    ref_logprobs: list[float]
    advantages: list[float]
    returns: list[float]
    score: float
    kl_div: list[float]
    values: list[float]
    kl_pen: float
    cumulative_reward: float


from adaptive_harmony.core.utils import log_args


class PPO:
    @log_args
    def __init__(
        self,
        data_set: list[StringThread],  # (positive_sample, negative_sample)
        model: TrainingModel,
        value_model: TrainingModel,
        scoring_fn: Callable[[StringThread], Coroutine[Any, Any, float]],
        logger: Logger,
        lr_policy: float = 0.75e-6,
        lr_value: float = 1e-6,
        num_samples_per_batch=128,
        num_samples_per_mini_batch=128,
        max_grad_norm=1.0,
        clip_range=0.1,
        kl_beta=0.1,
        mini_epochs_per_batch=1,
        gae_lambda=0.95,
        gae_gamma=1.0,
        value_only_fraction=0.25,
        max_num_ppo_steps: int | None = None,
        validation_samples: list[StringThread] | None = None,
        validation_frequency: float = 0.2,
    ):
        training_data = data_set
        self.model_ref = None
        self.dataset = DataSet(training_data, allow_looping=True)
        self.validation_samples = validation_samples
        self.lr_schedule_value = CosineScheduler(lr_value)
        self.lr_schedule_policy = CombinedSchedule(lambda _: 0, CosineScheduler(lr_policy), value_only_fraction)
        self.model = model
        self.value_model = value_model
        self.samples_per_batch = num_samples_per_batch
        self.num_mini_epochs_per_batch = mini_epochs_per_batch

        self.logger = logger
        self.max_grad_norm = max_grad_norm
        self.scoring_fn = scoring_fn
        self.clip_range = clip_range
        self.kl_beta = kl_beta
        self.num_samples_per_mini_batch = num_samples_per_mini_batch
        self.max_num_batches = max_num_ppo_steps
        self.gae_lambda = gae_lambda
        self.gae_gamma = gae_gamma
        self.validation_frequency = validation_frequency
        self.last_validation_percentage = -1.0
        self.num_batches_processed = 0

    @property
    def completion_percentage(self):
        return (
            self.dataset.completion_percentage()
            if self.max_num_batches is None
            else min(self.num_batches_processed / self.max_num_batches, 1.0)
        )

    async def generate_and_score(self, prompt: StringThread):
        sample = await self.model.generate_tokens(prompt)
        string_sample = await self.model.detokenize_thread(sample)
        score = await self.scoring_fn(string_sample)

        return sample, string_sample, score

    async def generate_sample(self, prompt: StringThread):
        assert self.model_ref is not None, "Calling `process_sample_dpo` before reference model has been set"

        sample = await self.model.generate_tokens(prompt)
        string_sample = await self.model.detokenize_thread(sample)
        score = await self.scoring_fn(string_sample)
        values = await self.value_model.score(sample)

        logprobs = await self.model.logprobs_per_token(sample)
        ref_logprobs = await self.model_ref.logprobs_per_token(sample)

        kl = np.array(logprobs, dtype=np.float32) - np.array(ref_logprobs, dtype=np.float32)
        kl_pen = -kl * self.kl_beta
        rewards = np.array(kl_pen)
        rewards[-1] += score

        advantages = rl_utils.gae_advantages(values, rewards.tolist(), self.gae_lambda, self.gae_gamma)
        returns = rl_utils.discounted_cumulative_rewards(rewards.tolist(), self.gae_gamma)

        return Sample(
            sample=sample,
            string_sample=string_sample,
            logprobs=logprobs,
            ref_logprobs=ref_logprobs,
            advantages=advantages,
            returns=returns,
            score=score,
            values=values,
            cumulative_reward=sum(rewards),
            kl_div=kl.tolist(),
            kl_pen=np.sum(kl_pen).item(),
        )

    async def train_ppo(self, batch: Sample):
        await self.model.train_ppo(batch.sample, batch.logprobs, batch.advantages, self.clip_range)

    async def train_value(self, batch: Sample):
        await self.value_model.train_mse(batch.sample, batch.returns)

    async def run(self):
        self.model_ref = await self.model.clone_inf()

        while self.completion_percentage < 1.0:
            self.num_batches_processed += 1

            data = await async_map_batch(
                self.generate_sample,
                self.dataset,
                self.samples_per_batch,
            )

            lr_policy = self.lr_schedule_policy(self.completion_percentage)
            lr_value = self.lr_schedule_value(self.completion_percentage)

            returns = np.concatenate([batch.returns for batch in data])
            cur_values = np.concatenate([batch.values for batch in data])

            var_return = returns.var()
            mean_error = ((cur_values - returns) ** 2).mean()
            explained_variance = (1 - mean_error / (var_return + 1e-8)).item()

            logs = dict(
                completion_percentage=self.completion_percentage,
                score_mean=np.mean([batch.score for batch in data]).item(),
                score_std=np.std([batch.score for batch in data]).item(),
                returns=np.mean(np.concatenate([batch.returns for batch in data])),
                kl_div=np.mean(np.concatenate([batch.kl_div for batch in data])),
                advantages=np.mean(np.concatenate([batch.advantages for batch in data])),
                generation_length=np.mean([batch.sample.len_last_turn() for batch in data]),
                logprobs=np.mean(np.concatenate([batch.logprobs for batch in data])),
                ref_logprobs=np.mean(np.concatenate([batch.ref_logprobs for batch in data])),
                kl_penalty=np.mean([batch.kl_pen for batch in data]),
                explained_variance=explained_variance,
                cumulative_reward=np.mean([batch.cumulative_reward for batch in data]),
            )

            logs["training/completion_percentage"] = (
                self.completion_percentage
            )  # to have an comparable axis with prior runs

            should_run_validation = (
                self.validation_samples is not None
                and self.completion_percentage - self.last_validation_percentage >= self.validation_frequency
            )
            if should_run_validation:
                await self.run_validation()
                self.last_validation_percentage = self.completion_percentage

            if lr_policy > 0:
                for mini_batch in get_minibatches(
                    data, self.num_samples_per_mini_batch, self.num_mini_epochs_per_batch
                ):
                    await async_map(self.train_ppo, mini_batch)
                    logs |= await self.model.optim_step(lr_policy, wd=0, max_grad_norm=self.max_grad_norm)
                    self.logger(logs)

            for mini_batch in get_minibatches(data, self.num_samples_per_mini_batch, self.num_mini_epochs_per_batch):
                await async_map(self.train_value, mini_batch)
                logs |= await self.value_model.optim_step(lr_value, wd=0, max_grad_norm=self.max_grad_norm)
                self.logger(logs)

    async def run_validation(self):
        assert self.validation_samples is not None, "Validation samples must be set"
        print("Entering validation")

        validation_results = await async_map_batch(
            self.generate_and_score,
            iter(self.validation_samples),
            # this allows for a 50% failure rate in the validation set. We should have a flag in async_map_batch to simply
            # not retry. But it'll do for now.
            len(self.validation_samples) // 2,
        )
        scores = [score for sample, _, score in validation_results]
        gen_lengths = [sample.len_last_turn() for sample, _, score in validation_results]

        validation_logs = dict(
            **{
                f"validation/{key}": value
                for key, value in dict(
                    score_mean=np.mean(scores).item(),
                    score_std=np.std(scores).item(),
                    score_min=np.min(scores).item(),
                    score_max=np.max(scores).item(),
                    generation_length_mean=np.mean(gen_lengths).item(),
                    generation_length_std=np.std(gen_lengths).item(),
                    num_samples=len(validation_results),
                ).items()
            }
        ) | {"completion_percentage": self.completion_percentage}
        self.logger(validation_logs)

        print(f"Validation complete\nMean score: {validation_logs['validation/score_mean']:.4f}")
        return validation_logs
