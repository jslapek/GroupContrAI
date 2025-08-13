import boto3
import torch
from transformers import pipeline

BRT = boto3.Session().client("bedrock-runtime")
AI_FLAG = False

def query_llm(model, prompt):
    if not AI_FLAG:
        return "AI is disabled."

    if model == "text":
        # amazon.nova-micro-v1:0
        resp = BRT.converse(
            modelId="arn:aws:bedrock:eu-north-1:139824164881:inference-profile/eu.amazon.nova-micro-v1:0",
            system=[{"text":"You are a concise assistant."}],
            messages=[{"role":"user", "content":[{"text":f"{prompt}"}]}],
            inferenceConfig={"maxTokens": 100, "temperature": 0.3, "topP": 0.8}
        )
        return resp["output"]["message"]["content"][0]["text"]
    elif model == "encode":
        # amazon.titan-embed-text-v2:0
        pass
    elif model == "multimodal":
        # amazon.nova-lite-v1:0
        pass

def classify(content, classes):
    print("classifying...")
    pipe = pipeline("zero-shot-classification", model="MoritzLaurer/deberta-v3-base-zeroshot-v2.0")
    out = pipe(
        content,
        classes,
        multi_label=False
    )
    print(f"{out['labels']=}")
    print(f"{out['scores']=}")
    if out['scores'][0] < 0.65:
        return "UNKNOWN"
    return out['labels'][0] 
