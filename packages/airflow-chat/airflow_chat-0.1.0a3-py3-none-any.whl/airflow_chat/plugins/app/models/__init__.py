import os
model_type, model_id = os.environ.get('LLM_MODEL_ID', 'none:none').split(':', 1)

if model_type == 'bedrock':
    from app.models.inference.bedrock_model import ChatBedrock
    ChatModel = ChatBedrock
elif model_type == 'antropic':
    from app.models.inference.antropic_model import ChatAnthropic
    ChatModel = ChatAnthropic
elif model_type == 'openai':
    from app.models.inference.openai_model import ChatOpenAI
    ChatModel = ChatOpenAI
else:
    ChatModel = None
