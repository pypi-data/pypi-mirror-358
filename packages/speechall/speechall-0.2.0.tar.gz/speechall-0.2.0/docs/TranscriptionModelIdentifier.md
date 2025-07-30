# TranscriptionModelIdentifier

Unique identifier for a specific Speech-to-Text model, composed as `provider.model_name`. Used to select the engine for transcription.

## Enum

* `AMAZON_DOT_TRANSCRIBE` (value: `'amazon.transcribe'`)

* `ASSEMBLYAI_DOT_BEST` (value: `'assemblyai.best'`)

* `ASSEMBLYAI_DOT_NANO` (value: `'assemblyai.nano'`)

* `ASSEMBLYAI_DOT_SLAM_MINUS_1` (value: `'assemblyai.slam-1'`)

* `ASSEMBLYAI_DOT_UNIVERSAL` (value: `'assemblyai.universal'`)

* `AZURE_DOT_STANDARD` (value: `'azure.standard'`)

* `CLOUDFLARE_DOT_WHISPER` (value: `'cloudflare.whisper'`)

* `CLOUDFLARE_DOT_WHISPER_MINUS_LARGE_MINUS_V3_MINUS_TURBO` (value: `'cloudflare.whisper-large-v3-turbo'`)

* `CLOUDFLARE_DOT_WHISPER_MINUS_TINY_MINUS_EN` (value: `'cloudflare.whisper-tiny-en'`)

* `DEEPGRAM_DOT_BASE` (value: `'deepgram.base'`)

* `DEEPGRAM_DOT_BASE_MINUS_CONVERSATIONALAI` (value: `'deepgram.base-conversationalai'`)

* `DEEPGRAM_DOT_BASE_MINUS_FINANCE` (value: `'deepgram.base-finance'`)

* `DEEPGRAM_DOT_BASE_MINUS_GENERAL` (value: `'deepgram.base-general'`)

* `DEEPGRAM_DOT_BASE_MINUS_MEETING` (value: `'deepgram.base-meeting'`)

* `DEEPGRAM_DOT_BASE_MINUS_PHONECALL` (value: `'deepgram.base-phonecall'`)

* `DEEPGRAM_DOT_BASE_MINUS_VIDEO` (value: `'deepgram.base-video'`)

* `DEEPGRAM_DOT_BASE_MINUS_VOICEMAIL` (value: `'deepgram.base-voicemail'`)

* `DEEPGRAM_DOT_ENHANCED` (value: `'deepgram.enhanced'`)

* `DEEPGRAM_DOT_ENHANCED_MINUS_FINANCE` (value: `'deepgram.enhanced-finance'`)

* `DEEPGRAM_DOT_ENHANCED_MINUS_GENERAL` (value: `'deepgram.enhanced-general'`)

* `DEEPGRAM_DOT_ENHANCED_MINUS_MEETING` (value: `'deepgram.enhanced-meeting'`)

* `DEEPGRAM_DOT_ENHANCED_MINUS_PHONECALL` (value: `'deepgram.enhanced-phonecall'`)

* `DEEPGRAM_DOT_NOVA` (value: `'deepgram.nova'`)

* `DEEPGRAM_DOT_NOVA_MINUS_GENERAL` (value: `'deepgram.nova-general'`)

* `DEEPGRAM_DOT_NOVA_MINUS_PHONECALL` (value: `'deepgram.nova-phonecall'`)

* `DEEPGRAM_DOT_NOVA_MINUS_2` (value: `'deepgram.nova-2'`)

* `DEEPGRAM_DOT_NOVA_MINUS_2_MINUS_ATC` (value: `'deepgram.nova-2-atc'`)

* `DEEPGRAM_DOT_NOVA_MINUS_2_MINUS_AUTOMOTIVE` (value: `'deepgram.nova-2-automotive'`)

* `DEEPGRAM_DOT_NOVA_MINUS_2_MINUS_CONVERSATIONALAI` (value: `'deepgram.nova-2-conversationalai'`)

* `DEEPGRAM_DOT_NOVA_MINUS_2_MINUS_DRIVETHRU` (value: `'deepgram.nova-2-drivethru'`)

* `DEEPGRAM_DOT_NOVA_MINUS_2_MINUS_FINANCE` (value: `'deepgram.nova-2-finance'`)

* `DEEPGRAM_DOT_NOVA_MINUS_2_MINUS_GENERAL` (value: `'deepgram.nova-2-general'`)

* `DEEPGRAM_DOT_NOVA_MINUS_2_MINUS_MEDICAL` (value: `'deepgram.nova-2-medical'`)

* `DEEPGRAM_DOT_NOVA_MINUS_2_MINUS_MEETING` (value: `'deepgram.nova-2-meeting'`)

* `DEEPGRAM_DOT_NOVA_MINUS_2_MINUS_PHONECALL` (value: `'deepgram.nova-2-phonecall'`)

* `DEEPGRAM_DOT_NOVA_MINUS_2_MINUS_VIDEO` (value: `'deepgram.nova-2-video'`)

* `DEEPGRAM_DOT_NOVA_MINUS_2_MINUS_VOICEMAIL` (value: `'deepgram.nova-2-voicemail'`)

* `DEEPGRAM_DOT_NOVA_MINUS_3` (value: `'deepgram.nova-3'`)

* `DEEPGRAM_DOT_NOVA_MINUS_3_MINUS_GENERAL` (value: `'deepgram.nova-3-general'`)

* `DEEPGRAM_DOT_NOVA_MINUS_3_MINUS_MEDICAL` (value: `'deepgram.nova-3-medical'`)

* `DEEPGRAM_DOT_WHISPER` (value: `'deepgram.whisper'`)

* `DEEPGRAM_DOT_WHISPER_MINUS_BASE` (value: `'deepgram.whisper-base'`)

* `DEEPGRAM_DOT_WHISPER_MINUS_LARGE` (value: `'deepgram.whisper-large'`)

* `DEEPGRAM_DOT_WHISPER_MINUS_MEDIUM` (value: `'deepgram.whisper-medium'`)

* `DEEPGRAM_DOT_WHISPER_MINUS_SMALL` (value: `'deepgram.whisper-small'`)

* `DEEPGRAM_DOT_WHISPER_MINUS_TINY` (value: `'deepgram.whisper-tiny'`)

* `FALAI_DOT_ELEVENLABS_MINUS_SPEECH_MINUS_TO_MINUS_TEXT` (value: `'falai.elevenlabs-speech-to-text'`)

* `FALAI_DOT_SPEECH_MINUS_TO_MINUS_TEXT` (value: `'falai.speech-to-text'`)

* `FALAI_DOT_WHISPER` (value: `'falai.whisper'`)

* `FALAI_DOT_WIZPER` (value: `'falai.wizper'`)

* `FIREWORKSAI_DOT_WHISPER_MINUS_V3` (value: `'fireworksai.whisper-v3'`)

* `FIREWORKSAI_DOT_WHISPER_MINUS_V3_MINUS_TURBO` (value: `'fireworksai.whisper-v3-turbo'`)

* `GLADIA_DOT_STANDARD` (value: `'gladia.standard'`)

* `GOOGLE_DOT_ENHANCED` (value: `'google.enhanced'`)

* `GOOGLE_DOT_STANDARD` (value: `'google.standard'`)

* `GEMINI_DOT_GEMINI_MINUS_2_DOT_5_MINUS_FLASH_MINUS_PREVIEW_MINUS_05_MINUS_20` (value: `'gemini.gemini-2.5-flash-preview-05-20'`)

* `GEMINI_DOT_GEMINI_MINUS_2_DOT_5_MINUS_PRO_MINUS_PREVIEW_MINUS_06_MINUS_05` (value: `'gemini.gemini-2.5-pro-preview-06-05'`)

* `GEMINI_DOT_GEMINI_MINUS_2_DOT_0_MINUS_FLASH` (value: `'gemini.gemini-2.0-flash'`)

* `GEMINI_DOT_GEMINI_MINUS_2_DOT_0_MINUS_FLASH_MINUS_LITE` (value: `'gemini.gemini-2.0-flash-lite'`)

* `GROQ_DOT_DISTIL_MINUS_WHISPER_MINUS_LARGE_MINUS_V3_MINUS_EN` (value: `'groq.distil-whisper-large-v3-en'`)

* `GROQ_DOT_WHISPER_MINUS_LARGE_MINUS_V3` (value: `'groq.whisper-large-v3'`)

* `GROQ_DOT_WHISPER_MINUS_LARGE_MINUS_V3_MINUS_TURBO` (value: `'groq.whisper-large-v3-turbo'`)

* `IBM_DOT_STANDARD` (value: `'ibm.standard'`)

* `OPENAI_DOT_WHISPER_MINUS_1` (value: `'openai.whisper-1'`)

* `OPENAI_DOT_GPT_MINUS_4O_MINUS_TRANSCRIBE` (value: `'openai.gpt-4o-transcribe'`)

* `OPENAI_DOT_GPT_MINUS_4O_MINUS_MINI_MINUS_TRANSCRIBE` (value: `'openai.gpt-4o-mini-transcribe'`)

* `REVAI_DOT_MACHINE` (value: `'revai.machine'`)

* `REVAI_DOT_FUSION` (value: `'revai.fusion'`)

* `SPEECHMATICS_DOT_ENHANCED` (value: `'speechmatics.enhanced'`)

* `SPEECHMATICS_DOT_STANDARD` (value: `'speechmatics.standard'`)

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


