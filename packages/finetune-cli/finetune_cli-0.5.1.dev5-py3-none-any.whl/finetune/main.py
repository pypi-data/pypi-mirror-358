import typer

app = typer.Typer(
    name="fine-tuning tools.",
    no_args_is_help=True,
)

@app.command()
def hive_reward_train(
        hive_reward_folder_path: str = typer.Argument(..., help="Path to the hive-reward dataset folder."),
        model_name: str = typer.Argument('Qwen2.5-0.5B-Instruct', help="Model name for training."),
        SYSTEM_PROMPT: str = typer.Argument(
            '你是一名专家，请不要直接给出答案，而是经过严谨而深思熟虑的思考后再给出答案，其中要把每一步的思考过程不可省略的详细说出来，并把思考过程放在<think></think>中显示。',
            help="System prompt for the training faster."),
        SYSTEM_PROMPT_FREQ: float = typer.Argument(0.1, help="Frequency of the system prompt in the training."),
        max_prompt_length: int = typer.Argument(25565, help="Maximum prompt length for the training."),
        max_seq_length: int = typer.Argument(128000, help="Maximum sequence length for the training."),
        alpaca_dataset_path: str = typer.Argument("", help="Path to the alpaca dataset for training."),
        logging_steps: int = typer.Argument(10, help="Logging steps for the training."),
        save_steps: int = typer.Argument(1000, help="Save steps for the training."),
        use_vllm: bool = typer.Argument(True, help="Whether to use vllm for training."),
        report_to: str = typer.Argument("tensorboard",
                                        help="Reporting tool for the training, e.g., 'wandb' or 'tensorboard'."),
        fp16: bool = typer.Argument(True, help="Whether to use fp16 for training."),
        learning_rate: float = typer.Argument(5e-4, help="Learning rate for the training."),
        num_train_epochs: int = typer.Argument(3, help="Number of training epochs."),
        max_steps: int = typer.Argument(10000, help="Maximum number of training steps."),
        train_model: list[str] = typer.Option(
            ['q_proj', 'gate_proj', 'up_proj', 'v_proj', 'k_proj', 'down_proj', 'o_proj'],
            help="List of model components to train."),
        LoRA_r: int = typer.Argument(8, help="LoRA rank for the training."),
        LoRA_alpha: int = typer.Argument(16, help="LoRA alpha for the training."),
):
    from finetune.GRPO.hivetrainer import HiveTrainer
    T = HiveTrainer(
        **locals()  # unpack all local variables as arguments
    )
    T.train()


def main():
    """
    entrypoint
    """
    app()
