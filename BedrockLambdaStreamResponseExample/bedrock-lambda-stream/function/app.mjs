import {
  BedrockRuntimeClient,
  InvokeModelWithResponseStreamCommand
} from "@aws-sdk/client-bedrock-runtime";

const modelId = "anthropic.claude-3-haiku-20240307-v1:0";

const client = new BedrockRuntimeClient({ region: "us-east-1" });

export const lambdaHandler = awslambda.streamifyResponse(async (event, responseStream, context) => {
  const body = JSON.parse(event.body);
  const prompt = body.prompt;

  // Prepare the payload for the model.
  const payload = {
    anthropic_version: "bedrock-2023-05-31",
    max_tokens: 1000,
    messages: [
      {
        role: "user",
        content: [{ type: "text", text: prompt }],
      },
    ],
  };

  // Invoke Claude with the payload and wait for the response.
  const command = new InvokeModelWithResponseStreamCommand({
    contentType: "application/json",
    body: JSON.stringify(payload),
    modelId,
  });
  const apiResponse = await client.send(command);


 
   // Decode and process the response stream
   for await (const item of apiResponse.body) {
     const chunk = JSON.parse(new TextDecoder().decode(item.chunk.bytes));
     const chunk_type = chunk.type;
 
     if (chunk_type === "content_block_delta") {
       const text = chunk.delta.text;
       responseStream.write(text);
     }
   }

   responseStream.end();
}
);