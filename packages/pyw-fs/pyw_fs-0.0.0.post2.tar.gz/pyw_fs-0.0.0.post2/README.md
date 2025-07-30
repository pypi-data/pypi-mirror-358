# pyw-fs 📁
[![PyPI](https://img.shields.io/pypi/v/pyw-fs.svg)](https://pypi.org/project/pyw-fs/)
[![CI](https://github.com/pythonWoods/pyw-fs/actions/workflows/ci.yml/badge.svg)](https://github.com/pythonWoods/pyw-fs/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Unified filesystem abstraction per **local**, **S3**, **GCS** e altri storage backends.

## Overview

**pyw-fs** elimina le differenze tra filesystem locali e cloud storage, fornendo un'API unificata basata su fsspec. Scrivi il codice una volta e funziona ovunque: dal disco locale ad Amazon S3, Google Cloud Storage, Azure Blob e oltre.

## Installation

```bash
# Core + local filesystem
pip install pyw-fs

# Con support S3
pip install pyw-fs[s3]

# Con support Google Cloud Storage  
pip install pyw-fs[gcs]

# Con support Azure Blob Storage
pip install pyw-fs[azure]

# Support completo per tutti i cloud providers
pip install pyw-fs[cloud]

# Tutto incluso + extras per development
pip install pyw-fs[full]
```

### Cloud Provider Setup

```bash
# AWS S3
pip install pyw-fs[s3]          # → s3fs, boto3

# Google Cloud Storage  
pip install pyw-fs[gcs]         # → gcsfs, google-cloud-storage

# Azure Blob Storage
pip install pyw-fs[azure]       # → adlfs, azure-storage-blob

# SFTP/SSH
pip install pyw-fs[ssh]         # → paramiko

# HTTP/FTP
pip install pyw-fs[http]        # → aiohttp, requests-ftp
```

## Quick Start

### 🚀 Universal File Operations

```python
from pyw.fs import open, exists, listdir, copy

# Stesso codice per tutti i filesystem
paths = [
    "local/file.txt",
    "s3://my-bucket/file.txt", 
    "gs://my-bucket/file.txt",
    "azure://container/file.txt"
]

for path in paths:
    with open(path, 'r') as f:
        content = f.read()
        print(f"{path}: {len(content)} chars")
```

### 📂 Directory Operations

```python
from pyw.fs import listdir, makedirs, rmtree, glob

# Cross-platform directory operations
base_paths = ["./data", "s3://bucket/data", "gs://bucket/data"]

for base in base_paths:
    # Create directories
    makedirs(f"{base}/processed", exist_ok=True)
    
    # List contents
    files = listdir(f"{base}/raw")
    
    # Pattern matching
    csv_files = glob(f"{base}/raw/*.csv")
    
    # Cleanup
    rmtree(f"{base}/temp", ignore_errors=True)
```

### 🔄 File Transfer & Sync

```python
from pyw.fs import copy, sync, move

# Cross-storage copying
copy("local/data.csv", "s3://backup/data.csv")
copy("s3://source/file.json", "gs://destination/file.json")

# Directory synchronization
sync("./local_folder", "s3://bucket/remote_folder", 
     delete=True, exclude="*.tmp")

# Batch operations
files_to_backup = glob("./important/*.json")
for file in files_to_backup:
    copy(file, f"s3://backup/{file}")
```

## Advanced Features

### 🏗️ Filesystem Objects

```python
from pyw.fs import get_filesystem, FileSystem

# Get filesystem instance
fs = get_filesystem("s3://my-bucket")
print(f"Protocol: {fs.protocol}")
print(f"Root: {fs.root}")

# Direct filesystem operations
fs.makedirs("processed/2024", exist_ok=True)
files = fs.ls("raw/", detail=True)

# Context manager
with FileSystem("gs://analytics-bucket") as fs:
    fs.put_text("report.txt", "Analysis complete")
    content = fs.cat_file("data.json")
```

### 🔧 Configuration & Credentials

```python
from pyw.fs import configure_storage, StorageConfig

# Global configuration
configure_storage({
    "s3": {
        "profile": "prod",
        "region": "eu-west-1",
        "endpoint_url": None  # For MinIO/LocalStack
    },
    "gcs": {
        "project": "my-project-id",
        "token": "path/to/service-account.json"
    },
    "azure": {
        "account_name": "mystorageaccount",
        "account_key": "key_from_env"  # Uses $AZURE_STORAGE_KEY
    }
})

# Per-operation configuration
s3_config = StorageConfig(
    provider="s3",
    profile="staging",
    region="us-east-1"
)

with open("s3://staging-bucket/data.json", config=s3_config) as f:
    data = f.read()
```

### 📊 Streaming & Large Files

```python
from pyw.fs import open_stream, read_chunks, upload_stream

# Streaming read per file grandi
def process_large_csv(path):
    with open_stream(path, mode='rb') as stream:
        for chunk in read_chunks(stream, chunk_size=1024*1024):  # 1MB chunks
            process_chunk(chunk)

# Streaming upload
def backup_large_file(local_path, remote_path):
    with open(local_path, 'rb') as local_file:
        upload_stream(local_file, remote_path, 
                     chunk_size=5*1024*1024)  # 5MB chunks

# Progress monitoring
from pyw.fs.utils import ProgressCallback

callback = ProgressCallback(desc="Uploading data")
copy("large_file.zip", "s3://bucket/large_file.zip", 
     callback=callback)
```

### 🔍 Advanced Path Operations

```python
from pyw.fs import Path, glob_advanced, find_files

# Path object per manipolazione elegante
path = Path("s3://bucket/data/2024/01/file.csv")
print(path.protocol)     # s3
print(path.bucket)       # bucket  
print(path.key)          # data/2024/01/file.csv
print(path.parent)       # s3://bucket/data/2024/01
print(path.stem)         # file
print(path.suffix)       # .csv

# Advanced globbing
files = glob_advanced(
    "s3://bucket/logs/*/2024/*/*.json",
    include_hidden=False,
    follow_symlinks=False,
    max_depth=3
)

# Smart file discovery
csv_files = find_files(
    "gs://data-lake",
    patterns=["*.csv", "*.tsv"],
    exclude_patterns=["*_temp*", ".*"],
    modified_after="2024-01-01",
    size_range=(1024, 100*1024*1024)  # 1KB to 100MB
)
```

### 🔒 Security & Access Control

```python
from pyw.fs import SecureFS, EncryptedStorage

# Secure filesystem con encryption
secure_fs = SecureFS(
    "s3://sensitive-bucket",
    encryption_key="path/to/key.pem",
    access_policy="read-only"
)

with secure_fs.open("confidential.txt") as f:
    content = f.read()  # Auto-decrypted

# Client-side encryption wrapper
encrypted = EncryptedStorage(
    backend="s3://encrypted-bucket",
    algorithm="AES256",
    key_source="aws-kms",  # or "local", "vault"
    key_id="arn:aws:kms:region:account:key/key-id"
)

encrypted.put_text("secret.txt", "Sensitive data")
decrypted = encrypted.cat_text("secret.txt")
```

## Integration Patterns

### 🐼 DataFrame Integration

```python
import pandas as pd
from pyw.fs import read_dataframe, write_dataframe

# Read from any storage
df = read_dataframe("s3://data/sales.csv")
df2 = read_dataframe("gs://analytics/users.parquet")

# Write to any storage
write_dataframe(df, "azure://reports/monthly.xlsx")

# Streaming per dataset grandi
def process_large_dataset(path):
    for chunk in read_dataframe(path, chunksize=10000):
        processed = transform_data(chunk)
        write_dataframe(processed, f"s3://output/chunk_{chunk.index[0]}.parquet")
```

### 🗄️ Database Backup Integration

```python
from pyw.fs import DatabaseBackup
import sqlalchemy

# Automated database backups
backup = DatabaseBackup(
    database_url="postgresql://user:pass@host/db",
    storage_path="s3://backups/db",
    compression="gzip",
    encryption=True
)

# Scheduled backup
backup.create_backup(
    tables=["users", "orders", "products"],
    format="parquet",
    partition_by="date"
)

# Point-in-time recovery
backup.restore_backup(
    backup_id="backup_20240115_143022",
    target_database="postgresql://user:pass@host/db_restored"
)
```

### 📦 Archive & Compression

```python
from pyw.fs import Archive, compress_directory

# Create archives across storage systems
archive = Archive("s3://archives/project_2024.tar.gz")
archive.add_directory("./project", exclude="*.pyc")
archive.add_file("s3://source/important.json", "backup/important.json")
archive.save()

# Compress and upload directories
compress_directory(
    source="./large_project",
    destination="gs://backups/project.zip",
    compression="zip",
    exclude_patterns=["__pycache__", "*.log", ".git"]
)

# Extract from remote archives
with Archive("s3://archives/data.tar.gz") as archive:
    archive.extract_to("./restored_data")
    archive.extract_file("config.json", "./config.json")
```

### 🌐 Web Framework Integration

```python
# FastAPI file upload/download
from fastapi import FastAPI, UploadFile
from pyw.fs import save_upload, serve_file

app = FastAPI()

@app.post("/upload")
async def upload_file(file: UploadFile):
    # Save to any storage backend
    path = f"s3://uploads/{file.filename}"
    await save_upload(file, path)
    return {"path": path}

@app.get("/download/{file_path:path}")
async def download_file(file_path: str):
    # Serve from any storage backend
    return serve_file(f"s3://files/{file_path}")

# Django storage backend
# settings.py
DEFAULT_FILE_STORAGE = 'pyw.fs.integrations.django.PywStorage'
PYW_STORAGE_CONFIG = {
    'backend': 's3://django-media',
    'prefix': 'media/',
    'public_read': True
}
```

### 🧪 Testing & Development

```python
from pyw.fs.testing import TemporaryFilesystem, MockStorage

def test_file_processing():
    with TemporaryFilesystem() as tmp_fs:
        # Create test data
        tmp_fs.put_text("input.csv", "a,b,c\n1,2,3")
        
        # Test your function
        result = process_csv_file(tmp_fs.path("input.csv"))
        
        # Verify output
        assert tmp_fs.exists("output.json")
        output = tmp_fs.cat_json("output.json")
        assert len(output) == 1

# Mock cloud storage per unit tests
@MockStorage("s3://test-bucket", {"data.json": '{"test": true}'})
def test_s3_integration():
    # S3 calls sono automaticamente mocked
    data = load_from_s3("s3://test-bucket/data.json")
    assert data["test"] is True
```

## Configuration Management

### 🔧 Environment-based Configuration

```python
from pyw.fs import configure_from_env, get_default_config

# Auto-configure da environment variables
configure_from_env()

# Equivale a:
# AWS_PROFILE, AWS_REGION → S3 config
# GOOGLE_APPLICATION_CREDENTIALS → GCS config
# AZURE_STORAGE_ACCOUNT_NAME → Azure config

# Custom configuration file
from pyw.fs import load_config_file

config = load_config_file("storage_config.yaml")
# storage_config.yaml:
# providers:
#   s3:
#     profile: production
#     region: eu-west-1
#   gcs:
#     project: my-project
#     credentials: /path/to/service-account.json
```

### 📋 Connection Pooling & Caching

```python
from pyw.fs import ConnectionPool, enable_caching

# Connection pooling per performance
pool = ConnectionPool(
    max_connections=10,
    connection_timeout=30,
    retry_attempts=3
)

configure_storage({"connection_pool": pool})

# File metadata caching
enable_caching(
    cache_size=1000,
    ttl=300,  # 5 minutes
    cache_file_contents=False  # Solo metadata
)

# Custom cache backend
from pyw.fs.cache import RedisCache

cache = RedisCache(
    host="redis.example.com",
    port=6379,
    db=0
)
configure_storage({"cache": cache})
```

## Performance Optimization

### ⚡ Parallel Operations

```python
from pyw.fs import parallel_copy, parallel_sync, ParallelConfig

# Parallel file operations
files_to_copy = [
    ("local/file1.txt", "s3://bucket/file1.txt"),
    ("local/file2.txt", "s3://bucket/file2.txt"),
    ("local/file3.txt", "s3://bucket/file3.txt"),
]

parallel_copy(
    files_to_copy,
    max_workers=5,
    chunk_size=1024*1024,
    show_progress=True
)

# Parallel directory sync
parallel_sync(
    source="./data",
    destination="s3://backup/data",
    config=ParallelConfig(
        max_workers=10,
        max_concurrent_uploads=5,
        chunk_size=5*1024*1024
    )
)
```

### 📊 Performance Monitoring

```python
from pyw.fs import PerformanceMonitor, get_stats

# Monitor filesystem operations
with PerformanceMonitor() as monitor:
    copy("large_file.zip", "s3://bucket/large_file.zip")
    
print(f"Transfer speed: {monitor.transfer_speed_mbps:.1f} MB/s")
print(f"Total time: {monitor.elapsed_time:.2f}s")

# Global statistics
stats = get_stats()
print(f"Total operations: {stats.total_operations}")
print(f"Average speed: {stats.average_speed_mbps:.1f} MB/s")
print(f"Error rate: {stats.error_rate:.2%}")

# Performance profiling
from pyw.fs.profiling import profile_operation

@profile_operation
def bulk_upload(files):
    for file in files:
        copy(file, f"s3://bucket/{file}")

bulk_upload(["file1.txt", "file2.txt", "file3.txt"])
```

### 🔄 Smart Caching & Prefetching

```python
from pyw.fs import SmartCache, enable_prefetching

# Intelligent caching
cache = SmartCache(
    max_size="1GB",
    eviction_policy="LRU",
    compression=True,
    persist_to_disk=True
)

# Prefetch pattern-based files
enable_prefetching(
    patterns=["*.csv", "*.json"],
    max_prefetch_size="100MB",
    prefetch_on_list=True
)

# Predictive caching
from pyw.fs.ml import PredictiveCache

predictive = PredictiveCache()
predictive.learn_access_patterns("./access_logs.json")

# Auto-prefetch files likely to be accessed
predictive.prefetch_likely_files(threshold=0.8)
```

## CLI Tools

```bash
# List files across storage systems
pyw-fs ls s3://bucket/path --recursive --human-readable

# Copy with progress bar
pyw-fs cp local_file.txt s3://bucket/remote_file.txt --progress

# Sync directories
pyw-fs sync ./local_dir s3://bucket/remote_dir --delete --dry-run

# File information
pyw-fs info s3://bucket/file.txt --detailed

# Bulk operations
pyw-fs bulk-copy files_list.txt s3://bucket/ --parallel=10

# Storage usage analysis
pyw-fs du s3://bucket --summarize --sort-by-size

# Test storage connectivity
pyw-fs test-connection s3://bucket gcs://bucket azure://container

# Performance benchmarking
pyw-fs benchmark s3://bucket --operation=upload --file-size=100MB --iterations=10

# Cleanup utilities
pyw-fs cleanup s3://bucket --older-than=30d --pattern="*.tmp"
```

## Cloud Provider Specifics

### ☁️ AWS S3 Advanced Features

```python
from pyw.fs.providers import S3FileSystem

# S3-specific operations
s3 = S3FileSystem(
    profile="production",
    region="eu-west-1",
    endpoint_url=None  # For MinIO compatibility
)

# Server-side encryption
s3.put_text("s3://bucket/encrypted.txt", "data", 
           ServerSideEncryption="AES256")

# Multipart upload per file grandi
s3.upload_large_file("large_dataset.csv", "s3://bucket/data.csv",
                    multipart_threshold=100*1024*1024)

# Presigned URLs
url = s3.generate_presigned_url("s3://bucket/file.txt", expires_in=3600)

# S3 versioning
versions = s3.list_versions("s3://bucket/document.txt")
s3.restore_version("s3://bucket/document.txt", version_id="version123")
```

### 🌐 Google Cloud Storage

```python
from pyw.fs.providers import GCSFileSystem

gcs = GCSFileSystem(
    project="my-project",
    token="path/to/service-account.json"
)

# GCS-specific metadata
gcs.put_text("gs://bucket/file.txt", "data",
            metadata={"department": "analytics", "version": "1.0"})

# Lifecycle management
gcs.set_lifecycle_policy("gs://bucket", {
    "rules": [{
        "action": {"type": "Delete"},
        "condition": {"age": 365}
    }]
})

# Signed URLs
signed_url = gcs.generate_signed_url("gs://bucket/file.txt", 
                                   method="GET", expires=3600)
```

### 🔷 Azure Blob Storage

```python
from pyw.fs.providers import AzureFileSystem

azure = AzureFileSystem(
    account_name="mystorageaccount",
    account_key="...",  # or use account_url + credential
)

# Azure-specific features
azure.put_text("azure://container/file.txt", "data",
              content_type="text/plain",
              cache_control="max-age=3600")

# Blob tiers
azure.set_blob_tier("azure://container/archive.zip", "Archive")

# SAS tokens
sas_url = azure.generate_sas_url("azure://container/file.txt",
                                permission="read", expires="2024-12-31")
```

## Error Handling & Resilience

### 🛡️ Robust Error Handling

```python
from pyw.fs import FileSystemError, RetryConfig, CircuitBreaker
from pyw.fs.exceptions import *

# Custom retry configuration
retry_config = RetryConfig(
    max_attempts=5,
    backoff_factor=2.0,
    retry_on=[ConnectionError, TimeoutError],
    circuit_breaker=CircuitBreaker(failure_threshold=10, recovery_timeout=60)
)

try:
    with open("s3://unreliable-bucket/file.txt", retry_config=retry_config) as f:
        content = f.read()
except FileNotFoundError:
    print("File doesn't exist")
except PermissionError:
    print("Access denied")
except NetworkError as e:
    print(f"Network issue: {e}")
except FileSystemError as e:
    print(f"General filesystem error: {e}")

# Graceful degradation
from pyw.fs.fallback import FallbackFileSystem

# Primary: S3, Fallback: Local cache
fs = FallbackFileSystem([
    "s3://primary-bucket",
    "file://./cache",
    "gs://backup-bucket"
])

# Automatic fallback se S3 non disponibile
content = fs.cat_text("important_file.txt")
```

### 📊 Health Monitoring

```python
from pyw.fs.monitoring import HealthCheck, StorageMonitor

# Health check per storage backends
health = HealthCheck()
status = health.check_all_providers()

for provider, result in status.items():
    print(f"{provider}: {'✅' if result.healthy else '❌'}")
    if not result.healthy:
        print(f"  Error: {result.error}")
        print(f"  Latency: {result.latency_ms}ms")

# Continuous monitoring
monitor = StorageMonitor(
    check_interval=60,  # seconds
    alert_threshold=5000,  # ms
    alert_callback=send_slack_alert
)

monitor.start()
```

## Ecosystem Integration

**pyw-fs** integra perfettamente con altri moduli pythonWoods:

```python
# Con pyw-logger
from pyw.logger import get_logger
from pyw.fs import configure_logging

log = get_logger("filesystem")
configure_logging(logger=log, level="INFO")

# Automatic logging delle operazioni
copy("file.txt", "s3://bucket/file.txt")  
# → Log: "File copied: file.txt → s3://bucket/file.txt (1.2MB, 2.3s)"

# Con pyw-config
from pyw.config import get_config
from pyw.fs import configure_from_config

config = get_config()
configure_from_config(config.storage)

# Con pyw-secret per credentials management
from pyw.secret import get_secret
from pyw.fs import configure_credentials

aws_access_key = get_secret("AWS_ACCESS_KEY_ID")
aws_secret_key = get_secret("AWS_SECRET_ACCESS_KEY")

configure_credentials("s3", {
    "aws_access_key_id": aws_access_key,
    "aws_secret_access_key": aws_secret_key
})

# Con pyw-cli per command-line tools
from pyw.cli import command
from pyw.fs import sync

@command("sync-data")
def sync_data_command(source: str, destination: str, dry_run: bool = False):
    """Sync data between storage systems."""
    sync(source, destination, delete=True, dry_run=dry_run)
```

## Best Practices

### 🎯 Performance Guidelines

```python
# ✅ Good: Use streaming per file grandi
def process_large_file(path):
    with open_stream(path) as stream:
        for chunk in read_chunks(stream, 1024*1024):
            yield process_chunk(chunk)

# ❌ Bad: Load everything in memory
def process_large_file_bad(path):
    with open(path) as f:
        data = f.read()  # Potenzialmente GB in RAM
    return process_all_data(data)

# ✅ Good: Batch operations
files_to_copy = collect_files_to_copy()
parallel_copy(files_to_copy, max_workers=5)

# ❌ Bad: Sequential operations
for src, dst in files_to_copy:
    copy(src, dst)  # Lento e sequenziale
```

### 🔒 Security Best Practices

```python
# ✅ Good: Use environment variables per credentials
configure_storage({
    "s3": {
        "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
        "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY")
    }
})

# ❌ Bad: Hardcoded credentials
configure_storage({
    "s3": {
        "aws_access_key_id": "AKIAIOSFODNN7EXAMPLE",  # ❌ Mai fare così!
        "aws_secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
    }
})

# ✅ Good: Validate paths e sanitize input
def safe_file_operation(user_path):
    if not is_safe_path(user_path):
        raise ValueError("Unsafe path detected")
    
    canonical_path = sanitize_path(user_path)
    return process_file(canonical_path)
```

## Philosophy

* **Universal API** – stesso codice per local, S3, GCS, Azure e qualsiasi fsspec backend
* **Performance first** – streaming, parallel operations, intelligent caching
* **Cloud native** – progettato per applicazioni moderne multi-cloud
* **Developer friendly** – API familiare simile a Python's pathlib e built-in open()
* **Production ready** – error handling robusto, monitoring, retry logic
* **Ecosystem integration** – lavora seamlessly con altri moduli pyw

## Roadmap

- 📁 **Enhanced abstractions**: Path-like objects, context managers avanzati
- ⚡ **Performance improvements**: Zero-copy operations, memory-mapped files
- 🔄 **Advanced sync**: Incremental sync, conflict resolution, versioning
- 🔐 **Security enhancements**: Encryption at transit/rest, access policies
- 📊 **Better monitoring**: Metrics export, performance analytics
- 🤖 **AI-powered optimization**: Predictive caching, smart prefetching
- 🌐 **Extended providers**: WebDAV, HDFS, database storage adapters

## Contributing

**pyw-fs** è un componente fondamentale dell'ecosistema pythonWoods:

1. **Fork & Clone**: `git clone https://github.com/pythonWoods/pyw-fs.git`
2. **Development setup**: `poetry install && poetry shell`
3. **Provider setup**: Configure test credentials per S3/GCS/Azure
4. **Quality checks**: `ruff check . && mypy && pytest --cov`
5. **Integration tests**: Test cross-storage operations
6. **Performance tests**: `pytest benchmarks/ --benchmark-only`
7. **Documentation**: Aggiorna esempi per nuovi provider
8. **Pull Request**: CI testa tutti i provider supportati

### Development Commands

```bash
# Setup test environment
make setup-test-env

# Run tests per specific provider
make test-s3
make test-gcs  
make test-azure

# Performance benchmarks
make benchmark-all

# Integration tests
make test-integration

# Documentation build
make docs-build
```

## Architecture Notes

```
pyw-fs/
├── pyw/
│   └── fs/
│       ├── __init__.py          # Public API
│       ├── core.py              # Core filesystem abstraction
│       ├── config.py            # Configuration management
│       ├── providers/           # Cloud provider implementations
│       │   ├── s3.py           # AWS S3
│       │   ├── gcs.py          # Google Cloud Storage
│       │   ├── azure.py        # Azure Blob Storage
│       │   └── local.py        # Local filesystem
│       ├── operations/          # High-level operations
│       │   ├── copy.py         # Copy operations
│       │   ├── sync.py         # Directory sync
│       │   └── archive.py      # Archive/compression
│       ├── utils/               # Utilities
│       │   ├── path.py         # Path manipulation
│       │   ├── stream.py       # Streaming operations
│       │   └── parallel.py     # Parallel processing
│       ├── integrations/        # Framework integrations
│       ├── testing.py           # Test utilities
│       ├── monitoring.py        # Health checks & metrics
│       └── cli.py               # Command-line interface
├── benchmarks/                  # Performance tests
├── examples/                    # Usage examples
└── tests/                       # Test suite
```

Felice file management nella foresta di **pythonWoods**! 🌲📁

## Links utili

Documentazione dev (work-in-progress) → https://pythonwoods.dev/docs/pyw-fs/latest/

Issue tracker → https://github.com/pythonWoods/pyw-fs/issues  

Changelog → https://github.com/pythonWoods/pyw-fs/releases

Performance benchmarks → https://pythonwoods.dev/benchmarks/pyw-fs/

Provider compatibility → https://pythonwoods.dev/docs/pyw-fs/providers/

© pythonWoods — MIT License