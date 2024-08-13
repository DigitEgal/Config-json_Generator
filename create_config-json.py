import os
import re
import json
import subprocess
import sys

def get_transformers_version():
    try:
        import transformers
        return transformers.__version__
    except ImportError:
        print("The 'transformers' library is not installed.")
        install = input("Do you want to install 'transformers' now? (y/n): ").strip().lower()
        if install == 'y':
            subprocess.check_call([sys.executable, "-m", "pip", "install", "transformers"])
            import transformers
            return transformers.__version__
        else:
            print("Cannot proceed without the 'transformers' library.")
            sys.exit(1)

def scrape_finetune_script(script_path):
    config = {}
    with open(script_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Regex patterns to detect key configurations
    patterns = {
        "hidden_size": r"hidden_size\s*=\s*(\d+)",
        "num_hidden_layers": r"num_hidden_layers\s*=\s*(\d+)",
        "intermediate_size": r"intermediate_size\s*=\s*(\d+)",
        "max_position_embeddings": r"max_position_embeddings\s*=\s*(\d+)",
        "num_attention_heads": r"num_attention_heads\s*=\s*(\d+)",
        "model_type": r"model_name\s*=\s*[\"'](.+?)[\"']",
        "rope_scaling": r"rope_scaling\s*=\s*(\{.*?\})",
        "use_cache": r"use_cache\s*=\s*(True|False)",
        "quantization_config": r"quantization_config\s*=\s*(\{.*?\})",
    }

    for key, pattern in patterns.items():
        for line in lines:
            match = re.search(pattern, line)
            if match:
                if key in ["rope_scaling", "quantization_config"]:  # Handle dictionary parsing
                    config[key] = eval(match.group(1))
                else:
                    config[key] = match.group(1)
                break

    return config

def ask_user_for_config_option(name, default=None, mandatory=True):
    while True:
        prompt = f"Please enter {name} (default: {default}){' [optional]' if not mandatory else ''}: "
        user_input = input(prompt).strip()
        if not user_input and default is not None:
            return default
        if not user_input and not mandatory:
            return None
        try:
            return eval(user_input) if isinstance(default, (int, float, dict, list)) else user_input
        except (NameError, SyntaxError):
            print(f"Invalid input for {name}. Please try again.")

def load_existing_config(config_path):
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def create_config(script_path, existing_config_path=None, output_dir="."):
    # Load existing config if provided
    existing_config = load_existing_config(existing_config_path) if existing_config_path else {}

    # Scrape the finetune script
    scraped_config = scrape_finetune_script(script_path)

    # Merge scraped config with existing config, prioritizing the scraped values
    config = {**existing_config, **scraped_config}

    mandatory_fields = {
        "_name_or_path": "Please provide the model name or path (e.g., 'unsloth/Meta-Llama-3.1-8B'): ",
        "architectures": "Please provide the architecture (e.g., 'LlamaForCausalLM'): ",
        "hidden_size": "Please provide the hidden size (e.g., 4096): ",
        "num_hidden_layers": "Please provide the number of hidden layers (e.g., 32): ",
        "intermediate_size": "Please provide the intermediate size (e.g., 14336): ",
        "max_position_embeddings": "Please provide the max position embeddings (e.g., 131072): ",
        "num_attention_heads": "Please provide the number of attention heads (e.g., 32): ",
        "model_type": "Please provide the model type (e.g., 'llama'): ",
        "vocab_size": "Please provide the vocabulary size (e.g., 128256): ",
        "torch_dtype": "Please provide the torch dtype (e.g., 'bfloat16'): ",
        "transformers_version": get_transformers_version(),
    }

    optional_fields = {
        "attention_bias": "Does the model use attention bias? (True/False): ",
        "attention_dropout": "Please provide the attention dropout rate (e.g., 0.0): ",
        "bos_token_id": "Please provide the BOS token ID (e.g., 128000): ",
        "eos_token_id": "Please provide the EOS token ID (e.g., 128001): ",
        "mlp_bias": "Does the model use MLP bias? (True/False): ",
        "num_key_value_heads": "Please provide the number of key/value heads (e.g., 8): ",
        "pad_token_id": "Please provide the PAD token ID (e.g., 128004): ",
        "pretraining_tp": "Please provide the pretraining TP (e.g., 1): ",
        "rope_scaling": "Provide rope scaling settings if used (leave blank if not): ",
        "rope_theta": "Please provide the rope theta (e.g., 500000.0): ",
        "tie_word_embeddings": "Are word embeddings tied? (True/False): ",
        "use_cache": "Does the model use cache? (True/False): ",
        "quantization_config": "Provide quantization settings if used (leave blank if not): ",
        "rms_norm_eps": "Please provide the RMS norm epsilon (e.g., 1e-05): ",
    }

    # Fill in mandatory fields
    for field, prompt in mandatory_fields.items():
        if field in config:
            print(f"{field} detected: {config[field]}")
        else:
            config[field] = ask_user_for_config_option(field, default=existing_config.get(field), mandatory=True)

    # Fill in optional fields
    for field, prompt in optional_fields.items():
        if field in config:
            print(f"{field} detected: {config[field]}")
        else:
            config[field] = ask_user_for_config_option(field, default=existing_config.get(field), mandatory=False)

    # Remove optional fields that were not provided
    config = {k: v for k, v in config.items() if v is not None}

    # Final confirmation and review
    print("\nConfig entries detected and filled:")
    for key, value in config.items():
        print(f"{key}: {value}")

    modify = input("\nDo you want to modify any entry? (y/n): ").strip().lower()
    if modify == 'y':
        while True:
            print("Enter the number corresponding to the field you want to modify or press Enter to continue:")
            for i, key in enumerate(config.keys(), 1):
                print(f"{i}. {key}: {config[key]}")
            choice = input("Your choice: ").strip()
            if not choice:
                break
            if choice.isdigit() and 1 <= int(choice) <= len(config):
                key_to_modify = list(config.keys())[int(choice) - 1]
                config[key_to_modify] = ask_user_for_config_option(key_to_modify, default=config[key_to_modify])

    # Check if a config.json already exists
    config_path = os.path.join(output_dir, "config.json")
    if os.path.exists(config_path):
        overwrite = input(f"{config_path} already exists. Do you want to overwrite it? (y/n): ").strip().lower()
        if overwrite != 'y':
            new_name = input("Enter a new name for the config file (e.g., config_new.json): ").strip()
            config_path = os.path.join(output_dir, new_name)

    # Write the config.json
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)

    print(f"Config saved to {config_path}")

if __name__ == "__main__":
    script_name = input("Please enter the finetune script filename (default: run_finetune.py): ").strip() or "run_finetune.py"
    script_path = os.path.join(os.getcwd(), script_name)

    existing_config = input("Do you want to load an existing config.json for defaults? (y/n): ").strip().lower()
    existing_config_path = None
    if existing_config == 'y':
        existing_config_name = input("Please enter the config.json filename (default: config.json): ").strip() or "config.json"
        existing_config_path = os.path.join(os.getcwd(), existing_config_name)

    create_config(script_path, existing_config_path)
