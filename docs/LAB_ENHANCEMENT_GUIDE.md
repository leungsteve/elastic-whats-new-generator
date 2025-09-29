# Lab Enhancement Guide - Reaching Instruqt Quality

## Analysis of Exemplary LOOKUP JOIN Lab

### What Makes It Excellent

1. **Compelling Executive Narrative**
   - Opens with CEO quote creating urgency
   - "Record Black Friday sales BUT shipping delays and inventory issues"
   - Makes the learner the hero solving real business problems

2. **Clear Architecture Visualization**
   - Shows data architecture upfront
   - Explains WHY data is separated (multiple systems)
   - Sets context before diving into technical details

3. **Technical Rigor**
   - Explains LOOKUP vs ENRICH comparison
   - Shows when to use each approach
   - Includes critical configuration (`"index.mode": "lookup"`)

4. **Progressive Complexity**
   - Challenge 1: Single join (orders + customers)
   - Challenge 2: Multi-index (3 tables)
   - Challenge 3: All 5 tables with advanced analytics
   - Each builds on previous knowledge

5. **Business Intelligence Focus**
   - Every query answers a specific business question
   - Results include actionable insights
   - "Alert! 4K Smart TV in Los Angeles has LOW_STOCK"

6. **Complete Verification**
   - Shows expected output for EVERY command
   - Includes error states (404 before creation)
   - Troubleshooting section with common errors

7. **Visual Learning**
   - Screenshots of expected results
   - Makes it easy to verify you're on track
   - Reduces cognitive load

## Specific Improvements for Our Lab Generator

### 1. Enhanced Story Structure

**Current**: Basic scenario description
**Improved**: Executive-level narrative with urgency

```yaml
story_context:
  executive_hook: |
    > "CEO Quote creating urgency and business context"

  role: "You're a [specific role] at [company name]"

  challenge: "Specific business problem that must be solved"

  why_it_matters: "Stakes and consequences"

  mission: "What you'll accomplish with these features"
```

### 2. Data Architecture Section

**Add Before Setup**:
```markdown
## The Data Challenge

[CompanyName]'s data lives in separate systems:
- **Orders** (Main Index) - [description]
- **Customers** (Lookup) - [description]
- **Products** (Lookup) - [description]

[Visual ASCII diagram showing relationships]

Your mission: Join this data to uncover patterns and solve business problems!
```

### 3. Enhanced Verification Strategy

**Current**: Basic command output
**Improved**: Multi-step verification

```markdown
### Verify Cleanup (Should return empty results)
[Command]
Expected result:
```nocopy
{error message showing no indices}
```

### Verify Data Loading
[Command]
Expected Results:
```nocopy
index      health status docs.count
orders     green  open           50
customers  green  open           20
```
```

### 4. Business Question Format

**Current**: "Create a query that..."
**Improved**: Executive-style business questions

```markdown
## Challenge 3: Multi-Index Analysis

Business Question: "I need to see our Black Friday performance by product
category, but only for Premium customers. Include warehouse performance ratings."

Your Challenge: Complete this query using multiple LOOKUP JOINs:
[Query template or hints]
```

### 5. Key Insights Section

**Add After Each Major Query**:
```markdown
**Key Business Insights**:
- [Insight 1 with specific numbers]
- Alert! [Critical finding that needs action]
- [Pattern discovered]
```

### 6. Technical Deep-Dive Callouts

```markdown
### How the Command Works
The LOOKUP JOIN command adds fields from the lookup index as new columns
to your results table based on matching values in the join field.

```nocopy
LOOKUP JOIN <lookup_index> ON <field_name>
LOOKUP JOIN <lookup_index> ON <field_name1>, <field_name2>
```

If you're familiar with SQL, LOOKUP JOIN has left-join behavior...
```

### 7. Complete Troubleshooting Section

```markdown
### Troubleshooting: If you get "verification_exception" errors:

1. **Check index mode**: Run `GET /<index_name>/_settings` to verify...
2. **Clean and recreate**: Use DELETE commands and recreate indices
3. **Verify data**: Use count commands to ensure all data loaded properly

### Common LOOKUP JOIN Requirements:
- ✅ Lookup indices MUST have `"index.mode": "lookup"` setting
- ✅ Join fields must have compatible data types
- ✅ Field names must match exactly between indices
```

## Updated Lab Generation Prompt

### Enhanced System Prompt Additions

```yaml
lab_generator:
  system_prompt: |
    [Keep existing prompt, ADD these sections]

    EXECUTIVE NARRATIVE STRUCTURE:
    - Start with CEO/executive quote expressing business urgency
    - Frame learner as the hero solving a critical business problem
    - Use specific company name (e.g., "TechMart", "RetailCo")
    - Include "mission statement" that creates excitement

    DATA ARCHITECTURE SECTION (Before Setup):
    - Visual representation of data relationships
    - Explain WHY data is separated across systems
    - List each index with its purpose
    - Show how joins will uncover insights

    VERIFICATION STRATEGY:
    - Show expected errors when indices don't exist
    - Include verification commands after EVERY major step
    - Use `GET /_cat/indices` to show doc counts
    - Screenshots or ASCII tables showing expected output

    BUSINESS QUESTION FORMAT:
    Each challenge must include:
    1. Executive-style business question in quotes
    2. "Your Challenge:" task description
    3. Query to complete (with hints)
    4. Expected results with SPECIFIC NUMBERS
    5. "Key Business Insights" section explaining results

    TECHNICAL DEPTH:
    - Explain HOW commands work, not just WHAT they do
    - Compare with alternatives (e.g., "LOOKUP JOIN vs ENRICH")
    - Include critical configuration requirements
    - Add "Pro Tips" for optimization

    TROUBLESHOOTING SECTION (Required):
    - Common errors and their solutions
    - Verification commands to debug
    - Requirements checklist
    - Cleanup commands

    VISUAL LEARNING:
    - Use ASCII tables for expected output
    - Include result counts and specific values
    - Format output in ```nocopy blocks
    - Use emoji for status (✅ ❌ ⚠️)
```

### Enhanced User Prompt

```yaml
  user_prompt: |
    Create an Instruqt-quality hands-on lab for Elastic {domain}.

    FEATURES TO TEACH: {feature_list}

    EXECUTIVE NARRATIVE:
    - Create a compelling CEO quote expressing business urgency
    - Frame as "[Role] at [Company]" solving critical business problem
    - Use scenario: {scenario_type}
    - Data volume: {data_size}

    REQUIRED LAB COMPONENTS:

    1. EXECUTIVE HOOK (2-3 paragraphs)
       - CEO quote with urgency
       - Your role and company
       - Specific business challenge
       - Mission statement

    2. DATA ARCHITECTURE VISUALIZATION
       - ASCII diagram of data relationships
       - Why data is separated
       - Purpose of each index

    3. SETUP WITH COMPLETE VERIFICATION
       - Verify cleanup (show 404 errors)
       - Create indices with critical configs
       - Load sample data (50-500 records)
       - Verify data loading with counts

    4. PROGRESSIVE CHALLENGES (5-7)
       Each challenge MUST include:
       - Business Question: "Executive quote"
       - Your Challenge: Task description
       - Query template or hints
       - Expected Results: Specific numbers/output
       - Key Business Insights: What results mean

    5. TECHNICAL DEEP-DIVES
       - "How the Command Works" explanations
       - Comparison with alternatives
       - Critical configuration requirements
       - Pro tips for optimization

    6. TROUBLESHOOTING SECTION
       - Common errors and solutions
       - Verification checklist
       - Cleanup commands

    OUTPUT REQUIREMENTS:
    - All ES|QL must be valid for Elasticsearch 8.15+
    - Include ```nocopy blocks for expected output
    - Use specific numbers in examples (not "123")
    - Show success AND error states
    - Format as Instruqt-ready markdown
```

## Implementation Checklist

To reach Instruqt quality, our labs MUST include:

- [ ] Executive-level opening with CEO quote
- [ ] Company name and learner role
- [ ] Data architecture visualization
- [ ] Verification after EVERY step
- [ ] Business questions in executive language
- [ ] Specific numbers in expected results
- [ ] "Key Insights" after major queries
- [ ] Technical explanations (not just commands)
- [ ] Complete troubleshooting section
- [ ] Cleanup commands
- [ ] Visual output formatting (ASCII tables)

## Example Transformation

### Before (Current Style)
```markdown
## Challenge 1: Basic Query
Write a query to find customers.

```sql
FROM customers | LIMIT 10
```
```

### After (Instruqt Style)
```markdown
## Your First Customer Analysis

Business Question: "Show me our top customers - I need names, tiers, and regions"

Your Challenge: Write an ES|QL query that retrieves customer details

```sql
FROM customers
| KEEP customer_name, tier, region
| SORT customer_name
```

Expected Result:
![CustomerList.png](assets/customer-list.png)

**Key Business Insights**:
- 4 Premium customers across 3 regions
- Gold tier represents 30% of customer base
- West region has highest premium concentration
```

## Metrics for Success

Our labs should achieve:

1. **Engagement**: Learner excited to solve business problem
2. **Clarity**: Zero ambiguity about what to do next
3. **Verification**: Can confirm success at every step
4. **Learning**: Understands WHY, not just HOW
5. **Completeness**: No missing steps or "figure it out yourself"
6. **Real-World**: Applicable to actual job scenarios

## Next Steps

1. Update `config/llm_prompts.yaml` with enhanced lab_generator prompts
2. Test with existing features (LOOKUP JOIN, BBQ, etc.)
3. Compare generated labs against this checklist
4. Iterate on prompt refinements
5. Build library of exemplary labs for training data