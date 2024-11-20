terraform {
  required_version = ">= 1.9.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.74.0"
    }
  }
  backend "s3" {
    bucket         = "pgr301-2024-terraform-state-candidate69"
    key            = "lambda-sqs/terraform.tfstate"
    region         = "eu-west-1"
    encrypt        = true
  }
}

provider "aws" {
  region = "eu-west-1"
}

resource "aws_sqs_queue" "image_processing_queue" {
  name = "image-processing-queue"
}

resource "aws_iam_role" "lambda_execution_role" {
  name = "lambda_execution_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy" "lambda_policy" {
  name   = "lambda_policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ]
        Effect   = "Allow"
        Resource = aws_sqs_queue.image_processing_queue.arn
      },
      {
        Action = [
          "s3:PutObject"
        ]
        Effect   = "Allow"
        Resource = "arn:aws:s3:::pgr301-couch-explorers-candidate69/*"
      },
      {
        Action = "logs:*"
        Effect = "Allow"
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_policy_attachment" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

resource "aws_lambda_function" "image_processor" {
  function_name    = "image_processor_lambda"
  role             = aws_iam_role.lambda_execution_role.arn
  runtime          = "python3.9"
  handler          = "lambda_sqs.lambda_handler"
  filename         = "${path.module}/lambda/lambda_sqs.zip"
  timeout          = 30
  environment {
    variables = {
      BUCKET_NAME = "pgr301-couch-explorers-candidate69"
    }
  }
  source_code_hash = filebase64sha256("${path.module}/lambda/lambda_sqs.zip")
}

resource "aws_lambda_event_source_mapping" "sqs_lambda_mapping" {
  event_source_arn = aws_sqs_queue.image_processing_queue.arn
  function_name    = aws_lambda_function.image_processor.arn
  batch_size       = 10
  enabled          = true
}