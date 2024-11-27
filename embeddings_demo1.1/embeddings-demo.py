import json
import os
import sys

import boto3
import botocore

import numpy as np
from numpy.linalg import norm

module_path = ".."
sys.path.append(os.path.abspath(module_path))

bedrock_client = boto3.client('bedrock-runtime',region_name=os.environ.get("AWS_DEFAULT_REGION", None))

# 埋め込みを行う基盤モデルを使用
modelId="amazon.titan-embed-text-v1"


# 文の埋め込みベクトルを生成する関数
def sen2vec(sentence):
    # Convert the given sentence to a vector representation using a text embedding model.  
    input_body = {"inputText": sentence}
    try:
        response = bedrock_client.invoke_model(
            body=json.dumps(input_body),
            modelId=modelId,
            accept="application/json",
            contentType="application/json",
            )
        response_body = json.loads(response.get("body").read())
        vector = np.array(response_body.get("embedding"))            
        return vector
    except Exception as e:
        print(e)

# ドキュメントのファイルを読み込み用の配列を初期化
with open("documents-jp.txt") as doc:
    num_records = len(doc.readlines())
    
doc_array=np.empty(shape=(num_records), dtype="S255")
embed_array = np.zeros(shape=(num_records, 1536))

# ドキュメントのファイルを読み込み、ベクトル化データを配列へ格納
with open("documents-jp.txt") as doc:
    for num, line in enumerate(doc, 0):
      doc = line.strip('\n')
      doc_array[num] = doc.encode("UTF-8")
      embed_array[num] = sen2vec(doc)

print("ベクトル化データの配列のサイズ")
print(embed_array.shape)
print("----")
print("ベクトル化データの配列の内容") 
print(embed_array)
print("----")
#類似性検索を使用してインタラクティブにクエリ
#行列ベクトルストアから関連ドキュメントを引き出すために類似性検索を使用するインタラクティブなクエリを実行
#類似度のしきい値として0.5を使用して、幻影(ハルシネーション)を限定します。
#ドキュメントストアのコース名に関連するクエリは、成功した結果につながります。
#結果のいずれも0.5のしきい値を超えない場合、「わかりません」が応答になります。

query = "Architecting on AWS は何日間コースですか？"
#query = "Amazon SageMaker Studio for Data Scientistsは何日間コースですか？"
#query = "車のタイヤを交換するにはどうしたらいいですか？"
    
embed_query = sen2vec(query)
denominator = norm(embed_array, axis=1) * norm(embed_query)
similarity = embed_array.dot(embed_query) / denominator
max_value = max(similarity)
max_value_index = similarity.argmax()
print("\nクエリ: " + query)
if max_value > 0.5:
    print("質問に回答できるドキュメント: " + doc_array[max_value_index].decode('UTF-8'))
else:
    print("回答: " + "わかりません。")
print("\nSimilarity vector used for document selection")
print(similarity)
        