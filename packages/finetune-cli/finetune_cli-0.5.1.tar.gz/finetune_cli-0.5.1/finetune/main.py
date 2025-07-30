import typer

app = typer.Typer(
    name="fine-tuning tools.",
    no_args_is_help=True,
)


@app.command()
def hive_reward_train(
        hive_reward_folder_path: str = typer.Argument(..., help="Path to the hive-reward dataset folder."),
        model_name: str = typer.Argument('Qwen2.5-0.5B-Instruct', help="Model name for training."),
        SYSTEM_PROMPT: str = typer.Option(
            '你是一名专家，请不要直接给出答案，而是经过严谨而深思熟虑的思考后再给出答案，其中要把每一步的思考过程不可省略的详细说出来，并把思考过程放在<think></think>中显示。',
            help="System prompt for the training faster."),
        SYSTEM_PROMPT_FREQ: float = typer.Option(0.1, help="Frequency of the system prompt in the training."),
        max_prompt_length: int = typer.Option(25565, help="Maximum prompt length for the training."),
        max_seq_length: int = typer.Option(1024, help="Maximum sequence length for the training."),
        alpaca_dataset_path: str = typer.Argument("", help="Path to the alpaca dataset for training."),
        logging_steps: int = typer.Option(1, help="Logging steps for the training."),
        save_steps: int = typer.Option(100, help="Save steps for the training."),
        use_vllm: bool = typer.Option(True, help="Whether to use vllm for training."),
        report_to: str = typer.Option("tensorboard",
                                      help="Reporting tool for the training, e.g., 'wandb' or 'tensorboard'."),
        fp16: bool = typer.Option(True, help="Whether to use fp16 for training."),
        learning_rate: float = typer.Option(5e-4, help="Learning rate for the training."),
        num_train_epochs: int = typer.Option(3, help="Number of training epochs."),
        max_steps: int = typer.Option(10000, help="Maximum number of training steps."),
        train_model: list[str] = typer.Option(
            ['q_proj', 'gate_proj', 'up_proj', 'v_proj', 'k_proj', 'down_proj', 'o_proj'],
            help="List of model components to train."),
        LoRA_r: int = typer.Option(8, help="LoRA rank for the training."),
        LoRA_alpha: int = typer.Option(16, help="LoRA alpha for the training."),
        per_device_train_batch_size: int = typer.Option(4, help="Batch size per device for training."),
        gradient_checkpointing: bool = typer.Option(True, help="Whether to use gradient checkpointing for training."),
        load_in_8bit: bool = typer.Option(False, help="Whether to load the model in 8-bit for training."),
        vllm_gpu_memory_utilization: float = typer.Option(0.95, help="GPU memory utilization for vllm."),
        vllm_server_host: str = typer.Option('localhost', help="Host for the vllm server."),
        vllm_server_port: int = typer.Option(8000, help="Port for the vllm server.")
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
