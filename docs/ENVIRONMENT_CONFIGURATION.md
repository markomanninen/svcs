# SVCS Environment Configuration Guide

This## AI Fallback Chain

SVCS attempts AI analysis in this order:
1. **Google Gemini** (if `GOOGLE_API_KEY` set)
2. **OpenAI GPT-4o-mini** (if `OPENAI_API_KEY` set)  
3. **Anthropic Claude** (if `ANTHROPIC_API_KEY` set)
4. **Ollama Local** (if Ollama is running)

## Available Models

### Google Gemini Models
- `gemini-2.5-flash` (latest, recommended) - Best price/performance balance
- `gemini-2.5-pro` - Most capable, higher cost
- `gemini-1.5-flash` - Previous generation, stable
- `gemini-1.5-pro` - Previous generation, more capable

### OpenAI Models  
- `gpt-4o-mini` (recommended) - Fast and cost-effective
- `gpt-4o` - More capable, higher cost
- `gpt-4-turbo` - Previous generation
- `gpt-3.5-turbo` - Older, budget option

### Anthropic Claude Models
- `claude-3-5-haiku-20241022` (latest, recommended) - Fast and efficient
- `claude-3-5-sonnet-20241022` - Balanced performance
- `claude-3-opus-20240229` - Most capable, highest cost
- `claude-3-haiku-20240307` - Previous generation

### Ollama Models
- `deepseek-r1:8b` (recommended) - Good reasoning capabilities
- `llama2:13b` - Alternative option
- `codellama:13b` - Code-focused
- Any locally available model via `ollama list`nt explains how to configure SVCS using environment variables through the `.env` file.

## Quick Setup

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your preferences:
   ```bash
   nano .env  # or use your preferred editor
   ```

3. SVCS will automatically load these settings

## Configuration Categories

### 🤖 AI Analysis Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `GOOGLE_API_KEY` | None | Google Gemini API key (primary AI) |
| `GOOGLE_MODEL` | `gemini-2.5-flash` | Google Gemini model to use |
| `OPENAI_API_KEY` | None | OpenAI API key (fallback) |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model to use |
| `ANTHROPIC_API_KEY` | None | Anthropic Claude API key (fallback) |
| `ANTHROPIC_MODEL` | `claude-3-5-haiku-20241022` | Anthropic model to use |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `deepseek-r1:8b` | Ollama model for analysis |
| `AI_TIMEOUT` | `30` | AI analysis timeout (seconds) |
| `AI_COMPLEXITY_THRESHOLD` | `2` | Minimum complexity for AI analysis |
| `AI_MAX_RETRIES` | `3` | Maximum retries for AI calls |

### 🔧 General SVCS Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `SVCS_DEBUG` | `false` | Enable debug output |
| `SVCS_DB_PATH` | `.svcs/semantic.db` | Database file path |
| `SVCS_ENABLE_HOOKS` | `true` | Enable git hooks |

## AI Fallback Chain

SVCS attempts AI analysis in this order:
1. **Google Gemini** (if `GOOGLE_API_KEY` set)
2. **OpenAI** (if `OPENAI_API_KEY` set)  
3. **Anthropic Claude** (if `ANTHROPIC_API_KEY` set)
4. **Ollama Local** (if Ollama is running)

## Model Selection

All AI providers support custom model selection via environment variables:

### Google Gemini Models
- `gemini-1.5-flash` (default) - Fast, cost-effective
- `gemini-1.5-pro` - Higher quality, slower
- `gemini-1.0-pro` - Legacy model

### OpenAI Models  
- `gpt-4o-mini` (default) - Cost-effective, good quality
- `gpt-4o` - Higher quality, more expensive
- `gpt-4-turbo` - Previous generation
- `gpt-3.5-turbo` - Budget option

### Anthropic Models
- `claude-3-haiku-20240307` (default) - Fast, economical
- `claude-3-sonnet-20240229` - Balanced performance
- `claude-3-opus-20240229` - Highest quality

### Ollama Models (Local)
- `deepseek-r1:8b` (default) - Good code analysis
- `llama2:13b` - General purpose
- `codellama:7b` - Code-focused
- `mistral:7b` - Efficient alternative

Example `.env` with custom models:
```bash
GOOGLE_MODEL=gemini-1.5-pro
OPENAI_MODEL=gpt-4o
ANTHROPIC_MODEL=claude-3-sonnet-20240229
OLLAMA_MODEL=codellama:13b
```

## Complexity Threshold

The `AI_COMPLEXITY_THRESHOLD` determines when AI analysis is triggered:

- **1**: Very sensitive (analyzes simple changes)
- **2**: Balanced (default, good for most projects)
- **3**: Conservative (only complex changes)
- **4+**: Very selective (major refactoring only)

## Examples

### Development Setup
```bash
# .env for development
SVCS_DEBUG=true
AI_COMPLEXITY_THRESHOLD=1
OLLAMA_MODEL=deepseek-r1:8b
```

### Production Setup
```bash
# .env for production
GOOGLE_API_KEY=your_actual_api_key_here
AI_COMPLEXITY_THRESHOLD=2
SVCS_DEBUG=false
```

### Local-Only Setup (No Cloud APIs)
```bash
# .env for local Ollama only
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=deepseek-r1:8b
AI_COMPLEXITY_THRESHOLD=2
```

## Security Notes

- ⚠️ **Never commit `.env` files** to version control
- ✅ The `.env` file is already in `.gitignore`
- ✅ Use `.env.example` for sharing configuration templates
- ✅ Store production API keys securely (e.g., CI/CD secrets)

## Troubleshooting

### Configuration not loading?
1. Check `.env` file exists in project root
2. Verify `python-dotenv` is installed: `pip install python-dotenv`
3. Enable debug mode: `SVCS_DEBUG=true`

### AI analysis not working?
1. Check API keys are valid
2. Verify model availability (for Ollama: `ollama list`)
3. Lower complexity threshold for testing: `AI_COMPLEXITY_THRESHOLD=1`

### Debug output
Enable debug mode to see configuration loading:
```bash
echo "SVCS_DEBUG=true" >> .env
```

This will show which settings are loaded and which AI models are attempted.
