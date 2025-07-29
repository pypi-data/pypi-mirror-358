import oss2
from dotenv import load_dotenv
import os
from pathlib import Path
import uuid

load_dotenv()


class OSSClient:
    access_key_id = os.getenv('PYHURL_OSS_ACCESS_KEY_ID', '')
    access_key_secret = os.getenv('PYHURL_OSS_ACCESS_KEY_SECRET', '')
    bucket_name = os.getenv('PYHURL_OSS_BUCKET_NAME', '')
    endpoint = os.getenv('PYHURL_OSS_ENDPOINT', '')

    auth = oss2.Auth(access_key_id, access_key_secret)
    bucket = oss2.Bucket(auth, endpoint, bucket_name)

    @classmethod
    def upload(cls, oss_filename: str, data) -> str:
        headers = dict()
        headers["x-oss-object-acl"] = oss2.OBJECT_ACL_PUBLIC_READ
        cls.bucket.put_object(oss_filename, data, headers=headers)
        return f"https://{cls.bucket_name}.{cls.endpoint.replace('https://', '')}/{oss_filename}"
