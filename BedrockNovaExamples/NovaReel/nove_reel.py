#
# https://aws.amazon.com/jp/blogs/aws/introducing-amazon-nova-frontier-intelligence-and-industry-leading-price-performance/
#
import base64
import random
import time

import boto3

S3_DESTINATION_BUCKET = "<出力バケット名>"
AWS_REGION = "us-east-1"
MODEL_ID = "amazon.nova-reel-v1:0"
SLEEP_TIME = 30
input_image_path = "seascape.png" # 海岸の風景の画像
video_prompt = "drone view flying over a coastal landscape" # 海岸の風景を飛行するドローン視点の映像

bedrock_runtime = boto3.client("bedrock-runtime", region_name=AWS_REGION)

# Load the input image as a Base64 string.
with open(input_image_path, "rb") as f:
    input_image_bytes = f.read()
    input_image_base64 = base64.b64encode(input_image_bytes).decode("utf-8")

model_input = {
    "taskType": "TEXT_VIDEO",
    "textToVideoParams": {
        "text": video_prompt,
        "images": [{ "format": "png", "source": { "bytes": input_image_base64 } }]
        },
    "videoGenerationConfig": {
        "durationSeconds": 6,  # 現在は 6 のみサポート
        "fps": 24,
        "dimension": "1280x720",
        "seed": random.randint(0, 2147483648)
    }
}

invocation = bedrock_runtime.start_async_invoke(
    modelId=MODEL_ID,
    modelInput=model_input,
    outputDataConfig={"s3OutputDataConfig": {"s3Uri": f"s3://{S3_DESTINATION_BUCKET}"}}
)

invocation_arn = invocation["invocationArn"]
s3_prefix = invocation_arn.split('/')[-1]
s3_location = f"s3://{S3_DESTINATION_BUCKET}/{s3_prefix}"

print(f"\nS3 URI: {s3_location}")

while True:
    response = bedrock_runtime.get_async_invoke(
        invocationArn=invocation_arn
    )
    status = response["status"]
    print(f"Status: {status}")
    if status != "InProgress":
        break
    time.sleep(SLEEP_TIME)
if status == "Completed":
    print(f"\nVideo is ready at {s3_location}/output.mp4")
else:
    print(f"\nVideo generation status: {status}")