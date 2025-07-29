import importlib.metadata

try:
    __version__ = importlib.metadata.version("mem0ai")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.1.0-dev"  # 开发版本
from mem0.client.main import AsyncMemoryClient, MemoryClient  # noqa
from mem0.memory.main import Memory, AsyncMemory  # noqa
