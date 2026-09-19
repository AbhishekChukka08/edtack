import re

def clean_mermaid_code(raw_code: str) -> str:
    """Cleans and sanitizes raw LLM output into valid, wide-aspect Mermaid code."""
    if not raw_code:
        return ""
    
    # Remove markdown codeblocks (```mermaid ... ```)
    code = re.sub(r'```(?:mermaid)?', '', raw_code, flags=re.IGNORECASE).strip()
    
    lines = [line.strip() for line in code.split('\n') if line.strip()]
    if not lines:
        return ""
    
    first_line = lines[0]
    if not (first_line.startswith("graph ") or first_line.startswith("flowchart ") or first_line.startswith("sequenceDiagram")):
        lines.insert(0, "graph TD")
        first_line = lines[0]
        
    # If a linear pipeline has many sequential nodes in graph TD, convert to graph LR for wide readability
    if "graph TD" in first_line:
        arrow_count = code.count("-->")
        diamond_count = code.count("{")
        if arrow_count >= 5 and diamond_count <= 2:
            lines[0] = lines[0].replace("graph TD", "graph LR")
            
    return "\n".join(lines)


FALLBACK_MERMAID_LIBRARY = {
    "transformer-attention-qkv": {
        "slide_1": {
            "mermaid": """graph TD
  Input["🔤 Input Tokens: ['The', 'robot', 'saw', 'the', 'cat']"] --> Embed["Vector Embeddings (d_model = 4096)"]
  Embed --> WQ["Query Projection (W_Q)"]
  Embed --> WK["Key Projection (W_K)"]
  Embed --> WV["Value Projection (W_V)"]
  WQ --> Dot["(Q · K^T) / sqrt(d_k)"]
  WK --> Dot
  Dot --> Softmax["Softmax (Attention Probabilities)"]
  Softmax --> Out["Contextual Output = Attention · V"]
  WV --> Out
  
  style Input fill:#DBEAFE,stroke:#0F172A,stroke-width:2px,color:#0F172A
  style Embed fill:#FEF9C3,stroke:#0F172A,stroke-width:2px,color:#0F172A
  style WQ fill:#F8FAFC,stroke:#0F172A,stroke-width:1.5px,color:#0F172A
  style WK fill:#F8FAFC,stroke:#0F172A,stroke-width:1.5px,color:#0F172A
  style WV fill:#F8FAFC,stroke:#0F172A,stroke-width:1.5px,color:#0F172A
  style Softmax fill:#EDE9FE,stroke:#7C3AED,stroke-width:2px,color:#5B21B6
  style Out fill:#DCFCE7,stroke:#16A34A,stroke-width:2.5px,color:#166534""",
            "micro_infographic": {
                "title": "🧠 The Q, K, V Mental Model",
                "table": {
                    "headers": ["Component", "Mathematical Role", "Real-World Analogy", "Dimensions"],
                    "rows": [
                        ["Query (Q)", "What token seeks", "Search bar query", "<span class='info-badge badge-blue'>[seq, d_k]</span>"],
                        ["Key (K)", "What token contains", "YouTube video tags", "<span class='info-badge badge-yellow'>[seq, d_k]</span>"],
                        ["Value (V)", "Information payload", "Actual video content", "<span class='info-badge badge-green'>[seq, d_v]</span>"]
                    ]
                },
                "notes": "💡 Without Q, K, V projections, tokens would only match identical words. Projections allow words like 'king' and 'queen' to attend to each other across semantic space."
            }
        },
        "slide_2": {
            "mermaid": """graph LR
  Q["Token: 'bank' (Query)"] --> Dot["Dot Product (Q · K)"]
  K1["Key: 'river'"] -->|Score: 0.92| Dot
  K2["Key: 'money'"] -->|Score: 0.05| Dot
  Dot --> Softmax["Softmax Weights"]
  Softmax --> WeightedSum["Weighted Value Sum"]
  V1["Value: 'river water'"] --> WeightedSum
  WeightedSum --> Result["Context Vector: Geographical Bank"]
  
  style Q fill:#DBEAFE,stroke:#0F172A,stroke-width:2px,color:#0F172A
  style Dot fill:#FEF9C3,stroke:#0F172A,stroke-width:2px,color:#0F172A
  style Softmax fill:#EDE9FE,stroke:#0F172A,stroke-width:2px,color:#0F172A
  style WeightedSum fill:#DCFCE7,stroke:#16A34A,stroke-width:2.5px,color:#166534
  style Result fill:#DCFCE7,stroke:#16A34A,stroke-width:2.5px,color:#166534""",
            "micro_infographic": {
                "title": "⚡ 4-Step Self-Attention Calculation",
                "table": {
                    "headers": ["Step", "Formula", "Operation", "Hardware Speed"],
                    "rows": [
                        ["1. Compatibility", "S = Q · K^T", "Matrix multiplication (GEMM)", "<span class='info-badge badge-green'>Tensor Core O(N^2)</span>"],
                        ["2. Scale", "S / sqrt(d_k)", "Prevents softmax saturation", "<span class='info-badge badge-blue'>Element-wise</span>"],
                        ["3. Probability", "A = Softmax(S)", "Row-wise normalization (sum=1)", "<span class='info-badge badge-yellow'>Softmax kernel</span>"],
                        ["4. Context Mix", "Output = A · V", "Weighted semantic blend", "<span class='info-badge badge-green'>Tensor Core</span>"]
                    ]
                },
                "notes": "📌 Multi-head attention repeats this process 32 to 128 times in parallel, allowing the model to simultaneously attend to syntax, grammar, and long-range facts."
            }
        }
    },
    "modern-rag-pipeline": {
        "slide_1": {
            "mermaid": """graph TD
  User["👤 User Question"] --> DirectLLM["🤖 Pure LLM (Static Pre-training)"]
  DirectLLM --> Hallucination["🚨 Hallucination / Outdated Data (Knowledge Cutoff)"]
  
  User --> HybridRAG["⚡ RAG Pipeline (Retrieve + Augment)"]
  HybridRAG --> Grounded["✅ Grounded Answer with Exact Citations"]
  
  style User fill:#DBEAFE,stroke:#0F172A,stroke-width:2px,color:#0F172A
  style DirectLLM fill:#FEE2E2,stroke:#0F172A,stroke-width:2px,color:#991B1B
  style Hallucination fill:#FEF2F2,stroke:#DC2626,stroke-width:2px,color:#991B1B
  style HybridRAG fill:#DCFCE7,stroke:#0F172A,stroke-width:2px,color:#166534
  style Grounded fill:#DCFCE7,stroke:#16A34A,stroke-width:2.5px,color:#166534""",
            "micro_infographic": {
                "title": "📊 Why RAG Beats Pure LLMs",
                "table": {
                    "headers": ["Feature", "Direct LLM Prompting", "RAG Pipeline", "Advantage"],
                    "rows": [
                        ["Knowledge Cutoff", "Frozen at training date", "Real-time (live databases)", "<span class='info-badge badge-green'>Always Current</span>"],
                        ["Hallucination Rate", "15% - 30% on niche facts", "< 2% with citation grounding", "<span class='info-badge badge-green'>Audit-Ready</span>"],
                        ["Private Enterprise Data", "Requires costly fine-tuning", "Instant vector search indexing", "<span class='info-badge badge-green'>Zero Retraining</span>"]
                    ]
                }
            }
        },
        "slide_2": {
            "mermaid": """graph LR
  Doc["📄 Raw Docs"] --> Chunk["✂️ Chunking (512 tokens)"]
  Chunk --> Embed["📐 Embedding Model"]
  Embed --> VDB[("🗄️ Vector Database")]
  
  Query["🔍 User Query"] --> QEmbed["Embedding"]
  QEmbed --> Search["Cosine Similarity"]
  VDB --> Search
  Search --> TopK["Top-K Chunks"]
  TopK --> Synth["🤖 LLM Context Synthesis"]
  Query --> Synth
  Synth --> Answer["💬 Grounded Response"]
  
  style Doc fill:#DBEAFE,stroke:#0F172A,stroke-width:2px,color:#0F172A
  style VDB fill:#FEF9C3,stroke:#0F172A,stroke-width:2px,color:#0F172A
  style Query fill:#DBEAFE,stroke:#0F172A,stroke-width:2px,color:#0F172A
  style TopK fill:#EDE9FE,stroke:#0F172A,stroke-width:2px,color:#5B21B6
  style Synth fill:#DCFCE7,stroke:#0F172A,stroke-width:2px,color:#166534
  style Answer fill:#DCFCE7,stroke:#16A34A,stroke-width:2.5px,color:#166534""",
            "micro_infographic": {
                "title": "⚡ RAG Pipeline SLA Targets",
                "table": {
                    "headers": ["Stage", "Typical Tool", "Latency SLA", "Bottleneck"],
                    "rows": [
                        ["Vector Retrieval", "Pinecone / Qdrant / Milvus", "5ms - 25ms", "Index size / HNSW graph"],
                        ["Reranking", "Cohere / BGE Cross-Encoder", "40ms - 80ms", "Model FLOPs per chunk"],
                        ["LLM Generation", "Gemini / Claude / GPT-4", "400ms - 1200ms", "Time to First Token (TTFT)"]
                    ]
                }
            }
        }
    },
    "database-indexing-b-trees": {
        "slide_1": {
            "mermaid": """graph TD
  Query["🔍 SELECT * FROM users WHERE id = 42"] --> Table[("🗄️ Un-indexed Table (1,000,000 Rows)")]
  Table --> Row1["Scan Row 1 ❌"]
  Row1 --> Row2["Scan Row 2 ❌"]
  Row2 -. Sequential I/O .-> RowN["Scan Row 42 ✅"]
  RowN --> Pen["💥 Massive Disk Latency (O(N) Full Table Scan)"]
  
  style Query fill:#DBEAFE,stroke:#0F172A,stroke-width:2px,color:#0F172A
  style Table fill:#FEE2E2,stroke:#0F172A,stroke-width:2px,color:#0F172A
  style Row1 fill:#F8FAFC,stroke:#0F172A,stroke-width:1.5px,color:#475569
  style Row2 fill:#F8FAFC,stroke:#0F172A,stroke-width:1.5px,color:#475569
  style RowN fill:#DCFCE7,stroke:#0F172A,stroke-width:2px,color:#166534
  style Pen fill:#FEF2F2,stroke:#DC2626,stroke-width:2px,color:#991B1B""",
            "micro_infographic": {
                "title": "📊 The Cost of Missing Indexes",
                "table": {
                    "headers": ["Scan Method", "10,000 Rows", "1,000,000 Rows", "Time Complexity"],
                    "rows": [
                        ["Full Table Scan", "10,000 reads (12ms)", "1,000,000 reads (1.2s)", "<span class='info-badge badge-red'>O(N) Slow</span>"],
                        ["B-Tree Index Scan", "3 page reads (0.4ms)", "3 page reads (0.4ms)", "<span class='info-badge badge-green'>O(log N) Fast</span>"]
                    ]
                },
                "notes": "💡 Without an index, the database engine must load every physical data page from SSD storage into memory."
            }
        },
        "slide_2": {
            "mermaid": """graph TD
  Query["🔍 Key: 33"] --> Root["🌲 Root Page: [20 | 50]"]
  Root -->|Key < 20| L1["📄 Page 1: [5, 12, 18]"]
  Root -->|20 <= Key < 50| L2["📄 Page 2: [25, 33, 47]"]
  Root -->|Key >= 50| L3["📄 Page 3: [55, 68, 90]"]
  L2 --> Match["🎯 Pointer -> Row on Disk (33)"]
  L1 -. Doubly-Linked Leaf List .-> L2
  L2 -. Doubly-Linked Leaf List .-> L3
  
  style Query fill:#DBEAFE,stroke:#0F172A,stroke-width:2px,color:#0F172A
  style Root fill:#FEF9C3,stroke:#0F172A,stroke-width:2px,color:#0F172A
  style L1 fill:#F8FAFC,stroke:#0F172A,stroke-width:2px,color:#0F172A
  style L2 fill:#DCFCE7,stroke:#0F172A,stroke-width:2.5px,color:#166534
  style L3 fill:#F8FAFC,stroke:#0F172A,stroke-width:2px,color:#0F172A
  style Match fill:#DCFCE7,stroke:#16A34A,stroke-width:2px,color:#166534""",
            "micro_infographic": {
                "title": "⚡ B-Tree Search Efficiency",
                "table": {
                    "headers": ["Index Level", "Keys Checked", "IOPS Consumed", "Status"],
                    "rows": [
                        ["Level 1 (Root)", "Checked [20, 50] (RAM)", "0 (In-Memory Buffer)", "<span class='info-badge badge-blue'>Cached</span>"],
                        ["Level 2 (Leaf)", "Found Key 33 (Page 2)", "1 Page Read (4KB)", "<span class='info-badge badge-green'>O(1) Leaf Hit</span>"],
                        ["Leaf Linked List", "Scan 33 to 47 for ranges", "Sequential Pre-fetch", "<span class='info-badge badge-yellow'>Instant Range</span>"]
                    ]
                },
                "notes": "📌 Leaf nodes are interconnected via bidirectional pointers, turning expensive range queries (`BETWEEN A AND B`) into linear traversals."
            }
        }
    },
    "redis-cache-aside": {
        "slide_1": {
            "mermaid": """graph TD
  Client["📱 10,000 App Threads"] -->|Direct Queries| DB[("🗄️ Single SQL Database")]
  DB --> Lock["🔒 Connection Pool Exhaustion"]
  Lock --> Timeout["💥 504 Gateway Timeout (Database Meltdown)"]
  
  style Client fill:#DBEAFE,stroke:#0F172A,stroke-width:2px,color:#0F172A
  style DB fill:#FEE2E2,stroke:#0F172A,stroke-width:2px,color:#991B1B
  style Lock fill:#FEF2F2,stroke:#DC2626,stroke-width:2px,color:#991B1B
  style Timeout fill:#DC2626,stroke:#7F1D1D,stroke-width:2px,color:#FFFFFF""",
            "micro_infographic": {
                "title": "⚠️ The Read Bottleneck",
                "table": {
                    "headers": ["Metric", "Direct Database", "With Cache-Aside", "Improvement"],
                    "rows": [
                        ["Read Latency", "15ms - 80ms", "0.5ms - 2ms", "<span class='info-badge badge-green'>40x Faster</span>"],
                        ["Max Throughput", "5,000 QPS", "150,000+ QPS", "<span class='info-badge badge-green'>30x Scale</span>"]
                    ]
                }
            }
        },
        "slide_2": {
            "mermaid": """graph TD
  App["📱 App Service"] --> Cache{"⚡ Redis Cache<br/>(Key Exists?)"}
  Cache -->|🟢 HIT 95%| ReturnFast["🚀 Return Cached Data (0.8ms)"]
  Cache -->|🔴 MISS 5%| ReadDB[("🗄️ Read Primary Postgres DB")]
  ReadDB --> Populate["⚡ Set Key in Redis (TTL: 3600s)"]
  Populate --> ReturnFast
  
  style App fill:#DBEAFE,stroke:#0F172A,stroke-width:2px,color:#0F172A
  style Cache fill:#FEF9C3,stroke:#0F172A,stroke-width:2px,color:#0F172A
  style ReturnFast fill:#DCFCE7,stroke:#16A34A,stroke-width:2.5px,color:#166534
  style ReadDB fill:#FEE2E2,stroke:#0F172A,stroke-width:2px,color:#991B1B
  style Populate fill:#EDE9FE,stroke:#0F172A,stroke-width:2px,color:#5B21B6""",
            "micro_infographic": {
                "title": "💡 Cache-Aside Lifecycle Guarantees",
                "table": {
                    "headers": ["Step", "Action", "Failure Scenario", "Mitigation"],
                    "rows": [
                        ["Cache Miss", "Read from SQL DB", "DB down", "Circuit Breaker fallback"],
                        ["Cache Update", "SET key value EX 3600", "Redis down", "Graceful degrade to DB"],
                        ["Write Operation", "Write DB -> Invalidate Cache", "Stale reads", "Always set short TTLs"]
                    ]
                }
            }
        }
    },
    "single-point-of-failure-ha": {
        "slide_1": {
            "mermaid": """graph TD
  Client["📱 50,000 Users"] --> LB["⚖️ Single Load Balancer"]
  LB --> API["⚙️ App Cluster"]
  LB --> Failure["💥 Hardware Switch Fails (SPOF)"]
  Failure --> Outage["🚨 100% Complete System Outage"]
  
  style Client fill:#DBEAFE,stroke:#0F172A,stroke-width:2px,color:#0F172A
  style LB fill:#FEE2E2,stroke:#DC2626,stroke-width:2.5px,color:#991B1B
  style API fill:#F8FAFC,stroke:#0F172A,stroke-width:2px,color:#0F172A
  style Failure fill:#DC2626,stroke:#7F1D1D,stroke-width:2px,color:#FFFFFF
  style Outage fill:#FEF2F2,stroke:#DC2626,stroke-width:2px,color:#991B1B""",
            "micro_infographic": {
                "title": "⚠️ Identifying Single Points of Failure",
                "table": {
                    "headers": ["Architecture Tier", "Common SPOF", "Blast Radius", "Solution"],
                    "rows": [
                        ["Ingress Tier", "Single Load Balancer", "100% Traffic Drop", "VRRP Active-Passive Pair"],
                        ["Database Tier", "Single Primary Node", "Zero Writes Allowed", "Auto-failover Read Replica"],
                        ["DNS Tier", "Single Nameserver", "Domain Unreachable", "Anycast Multi-Cloud DNS"]
                    ]
                }
            }
        },
        "slide_2": {
            "mermaid": """graph TD
  Users["📱 Global Users"] --> VIP["🌐 Virtual IP (Floating Anycast)"]
  VIP --> ActiveLB["⚖️ Primary LB (ACTIVE)"]
  ActiveLB -. Heartbeat VRRP .-> PassiveLB["⚖️ Standby LB (HOT PASSIVE)"]
  ActiveLB --> App1["⚙️ App Server Pod 1"]
  ActiveLB --> App2["⚙️ App Server Pod 2"]
  PassiveLB -. Auto-Promotes on Heartbeat Loss .-> App1
  
  style Users fill:#DBEAFE,stroke:#0F172A,stroke-width:2px,color:#0F172A
  style VIP fill:#FEF9C3,stroke:#0F172A,stroke-width:2px,color:#0F172A
  style ActiveLB fill:#DCFCE7,stroke:#16A34A,stroke-width:2.5px,color:#166534
  style PassiveLB fill:#FEE2E2,stroke:#0F172A,stroke-width:2px,color:#991B1B
  style App1 fill:#EDE9FE,stroke:#0F172A,stroke-width:2px,color:#5B21B6
  style App2 fill:#EDE9FE,stroke:#0F172A,stroke-width:2px,color:#5B21B6""",
            "micro_infographic": {
                "title": "🛡️ High Availability Failover Flow",
                "table": {
                    "headers": ["State", "Primary Node", "Standby Node", "User Impact"],
                    "rows": [
                        ["Normal Operations", "Handling 100% Traffic", "Listening to Heartbeat (Idle)", "<span class='info-badge badge-green'>0ms Delay</span>"],
                        ["Primary Crash Detected", "Dead (Heartbeat Lost)", "Acquires Virtual IP (Promoted)", "<span class='info-badge badge-yellow'>Sub-3s Failover</span>"],
                        ["Recovery Complete", "Re-enters as Standby", "Now Active Primary", "<span class='info-badge badge-green'>100% Uptime</span>"]
                    ]
                }
            }
        }
    }
}

def get_mermaid_for_slide(topic_id: str, slide_number: int) -> dict:
    """Returns topic-specific mermaid code and micro-infographic block if configured."""
    topic_data = FALLBACK_MERMAID_LIBRARY.get(topic_id)
    if not topic_data:
        # Generic high-availability fallback
        if slide_number == 1:
            return {
                "mermaid": """graph TD
  Client["📱 Client Requests (100k QPS)"] --> Gate["🚪 Single Gateway API"]
  Gate --> DB[("🗄️ Overloaded Storage Primary")]
  DB --> Fail["💥 Single Point of Bottleneck"]
  
  style Client fill:#DBEAFE,stroke:#0F172A,stroke-width:2px,color:#0F172A
  style Gate fill:#FEF9C3,stroke:#0F172A,stroke-width:2px,color:#0F172A
  style DB fill:#FEE2E2,stroke:#DC2626,stroke-width:2px,color:#991B1B
  style Fail fill:#FEF2F2,stroke:#DC2626,stroke-width:2px,color:#991B1B""",
                "micro_infographic": None
            }
        elif slide_number == 2:
            return {
                "mermaid": """graph LR
  Client["📱 Client"] --> LB["⚖️ Load Balancer"]
  LB --> Node1["⚙️ Cluster Node 1"]
  LB --> Node2["⚙️ Cluster Node 2"]
  Node1 --> Cache["⚡ Distributed Cache"]
  Node2 --> Cache
  Cache -. Sync .-> DB[("🗄️ Database Replicas")]
  
  style Client fill:#DBEAFE,stroke:#0F172A,stroke-width:2px,color:#0F172A
  style LB fill:#FEF9C3,stroke:#0F172A,stroke-width:2px,color:#0F172A
  style Node1 fill:#EDE9FE,stroke:#0F172A,stroke-width:2px,color:#0F172A
  style Node2 fill:#EDE9FE,stroke:#0F172A,stroke-width:2px,color:#0F172A
  style Cache fill:#DCFCE7,stroke:#16A34A,stroke-width:2px,color:#166534
  style DB fill:#F8FAFC,stroke:#0F172A,stroke-width:2px,color:#0F172A""",
                "micro_infographic": None
            }
        return {}

    slide_key = f"slide_{slide_number}"
    return topic_data.get(slide_key, {})
