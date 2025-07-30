import os
import requests

from requests.auth import HTTPBasicAuth

class JFROGDownloader:
    def __init__(self, base_url, repo):
        self.base_url = base_url
        self.repo = repo
    
    def set_user(self, user, api_key):
        self.auth = HTTPBasicAuth(user, api_key)

    def _authenticate_url(self, url):
        request = requests.get(url, auth=self.auth, stream=True)
        if request.status_code == 200:
            return request
        raise Exception(f"❌ Failed to authenticate to the api:{url}")
    
    def _download_file(self, file_path, output_file):
        url = f"{self.base_url}/{self.repo}/{file_path}"
        request = self._authenticate_url(url)
        total_size = int(request.headers.get('content-length', 0))
        downloaded = 0
        chunk_size = 8192  # 8 KB

        with open(output_file, "wb") as f:
            print(f"📥 Download started {file_path}")
            for chunk in request.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    percent = (downloaded / total_size) * 100 if total_size else 0
                    print(f"\r📥 Downloading {os.path.basename(output_file)}: {percent:.2f}%", end='')
        print(f"\n✅ Download complete: {output_file}")

    def download_file(self, file_path, output_folder):
        file = file_path.split('/')[-1]
        output_file = os.path.join(output_folder, file)
        self._download_file(file_path, output_file)

    def download_folder(self, folder_path, output_folder, neglate_files=[], neglate_patterns=[]):
        url = f"{self.base_url}/api/storage/{self.repo}/{folder_path}/"
        request = self._authenticate_url(url)
        data = request.json()
        
        children = data.get("children", [])
        output_folder_path = folder_path.split('/')[-1]
        output_folder = f"{output_folder}/{output_folder_path}"
        os.makedirs(output_folder, exist_ok=True)
        print(f"📥 Download started {folder_path}")
        for item in children:
            item_name = item["uri"].strip("/")
            if item_name in neglate_files:
                continue
            if neglate_patterns and any(m in item_name for m in neglate_patterns):
                continue
            download_url = f"{folder_path}/{item_name}"
            if item["folder"]:
                self.download_folder(download_url, output_folder, neglate_files=neglate_files, neglate_patterns=neglate_patterns)
            else:
                self.download_file(download_url, output_folder)
        print(f"✅ Download Completed {folder_path}")

