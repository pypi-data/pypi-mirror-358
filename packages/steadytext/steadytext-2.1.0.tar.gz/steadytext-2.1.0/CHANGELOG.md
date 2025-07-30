# Changelog

## Version 2.1.0 (2025-06-29)

### New Features
- **Custom Seed Support:** Added support for custom seed parameter in generation and embedding functions for enhanced deterministic control.

### Bug Fixes
- Various stability improvements and minor fixes.

## Version 2.0.4 (2025-06-28)

### Bug Fixes
- Documentation updates and code formatting improvements.
- Fixed various linting and type checking issues.

## Version 2.0.3 (2025-06-28)

### Bug Fixes
- Minor bug fixes and performance improvements.

## Version 2.0.2 (2025-06-28)

### Bug Fixes
- Fixed model loading and caching issues.

## Version 2.0.1 (2025-06-28)

### Bug Fixes
- **Fixed Model Repository:** Updated Gemma-3n model repository from `ggml-org` to `ggml-org` which hosts the latest GGUF versions
  - E2B model: Now uses `ggml-org/gemma-3n-E2B-it-GGUF` with filename `gemma-3n-E2B-it-Q8_0.gguf`
  - E4B model: Now uses `ggml-org/gemma-3n-E4B-it-GGUF` with filename `gemma-3n-E4B-it-Q8_0.gguf`

## Version 2.0.0 (2025-06-28)

### Major Changes
- **Switched to Gemma-3n:** The default generation model is now `gemma-3n-E2B-it-GGUF` (ggml-org/gemma-3n-E2B-it-GGUF).
- **Changed Default Model Size:** Default model changed from Gemma-3n-4B to Gemma-3n-2B for faster generation while maintaining quality.
- **Deprecated Thinking Mode:** The `thinking_mode` parameter has been removed from all functions and the CLI. Temperature=0 deterministic generation works better without thinking mode.
- **Model Registry Update:** Updated to focus on Gemma-3n models (2B and 4B variants).

### New Features
- **Configurable Generation Length:** Added `max_new_tokens` parameter to `generate()` and `generate_iter()` functions to control output length.
- **CLI Support:** Added `--max-new-tokens` flag to CLI for controlling generation length.

### Configuration Changes
- Reduced default context window from 3072 to 2048 tokens.
- Reduced default max new tokens for generation from 1024 to 512.
- Embedding model remains `Qwen3-Embedding-0.6B-GGUF` with 1024 dimensions.

### Breaking Changes
- Removed `thinking_mode` parameter from `generate()`, `generate_iter()`, and CLI
- Removed `--think` flag from CLI
- Changed default generation model from Qwen3-1.7B to Gemma-3n-E2B
- Changed default model size from "large" (4B) to "small" (2B)

## Version 1.3.5 (2025-06-23)

- Minor bug fixes and performance improvements.
