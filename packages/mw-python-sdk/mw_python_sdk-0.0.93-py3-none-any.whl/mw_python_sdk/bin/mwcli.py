import asyncio
import os
import subprocess
import requests
import typer

llm = typer.Typer(short_help="The LLM management.")


@llm.command(short_help="Start a server for the LLM.")
def serve(
    model: str = typer.Argument("", help="The ID or the path of the LLM model to use."),
    model_name: str = typer.Argument("", help="The name of the LLM model to use."),
    parallal_size: int = typer.Option(0, help="The number of GPUs to use."),
    host: str = typer.Option("0.0.0.0", help="The host of the server."),
    port: int = typer.Option(8000, help="The port of the server."),
    quantization: str = typer.Option(None, help="The quantization method to use."),
    load_format: str = typer.Option(None, help="The load format to use."),
    enforce_eager: bool = typer.Option(
        False, help="Whether to enforce eager execution."
    ),
    max_num_seq: int = typer.Option(2, help="The maximum number of sequences."),
    max_model_len: int = typer.Option(4096, help="The maximum model length."),
    gpu_memory_utilization: float = typer.Option(
        0.98, help="The GPU memory utilization."
    ),
):
    from mw_python_sdk.llm.inference import serve

    serve(
        model,
        model_name=model_name,
        host=host,
        port=port,
        max_num_seq=max_num_seq,
        max_model_len=max_model_len,
        tensor_parallel_size=parallal_size,
        gpu_memory_utilization=gpu_memory_utilization,
        quantization=quantization,
        load_format=load_format,
        enforce_eager=enforce_eager,
    )


def download_file_if_not_exists(url, save_path):
    if not os.path.exists(save_path):  # Check if the file already exists
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(save_path, "wb") as file:
                file.write(response.content)
            print(f"File downloaded and saved as {save_path}")
        else:
            print(f"Failed to download file. HTTP status code: {response.status_code}")
    else:
        print(f"File {save_path} already exists.")


@llm.command(short_help="Collect the metrics of a running LLM server.")
def collect(
    duration: int = typer.Option(600, help="The duration of the collection."),
    print_metrics: bool = typer.Option(False, help="Whether to print the metrics."),
):
    from mw_python_sdk.llm.monitor import collect_with_duration
    from mw_python_sdk import create_dataset

    if not os.path.exists("./llm_benchmark"):
        os.makedirs("./llm_benchmark")
    if os.path.exists("./llm_benchmark/metrics.csv"):
        os.remove("./llm_benchmark/metrics.csv")
    collect_with_duration(duration, "./llm_benchmark/metrics.csv", print_metrics)
    create_dataset("llm_benchmark", "./llm_benchmark", "", "llm benchmark metrics")


@llm.command(short_help="Bench an online serving model.")
def bench(
    base_url: str = typer.Option(
        "http://127.0.0.1:8000", help="The base URL of the model."
    ),
    model: str = typer.Option(None, help="The ID of the model to use."),
    tokenizer: str = typer.Option(None, help="The tokenizer path to use."),
    dataset_name: str = typer.Option("sharegpt", help="The dataset name to use."),
    dataset_path: str = typer.Option(None, help="The dataset path to use."),
    backend: str = typer.Option("vllm", help="The backend to use."),
    share_gpt_context_length: int = typer.Option(
        4096, help="The shared GPT context length."
    ),
    num_prompts: int = typer.Option(1000, help="The number of prompts to use."),
    output_len: int = typer.Option(None, help="The output length."),
    request_rate: float = typer.Option(float("inf"), help="The request rate."),
    max_concurrency: int = typer.Option(None, help="The maximum concurrency."),
    disable_tqdm: bool = typer.Option(False, help="Whether to disable tqdm."),
):
    from mw_python_sdk.llm.bench import (
        benchmark,
        get_dataset,
        get_tokenizer,
        set_ulimit,
    )
    from mw_python_sdk.llm.plot import plot_metrics

    set_ulimit()
    api_url = f"{base_url}/v1/completions"
    model_url = f"{base_url}/v1/models"
    if model is None:
        response = requests.get(model_url, timeout=10)
        model_list = response.json().get("data", [])
        model = model_list[0]["id"] if model_list else None
    if tokenizer is None:
        print("tokenizer not specified, download default tokenizer.")
        # download from https://heywhale-public.oss-cn-shanghai.aliyuncs.com/llm-bench/tokenizer.json
        download_file_if_not_exists(
            "https://heywhale-public.oss-cn-shanghai.aliyuncs.com/llm-bench/tokenizer.json",
            "tokenizer.json",
        )
        tokenizer = "tokenizer.json"
    if dataset_path is None:
        print("dataset path not specified, download default dataset.")
        # download from https://heywhale-public.oss-cn-shanghai.aliyuncs.com/llm-bench/ShareGPT_V3_unfiltered_cleaned_split.json
        download_file_if_not_exists(
            "https://heywhale-public.oss-cn-shanghai.aliyuncs.com/llm-bench/ShareGPT_V3_unfiltered_cleaned_split.json",
            "ShareGPT_V3_unfiltered_cleaned_split.json",
        )
        dataset_path = "ShareGPT_V3_unfiltered_cleaned_split.json"
    print(f"Using tokenzier: {tokenizer}")
    print(f"Get dataset {dataset_name} from {dataset_path}")
    tkzr = get_tokenizer(tokenizer)
    input_requests = get_dataset(
        dataset_name,
        dataset_path,
        num_prompts,
        share_gpt_context_length,
        output_len,
        tkzr,
    )
    asyncio.run(
        benchmark(
            backend=backend,
            api_url=api_url,
            base_url=base_url,
            model_id=model,
            tokenizer=tkzr,
            input_requests=input_requests,
            request_rate=request_rate,
            max_concurrency=max_concurrency,
            disable_tqdm=disable_tqdm,
            lora_name="",
            extra_request_body=dict(),
            profile=False,
        )
    )
    if os.environ.get("MW_TOKEN") is None:
        print("MW_TOKEN not set, skip handling metrics.")
        return
    from mw_python_sdk import download_file, list_datasets

    iter = list_datasets("llm_benchmark")
    dataset = next(iter)
    print("Downloading metrics.csv from dataset", dataset._id)
    if os.path.exists("metrics.csv"):
        os.remove("metrics.csv")
    if os.path.exists("metrics.png"):
        os.remove("metrics.png")
    downloaded_file = download_file(dataset._id, "metrics.csv", local_dir="./")
    plot_metrics(downloaded_file, "metrics.png")
    print("Saved metrics plot as metrics.png")


datasets = typer.Typer(short_help="The datasets management.")


@datasets.command(short_help="Create a new dataset by uploading a directory.")
def create(
    name: str = typer.Argument(..., help="The name of the dataset to create."),
    source: str = typer.Argument(..., help="The path to the directory to upload."),
    description: str = typer.Option(None, help="The description of the dataset."),
):
    from mw_python_sdk import create_dataset

    create_dataset(name, source, "", description)
    return


@datasets.command(short_help="Upload a file or directory to the dataset.")
def upload(
    source: str = typer.Argument(
        help="The path to the file or the directory to upload."
    ),
    destination: str = typer.Argument(
        help="The destination of the file or the directory in the dataset."
    ),
    dataset: str = typer.Argument(help="The ID of the dataset to upload in."),
    overwrite: bool = typer.Option(
        False, help="Whether to overwrite the file if it already exists."
    ),
    recursive: bool = typer.Option(
        False, "-r", help="Whether to recursively upload all files in the directory."
    ),
):
    import os

    from mw_python_sdk import upload_file, upload_folder

    if recursive:
        if not os.path.isdir(source):
            raise ValueError("Source must be a directory when using --recursive.")
        upload_folder(source, destination, dataset, overwrite)
        return
    else:
        upload_file(source, destination, dataset, overwrite)
        return


@datasets.command(short_help="Download a file or directory from the dataset.")
def download(
    dataset: str = typer.Argument(..., help="The ID of the dataset to download from."),
    source: str = typer.Argument(
        None, help="The name of the file or the directory to download."
    ),
    destination: str = typer.Option(
        None, "-d", help="The destination directory of the downloaded file."
    ),
    recursive: bool = typer.Option(
        False,
        "-r",
        help="Whether to recursively download all files in the directory.",
    ),
):
    from mw_python_sdk import download_dir, download_file

    if recursive or source is None:
        downloaded_dir = download_dir(dataset, sub_dir=source, local_dir=destination)
        print(f"Successfully downloaded to {downloaded_dir}")
        return
    else:
        downloaded_file = download_file(dataset, source, local_dir=destination)
        print(f"Successfully downloaded to {downloaded_file}")
        return


app = typer.Typer()
app.add_typer(llm, name="llm")
app.add_typer(datasets, name="ds")


@app.command(short_help="Set up a fast reverse proxy.")
def frp(port: int = typer.Argument(..., help="The port of the proxy.")):
    from mw_python_sdk.frp import fast_reverse_proxy

    fast_reverse_proxy(port)


@app.command(short_help="Set up a SSH tunnel.")
def ssh(
    port: int = typer.Option(
        22,
        "-p",
        help="The ssh port to use. Default is 22.",
    ),
    password: str = typer.Option(
        "P@ssword123",
        "-P",
        help="The password to use. Default is P@ssword123.",
    ),
):
    from mw_python_sdk.frp import fast_reverse_proxy_ssh

    fast_reverse_proxy_ssh(port, password)


@app.command(short_help="Set a VSCode tunnel for remote development.")
def tunnel():
    # Set up cache directory
    cache_dir = os.path.expanduser("~/.cache/mw/bin")
    os.makedirs(cache_dir, exist_ok=True)
    if not os.path.exists(os.path.join(cache_dir, "code")):
        download_file_if_not_exists(
            "https://heywhale-public.oss-cn-shanghai.aliyuncs.com/vscode/code",
            os.path.join(cache_dir, "code"),
        )
    # Make executable
    # print("Make file executable")
    os.chmod(os.path.join(cache_dir, "code"), 0o755)
    # run the command 'code tunnel' and pipe the input and the output
    process = subprocess.Popen(
        [os.path.join(cache_dir, "code"), "tunnel"], universal_newlines=True
    )
    process.wait()


if __name__ == "__main__":
    app()
