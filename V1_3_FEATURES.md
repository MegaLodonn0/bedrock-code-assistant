# V1.3 Features - Model Selection & Usage Tracking

## Overview
V1.3 introduces a complete redesign of the model selection experience with real-time usage limit tracking.

## Key Improvements

### 1. Two-Stage Model Selection
The `/models` command now provides a superior user experience:

**Stage 1: Provider Selection**
- Full-screen interface showing all 17 providers
- Clear model count for each provider
- Simple numeric selection (1-17)

**Stage 2: Model Selection**
- Full-screen dedicated interface for chosen provider
- All models from that provider clearly listed
- Model ID displayed for reference
- Easy numeric selection

### 2. Usage Limits Display
After model selection, users see:

```
[OK] Selected Model:
  Name: Claude Haiku 4.5
  ID: anthropic.claude-haiku-4-5-20251001-v1:0
  Provider: Anthropic

Usage Limits:
  Daily: 0/100000..... [--------] 0%
  Monthly: 0/1000000.. [--------] 0%
```

**Features:**
- Real AWS Bedrock API queries (not mock data)
- Daily usage tracking with percentage
- Monthly usage tracking with percentage
- Color-coded progress bars:
  - Green: < 50% usage
  - Yellow: 50-80% usage
  - Red: > 80% usage

### 3. AWS Integration
The `/usage` command queries actual AWS Bedrock metrics:
- Calls `list_provisioned_model_throughputs()`
- Retrieves real daily/monthly usage
- Displays provisioned throughput information

## User Flow

```
User: /models
  ↓
[Provider Selection Screen]
  ↓
User selects provider (e.g., "Anthropic")
  ↓
[Model Selection Screen for Anthropic]
  ↓
User selects model (e.g., "Claude Haiku 4.5")
  ↓
[Confirmation with Usage Limits]
  ↓
Usage metrics displayed from AWS
```

## Technical Changes

### Modified Files
- **main.py**: Updated `_cmd_list_models()` to use `ProviderScreen` instead of table format

### Implementation Details
- Leverages existing `ProviderScreen` class for full-screen UI
- Uses `UsageTracker` for real AWS data retrieval
- Maintains Windows/Unix terminal compatibility
- All output uses ASCII-compatible symbols for Windows terminals

## Testing Notes
✅ Tested provider selection with all 17 providers
✅ Tested model selection for Anthropic (18 models)
✅ Verified usage limits display from AWS API
✅ Confirmed color-coded progress bars work correctly

## Future Enhancements
- [ ] Search/filter models by capability
- [ ] Show model pricing information
- [ ] Persist selected model choice
- [ ] Display model input/output token limits
- [ ] Show latest model version availability
