import json
import boto3
import os
import random
import base64

# Hent miljøvariabler
BEDROCK_REGION = os.environ.get("BEDROCK_REGION", "us-east-1")
S3_REGION = os.environ.get("S3_REGION", "eu-west-1")
MODEL_ID = os.environ.get("MODEL_ID", "amazon.titan-image-generator-v1")
BUCKET_NAME = os.environ.get("BUCKET_NAME")
CANDIDATE_NUMBER = os.environ.get("CANDIDATE_NUMBER")

# AWS-klienter
bedrock_client = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)
s3_client = boto3.client("s3", region_name=S3_REGION)

def lambda_handler(event, context):
    try:
        # Parse prompt fra HTTP body
        body = json.loads(event["body"])
        prompt = body.get("prompt", "Default prompt")
        
        # Generer unik filsti basert på kandidatnummer og seed
        seed = random.randint(0, 2147483647)
        s3_image_path = f"{CANDIDATE_NUMBER}/generated_image_{seed}.png"
        
        # Konfigurer forespørsel til Bedrock
        native_request = {
            "taskType": "TEXT_IMAGE",
            "textToImageParams": {"text": prompt},
            "imageGenerationConfig": {
                "numberOfImages": 1,
                "quality": "standard",
                "cfgScale": 8.0,
                "height": 1024,
                "width": 1024,
                "seed": seed,
            },
        }
        
        # Kall Bedrock-modellen
        response = bedrock_client.invoke_model(
            modelId=MODEL_ID,
            body=json.dumps(native_request),
            contentType="application/json"
        )
        
        # Dekode bildet fra Bedrock-svaret
        response_body = json.loads(response["body"])
        image_data = base64.b64decode(response_body["image"]["b64"])
        
        # Last opp bildet til S3
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=s3_image_path,
            Body=image_data,
            ContentType="image/png"
        )
        
        # Returner suksessrespons
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Image generated successfully",
                "s3_path": f"s3://{BUCKET_NAME}/{s3_image_path}"
            })
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }