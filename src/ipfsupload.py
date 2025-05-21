    import ipfshttpclient
    import os
    import hashlib

    class IPFSUploader:
        def __init__(self):
            try:
                print("Connecting to IPFS...")
                self.client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')
                self.client.id()
                print("Connected to IPFS.")
            except Exception as e:
                raise Exception(f"IPFS connection failed: {e}")

        def upload_image(self, image_path):
            """Upload an image to IPFS and return the hash"""
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"File not found: {image_path}")
            try:
                result = self.client.add(image_path)
                print(f"Image uploaded to IPFS with hash: {result['Hash']}")
                return result['Hash']
            except Exception as e:
                raise Exception(f"Failed to upload to IPFS: {e}")

        def get_sha256_hash(self, image_path):
            """Get the SHA-256 hash of an image"""
            with open(image_path, "rb") as img:
                return hashlib.sha256(img.read()).hexdigest()

    # Initialize the IPFS client
    ipfs_uploader = IPFSUploader()

    def upload_to_ipfs(image_path):
        """Upload image to IPFS and return hash"""
        try:
            ipfs_hash = ipfs_uploader.upload_image(image_path)
            return ipfs_hash
        except Exception as e:
            print(f"Error uploading image to IPFS: {str(e)}")
            return None

    # Example usage:
    image_path = "F:\PROJECT\Final_Year_project\Blockchain_Agri\src\data\train\crop\1.JPG"
    ipfs_hash = upload_to_ipfs(image_path)
    if ipfs_hash:
        print(f"IPFS Hash: {ipfs_hash}")
