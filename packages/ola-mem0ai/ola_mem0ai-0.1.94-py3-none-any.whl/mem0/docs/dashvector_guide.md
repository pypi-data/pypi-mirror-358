# 阿里云 DashVector 向量数据库使用指南

## 概述

DashVector 是阿里云提供的向量搜索服务，具有高性能、高可靠性和易用性。mem0 现已支持使用 DashVector 作为存储后端，本指南将介绍如何配置和使用 DashVector 作为 mem0 的向量存储。

## 安装

首先，确保您已经安装了 DashVector 客户端库：

```bash
pip install dashvector
```

或者使用 Poetry：

```bash
poetry add dashvector
```

## 配置 DashVector

要使用 DashVector 作为向量存储后端，您需要在配置中提供以下信息：

1. `url` - DashVector 服务的端点 URL
2. `api_key` - DashVector 服务的 API 密钥
3. `collection_name` - 存储向量的集合名称（默认为 "mem0"）
4. `embedding_model_dims` - 嵌入模型的维度（默认为 1536）
5. `metric_type` - 相似度搜索的度量类型（默认为 COSINE）

## 使用示例

### 基本配置

```python
from mem0 import Memory
from mem0.configs.vector_stores.dashvector import DashVectorConfig, MetricType

# 创建 DashVector 配置
dashvector_config = DashVectorConfig(
    url="https://your-dashvector-endpoint.aliyuncs.com",
    api_key="your-api-key",
    collection_name="my_memories",
    embedding_model_dims=1536,
    metric_type=MetricType.COSINE
)

# 创建 Memory 实例
memory = Memory(vector_store_type="dashvector", vector_store_config=dashvector_config)
```

### 添加和检索记忆

```python
# 添加记忆
memory.add(
    text="这是一条重要的记忆",
    metadata={"user_id": "user123", "importance": "high"}
)

# 检索相关记忆
results = memory.search(
    query="我需要找到重要的信息",
    limit=5,
    filters={"metadata": {"user_id": "user123"}}
)

# 打印结果
for result in results:
    print(f"ID: {result.id}")
    print(f"文本: {result.text}")
    print(f"相似度: {result.score}")
    print(f"元数据: {result.metadata}")
    print("---")
```

## 性能考虑

- DashVector 支持高效的向量搜索和过滤功能
- 对于大规模的向量集合，建议适当配置 DashVector 实例的规格
- 通过合理设置 `filters` 参数可以提高搜索效率

## 注意事项

1. 确保您的 API 密钥具有足够的权限来创建和管理集合
2. DashVector 对 metadata 的处理与 Milvus 略有不同，mem0 已进行了适配
3. 向量维度在创建集合后不能更改，请确保配置正确的维度

## 常见问题解答

**Q: 如何查看已创建的集合？**
A: 可以使用 DashVector 控制台查看，或者通过代码访问：

```python
from mem0.vector_stores.dashvector import DashVectorDB

db = DashVectorDB(url="...", api_key="...", collection_name="mem0", embedding_model_dims=1536, metric_type=MetricType.COSINE)
collections = db.list_cols()
print(collections)
```

**Q: 如何删除一个集合？**
A: 可以使用 `delete_col()` 方法删除集合：

```python
db.delete_col()
```

**Q: 如何优化查询性能？**
A: 合理使用过滤条件，避免检索不必要的数据，同时可以考虑在阿里云控制台调整实例的性能配置。 