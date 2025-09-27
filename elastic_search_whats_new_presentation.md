# Elastic What's New Presentation

## 1. Enhanced Data Integration & Operations

### Cross-Cluster Search with ES|QL LOOKUP JOIN
- **General Availability**: Cross-cluster search with ES|QL is now generally available as an Enterprise feature in Elasticsearch 8.19 and 9.1
- **Key Benefits**:
  - Query data across multiple clusters with a single, elegant query
  - Unify data across geographic regions, environments, or business units
  - No need to move or re-index data - queries securely gather data from all specified clusters

### LOOKUP JOIN in ES|QL
- **General Availability**: LOOKUP JOIN is now generally available, enabling live data correlation and distributed search across clusters
- **Capabilities**:
  - SQL-style LEFT JOIN behavior that combines data from query results with matching records from a lookup index
  - Better handling of multiple matches - creates multiple rows instead of multi-valued fields, making further analytics easier
  - Cross-cluster LOOKUP JOIN supported in versions 9.2.0+ with remote lookup joins

### AutoOps/Cloud Connected Alerts from Visualizations
- **Availability**: AutoOps is rapidly expanding to Elasticsearch clusters on Elastic Cloud, currently available for AWS US-East-1 with expansion across regions
- **Features**:
  - Analyze hundreds of Elasticsearch metrics in real time with alerts to detect ingestion bottlenecks, data structure misconfiguration, unbalanced loads, slow queries
  - Point-in-time drill-downs and resolution suggestions, including in-context Elasticsearch commands
  - Customizable event triggers and connections to PagerDuty, Slack, MS Teams, and webhooks

## 2. Vector Search Performance Revolution

### Better Binary Quantization (BBQ) by Default
- **Default Implementation**: BBQ is now the default quantization method for dense vectors of 384+ dimensions in Elasticsearch 9.1
- **Performance Gains**:
  - ~95% memory reduction while maintaining high ranking quality
  - When benchmarked across 10 industry-standard BEIR datasets, BBQ outperformed traditional float32-based search in 9 out of 10 cases
  - Up to 5x faster queries and 3.9x higher throughput compared to OpenSearch FAISS
  - 20-30x less quantization time and 2-5x faster queries compared to Product Quantization

### ACORN Filtered Vector Search
- **Innovation**: ACORN-1 is a new algorithm for filtered k-Nearest Neighbor (kNN) search that tightly integrates filtering into HNSW graph traversal
- **Performance**: Up to 5X speedups in real-world filtered vector search benchmarks, improving latency without compromising result accuracy
- **Flexibility**: Enables flexible filter definition at query time, even after documents have been ingested

### ELSER with Token Pruning
- **Enhancement**: Token pruning provides 3-4x improvement in 99th percentile latency for text expansion with ELSER
- **Methodology**: Identifies non-significant tokens based on frequency (5x more frequent than average) and weight thresholds
- **Relevance Preservation**: When pruned tokens are added back in a rescore block, relevance remains close to original non-pruned results with only marginal latency increase
- **Configuration**: Available through the sparse_vector query with pruning_config parameters for customized performance tuning

## 3. AI-Powered Infrastructure & Services

### Elastic Managed LLM
- **Out-of-the-Box Availability**: Elastic now includes a default managed LLM, prioritizing privacy and eliminating the need for additional setup or subscriptions
- **Infrastructure**: Currently proxying to AWS Bedrock in AWS US regions, beginning with us-east-1, with zero data retention configuration
- **Security**: All data encrypted in transit, no prompts or outputs stored by the model, only request metadata logged

### Elastic Inference Service (EIS)
- **Service Overview**: EIS enables AI-powered search as a service without deploying models in your cluster
- **Model Support**: Preconfigured inference endpoints for ELSER (.elser-2-elasticsearch) and E5 (.multilingual-e5-small-elasticsearch)
- **Benefits**: ELSER on EIS provides better performance for throughput and latency than ML nodes, running on managed GPU infrastructure

### ELSER, E5 & Elastic Rerank OOTB
- **ELSER v2**: Generally available with Intel-optimized and cross-platform versions, recommended for English language semantic search
- **E5 Model**: Recommended for non-English language documents and multilingual semantic search
- **Adaptive Allocations**: Dynamic resource adjustment based on demand, scaling down to 0 when inactive to save resources

### Agent Builder (Coming Soon)
- **Framework**: Agent Builder provides a complete framework for agent development, integrated into the Search AI Platform
- **Architecture**: Built on five key pillars: objectives, tools, open standards, evaluation, and security
- **Native Integration**: First agent is a native conversational agent in Kibana, ready-to-use without additional configuration
- **Developer Focus**: Developers define what the agent should do (objectives, tools, data) while the system manages reasoning and workflow execution

## Key Takeaways

1. **Cross-Cluster & Data Integration**: ES|QL now enables seamless querying across distributed clusters with native JOIN capabilities and intelligent operational monitoring through AutoOps.

2. **Vector Search Leadership**: Elastic leads with BBQ as default quantization (95% memory reduction), ACORN for 5x faster filtered search, and optimized ELSER with token pruning for better performance.

3. **AI-First Infrastructure**: Complete AI ecosystem with managed LLM, inference service, and upcoming Agent Builder framework for production-ready AI applications.

These innovations position Elastic as the comprehensive Search AI Platform, delivering enterprise-scale performance improvements while simplifying AI adoption and reducing infrastructure costs.