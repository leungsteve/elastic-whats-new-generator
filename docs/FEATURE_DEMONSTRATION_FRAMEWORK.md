# Feature Demonstration Framework: "Show, Don't Tell"

## The Core Problem

**Current State**: Labs that USE features but don't DEMONSTRATE them
**Example Issue**: ELSER with token pruning lab that never shows:
- ❌ What tokens look like BEFORE pruning
- ❌ What tokens look like AFTER pruning
- ❌ Storage reduction numbers
- ❌ Performance impact
- ❌ Quality maintained despite pruning

**Root Cause**: We're not asking "What is the observable evidence that this feature is working?"

---

## The Solution: Feature Demonstration Taxonomy

Every Elastic feature falls into one of these demonstration categories. Each category has **specific requirements** for what MUST be shown.

### Category 1: Performance Optimization Features
**What They Do**: Make things faster, cheaper, or more efficient
**Observable Evidence Required**: Before/After metrics

#### Features in This Category
- BBQ (Binary Quantization)
- ELSER Token Pruning
- ACORN Retrieval
- Index Sorting
- Frozen Tier

#### Demonstration Requirements (MANDATORY)

```markdown
## MUST Show:

### 1. Baseline Measurement (Before)
- Exact metric values WITHOUT the feature
- Example: "Current: 8.2s p99 latency, 192GB RAM, 1.2TB storage"

### 2. Feature Implementation
- Enable/configure the optimization
- Show the configuration change

### 3. Impact Measurement (After)
- Same metrics WITH the feature
- Example: "After BBQ: 0.8s p99 latency, 9GB RAM, 1.2TB storage"

### 4. Improvement Calculation
- Percentage gains
- Example: "10x faster, 95% less memory, same storage"

### 5. Quality Verification
- Prove performance gain didn't sacrifice quality
- Example: "98% recall maintained, results identical"

### 6. Cost/Business Impact
- Translate metrics to money/efficiency
- Example: "$38K/month savings + improved UX"
```

#### Example: ELSER Token Pruning Lab Structure

```markdown
## Challenge 1: See ELSER Tokens Without Pruning

**Business Context**: ELSER generates 100-150 tokens per document.
You're paying for storage and indexing time for ALL of them.

**Your Task**: Index 1000 documents with ELSER (no pruning) and examine tokens

```copy
PUT /articles_full_tokens
{
  "mappings": {
    "properties": {
      "content": {"type": "text"},
      "content_embedding": {
        "type": "sparse_vector",
        "inference_id": "elser_v2"
      }
    }
  }
}
```

**View the Tokens**:
```copy
GET /articles_full_tokens/_search
{
  "query": {"match_all": {}},
  "size": 1,
  "fields": ["content_embedding"]
}
```

**Expected Output**:
```nocopy
{
  "content_embedding": {
    "token1": 0.89,
    "token2": 0.87,
    "token3": 0.85,
    ... [showing 147 tokens total]
    "token147": 0.12
  }
}
```

**📊 Baseline Metrics**:
- Tokens per document: **147 average**
- Index size: **2.4 GB for 1000 docs**
- Indexing time: **18 seconds**

---

## Challenge 2: Enable Token Pruning

**Your Task**: Recreate index with token pruning at threshold 0.5

```copy
PUT /articles_pruned_tokens
{
  "mappings": {
    "properties": {
      "content": {"type": "text"},
      "content_embedding": {
        "type": "sparse_vector",
        "inference_id": "elser_v2_pruned"
      }
    }
  }
}

PUT _inference/sparse_embedding/elser_v2_pruned
{
  "service": "elser",
  "service_settings": {
    "num_allocations": 1,
    "num_threads": 1,
    "token_pruning_config": {
      "tokens_freq_ratio_threshold": 0.5,
      "tokens_weight_threshold": 0.4
    }
  }
}
```

**View the Pruned Tokens**:
```copy
GET /articles_pruned_tokens/_search
{
  "query": {"match_all": {}},
  "size": 1,
  "fields": ["content_embedding"]
}
```

**Expected Output**:
```nocopy
{
  "content_embedding": {
    "token1": 0.89,
    "token2": 0.87,
    "token3": 0.85,
    ... [showing only 23 tokens - 84% pruned!]
    "token23": 0.51
  }
}
```

**📊 After Pruning Metrics**:
- Tokens per document: **23 average** (84% reduction!)
- Index size: **0.45 GB for 1000 docs** (81% smaller!)
- Indexing time: **4 seconds** (4.5x faster!)

---

## Challenge 3: Verify Search Quality Maintained

**Critical Question**: Did we sacrifice search quality for performance?

**Your Task**: Run same searches on both indices, compare results

```copy
GET /articles_full_tokens,articles_pruned_tokens/_search
{
  "query": {
    "text_expansion": {
      "content_embedding": {
        "model_id": "elser_v2",
        "model_text": "machine learning deployment strategies"
      }
    }
  },
  "size": 10
}
```

**Compare Results Side-by-Side**:
| Metric | Full Tokens | Pruned Tokens | Impact |
|--------|-------------|---------------|---------|
| Top 10 results | Doc IDs: 1,5,3,7,2,9,4,8,6,10 | Doc IDs: 1,5,3,7,2,9,4,8,6,10 | **Identical!** |
| Query time | 145ms | 38ms | **3.8x faster** |
| Relevance scores | 0.89, 0.85, 0.82... | 0.88, 0.84, 0.81... | **~99% match** |

**✅ Key Finding**: Search quality virtually unchanged, but 3.8x faster!

---

## Challenge 4: Calculate Business Impact

**Your Production Scenario**:
- 50 million documents
- 100 queries/second
- Current: 2.4 GB × 50,000 = **120 TB storage**

**With Token Pruning**:
- Storage: 120 TB → **23 TB** (Save 97 TB)
- Query speed: 145ms → **38ms** (3.8x faster UX)
- Indexing: 18s/1000 docs → **4s/1000 docs** (4.5x faster)

**Cost Savings** (AWS us-east-1 pricing):
- Storage: 97 TB × $0.10/GB/mo = **$9,700/month saved**
- Compute: Faster queries = smaller instances = **$3,200/month saved**
- **Total: $12,900/month = $154,800/year**

**🎯 ROI**: Token pruning pays for itself immediately with zero quality loss!
```

---

### Category 2: Data Integration Features
**What They Do**: Combine data from multiple sources
**Observable Evidence Required**: Separate → Combined view

#### Features in This Category
- LOOKUP JOIN
- ENRICH
- Cross-cluster search
- Federated search

#### Demonstration Requirements (MANDATORY)

```markdown
## MUST Show:

### 1. The Separation Problem
- Show data living in different places
- Explain WHY it's separated (different systems/teams)
- Show limitation of querying each separately

### 2. The Manual Alternative
- Show what users do TODAY (exports, Excel joins, scripts)
- Quantify pain: time, errors, staleness

### 3. The Integration
- Execute the JOIN/ENRICH command
- Show combined results in single query

### 4. The Power Unlocked
- Show analytics that weren't possible before
- Example: "Now we can see customer tier + product + warehouse in one query"

### 5. Performance Proof
- Show it's fast despite joining multiple sources
- Example: "<500ms to join 5 indices with 100M rows"
```

---

### Category 3: Intelligence/AI Features
**What They Do**: Make dumb things smart
**Observable Evidence Required**: Failure → Success comparison

#### Features in This Category
- Semantic search (vs keyword)
- Agent Builder
- ELSER
- Anomaly detection
- ML model deployments

#### Demonstration Requirements (MANDATORY)

```markdown
## MUST Show:

### 1. The "Dumb" Baseline
- Show what DOESN'T work with current approach
- Example: Keyword search for "laptop" missing "notebook" results

### 2. The Failure Examples
- Give 3-5 queries that fail or give poor results
- Show low relevance scores, missing results

### 3. Enable Intelligence
- Deploy the ML model, semantic search, agent, etc.
- Show configuration

### 4. The "Smart" Results
- Same queries now return relevant results
- Show HIGH relevance scores, correct matches

### 5. Success Metrics
- Quantify improvement
- Example: "Recall improved from 42% → 87%"
- Show user satisfaction metrics if available

### 6. The "How Did It Know?" Moment
- Pick a surprising success
- Explain why AI understood semantic meaning
```

#### Example: Semantic Search vs Keyword

```markdown
## Challenge 1: Keyword Search Failures

**Your Task**: Search for "reduce cloud expenses" using keyword search

```copy
GET /articles/_search
{
  "query": {
    "match": {
      "content": "reduce cloud expenses"
    }
  }
}
```

**Results**: 3 documents found, all containing exact phrase

**❌ Missing**: Articles about:
- "Cost optimization strategies" (different words, same meaning)
- "Cloud spending cuts" (synonyms)
- "AWS bill reduction" (specific but relevant)

**Recall Rate**: 3/47 relevant docs = **6.4% recall**

---

## Challenge 2: Enable Semantic Search

**Your Task**: Add ELSER embeddings for semantic understanding

```copy
PUT _inference/sparse_embedding/elser_semantic
{
  "service": "elser",
  "service_settings": {
    "num_allocations": 1,
    "num_threads": 1
  }
}

POST /articles/_update_by_query?wait_for_completion=false
{
  "script": {
    "source": "ctx._source.content_embedding = params.embedding",
    "params": {
      "embedding": "{{elser_semantic}}"
    }
  }
}
```

---

## Challenge 3: Semantic Search Success

**Your Task**: Same search, now with semantic understanding

```copy
GET /articles/_search
{
  "query": {
    "text_expansion": {
      "content_embedding": {
        "model_id": "elser_semantic",
        "model_text": "reduce cloud expenses"
      }
    }
  }
}
```

**Results**: 44 documents found

**✅ Now Finding**:
- "Cost optimization strategies" (score: 0.89)
- "Cloud spending cuts" (score: 0.85)
- "AWS bill reduction" (score: 0.82)
- "FinOps best practices" (score: 0.78)

**Recall Rate**: 44/47 relevant docs = **93.6% recall**

**🎯 Improvement**: 6.4% → 93.6% = **14.6x better recall!**

---

## Challenge 4: The "How Did It Know?" Moment

**Surprising Success**: Query "reduce cloud expenses" found article titled
"FinOps Best Practices"

**Why It Worked**:
- Keyword would miss (no matching words!)
- ELSER understood semantic relationship:
  - "reduce" ≈ "optimize" ≈ "best practices"
  - "cloud expenses" ≈ "cloud costs" ≈ "FinOps"
  - Context: Both about saving money in cloud

**The Magic**: ELSER learned from millions of documents that these
concepts are related, even with zero word overlap.
```

---

### Category 4: Automation Features
**What They Do**: Replace manual processes with automatic ones
**Observable Evidence Required**: Manual → Automated comparison

#### Features in This Category
- Agent Builder
- Auto-scaling
- Index lifecycle management
- Automated rollups
- Watcher/Alerting

#### Demonstration Requirements (MANDATORY)

```markdown
## MUST Show:

### 1. The Manual Process
- Show step-by-step what humans do today
- Time each step
- Show error-prone points
- Calculate total time

### 2. The Pain Quantified
- How many times per day/week/month?
- Total human hours spent
- Cost of errors
- Delay in getting results

### 3. Implement Automation
- Configure the automatic process
- Show triggers, rules, workflows

### 4. The Automated Process
- Trigger the automation
- Show it happening without human intervention
- Compare speed

### 5. Time/Cost Savings
- Manual: X hours
- Automated: Y seconds
- Savings: Z hours/week, $N/month
```

---

### Category 5: Configuration/Operational Features
**What They Do**: Change system behavior, improve operations
**Observable Evidence Required**: Behavior change proof

#### Features in This Category
- Index sorting
- Security rules
- Data tiers
- Snapshot lifecycle
- Circuit breakers

#### Demonstration Requirements (MANDATORY)

```markdown
## MUST Show:

### 1. Default Behavior
- Show what happens WITHOUT the feature
- Document the limitation/problem

### 2. Enable Feature
- Show configuration change
- Explain what it changes

### 3. New Behavior
- Same scenario, different result
- Prove the behavior changed

### 4. The Improvement
- Quantify what got better
- Show metrics, logs, or outcomes
```

---

## Implementation: Feature Analysis Phase

### BEFORE generating any lab, the system MUST answer:

```yaml
feature_demonstration_analysis:
  feature_name: "ELSER Token Pruning"

  # Critical Questions (MUST answer all):
  category: "performance_optimization"  # From taxonomy above

  what_does_it_do: |
    Reduces number of tokens ELSER generates per document by removing
    low-importance tokens, reducing storage and improving speed.

  what_changes: |
    Token count per document: 100-150 → 20-30 (80% reduction)
    Index size: Proportionally smaller
    Indexing speed: Faster
    Query speed: Faster
    Search quality: Maintained (minimal loss)

  observable_evidence:
    before:
      - "View sparse_vector field showing 147 tokens"
      - "Measure index size: 2.4 GB for 1000 docs"
      - "Measure indexing time: 18 seconds"
      - "Measure query time: 145ms"

    after:
      - "View sparse_vector field showing 23 tokens"
      - "Measure index size: 0.45 GB for 1000 docs"
      - "Measure indexing time: 4 seconds"
      - "Measure query time: 38ms"

    proof_quality_maintained:
      - "Compare top 10 results from both indices"
      - "Show relevance scores within 1-2% of each other"
      - "Calculate recall: >95% maintained"

  demonstration_requirements:
    - "Show tokens array before pruning (full)"
    - "Show tokens array after pruning (reduced)"
    - "Compare sizes side-by-side"
    - "Prove search quality unchanged"
    - "Calculate cost savings"

  success_metrics:
    storage_reduction: "81%"
    speed_improvement: "3.8x faster queries, 4.5x faster indexing"
    quality_maintained: "99% relevance match, identical top results"
    cost_savings: "$12,900/month at 50M doc scale"
```

---

## Updated Lab Generator System Prompt

Add this MANDATORY phase:

```yaml
lab_generator:
  system_prompt: |
    [Previous content...]

    CRITICAL: FEATURE DEMONSTRATION PHASE (MUST complete before generating lab)

    Step 1: Classify Feature
    Determine which demonstration category:
    - Performance Optimization → Must show before/after metrics
    - Data Integration → Must show separate → combined
    - Intelligence/AI → Must show failure → success
    - Automation → Must show manual → automated
    - Configuration → Must show behavior change

    Step 2: Define Observable Evidence
    For THIS feature, what is the OBSERVABLE PROOF it's working?
    - What should learner SEE without the feature?
    - What should learner SEE with the feature?
    - What metrics QUANTIFY the improvement?
    - How do we PROVE quality/correctness maintained?

    Step 3: Design Demonstration Flow
    Create challenge sequence that SHOWS the evidence:
    - Challenge 1: Measure baseline (before)
    - Challenge 2: Enable feature
    - Challenge 3: Measure impact (after)
    - Challenge 4: Prove quality maintained
    - Challenge 5: Calculate business impact

    Step 4: Include Observable Outputs
    Every challenge must show EXACT outputs that prove it worked:
    - Not: "Storage is reduced"
    - YES: "Index size: 2.4 GB → 0.45 GB (81% reduction)"

    - Not: "Tokens are pruned"
    - YES: "Token count: 147 → 23 (84% pruned)"

    - Not: "Queries are faster"
    - YES: "Query time: 145ms → 38ms (3.8x faster)"

    FAILURE MODE TO AVOID:
    ❌ Labs that USE features but don't DEMONSTRATE what they do
    ❌ Generic queries that would work without the feature
    ❌ No before/after comparison
    ❌ No observable proof feature is active
    ❌ No metrics quantifying improvement

    SUCCESS CRITERIA:
    ✅ Learner can SEE the feature working (not just told it works)
    ✅ Metrics PROVE the improvement (not just described)
    ✅ Quality maintained is DEMONSTRATED (not assumed)
    ✅ Business value is CALCULATED (not estimated)
```

---

## Quality Validation Checklist

Before publishing ANY lab, validate:

### Evidence-Based Learning
- [ ] Learner sees the problem/baseline FIRST
- [ ] Learner sees the feature configuration
- [ ] Learner sees the improvement with EXACT metrics
- [ ] Learner sees proof quality/correctness maintained
- [ ] Learner sees business impact calculation

### Observable Proof Required
- [ ] Every claim has visible evidence
- [ ] Every metric is measured, not estimated
- [ ] Every comparison shows side-by-side numbers
- [ ] Every "better/faster" has percentage/multiplier

### Feature-Specific Demonstration
- [ ] Lab actually demonstrates THIS feature's mechanism
- [ ] Lab wouldn't work without THIS feature
- [ ] Lab shows what THIS feature uniquely provides
- [ ] Learner understands HOW this feature works, not just that it exists

---

## Example: Bad vs Good Lab

### ❌ Bad Lab (What We Currently Generate)

```markdown
## Challenge: Use ELSER Token Pruning

Configure ELSER with token pruning and run a search.

```copy
PUT /articles
{
  "mappings": {
    "properties": {
      "content_embedding": {
        "type": "sparse_vector"
      }
    }
  }
}
```

Run a search query and see the results.
```

**Problems**:
- No baseline shown
- No tokens visible
- No metrics measured
- No proof it's working
- Could work without pruning
- Doesn't demonstrate pruning at all

### ✅ Good Lab (What We Should Generate)

```markdown
## Challenge 1: Measure Baseline Without Pruning

Index 1000 articles and count tokens generated per document.

```copy
[Exact commands...]
```

Expected: 147 tokens per document, 2.4 GB index size

---

## Challenge 2: Enable Token Pruning

Configure threshold of 0.5 to prune low-value tokens.

```copy
[Exact configuration...]
```

---

## Challenge 3: Compare Token Counts

View tokens from both indices side-by-side.

Expected: 147 → 23 tokens (84% reduction!)

Before:
```nocopy
[Show 147 tokens...]
```

After:
```nocopy
[Show 23 tokens...]
```

---

## Challenge 4: Verify Search Quality

Run identical query on both, compare results.

Expected: Top 10 results identical, 99% relevance match

ROI: 81% storage savings = $12,900/month at scale
```

**Success**:
- Learner SEES tokens before/after
- Learner MEASURES reduction
- Learner PROVES quality maintained
- Learner CALCULATES business value

---

## Implementation Priority

1. **Immediate**: Add feature demonstration analysis to lab generation
2. **Week 1**: Update prompts with demonstration requirements
3. **Week 2**: Test with 5 different feature types
4. **Week 3**: Build feature taxonomy database
5. **Ongoing**: Refine based on user feedback

The goal: **Every lab proves the feature works through observable evidence, not descriptions.**