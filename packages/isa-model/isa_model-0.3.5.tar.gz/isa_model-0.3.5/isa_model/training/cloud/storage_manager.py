"""
Cloud Storage Manager for Training Assets

This module handles storage of datasets, models, and training artifacts
across different cloud storage providers (S3, GCS, Azure, etc.).
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

try:
    import boto3
    from botocore.exceptions import ClientError
    S3_AVAILABLE = True
except ImportError:
    S3_AVAILABLE = False
    boto3 = None

try:
    from google.cloud import storage as gcs
    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False
    gcs = None

logger = logging.getLogger(__name__)


@dataclass
class StorageConfig:
    """Configuration for cloud storage."""
    
    provider: str  # "s3", "gcs", "azure"
    bucket_name: str
    region: Optional[str] = None
    
    # Authentication
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    service_account_path: Optional[str] = None
    
    # Paths
    datasets_prefix: str = "datasets/"
    models_prefix: str = "models/"
    logs_prefix: str = "logs/"
    
    def __post_init__(self):
        """Validate configuration."""
        if self.provider not in ["s3", "gcs", "azure"]:
            raise ValueError(f"Unsupported storage provider: {self.provider}")
        
        if not self.bucket_name:
            raise ValueError("Bucket name is required")


class CloudStorageManager:
    """
    Cloud storage manager for training assets.
    
    Handles upload/download of datasets, models, and training artifacts
    across different cloud storage providers.
    
    Example:
        ```python
        # Configure S3 storage
        storage_config = StorageConfig(
            provider="s3",
            bucket_name="my-training-bucket",
            region="us-west-2",
            access_key="your-access-key",
            secret_key="your-secret-key"
        )
        
        # Initialize storage manager
        storage = CloudStorageManager(storage_config)
        
        # Upload dataset
        dataset_url = storage.upload_dataset("local_data.json", "my-dataset")
        
        # Upload trained model
        model_url = storage.upload_model("./trained_model/", "gemma-finetuned-v1")
        
        # Download model
        local_path = storage.download_model("gemma-finetuned-v1", "./downloaded_model/")
        ```
    """
    
    def __init__(self, config: StorageConfig):
        """
        Initialize cloud storage manager.
        
        Args:
            config: Storage configuration
        """
        self.config = config
        self._client = None
        self._initialize_client()
        
        logger.info(f"Storage manager initialized for {config.provider}://{config.bucket_name}")
    
    def _initialize_client(self) -> None:
        """Initialize storage client based on provider."""
        if self.config.provider == "s3":
            if not S3_AVAILABLE:
                raise ImportError("boto3 is required for S3 storage. Install with: pip install boto3")
            
            self._client = boto3.client(
                's3',
                aws_access_key_id=self.config.access_key,
                aws_secret_access_key=self.config.secret_key,
                region_name=self.config.region
            )
            
        elif self.config.provider == "gcs":
            if not GCS_AVAILABLE:
                raise ImportError("google-cloud-storage is required for GCS. Install with: pip install google-cloud-storage")
            
            if self.config.service_account_path:
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.config.service_account_path
            
            self._client = gcs.Client()
            
        else:
            raise NotImplementedError(f"Provider {self.config.provider} not implemented yet")
    
    def upload_dataset(self, local_path: str, dataset_name: str, 
                      metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Upload dataset to cloud storage.
        
        Args:
            local_path: Local path to dataset file
            dataset_name: Name for the dataset
            metadata: Optional metadata to store with dataset
            
        Returns:
            Cloud storage URL for the dataset
        """
        remote_path = f"{self.config.datasets_prefix}{dataset_name}.json"
        
        try:
            # Upload dataset file
            self._upload_file(local_path, remote_path)
            
            # Upload metadata if provided
            if metadata:
                metadata_path = f"{self.config.datasets_prefix}{dataset_name}_metadata.json"
                metadata_content = json.dumps(metadata, indent=2)
                self._upload_content(metadata_content, metadata_path)
            
            dataset_url = self._get_public_url(remote_path)
            logger.info(f"Dataset uploaded: {dataset_url}")
            return dataset_url
            
        except Exception as e:
            logger.error(f"Failed to upload dataset {dataset_name}: {e}")
            raise
    
    def download_dataset(self, dataset_name: str, local_path: str) -> str:
        """
        Download dataset from cloud storage.
        
        Args:
            dataset_name: Name of the dataset
            local_path: Local path to save dataset
            
        Returns:
            Local path to downloaded dataset
        """
        remote_path = f"{self.config.datasets_prefix}{dataset_name}.json"
        
        try:
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            self._download_file(remote_path, local_path)
            
            logger.info(f"Dataset downloaded to: {local_path}")
            return local_path
            
        except Exception as e:
            logger.error(f"Failed to download dataset {dataset_name}: {e}")
            raise
    
    def upload_model(self, local_model_dir: str, model_name: str,
                    metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Upload trained model to cloud storage.
        
        Args:
            local_model_dir: Local directory containing model files
            model_name: Name for the model
            metadata: Optional model metadata
            
        Returns:
            Cloud storage URL for the model
        """
        model_prefix = f"{self.config.models_prefix}{model_name}/"
        
        try:
            # Upload all model files
            model_files = []
            for root, dirs, files in os.walk(local_model_dir):
                for file in files:
                    local_file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(local_file_path, local_model_dir)
                    remote_path = f"{model_prefix}{relative_path}"
                    
                    self._upload_file(local_file_path, remote_path)
                    model_files.append(relative_path)
            
            # Upload model metadata
            if metadata is None:
                metadata = {}
            
            metadata.update({
                "model_name": model_name,
                "files": model_files,
                "upload_timestamp": self._get_timestamp()
            })
            
            metadata_path = f"{model_prefix}model_metadata.json"
            metadata_content = json.dumps(metadata, indent=2)
            self._upload_content(metadata_content, metadata_path)
            
            model_url = self._get_public_url(model_prefix)
            logger.info(f"Model uploaded: {model_url}")
            return model_url
            
        except Exception as e:
            logger.error(f"Failed to upload model {model_name}: {e}")
            raise
    
    def download_model(self, model_name: str, local_dir: str) -> str:
        """
        Download model from cloud storage.
        
        Args:
            model_name: Name of the model
            local_dir: Local directory to save model
            
        Returns:
            Local path to downloaded model
        """
        model_prefix = f"{self.config.models_prefix}{model_name}/"
        
        try:
            os.makedirs(local_dir, exist_ok=True)
            
            # First, get model metadata to know which files to download
            metadata_path = f"{model_prefix}model_metadata.json"
            metadata_content = self._download_content(metadata_path)
            metadata = json.loads(metadata_content)
            
            # Download all model files
            for file_path in metadata.get("files", []):
                remote_path = f"{model_prefix}{file_path}"
                local_file_path = os.path.join(local_dir, file_path)
                
                os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
                self._download_file(remote_path, local_file_path)
            
            logger.info(f"Model downloaded to: {local_dir}")
            return local_dir
            
        except Exception as e:
            logger.error(f"Failed to download model {model_name}: {e}")
            raise
    
    def upload_training_logs(self, local_log_dir: str, job_id: str) -> str:
        """Upload training logs to cloud storage."""
        logs_prefix = f"{self.config.logs_prefix}{job_id}/"
        
        try:
            for root, dirs, files in os.walk(local_log_dir):
                for file in files:
                    local_file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(local_file_path, local_log_dir)
                    remote_path = f"{logs_prefix}{relative_path}"
                    
                    self._upload_file(local_file_path, remote_path)
            
            logs_url = self._get_public_url(logs_prefix)
            logger.info(f"Training logs uploaded: {logs_url}")
            return logs_url
            
        except Exception as e:
            logger.error(f"Failed to upload training logs for job {job_id}: {e}")
            raise
    
    def list_datasets(self) -> List[Dict[str, Any]]:
        """List all datasets in storage."""
        try:
            datasets = []
            objects = self._list_objects(self.config.datasets_prefix)
            
            for obj in objects:
                if obj.endswith('.json') and not obj.endswith('_metadata.json'):
                    dataset_name = os.path.basename(obj).replace('.json', '')
                    datasets.append({
                        "name": dataset_name,
                        "path": obj,
                        "url": self._get_public_url(obj),
                        "size": self._get_object_size(obj),
                        "modified": self._get_object_modified_time(obj)
                    })
            
            return datasets
            
        except Exception as e:
            logger.error(f"Failed to list datasets: {e}")
            return []
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List all models in storage."""
        try:
            models = []
            prefixes = self._list_prefixes(self.config.models_prefix)
            
            for prefix in prefixes:
                model_name = prefix.rstrip('/').split('/')[-1]
                metadata_path = f"{prefix}model_metadata.json"
                
                try:
                    metadata_content = self._download_content(metadata_path)
                    metadata = json.loads(metadata_content)
                    
                    models.append({
                        "name": model_name,
                        "path": prefix,
                        "url": self._get_public_url(prefix),
                        "metadata": metadata,
                        "files_count": len(metadata.get("files", [])),
                        "upload_time": metadata.get("upload_timestamp", "")
                    })
                except:
                    # If metadata doesn't exist, add basic info
                    models.append({
                        "name": model_name,
                        "path": prefix,
                        "url": self._get_public_url(prefix),
                        "metadata": {},
                        "files_count": 0,
                        "upload_time": ""
                    })
            
            return models
            
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []
    
    def _upload_file(self, local_path: str, remote_path: str) -> None:
        """Upload file to storage."""
        if self.config.provider == "s3":
            self._client.upload_file(local_path, self.config.bucket_name, remote_path)
        elif self.config.provider == "gcs":
            bucket = self._client.bucket(self.config.bucket_name)
            blob = bucket.blob(remote_path)
            blob.upload_from_filename(local_path)
        else:
            raise NotImplementedError(f"Upload not implemented for {self.config.provider}")
    
    def _upload_content(self, content: str, remote_path: str) -> None:
        """Upload string content to storage."""
        if self.config.provider == "s3":
            self._client.put_object(
                Bucket=self.config.bucket_name,
                Key=remote_path,
                Body=content.encode('utf-8')
            )
        elif self.config.provider == "gcs":
            bucket = self._client.bucket(self.config.bucket_name)
            blob = bucket.blob(remote_path)
            blob.upload_from_string(content)
        else:
            raise NotImplementedError(f"Upload not implemented for {self.config.provider}")
    
    def _download_file(self, remote_path: str, local_path: str) -> None:
        """Download file from storage."""
        if self.config.provider == "s3":
            self._client.download_file(self.config.bucket_name, remote_path, local_path)
        elif self.config.provider == "gcs":
            bucket = self._client.bucket(self.config.bucket_name)
            blob = bucket.blob(remote_path)
            blob.download_to_filename(local_path)
        else:
            raise NotImplementedError(f"Download not implemented for {self.config.provider}")
    
    def _download_content(self, remote_path: str) -> str:
        """Download content as string."""
        if self.config.provider == "s3":
            response = self._client.get_object(Bucket=self.config.bucket_name, Key=remote_path)
            return response['Body'].read().decode('utf-8')
        elif self.config.provider == "gcs":
            bucket = self._client.bucket(self.config.bucket_name)
            blob = bucket.blob(remote_path)
            return blob.download_as_text()
        else:
            raise NotImplementedError(f"Download not implemented for {self.config.provider}")
    
    def _list_objects(self, prefix: str) -> List[str]:
        """List objects with given prefix."""
        if self.config.provider == "s3":
            response = self._client.list_objects_v2(
                Bucket=self.config.bucket_name,
                Prefix=prefix
            )
            return [obj['Key'] for obj in response.get('Contents', [])]
        elif self.config.provider == "gcs":
            bucket = self._client.bucket(self.config.bucket_name)
            blobs = bucket.list_blobs(prefix=prefix)
            return [blob.name for blob in blobs]
        else:
            raise NotImplementedError(f"List objects not implemented for {self.config.provider}")
    
    def _list_prefixes(self, prefix: str) -> List[str]:
        """List prefixes (directories) under given prefix."""
        if self.config.provider == "s3":
            response = self._client.list_objects_v2(
                Bucket=self.config.bucket_name,
                Prefix=prefix,
                Delimiter='/'
            )
            return [cp['Prefix'] for cp in response.get('CommonPrefixes', [])]
        elif self.config.provider == "gcs":
            # GCS doesn't have true directories, so we simulate by grouping by prefix
            bucket = self._client.bucket(self.config.bucket_name)
            blobs = bucket.list_blobs(prefix=prefix)
            prefixes = set()
            for blob in blobs:
                parts = blob.name[len(prefix):].split('/')
                if len(parts) > 1:
                    prefixes.add(f"{prefix}{parts[0]}/")
            return list(prefixes)
        else:
            raise NotImplementedError(f"List prefixes not implemented for {self.config.provider}")
    
    def _get_public_url(self, remote_path: str) -> str:
        """Get public URL for object."""
        if self.config.provider == "s3":
            return f"https://{self.config.bucket_name}.s3.{self.config.region}.amazonaws.com/{remote_path}"
        elif self.config.provider == "gcs":
            return f"https://storage.googleapis.com/{self.config.bucket_name}/{remote_path}"
        else:
            return f"{self.config.provider}://{self.config.bucket_name}/{remote_path}"
    
    def _get_object_size(self, remote_path: str) -> int:
        """Get object size in bytes."""
        try:
            if self.config.provider == "s3":
                response = self._client.head_object(Bucket=self.config.bucket_name, Key=remote_path)
                return response['ContentLength']
            elif self.config.provider == "gcs":
                bucket = self._client.bucket(self.config.bucket_name)
                blob = bucket.blob(remote_path)
                blob.reload()
                return blob.size
        except:
            return 0
    
    def _get_object_modified_time(self, remote_path: str) -> str:
        """Get object last modified time."""
        try:
            if self.config.provider == "s3":
                response = self._client.head_object(Bucket=self.config.bucket_name, Key=remote_path)
                return response['LastModified'].isoformat()
            elif self.config.provider == "gcs":
                bucket = self._client.bucket(self.config.bucket_name)
                blob = bucket.blob(remote_path)
                blob.reload()
                return blob.time_created.isoformat()
        except:
            return ""
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.utcnow().isoformat() 