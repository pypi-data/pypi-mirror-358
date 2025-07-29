#!/usr/bin/env python3
"""
Summarization Task: CNN DailyMail
This module provides a class for generating prompt variations for summarization tasks.
"""

from typing import Dict, Any
import argparse

from multipromptify.core.template_keys import (
    INSTRUCTION, PROMPT_FORMAT, QUESTION_KEY, GOLD_KEY,
    PARAPHRASE_WITH_LLM, FORMAT_STRUCTURE_VARIATION, TYPOS_AND_NOISE_VARIATION,
    CONTEXT_VARIATION, INSTRUCTION_VARIATIONS, PROMPT_FORMAT_VARIATIONS
)
from multipromptify_tasks.tasks.base_task import BaseTask
from multipromptify_tasks.constants import (
    DEFAULT_VARIATIONS_PER_FIELD, DEFAULT_PLATFORM, DEFAULT_MODEL_NAME,
    DEFAULT_MAX_VARIATIONS_PER_ROW, DEFAULT_MAX_ROWS, DEFAULT_RANDOM_SEED
)


class SummarizationTask(BaseTask):
    """Task for generating summarization prompt variations."""

    def __init__(self, variations_per_field: int = DEFAULT_VARIATIONS_PER_FIELD, api_platform: str = DEFAULT_PLATFORM, model_name: str = DEFAULT_MODEL_NAME,
                 max_rows: int = DEFAULT_MAX_ROWS, max_variations_per_row: int = DEFAULT_MAX_VARIATIONS_PER_ROW, random_seed: int = DEFAULT_RANDOM_SEED):
        super().__init__(
            task_name="Summarization Task: CNN DailyMail",
            output_filename="summarization_cnn_dailymail_variations.json",
            variations_per_field=variations_per_field,
            api_platform=api_platform,
            model_name=model_name,
            max_rows=max_rows,
            max_variations_per_row=max_variations_per_row,
            random_seed=random_seed
        )

    def load_data(self) -> None:
        """Load CNN DailyMail dataset from HuggingFace."""
        try:
            self.mp.load_dataset("cnn_dailymail", "3.0.0", split="train[:100]")
            print("✅ Successfully loaded CNN DailyMail dataset")
        except Exception as e:
            print(f"❌ Error loading CNN DailyMail dataset: {e}")
            print("Trying alternative dataset...")
            # Fallback to a simpler summarization dataset
            self.mp.load_dataset("samsum", split="train[:100]")
            print("✅ Successfully loaded samsum dataset")

    def get_template(self) -> Dict[str, Any]:
        """Get template configuration for summarization task."""
        return {
            INSTRUCTION: "You are a professional summarizer. Create a concise summary of the following text.",
            INSTRUCTION_VARIATIONS: [PARAPHRASE_WITH_LLM],
            PROMPT_FORMAT: "Article: {article}\nSummary: {highlights}",
            PROMPT_FORMAT_VARIATIONS: [
                FORMAT_STRUCTURE_VARIATION,  # Semantic-preserving format changes
            ],
            'article':
                [TYPOS_AND_NOISE_VARIATION
                 ],  # Add noise to the article text
            GOLD_KEY: "highlights"  # The summary is the gold standard
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--variations_per_field", type=int, default=DEFAULT_VARIATIONS_PER_FIELD)
    parser.add_argument("--api_platform", type=str, default=DEFAULT_PLATFORM)
    parser.add_argument("--model_name", type=str, default=DEFAULT_MODEL_NAME)
    parser.add_argument("--max_rows", type=int, default=DEFAULT_MAX_ROWS)
    parser.add_argument("--max_variations_per_row", type=int, default=DEFAULT_MAX_VARIATIONS_PER_ROW)
    parser.add_argument("--random_seed", type=int, default=DEFAULT_RANDOM_SEED)
    args = parser.parse_args()

    task = SummarizationTask(
        variations_per_field=args.variations_per_field,
        api_platform=args.api_platform,
        model_name=args.model_name,
        max_rows=args.max_rows,
        max_variations_per_row=args.max_variations_per_row,
        random_seed=args.random_seed
    )
    output_file = task.generate()
    print(f"\n🎉 Summarization task completed! Output saved to: {output_file}")
