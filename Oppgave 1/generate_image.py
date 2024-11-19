import json
import boto3
import os
import random

# AWS-klienter
bedrock_client = boto3.client("bedrock-runtime", region_name="us-east-1")
s3_client = boto3.client("s3")

# Konfigurasjon
MODEL_ID = "amazon.titan-image-generator-v1"
BUCKET_NAME = "pgr301-couch-explorers"
CANDIDATE_NUMBER = os.environ.get("CANDIDATE_NUMBER", "default_candidate")

def lambda_handler(event, context):
    try:
        # Parse HTTP body for prompt
        body = json.loads(event["body"])
        prompt = body.get("prompt", "Default prompt")
        
        # Random seed for unique image generation
        seed = random.randint(0, 2147483647)
        s3_image_path = f"{CANDIDATE_NUMBER}/generated_image_{seed}.png"
        
        # Prepare request to Bedrock
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
        
        # Invoke Bedrock model
        response = bedrock_client.invoke_model(
            modelId=MODEL_ID,
            body=json.dumps(native_request),
            contentType="application/json"
        )
        
        # Decode the image
        response_body = json.loads(response["body"])
        image_data = base64.b64decode(response_body["image"]["b64"])
        
        # Upload to S3
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=s3_image_path,
            Body=image_data,
            ContentType="image/png"
        )
        
        # Return success response
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Image generated successfully", "s3_path": f"s3://{BUCKET_NAME}/{s3_image_path}"})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }