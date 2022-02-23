from google.cloud import storage
from zipfile import ZipFile
import os

storage_client = storage.Client.create_anonymous_client()
blobs = [b for b in storage_client.list_blobs('wsi-storage') if b.name.lower().endswith('.zip')]
for blob in blobs:
    with blob.open('rt') as f:
        with  ZipFile("/local/my_files/my_file.zip", "w", compression=zipfile.ZIP_DEFLATED) as zf:
        archive = ZipFile(f.buffer)
        filepath = f'temp/{blob.name}'
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        archive.write(filepath)
        archive.close()
