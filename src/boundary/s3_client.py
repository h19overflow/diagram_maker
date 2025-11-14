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
if not bucket_name:
    raise ValueError(
        "S3_BUCKET_NAME environment variable is not set. "
        "Please set it in your .env file or environment."
    )


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


def upload_json_data_via_presigned_url(json_data, presigned_url):
    try:
        # Convert the JSON data (dict or JSON string) to a JSON string bytes for upload
        if isinstance(json_data, dict):
            json_str = json.dumps(json_data)
        else:
            json_str = json_data  # assume it's already a JSON string

        json_bytes = json_str.encode("utf-8")

        # Upload with HTTP PUT and Content-Type header
        headers = {"Content-Type": "application/json"}
        response = requests.put(
            presigned_url, data=json_bytes, headers=headers, timeout=10
        )
        response.raise_for_status()

        print("Upload successful")
        return True
    except Exception as e:
        print(f"Error uploading JSON data via presigned URL: {e}")
        raise e


def get_json_object_from_presigned_url(presigned_url):
    try:
        response = requests.get(presigned_url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error getting object from presigned URL: {e}")
        raise e


if __name__ == "__main__":
    put_presigned_url = generate_presigned_url(
        "uploads/test.json", "put_object", 3600
    )
    print(f"PUT URL: {put_presigned_url}")
    put_object_response = upload_json_data_via_presigned_url(
        {"test": "test"}, put_presigned_url
    )
    print(put_object_response)
    get_presigned_url = generate_presigned_url("uploads/test.json", "get_object", 3600)
    print(f"GET URL: {get_presigned_url}")
    get_object_response = get_json_object_from_presigned_url(get_presigned_url)
    print(get_object_response)
