# AWS Bedrock Code Assistant

An interactive, terminal-based code assistant powered by AWS Bedrock with support for multiple AI models.

## Features

- 🤖 **AI-Powered Code Assistance** - Ask questions and get instant responses from AWS Bedrock models
- 💬 **Interactive Mode** - Conversational interface with command support
- 📂 **File Operations** - Read and analyze code files
- ⚙️ **Command Execution** - Execute shell commands with safety confirmations
- 🎨 **Formatted Output** - Beautiful, colored terminal output
- 🔐 **Secure Configuration** - API keys stored locally, never committed to Git

## Requirements

- Python 3.8+
- AWS Account with Bedrock access
- boto3 library

## Installation

1. **Clone or download the project**
   ```bash
   cd copilot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure AWS credentials**
   ```bash
   # Copy the example config
   cp config.example.json config.json
   
   # Edit with your AWS credentials
   # config.json (DO NOT COMMIT THIS FILE - It's in .gitignore)
   {
     "aws": {
       "access_key_id": "YOUR_ACCESS_KEY_ID",
       "secret_access_key": "YOUR_SECRET_ACCESS_KEY",
       "region": "us-east-1"
     }
   }
   ```

## Usage

### Interactive Mode (Default)
```bash
python main.py
```

Then use commands:
- `ask <question>` - Ask the AI a question
- `models` - List available Bedrock models
- `exec <command>` - Execute a shell command
- `help` - Show available commands
- `exit` - Exit the assistant

### Command Line Mode

**Ask a question:**
```bash
python main.py ask "What is the best practice for error handling in Python?"
```

**List available models:**
```bash
python main.py list-models
```

**Execute a command:**
```bash
python main.py exec "python --version"
```

## Configuration

### config.example.json
Template configuration file for reference. This file is safe to commit.

### config.json
Your local configuration with AWS credentials. **This file is in .gitignore and should NEVER be committed.**

Create it by copying the example:
```bash
cp config.example.json config.json
```

Then edit with your credentials:
```json
{
  "aws": {
    "access_key_id": "YOUR_ACCESS_KEY_ID",
    "secret_access_key": "YOUR_SECRET_ACCESS_KEY",
    "region": "us-east-1"
  },
  "bedrock": {
    "default_model": "anthropic.claude-opus-4-5-20251101-v1:0",
    "max_tokens": 2048,
    "temperature": 0.7
  }
}
```

## Security Notes

⚠️ **CRITICAL SECURITY REQUIREMENTS:**

1. **Never commit API keys to Git**
   - `config.json` is in `.gitignore`
   - Always use local configuration files
   - For production, use AWS IAM roles

2. **Code Language**
   - All code is in English
   - All comments and documentation are in English
   - Maintains GitHub project standards

3. **Configuration**
   - Use `config.example.json` as a template
   - Create local `config.json` with your credentials
   - Environment variables support coming in v2

## Available Models

128+ models available through AWS Bedrock:

- **Claude** - Anthropic's Claude models (Opus, Sonnet, Haiku)
- **Llama** - Meta's Llama models (3.1, 3.2, 3.3)
- **Mistral** - Mistral AI models
- **Gemma** - Google's Gemma models
- **GPT** - OpenAI OSS models
- **DeepSeek** - DeepSeek research models
- **Nova** - Amazon's Nova models
- **Image Generation** - Stability AI models
- **Embeddings** - Multiple embedding models

Use `list-models` command to see all available options.

## Project Structure

```
copilot/
├── main.py                 # Entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── .gitignore             # Git ignore rules
├── config.example.json    # Configuration template (commit this)
├── config.json            # Local config (DO NOT COMMIT)
├── config/
│   ├── __init__.py
│   └── settings.py        # Configuration loading
├── core/
│   ├── __init__.py
│   └── aws_client.py      # Bedrock client
├── utils/
│   ├── __init__.py
│   ├── output.py          # Output formatting
│   └── command.py         # Command execution
├── commands/
│   └── __init__.py        # Command handlers
└── .git/                  # Version control
```

## Development

### Adding New Commands

1. Create a new file in `commands/`
2. Implement command class
3. Register in `main.py`

Example:
```python
class AnalyzeCommand:
    def execute(self, args):
        # Your command logic
        pass
```

## Troubleshooting

### Error: "Configuration file not found"
```bash
cp config.example.json config.json
# Edit config.json with your credentials
```

### Error: "Failed to list models"
- Check AWS credentials in `config.json`
- Verify Bedrock access in AWS account
- Ensure region is correct (default: us-east-1)

### Error: "Model invocation failed"
- Check model ID is correct
- Verify sufficient AWS credentials
- Check Bedrock throughput settings

## Contributing

This is a local development project. For improvements:

1. Create a new branch
2. Make your changes
3. Keep all code in English
4. Never commit `config.json`
5. Commit changes to Git

## License

MIT License

## Support

For issues or questions:
1. Check the README
2. Verify AWS configuration
3. Review error messages
4. Check AWS Bedrock documentation

---

**Version**: 1.0.0  
**Last Updated**: 2026-03-27
