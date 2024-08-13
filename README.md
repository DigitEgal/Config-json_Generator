# Config.json Generator for Finetune Scripts

This script generates a `config.json` file for machine learning models, tailored specifically for complex finetuning scripts. It automates the process by scraping relevant information from the finetuning script and allows the user to customize and verify all configurations before saving the file.

## Features

- **Script Scraping**: Automatically extracts key configuration values from your finetuning script to fill in the `config.json`.
- **Existing Config Usage**: Optionally load an existing `config.json` to use as a base template, pre-filling fields to minimize manual input.
- **Transformers Version Detection**: Automatically detects the installed version of the `transformers` library and fills it in the config file. If `transformers` is not installed, it will prompt the user to install it.
- **Interactive User Prompts**: Guides the user through any missing or unclear configuration fields, ensuring that only valid values are entered.
- **Optional Fields Handling**: Identifies and excludes optional fields if not needed, streamlining the configuration process.
- **Final Review and Modification**: After generating the `config.json`, the user is given a chance to review and modify any entries before saving.
- **Existing File Handling**: If a `config.json` file already exists in the directory, the user can choose to overwrite it or save the new file with a different name.

## Prerequisites

- **Python 3.x**
- **Transformers Library**: The script requires the `transformers` library to detect the version. If it's not installed, the script will offer to install it.

## Installation

Clone the repository and navigate to the directory containing the script:

```bash
git clone https://github.com/yourusername/your-repo.git
cd your-repo
```

Ensure you have the necessary Python packages installed:

```bash
pip install -r requirements.txt
```

## Usage

To generate the `config.json` file, run the script and follow the prompts:

```bash
python create_config_json.py
```

### Workflow

1. **Finetune Script Scraping**: The script first asks for the name of the finetuning script located in the current directory. It then scrapes the script for relevant configuration details.
   
2. **Optional Existing Config**: You can provide an existing `config.json` file to use as a template. The script will pre-fill fields using this file where possible.

3. **Auto-Detected Fields**: The script automatically detects the installed version of `transformers` and other system configurations, inserting these values into the config file.

4. **Interactive Configuration**: The user is prompted to provide any missing or unclear values, with clear instructions and examples.

5. **Review and Modify**: Before saving, the script displays all the collected and auto-filled values. The user can modify any entries if needed.

6. **Saving**: The user can choose to overwrite an existing `config.json` file or save the new configuration under a different name.

### Example

Here is an example session:

```plaintext
Please enter the finetune script filename (default: run_finetune.py): run_finetune.py
Do you want to load an existing config.json for defaults? (y/n): y
Please enter the config.json filename (default: config.json): config_existing.json
_transformers_version detected: 4.43.2
hidden_size detected: 4096
Please enter the intermediate size (default: 14336): 15360
...
Config entries detected and filled:
1. _name_or_path: unsloth/Meta-Llama-3.1-8B
2. hidden_size: 4096
3. intermediate_size: 15360
...
Do you want to modify any entry? (y/n): n
config.json already exists. Do you want to overwrite it? (y/n): n
Enter a new name for the config file (e.g., config_new.json): config_new.json
Config saved to config_new.json
```

## Troubleshooting

- **Incorrect Scraping**: If the script fails to correctly scrape values from the finetuning script, you may need to manually enter those values during the interactive prompts.
- **Transformers Version**: Ensure `transformers` is installed and properly configured in your environment to avoid issues with version detection.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request if you'd like to contribute.
