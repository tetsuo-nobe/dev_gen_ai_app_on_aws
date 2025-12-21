# Blog: https://aws.amazon.com/jp/blogs/news/amazon-nova-multimodal-embeddings-now-available-in-amazon-bedrock/
import json
import base64
import time
import boto3

MODEL_ID = "amazon.nova-2-multimodal-embeddings-v1:0"
EMBEDDING_DIMENSION = 3072

# Amazon Bedrock ランタイムクライアントを初期化します
bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-east-1")

#---------------------------------------------------
print(f"Generating text embedding with {MODEL_ID} ...")

# 埋め込むテキスト
text = "Amazon Novaはマルチモーダル基盤モデルです。"

# 埋め込みを作成します
request_body = {
    "taskType": "SINGLE_EMBEDDING",
    "singleEmbeddingParams": {
        "embeddingPurpose": "GENERIC_INDEX",
        "embeddingDimension": EMBEDDING_DIMENSION,
        "text": {"truncationMode": "END", "value": text},
    },
}

response = bedrock_runtime.invoke_model(
    body=json.dumps(request_body),
    modelId=MODEL_ID,
    contentType="application/json",
)

# 埋め込みを抽出します
response_body = json.loads(response["body"].read())
embedding = response_body["embeddings"][0]["embedding"]

print(f"Generated embedding with {len(embedding)} dimensions")

#---------------------------------------------------
# 画像を読み取ってエンコードします
print(f"Generating image embedding with {MODEL_ID} ...")

with open("cat.jpg", "rb") as f:
    image_bytes = base64.b64encode(f.read()).decode("utf-8")

# 埋め込みを作成します
request_body = {
    "taskType": "SINGLE_EMBEDDING",
    "singleEmbeddingParams": {
        "embeddingPurpose": "GENERIC_INDEX",
        "embeddingDimension": EMBEDDING_DIMENSION,
        "image": {
            "format": "jpeg",
            "source": {"bytes": image_bytes}
        },
    },
}

response = bedrock_runtime.invoke_model(
    body=json.dumps(request_body),
    modelId=MODEL_ID,
    contentType="application/json",
)

# 埋め込みを抽出します
response_body = json.loads(response["body"].read())
embedding = response_body["embeddings"][0]["embedding"]

print(f"Generated embedding with {len(embedding)} dimensions")

#---------------------------------------------------
# Amazon S3 クライアントを初期化します
s3 = boto3.client("s3", region_name="us-east-1")

print(f"Generating video embedding with {MODEL_ID} ...")

# Amazon S3 URI
S3_VIDEO_URI = "s3://tnobe-video-bucket/videos/sample.mp4"

# Amazon S3 出力バケットと場所
S3_EMBEDDING_DESTINATION_URI = "s3://tnobe-video-bucket/embeddings-output/"

# 音声付き動画の非同期埋め込みジョブを作成します
model_input = {
    "taskType": "SEGMENTED_EMBEDDING",
    "segmentedEmbeddingParams": {
        "embeddingPurpose": "GENERIC_INDEX",
        "embeddingDimension": EMBEDDING_DIMENSION,
        "video": {
            "format": "mp4",
            "embeddingMode": "AUDIO_VIDEO_COMBINED",
            "source": {
                "s3Location": {"uri": S3_VIDEO_URI}
            },
            "segmentationConfig": {
                "durationSeconds": 15  # 15 秒単位のチャンクにセグメント化します
            },
        },
    },
}

response = bedrock_runtime.start_async_invoke(
    modelId=MODEL_ID,
    modelInput=model_input,
    outputDataConfig={
        "s3OutputDataConfig": {
            "s3Uri": S3_EMBEDDING_DESTINATION_URI
        }
    },
)

invocation_arn = response["invocationArn"]
print(f"Async job started: {invocation_arn}")

# ジョブが完了するまでポーリングします
print("\nPolling for job completion...")
while True:
    job = bedrock_runtime.get_async_invoke(invocationArn=invocation_arn)
    status = job["status"]
    print(f"Status: {status}")

    if status != "InProgress":
        break
    time.sleep(15)

# ジョブが正常に完了したかどうかをチェックします
if status == "Completed":
    output_s3_uri = job["outputDataConfig"]["s3OutputDataConfig"]["s3Uri"]
    print(f"\nSuccess! Embeddings at: {output_s3_uri}")

    # S3 URI を解析してバケットとプレフィックスを取得します
    s3_uri_parts = output_s3_uri[5:].split("/", 1)  # プレフィックス「s3://」を削除します
    bucket = s3_uri_parts[0]
    prefix = s3_uri_parts[1] if len(s3_uri_parts) > 1 else ""

    # AUDIO_VIDEO_COMBINED モードは、embedding-audio-video.jsonl に出力します
    # output_s3_uri には既にジョブ ID が含まれているため、ファイル名を付加するだけです
    embeddings_key = f"{prefix}/embedding-audio-video.jsonl".lstrip("/")

    print(f"Reading embeddings from: s3://{bucket}/{embeddings_key}")

    # JSONL ファイルを読み取って解析します
    response = s3.get_object(Bucket=bucket, Key=embeddings_key)
    content = response['Body'].read().decode('utf-8')

    embeddings = []
    for line in content.strip().split('\n'):
        if line:
            embeddings.append(json.loads(line))

    print(f"\nFound {len(embeddings)} video segments:")
    for i, segment in enumerate(embeddings):
        print(f"  Segment {i}: {segment.get('startTime', 0):.1f}s - {segment.get('endTime', 0):.1f}s")
        print(f"    Embedding dimension: {len(segment.get('embedding', []))}")
else:
    print(f"\nJob failed: {job.get('failureMessage', 'Unknown error')}")
# Amazon S3 Vectors クライアントを初期化します
s3vectors = boto3.client("s3vectors", region_name="us-east-1")

# 設定
VECTOR_BUCKET = "tnobe-vector-store"
INDEX_NAME = "embeddings"

# ベクトルバケットとインデックスを作成します (存在していない場合)
try:
    s3vectors.get_vector_bucket(vectorBucketName=VECTOR_BUCKET)
    print(f"Vector bucket {VECTOR_BUCKET} already exists")
except s3vectors.exceptions.NotFoundException:
    s3vectors.create_vector_bucket(vectorBucketName=VECTOR_BUCKET)
    print(f"Created vector bucket: {VECTOR_BUCKET}")

try:
    s3vectors.get_index(vectorBucketName=VECTOR_BUCKET, indexName=INDEX_NAME)
    print(f"Vector index {INDEX_NAME} already exists")
except s3vectors.exceptions.NotFoundException:
    s3vectors.create_index(
        vectorBucketName=VECTOR_BUCKET,
        indexName=INDEX_NAME,
        dimension=EMBEDDING_DIMENSION,
        dataType="float32",
        distanceMetric="cosine"
    )
    print(f"Created index: {INDEX_NAME}")

texts = [
    "AWS での機械学習",
    "Amazon Bedrockは基礎モデルを提供します。",
    "S3 Vectors はセマンティック検索を可能にします。"
]

print(f"\nGenerating embeddings for {len(texts)} texts...")

# Amazon Nova を使用して各テキストの埋め込みを生成します
vectors = []
for text in texts:
    response = bedrock_runtime.invoke_model(
        body=json.dumps({
            "taskType": "SINGLE_EMBEDDING",
            "singleEmbeddingParams": {
                "embeddingPurpose": "GENERIC_INDEX",
                "embeddingDimension": EMBEDDING_DIMENSION,
                "text": {"truncationMode": "END", "value": text}
            }
        }),
        modelId=MODEL_ID,
        accept="application/json",
        contentType="application/json"
    )

    response_body = json.loads(response["body"].read())
    embedding = response_body["embeddings"][0]["embedding"]

    vectors.append({
        "key": f"text:{text[:50]}",  # 一意の識別子
        "data": {"float32": embedding},
        "metadata": {"type": "text", "content": text}
    })
    print(f"  ✓ Generated embedding for: {text}")

# 1 回の呼び出しで、保存するすべてのベクトルを追加します
s3vectors.put_vectors(
    vectorBucketName=VECTOR_BUCKET,
    indexName=INDEX_NAME,
    vectors=vectors
)

print(f"\nSuccessfully added {len(vectors)} vectors to the store in one put_vectors call!")
# クエリするテキスト
query_text = "基盤モデル"  

print(f"\nGenerating embeddings for query '{query_text}' ...")

# 埋め込みを生成します
response = bedrock_runtime.invoke_model(
    body=json.dumps({
        "taskType": "SINGLE_EMBEDDING",
        "singleEmbeddingParams": {
            "embeddingPurpose": "GENERIC_RETRIEVAL",
            "embeddingDimension": EMBEDDING_DIMENSION,
            "text": {"truncationMode": "END", "value": query_text}
        }
    }),
    modelId=MODEL_ID,
    accept="application/json",
    contentType="application/json"
)

response_body = json.loads(response["body"].read())
query_embedding = response_body["embeddings"][0]["embedding"]

print(f"Searching for similar embeddings...\n")

# 最も類似した上位 5 つのベクトルを検索します
response = s3vectors.query_vectors(
    vectorBucketName=VECTOR_BUCKET,
    indexName=INDEX_NAME,
    queryVector={"float32": query_embedding},
    topK=5,
    returnDistance=True,
    returnMetadata=True
)

# 結果を表示します
print(f"Found {len(response['vectors'])} results:\n")
for i, result in enumerate(response["vectors"], 1):
    print(f"{i}. {result['key']}")
    print(f"   Distance: {result['distance']:.4f}")
    if result.get("metadata"):
        print(f"   Metadata: {result['metadata']}")

    print()
