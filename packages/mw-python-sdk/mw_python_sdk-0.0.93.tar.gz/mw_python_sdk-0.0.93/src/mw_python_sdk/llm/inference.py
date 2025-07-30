import uvicorn
import json
import os
import tempfile
import subprocess
from typing import Optional
from mw_python_sdk import download_dir, download_file, upload_file

# TODO:  python -m vllm.entrypoints.openai.api_server --max-num-seq=2 --max-model-len=4096
# --served-model-name=llama3.2 --dtype=half --model
# ~/.cache/mw/datasets/673ee141f375c298a7100cd2/snapshots/673ee141f375c298a7100cfa
# --quantization bitsandbytes --load-format bitsandbytes --enforce-eager


def get_gpu_count():
    # Get the value of NVIDIA_VISIBLE_DEVICES environment variable
    visible_devices = os.getenv("NVIDIA_VISIBLE_DEVICES", "")

    if not visible_devices:
        raise ValueError("NVIDIA_VISIBLE_DEVICES is not set or empty.")

    # The environment variable can be a comma-separated list of GPU indices or UUIDs.
    # Count the number of items in the list
    gpu_count = len(visible_devices.split(","))

    return gpu_count


def get_first_gpu_type():
    # Run the nvidia-smi command to get GPU info
    result = subprocess.run(
        ["nvidia-smi", "-L"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    if result.returncode != 0:
        raise Exception(
            "Error executing nvidia-smi. Ensure NVIDIA drivers are installed and nvidia-smi is accessible."
        )

    # Extract the first GPU from the output
    gpu_info = result.stdout.strip().split("\n")[0]

    return gpu_info


def serve(
    model_id: str,
    model_name: str,
    host: str = "127.0.0.1",
    port: int = 8080,
    dtype: str = "auto",
    max_model_len: int = 1024,
    max_num_seq: int = 10,
    tensor_parallel_size: int = 0,
    gpu_memory_utilization: float = 0.98,
    quantization: Optional[str] = None,
    load_format: Optional[str] = None,
    enforce_eager: bool = False,
):
    if model_id == "_echo_":
        uvicorn.run("mw_python_sdk.llm.echo_server:app", host=host, port=port)
    else:
        if os.path.exists(model_id):
            model_dir = model_id
        else:
            model_dir = download_dir(model_id)
            if model_name == "":
                model_name = model_id
        gpu_type = get_first_gpu_type()
        if "V100" in gpu_type:
            dtype = "half"
        if tensor_parallel_size == 0:
            tensor_parallel_size = get_gpu_count()
        # quantization
        extra_arguments = ""
        if quantization:
            extra_arguments += f" --quantization {quantization}"
        if load_format:
            extra_arguments += f" --load-format {load_format}"
        if enforce_eager:
            extra_arguments += " --enforce-eager"
        subprocess.call(
            [
                "bash",
                "-c",
                (
                    f"python -m vllm.entrypoints.openai.api_server --tensor-parallel-size {tensor_parallel_size} "
                    f"--max-num-seq={max_num_seq} "
                    f"--max-model-len={max_model_len} --served-model-name={model_name} "
                    f"--trust-remote-code "
                    f"--gpu-memory-utilization={gpu_memory_utilization} "
                    f"--dtype={dtype} --model '{model_dir}' --host {host} --port {port} {extra_arguments}"
                ),
            ]
        )


def inference(
    model_id: str,
    source_dataset_id: str,
    source_dataset_path: str,
    destination_dataset_id: str,
    destination_dataset_path: str,
    dtype: str = "half",
    max_model_len: int = 4096,
):
    from vllm import LLM, SamplingParams

    model_dir = download_dir(model_id)
    input_content_path = download_file(source_dataset_id, source_dataset_path)

    with open(input_content_path, "r") as input_file:
        prompts = json.load(input_file)
        # Create a sampling params object.
        sampling_params = SamplingParams(temperature=0.8, top_p=0.95)
        # Create an LLM.
        llm = LLM(model=str(model_dir), dtype=dtype, max_model_len=max_model_len)
        # Generate texts from the prompts. The output is a list of RequestOutput objects
        # that contain the prompt, generated text, and other information.
        outputs = llm.generate(prompts, sampling_params)
        answers = []
        # Print the outputs.
        for output in outputs:
            prompt = output.prompt
            generated_text = output.outputs[0].text
            answers.append({"prompt": prompt, "answer": generated_text})
        # Create a temporary file
        with tempfile.NamedTemporaryFile(
            delete=False, mode="w+", suffix=".json"
        ) as tmp_file:
            # Write the Python object as JSON to the temporary file
            json.dump(answers, tmp_file)
            tmp_file.flush()
            # print(tmp_file.name)
            upload_file(
                tmp_file.name,
                destination_dataset_path,
                destination_dataset_id,
                overwrite=True,
            )
