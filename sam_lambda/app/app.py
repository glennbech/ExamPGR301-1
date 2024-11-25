import base64
import boto3
import json
import os
import random

# Set up the AWS clients
bedrock_client = boto3.client("bedrock-runtime", region_name="us-east-1")
s3_client = boto3.client("s3")

# Lambda handler
def lambda_handler(event, context):
    try:

        bucket_name = os.environ["BUCKET_NAME"]

        body = json.loads(event["body"])
        prompt = body["prompt"]

        seed = random.randint(0, 2147483647)
        s3_image_path = f"{os.environ['CANDIDATE_NUMBER']}/generated_images/titan_{seed}.png"

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

        response = bedrock_client.invoke_model(modelId="amazon.titan-image-generator-v1", body=json.dumps(native_request))
        model_response = json.loads(response["body"].read())

        base64_image_data = model_response["images"][0]
        image_data = base64.b64decode(base64_image_data)

        s3_client.put_object(Bucket=bucket_name, Key=s3_image_path, Body=image_data)

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Image generated", "s3_uri": f"s3://{bucket_name}/{s3_image_path}"}),
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
        }