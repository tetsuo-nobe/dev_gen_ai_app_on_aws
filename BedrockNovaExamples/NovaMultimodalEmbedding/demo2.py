import json
import base64
import time
import boto3

MODEL_ID = "amazon.nova-2-multimodal-embeddings-v1:0"
EMBEDDING_DIMENSION = 3072

# Amazon Bedrock ランタイムクライアントを初期化します
bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-east-1")

# Amazon S3 Vectors クライアントを初期化します
s3vectors = boto3.client("s3vectors", region_name="us-east-1")

# 設定
VECTOR_BUCKET = "tnobe-vector-store"
INDEX_NAME = "embeddings2"

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

#---------------------------------------------------
# 画像の埋め込みを生成し、S3 Vectors に格納する

IMAGE_FILES = ["cat.jpg","cherry.jpg"]
print(f"Generating image embedding with {MODEL_ID} ...")

vectors = []

for img_file in IMAGE_FILES:
    # 画像を読み取ってエンコードします
    with open(img_file, "rb") as f:
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

    # 埋め込みを配列に追加
    vectors.append({
            "key": f"text:{img_file}",  # 一意の識別子
            "data": {"float32": embedding},
            "metadata": {"type": "text", "content": img_file}
    })

# 1 回の呼び出しですべてのベクトルを S3 Vetocrs に格納
s3vectors.put_vectors(
    vectorBucketName=VECTOR_BUCKET,
    indexName=INDEX_NAME,
    vectors=vectors
)

print(f"\nSuccessfully added {len(vectors)} vectors to the store in one put_vectors call!")

# S3 Vectors に対するクエリのテキスト
query_text = "猫の画像"  

print(f"\nGenerating embeddings for query '{query_text}' ...")

# クエリテキストの埋め込みを生成します
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