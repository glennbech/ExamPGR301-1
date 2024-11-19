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
        # Get the bucket name from environment variables
        bucket_name = os.environ["BUCKET_NAME"]

        # Parse input prompt from event body
        body = json.loads(event["body"])
        prompt = body["prompt"]

        # Generate a random seed for the image
        seed = random.randint(0, 2147483647)
        s3_image_path = f"{os.environ['CANDIDATE_NUMBER']}/generated_images/titan_{seed}.png"

        # Prepare the request to AWS Bedrock
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

        # Call Bedrock to generate the image
        response = bedrock_client.invoke_model(modelId="amazon.titan-image-generator-v1", body=json.dumps(native_request))
        model_response = json.loads(response["body"].read())

        # Extract and decode the Base64 image data
        base64_image_data = model_response["images"][0]
        image_data = base64.b64decode(base64_image_data)

        # Upload the decoded image data to S3
        s3_client.put_object(Bucket=bucket_name, Key=s3_image_path, Body=image_data)

        # Return the S3 URI of the uploaded image
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Image generated", "s3_uri": f"s3://{bucket_name}/{s3_image_path}"}),
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
        }