import typer

app = typer.Typer(
    name="fine-tuning tools.",
    no_args_is_help=True,
)


# @app.callback()
# def callback(
#         index_file: str = typer.Option(
#             '',
#             help="Input a index txt,read line by line.",
#         ),
#         index_folder: str = typer.Option(
#             '',
#             help="Input a folder,i'll read all the .md files."
#         ),
#         input_parquet_file: str = typer.Option(
#             '',
#             help='Path to the input parquet file.'
#         ),
#         encoding: str = typer.Option(
#             'utf-8',
#             help='Encoding of the input files, default is utf-8.'
#         ),
#         instructions: str = typer.Option(
#             '',
#             help="Alpaca's instruction for the fine-tuning process."
#         ),
#         system_prompt: str = typer.Option(
#             '请根据题目和原文作答，并给出准确的答案。',
#             help="System prompt for the fine-tuning process.",
#         ),
#         response_prefix: str = typer.Option(
#             '<think>',
#             help="Prefix to be added before the response."
#         ),
#         response_suffix: str = typer.Option(
#             default='',
#             help="Suffix to be added after the response."
#         ),
#         openai_api_key: str = typer.Option(
#             '',
#             help="OpenAI API key for using OpenAI services.",
#         ),
#         openai_api_endpoint: str = typer.Option(
#             '',
#             help="OpenAI API endpoint for using OpenAI services.",
#         ),
#         default_model: str = typer.Option(
#             'QwQ-32B',
#             help="Default model for the fine-tuning process.",
#         ),
# ):
#     """
#     Callback function to initialize the finetune tools with provided options.
#     """
#     for k in locals().keys():
#         di[k] = locals()[k]
#
#
# def init_FT() -> finetune_tools:
#     """
#     Initialize the finetune tools instance and register it for cleanup on exit.
#     """
#     FT = finetune_tools()
#     atexit.register(FT.save)
#     return FT
#
#
# @app.command()
# def exam():
#     """
#     Execute the exam method.
#     """
#     FT = init_FT()
#     FT.exam()
#
#
# @app.command()
# def gen_questions():
#     """
#     Generate questions for exam.
#     """
#     FT = init_FT()
#     FT.gen_questions()
#
#
# @app.command()
# def gen_questions_by_index_file():
#     """
#     Generate questions by index file.
#     """
#     FT = init_FT()
#     FT.gen_questions_by_index_file()
#
#
# @app.command()
# def gen_questions_by_index_folder():
#     """
#     Generate questions by index folder.
#     """
#     FT = init_FT()
#     FT.gen_questions_by_index_folder()
#
#
# @app.command()
# def convert_json_tmp_to_alpaca_file_path(convert_json_tmp_to_alpaca_file_path: str):
#     """
#     Convert json.tmp's file to alpaca json dataset.
#     """
#     FT = init_FT()
#     FT.convert_json_tmp_to_alpaca(convert_json_tmp_to_alpaca_file_path)
#
#
# @app.command()
# def recovery_parquet_from_pkl_invoke():
#     """
#     Recovery parquet from pkl.
#     """
#     FT = init_FT()
#     FT.recovery_parquet_from_pkl_invoke()
#
#
# @app.command()
# def convert_parquet_to_json_invoke():
#     """
#     Directly convert parquet to json.
#     """
#     FT = init_FT()
#     FT.convert_parquet_to_json_invoke()
#
#
# @app.command()
# def filter_parquet_instructions_invoke(filter_parquet_instructions: str):
#     """
#     筛选问题集的指令，请仿照default内容进行直接的要求
#     """
#     FT = init_FT()
#     FT.filter_parquet_instructions_invoke(filter_parquet_instructions)


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
        learning_rate: float = typer.Argument(2e-4, help="Learning rate for the training."),
        num_train_epochs: int = typer.Argument(3, help="Number of training epochs."),
        max_steps: int = typer.Argument(10000, help="Maximum number of training steps."),
        train_model: list[str] = typer.Argument(['q_proj', 'k_proj', 'v_proj'],
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
