# Azure Speech Services Configuration

## Required Environment Variables

```bash
# Azure Speech Services (STT)
EKKO_AZURE_SPEECH_KEY=your-azure-speech-key-here
EKKO_AZURE_SPEECH_REGION=northeurope
EKKO_AZURE_SPEECH_LANGUAGE=da-DK

# OpenAI (LLM)
EKKO_OPENAI_API_KEY=your-openai-api-key-here

# Azure OpenAI (Alternative to OpenAI)
# EKKO_AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
# EKKO_AZURE_OPENAI_KEY=your-azure-openai-key
# EKKO_AZURE_OPENAI_VERSION=2025-02-01-preview

# Application
EKKO_ENVIRONMENT=local
EKKO_DEBUG=true
EKKO_HOST=127.0.0.1
EKKO_PORT=8000
```

## Getting Azure Speech Services Credentials

1. **Create Azure Account** (if you don't have one):
   - Go to <https://azure.microsoft.com/>
   - Sign up for free tier (includes 5 hours of free speech recognition per month)

2. **Create a Speech Service Resource**:

   ```bash
   # Using Azure CLI
   az cognitiveservices account create \
     --name ekko-speech \
     --resource-group ekko-rg \
     --kind SpeechServices \
     --sku F0 \
     --location northeurope
   ```

   Or use the Azure Portal:
   - Navigate to <https://portal.azure.com>
   - Search for "Speech Services"
   - Click "Create" → "Speech"
   - Fill in resource details
   - Select "Free F0" pricing tier for development
   - Click "Review + Create"

3. **Get Your Credentials**:

   ```bash
   # Using Azure CLI
   az cognitiveservices account keys list \
     --name ekko-speech \
     --resource-group ekko-rg
   ```

   Or from Azure Portal:
   - Go to your Speech resource
   - Click "Keys and Endpoint" in the left menu
   - Copy KEY 1 or KEY 2
   - Note the REGION (e.g., "northeurope")

4. **Set Environment Variables**:

   ```bash
   export EKKO_AZURE_SPEECH_KEY="paste-your-key-here"
   export EKKO_AZURE_SPEECH_REGION="northeurope"
   ```

## Supported Regions

Common Azure Speech Services regions:

- `northeurope` (Ireland)
- `westeurope` (Netherlands)
- `eastus` (Virginia, USA)
- `westus` (California, USA)
- `southeastasia` (Singapore)

For full list: <https://learn.microsoft.com/en-us/azure/ai-services/speech-service/regions>

## Supported Languages

The application is configured for Danish (`da-DK`) by default. To change:

```bash
export EKKO_AZURE_SPEECH_LANGUAGE=en-US  # English (US)
# or
export EKKO_AZURE_SPEECH_LANGUAGE=sv-SE  # Swedish
# or
export EKKO_AZURE_SPEECH_LANGUAGE=no-NO  # Norwegian
```

Full language support: <https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support>

## Audio Requirements

Azure Speech SDK expects:

- **Sample Rate**: 16 kHz (recommended for speech)
- **Channels**: Mono (1 channel)
- **Sample Width**: 16-bit PCM

The application captures at 48 kHz stereo and converts internally before sending to Azure.

## Free Tier Limits

Azure Speech Services free tier (F0):

- **Speech-to-Text**: 5 audio hours per month
- **Real-time transcription**: 20 concurrent requests
- **Rate**: 60 concurrent requests/minute

After free tier exhausted, costs are:

- Standard: $1 per audio hour
- Custom speech: $1.40 per audio hour

## Troubleshooting

### "EKKO_AZURE_SPEECH_KEY environment variable is required"

- Ensure the environment variable is set before starting the app
- Check for typos in the variable name
- Verify the key is not empty

### "Failed to create recognizer"

- Check that your region is correct
- Verify your subscription key is valid
- Ensure you have network connectivity
- Check that you haven't exceeded free tier limits

### "No speech recognized"

- Verify your microphone is working
- Check audio input device settings
- Ensure audio sample rate is 16 kHz
- Try increasing microphone volume

### High latency / slow transcription

- Check network connection quality
- Verify you're using the closest Azure region
- Consider upgrading from free tier if rate-limited

## Cost Monitoring

To monitor your Azure Speech Services usage:

```bash
# Check usage (Azure CLI)
az monitor metrics list \
  --resource /subscriptions/{subscription-id}/resourceGroups/ekko-rg/providers/Microsoft.CognitiveServices/accounts/ekko-speech \
  --metric TotalCalls \
  --start-time 2026-05-01T00:00:00Z
```

Or use Azure Portal → Cost Management + Billing → Cost Analysis

## Migration from Faster Whisper

If you were using the old Faster Whisper implementation:

1. **Dependencies**:
   - Old: `faster-whisper`, `ctranslate2` (large, CPU/GPU-bound)
   - New: `azure-cognitiveservices-speech` (lightweight, cloud-based)

2. **Configuration**:
   - Old env vars `EKKO_STT_DEVICE` and `EKKO_STT_COMPUTE_TYPE` are deprecated
   - New env vars: `EKKO_AZURE_SPEECH_KEY`, `EKKO_AZURE_SPEECH_REGION`, `EKKO_AZURE_SPEECH_LANGUAGE`

3. **Latency**:
   - Old: 5+ seconds (batched every 5 seconds)
   - New: ~300ms (true streaming)

4. **Model**:
   - Old: Local model file (~150MB download)
   - New: Cloud-based (no local model)

5. **Offline Operation**:
   - Old: Works offline
   - New: Requires internet connection

If you need offline operation, the old Faster Whisper implementation can be restored by:

- Adding `faster-whisper>=1.2.0` to dependencies
- Reverting the STT adapter factory
- This is not recommended for production use
