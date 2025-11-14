import boto3
from dotenv import load_dotenv
import os
from botocore.exceptions import ClientError
import requests
import json

load_dotenv()
# Initialize S3 client
s3 = boto3.client("s3")
# Define your bucket name and local file path
bucket_name = os.getenv("S3_BUCKET_NAME_KB")

def generate_presigned_url(
    s3_object_key,
    client_method="get_object",
    expires_in=3600,
    content_type="application/json",
):
    params = {"Bucket": bucket_name, "Key": s3_object_key}
    if client_method == "put_object":
        params["ContentType"] = content_type

    try:
        url = s3.generate_presigned_url(
            ClientMethod=client_method, Params=params, ExpiresIn=expires_in
        )
    except ClientError as e:
        print(f"Error generating presigned URL: {e}")
        raise e
    return url


def request_via_presigned_url(
    presigned_url, method="GET", json_data=None, content_type="application/json"
):
    headers = {}
    if method == "PUT" and json_data is not None:
        headers["Content-Type"] = content_type
        if isinstance(json_data, dict):
            json_str = json.dumps(json_data)
        else:
            json_str = json_data
        data = json_str.encode("utf-8")
    else:
        data = None

    try:
        response = requests.request(method, presigned_url, data=data, headers=headers, timeout=10)
        response.raise_for_status()

        if method == "GET":
            return response.json()
        print("Upload successful")
        return True
    except Exception as e:
        print(f"Error with presigned URL request: {e}")
        raise e


if __name__ == "__main__":
    put_presigned_url = generate_presigned_url(
        "uploads/test.json", "put_object", 3600
    )
    print(f"PUT URL: {put_presigned_url}")
    put_object_response = request_via_presigned_url(
        put_presigned_url, "PUT", {"test": "test"}
    )
    print(put_object_response)
    get_presigned_url = generate_presigned_url("uploads/test.json", "get_object", 3600)
    print(f"GET URL: {get_presigned_url}")
    get_object_response = request_via_presigned_url(get_presigned_url, "GET")
    print(get_object_response)
