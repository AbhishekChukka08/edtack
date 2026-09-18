def get_smart_icon(label: str, sub: str, idx: int) -> str:
    """Selects an authentic tech emoji based on node purpose."""
    text = f"{label} {sub}".lower()
    if any(k in text for k in ["client", "user", "mobile", "phone", "browser", "traffic"]):
        return "📱"
    if any(k in text for k in ["balance", "lb", "proxy", "gateway", "ingress"]):
        return "⚖️"
    if any(k in text for k in ["health", "check", "heartbeat", "monitor", "ping"]):
        return "💓"
    if any(k in text for k in ["redirect", "failover", "route", "switch"]):
        return "🔀"
    if any(k in text for k in ["cache", "redis", "memcache", "memory", "ram"]):
        return "⚡"
    if any(k in text for k in ["db", "database", "sql", "postgres", "shard", "storage"]):
        return "🗄️"
    if any(k in text for k in ["queue", "kafka", "rabbit", "stream", "buffer"]):
        return "📬"
    if any(k in text for k in ["api", "server", "app", "worker", "service", "cluster"]):
        return "⚙️"
    fallbacks = ["📱", "⚙️", "🗄️", "☁️"]
    return fallbacks[idx % len(fallbacks)]


def generate_client_server_db_svg(title: str = "Client -> Server -> Database Overload") -> str:
    """Slide 1 Problem SVG: Hand-sketched Bottleneck Architecture (600px tall)."""
    svg_width = 960
    svg_height = 600

    return f'''
    <svg width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <marker id="sketch-arr-blue" markerWidth="10" markerHeight="8" refX="8" refY="4" orient="auto">
          <path d="M 1 1 L 9 4 L 1 7" fill="none" stroke="#2563EB" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />
        </marker>
        <marker id="sketch-arr-red" markerWidth="10" markerHeight="8" refX="8" refY="4" orient="auto">
          <path d="M 1 1 L 9 4 L 1 7" fill="none" stroke="#DC2626" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />
        </marker>
      </defs>

      <!-- Whiteboard Canvas with Hand-drawn Charcoal Border -->
      <rect x="12" y="12" width="936" height="576" rx="16" fill="#FFFFFF" stroke="#0F172A" stroke-width="2.5" />
      <rect x="16" y="16" width="928" height="568" rx="14" fill="none" stroke="#E2E8F0" stroke-width="1.5" stroke-dasharray="8,6" />

      <!-- Sketched Header Tag -->
      <rect x="40" y="30" width="260" height="34" rx="17" fill="#FEF9C3" stroke="#0F172A" stroke-width="2" />
      <text x="170" y="53" font-family="Kalam, cursive" font-size="16" font-weight="700" fill="#0F172A" text-anchor="middle">✏️ ARCHITECTURE SKETCH</text>

      <!-- Node 1: Clients (Smartphones & Laptops) -->
      <g transform="translate(45, 95)">
        <rect width="220" height="260" rx="14" fill="#F8FAFC" stroke="#0F172A" stroke-width="2.5" />
        <rect x="20" y="16" width="180" height="28" rx="14" fill="#E0F2FE" stroke="#0F172A" stroke-width="1.5" />
        <text x="110" y="35" font-family="Kalam, cursive" font-size="13" font-weight="700" fill="#0369A1" text-anchor="middle">① USER TRAFFIC</text>
        
        <text x="110" y="115" font-family="'Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji', sans-serif" font-size="48" text-anchor="middle">📱💻</text>
        <text x="110" y="160" font-family="Kalam, cursive" font-size="22" font-weight="700" fill="#0F172A" text-anchor="middle">100k+ Users</text>
        <text x="110" y="190" font-family="'Patrick Hand', cursive" font-size="16" fill="#475569" text-anchor="middle">Concurrent HTTP Requests</text>
        
        <rect x="18" y="212" width="184" height="26" rx="6" fill="#FEF9C3" stroke="#CA8A04" stroke-width="1.5" />
        <text x="110" y="230" font-family="'Fira Code', monospace" font-size="12" font-weight="700" fill="#854D0E" text-anchor="middle">GET /orders (100k QPS)</text>
      </g>

      <!-- Curved Arrow: Clients -> Backend -->
      <path d="M 265 220 Q 315 200 355 220" fill="none" stroke="#2563EB" stroke-width="3" stroke-dasharray="6,4" marker-end="url(#sketch-arr-blue)" />
      <rect x="280" y="175" width="65" height="24" rx="12" fill="#DBEAFE" stroke="#2563EB" stroke-width="1.5" />
      <text x="312" y="191" font-family="Kalam, cursive" font-size="12" font-weight="700" fill="#1D4ED8" text-anchor="middle">HTTP/2</text>

      <!-- Node 2: Backend App Servers -->
      <g transform="translate(365, 95)">
        <rect width="225" height="260" rx="14" fill="#F0FDF4" stroke="#0F172A" stroke-width="2.5" />
        <rect x="20" y="16" width="185" height="28" rx="14" fill="#DCFCE7" stroke="#0F172A" stroke-width="1.5" />
        <text x="112" y="35" font-family="Kalam, cursive" font-size="13" font-weight="700" fill="#15803D" text-anchor="middle">② APP SERVERS</text>
        
        <text x="112" y="115" font-family="'Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji', sans-serif" font-size="48" text-anchor="middle">⚙️☁️</text>
        <text x="112" y="160" font-family="Kalam, cursive" font-size="22" font-weight="700" fill="#0F172A" text-anchor="middle">Stateless API</text>
        <text x="112" y="190" font-family="'Patrick Hand', cursive" font-size="16" fill="#475569" text-anchor="middle">Auto-scaled Kubernetes</text>
        
        <rect x="18" y="212" width="189" height="26" rx="6" fill="#DCFCE7" stroke="#16A34A" stroke-width="1.5" />
        <text x="112" y="230" font-family="'Fira Code', monospace" font-size="12" font-weight="700" fill="#166534" text-anchor="middle">Pool: 50 Pods (Healthy)</text>
      </g>

      <!-- Curved Arrow: Backend -> Database (Overload Red) -->
      <path d="M 590 220 Q 640 200 680 220" fill="none" stroke="#DC2626" stroke-width="3.5" stroke-dasharray="6,4" marker-end="url(#sketch-arr-red)" />
      <rect x="605" y="175" width="70" height="24" rx="12" fill="#FEE2E2" stroke="#DC2626" stroke-width="1.5" />
      <text x="640" y="191" font-family="Kalam, cursive" font-size="12" font-weight="700" fill="#B91C1C" text-anchor="middle">100% I/O 💥</text>

      <!-- Node 3: Overloaded Single Database (Red Bottleneck) -->
      <g transform="translate(690, 80)">
        <rect width="225" height="290" rx="14" fill="#FEF2F2" stroke="#DC2626" stroke-width="3" />
        <rect x="15" y="16" width="195" height="28" rx="14" fill="#FEE2E2" stroke="#DC2626" stroke-width="1.5" />
        <text x="112" y="35" font-family="Kalam, cursive" font-size="12" font-weight="700" fill="#991B1B" text-anchor="middle">🔥 CRITICAL BOTTLENECK</text>
        
        <text x="112" y="115" font-family="'Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji', sans-serif" font-size="50" text-anchor="middle">🗄️🔥</text>
        <text x="112" y="160" font-family="Kalam, cursive" font-size="22" font-weight="700" fill="#991B1B" text-anchor="middle">Single Primary DB</text>
        <text x="112" y="190" font-family="'Patrick Hand', cursive" font-size="16" fill="#B91C1C" text-anchor="middle">Disk Queue Backlog ⚠️</text>
        
        <rect x="15" y="215" width="195" height="28" rx="8" fill="#DC2626" stroke="#991B1B" stroke-width="1.5" />
        <text x="112" y="233" font-family="'Fira Code', monospace" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">LOCK CONTENTION</text>
        
        <text x="112" y="268" font-family="Kalam, cursive" font-size="14" font-weight="700" fill="#B91C1C" text-anchor="middle">❌ 504 Gateway Timeout</text>
      </g>

      <!-- Handwritten Sticky Note Callout Box at Bottom -->
      <g transform="translate(45, 385)">
        <rect width="870" height="180" rx="12" fill="#FEF9C3" stroke="#0F172A" stroke-width="2" />
        <rect x="385" y="-10" width="100" height="20" rx="2" fill="rgba(226, 232, 240, 0.85)" stroke="#94A3B8" stroke-width="1" stroke-dasharray="4,3" />
        
        <text x="35" y="40" font-size="24">📌</text>
        <text x="70" y="38" font-family="Kalam, cursive" font-size="21" font-weight="700" fill="#0F172A">Why Single Databases Melt Down (The Physical Limit):</text>
        
        <text x="70" y="74" font-family="'Plus Jakarta Sans', sans-serif" font-size="15" font-weight="600" fill="#1E293B">• Disk IOPS Wall: Physical NVMe/SSD disks hit IOPS caps under sudden read/write surges.</text>
        <text x="70" y="106" font-family="'Plus Jakarta Sans', sans-serif" font-size="15" font-weight="600" fill="#1E293B">• Connection Depletion: 10,000 backend threads saturate Postgres/MySQL max_connections.</text>
        <text x="70" y="138" font-family="'Plus Jakarta Sans', sans-serif" font-size="15" font-weight="700" fill="#DC2626">• The Domino Effect: Slow DB queries block upstream API workers, triggering cascading 504 timeouts.</text>
      </g>
    </svg>
    '''


def generate_horizontal_flow_svg(nodes: list[dict]) -> str:
    """Sketched step-by-step whiteboard flow with smart icons and curved arrows (600px tall)."""
    if not nodes:
        return ""

    svg_width = 960
    svg_height = 600
    num_nodes = len(nodes)

    if num_nodes == 4:
        node_width = 185
        spacing = 42
        start_x = 42
    else:
        node_width = 240
        spacing = 75
        start_x = 55

    node_height = 260

    svg_parts = [
        f'<svg width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}" fill="none" xmlns="http://www.w3.org/2000/svg">',
        '  <defs>',
        '    <marker id="sketch-flow-arr" markerWidth="9" markerHeight="7" refX="7" refY="3.5" orient="auto">',
        '      <path d="M 1 1 L 8 3.5 L 1 6" fill="none" stroke="#2563EB" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" />',
        '    </marker>',
        '  </defs>',
        f'  <rect x="12" y="12" width="{svg_width-24}" height="{svg_height-24}" rx="16" fill="#FFFFFF" stroke="#0F172A" stroke-width="2.5" />',
        f'  <rect x="16" y="16" width="{svg_width-32}" height="{svg_height-32}" rx="14" fill="none" stroke="#E2E8F0" stroke-width="1.5" stroke-dasharray="8,6" />',
        '  <rect x="40" y="30" width="280" height="34" rx="17" fill="#EDE9FE" stroke="#0F172A" stroke-width="2" />',
        '  <text x="180" y="53" font-family="Kalam, cursive" font-size="16" font-weight="700" fill="#5B21B6" text-anchor="middle">🔄 STEP-BY-STEP DATA FLOW</text>'
    ]

    y = 85

    for idx, node in enumerate(nodes):
        x = start_x + idx * (node_width + spacing)
        label = node.get("label", f"Step {idx+1}")
        sub = node.get("sub", "")
        icon = node.get("icon") or get_smart_icon(label, sub, idx)
        step_label = node.get("step", f"STEP {idx+1}")
        status = node.get("status", "")

        # Connector Curved Arrow between nodes
        if idx < num_nodes - 1:
            arrow_x1 = x + node_width
            arrow_x2 = x + node_width + spacing
            mid_x = (arrow_x1 + arrow_x2) // 2
            svg_parts.append(
                f'  <path d="M {arrow_x1 + 4} {y + (node_height//2)} Q {mid_x} {y + (node_height//2) - 16} {arrow_x2 - 4} {y + (node_height//2)}" '
                f'fill="none" stroke="#2563EB" stroke-width="2.5" stroke-dasharray="5,3" marker-end="url(#sketch-flow-arr)" />'
            )
            svg_parts.append(
                f'  <circle cx="{mid_x}" cy="{y + (node_height//2) - 18}" r="10" fill="#DBEAFE" stroke="#2563EB" stroke-width="1.5" />'
                f'  <text x="{mid_x}" y="{y + (node_height//2) - 14}" font-family="Kalam, cursive" font-size="11" font-weight="700" fill="#1D4ED8" text-anchor="middle">{idx+1}</text>'
            )

        is_highlight = idx == 1 or node.get("highlight", False)
        border_col = "#0F172A"
        bg_col = "#FEF9C3" if is_highlight else "#F8FAFC"
        badge_bg = "#FDE047" if is_highlight else "#E2E8F0"
        badge_text = "#854D0E" if is_highlight else "#334155"

        svg_parts.append(f'  <g transform="translate({x}, {y})">')
        svg_parts.append(
            f'    <rect width="{node_width}" height="{node_height}" rx="14" fill="{bg_col}" stroke="{border_col}" stroke-width="2.5" />'
        )
        svg_parts.append(
            f'    <rect x="14" y="14" width="{node_width - 28}" height="26" rx="13" fill="{badge_bg}" stroke="#0F172A" stroke-width="1.5" />'
        )
        svg_parts.append(
            f'    <text x="{node_width//2}" y="32" font-family="Kalam, cursive" font-size="12" font-weight="700" fill="{badge_text}" text-anchor="middle">{step_label}</text>'
        )
        svg_parts.append(
            f'    <text x="{node_width//2}" y="115" font-family="\'Segoe UI Emoji\', \'Apple Color Emoji\', \'Noto Color Emoji\', sans-serif" font-size="48" text-anchor="middle">{icon}</text>'
        )
        svg_parts.append(
            f'    <text x="{node_width//2}" y="160" font-family="Kalam, cursive" font-size="20" font-weight="700" fill="#0F172A" text-anchor="middle">{label}</text>'
        )
        if sub:
            svg_parts.append(
                f'    <text x="{node_width//2}" y="190" font-family="\'Patrick Hand\', cursive" font-size="15" fill="#475569" text-anchor="middle">{sub}</text>'
            )
        if status:
            svg_parts.append(
                f'    <rect x="14" y="214" width="{node_width - 28}" height="24" rx="6" fill="#DCFCE7" stroke="#16A34A" stroke-width="1.5" />'
                f'    <text x="{node_width//2}" y="231" font-family="\'Fira Code\', monospace" font-size="11" font-weight="700" fill="#166534" text-anchor="middle">{status}</text>'
            )
        svg_parts.append('  </g>')

    # Bottom Sticky Note Callout Box
    svg_parts.append(f'''
      <g transform="translate(45, 375)">
        <rect width="870" height="190" rx="12" fill="#DCFCE7" stroke="#0F172A" stroke-width="2" />
        <rect x="385" y="-10" width="100" height="20" rx="2" fill="rgba(226, 232, 240, 0.85)" stroke="#94A3B8" stroke-width="1" stroke-dasharray="4,3" />
        
        <text x="35" y="40" font-size="24">💡</text>
        <text x="70" y="38" font-family="Kalam, cursive" font-size="21" font-weight="700" fill="#065F46">The Architectural Breakthrough:</text>
        
        <text x="70" y="74" font-family="'Plus Jakarta Sans', sans-serif" font-size="15" font-weight="600" fill="#1E293B">• Fast-Path In-Memory Lookup: Sub-millisecond reads from cache or buffer before touching disk.</text>
        <text x="70" y="106" font-family="'Plus Jakarta Sans', sans-serif" font-size="15" font-weight="600" fill="#1E293B">• Asynchronous Decoupling: Writes are logged to a durable queue and processed in background batches.</text>
        <text x="70" y="138" font-family="'Plus Jakarta Sans', sans-serif" font-size="15" font-weight="700" fill="#15803D">• Zero Downtime Failover: If any node fails, healthy replicas take over without dropping traffic.</text>
      </g>
    ''')

    svg_parts.append('</svg>')
    return "\n".join(svg_parts)


def generate_comparison_table_svg() -> str:
    """Hand-sketched side-by-side comparison notebook sheet (680px tall)."""
    svg_width = 960
    svg_height = 680

    return f'''
    <svg width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="12" y="12" width="936" height="656" rx="16" fill="#FFFFFF" stroke="#0F172A" stroke-width="2.5" />
      <rect x="16" y="16" width="928" height="648" rx="14" fill="none" stroke="#E2E8F0" stroke-width="1.5" stroke-dasharray="8,6" />

      <!-- Section Header -->
      <rect x="40" y="32" width="280" height="34" rx="17" fill="#FEF9C3" stroke="#0F172A" stroke-width="2" />
      <text x="180" y="55" font-family="Kalam, cursive" font-size="16" font-weight="700" fill="#0F172A" text-anchor="middle">⚖️ HEAD-TO-HEAD TRADE-OFFS</text>

      <!-- Column 1: Option A (e.g. Token Bucket / Kafka) -->
      <g transform="translate(45, 85)">
        <rect width="415" height="420" rx="14" fill="#EFF6FF" stroke="#0F172A" stroke-width="2.5" />
        <rect x="160" y="-10" width="95" height="20" rx="2" fill="rgba(226, 232, 240, 0.85)" stroke="#94A3B8" stroke-width="1" stroke-dasharray="4,3" />
        
        <text x="207" y="50" font-family="Kalam, cursive" font-size="26" font-weight="700" fill="#1D4ED8" text-anchor="middle">⚡ Pattern A: Log / Token</text>
        <text x="207" y="78" font-family="'Patrick Hand', cursive" font-size="18" fill="#3B82F6" text-anchor="middle">Optimized for Burst &amp; High Throughput</text>

        <g transform="translate(25, 105)">
          <rect width="365" height="52" rx="8" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.5" />
          <text x="20" y="32" font-family="'Plus Jakarta Sans', sans-serif" font-size="15" font-weight="700" fill="#0F172A">Traffic: <tspan fill="#2563EB">Allows Controlled Bursts</tspan></text>
        </g>
        <g transform="translate(25, 170)">
          <rect width="365" height="52" rx="8" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.5" />
          <text x="20" y="32" font-family="'Plus Jakarta Sans', sans-serif" font-size="15" font-weight="700" fill="#0F172A">Storage: <tspan fill="#2563EB">In-Memory Atomic Counter</tspan></text>
        </g>
        <g transform="translate(25, 235)">
          <rect width="365" height="52" rx="8" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.5" />
          <text x="20" y="32" font-family="'Plus Jakarta Sans', sans-serif" font-size="15" font-weight="700" fill="#0F172A">Complexity: <tspan fill="#15803D">O(1) Ultra-fast Math</tspan></text>
        </g>
        <g transform="translate(25, 300)">
          <rect width="365" height="52" rx="8" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.5" />
          <text x="20" y="32" font-family="'Plus Jakarta Sans', sans-serif" font-size="15" font-weight="700" fill="#0F172A">Throughput: <tspan fill="#15803D">1,000,000+ QPS</tspan></text>
        </g>
        <g transform="translate(25, 365)">
          <rect width="365" height="40" rx="8" fill="#DBEAFE" stroke="#2563EB" stroke-width="1.5" />
          <text x="182" y="25" font-family="Kalam, cursive" font-size="15" font-weight="700" fill="#1D4ED8" text-anchor="middle">🎯 Best for User APIs &amp; Gateways</text>
        </g>
      </g>

      <!-- Column 2: Option B (e.g. Leaky Bucket / RabbitMQ) -->
      <g transform="translate(500, 85)">
        <rect width="415" height="420" rx="14" fill="#F0FDF4" stroke="#0F172A" stroke-width="2.5" />
        <rect x="160" y="-10" width="95" height="20" rx="2" fill="rgba(226, 232, 240, 0.85)" stroke="#94A3B8" stroke-width="1" stroke-dasharray="4,3" />
        
        <text x="207" y="50" font-family="Kalam, cursive" font-size="26" font-weight="700" fill="#166534" text-anchor="middle">🪣 Pattern B: Queue / Leaky</text>
        <text x="207" y="78" font-family="'Patrick Hand', cursive" font-size="18" fill="#15803D" text-anchor="middle">Strict Constant Output Rate</text>

        <g transform="translate(25, 105)">
          <rect width="365" height="52" rx="8" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.5" />
          <text x="20" y="32" font-family="'Plus Jakarta Sans', sans-serif" font-size="15" font-weight="700" fill="#0F172A">Traffic: <tspan fill="#15803D">Smooth Constant Outflow</tspan></text>
        </g>
        <g transform="translate(25, 170)">
          <rect width="365" height="52" rx="8" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.5" />
          <text x="20" y="32" font-family="'Plus Jakarta Sans', sans-serif" font-size="15" font-weight="700" fill="#0F172A">Storage: <tspan fill="#15803D">FIFO Queue Buffer</tspan></text>
        </g>
        <g transform="translate(25, 235)">
          <rect width="365" height="52" rx="8" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.5" />
          <text x="20" y="32" font-family="'Plus Jakarta Sans', sans-serif" font-size="15" font-weight="700" fill="#0F172A">Complexity: <tspan fill="#D97706">Queue memory allocation</tspan></text>
        </g>
        <g transform="translate(25, 300)">
          <rect width="365" height="52" rx="8" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.5" />
          <text x="20" y="32" font-family="'Plus Jakarta Sans', sans-serif" font-size="15" font-weight="700" fill="#0F172A">Throughput: <tspan fill="#D97706">Bounded by Queue Size</tspan></text>
        </g>
        <g transform="translate(25, 365)">
          <rect width="365" height="40" rx="8" fill="#DCFCE7" stroke="#16A34A" stroke-width="1.5" />
          <text x="182" y="25" font-family="Kalam, cursive" font-size="15" font-weight="700" fill="#166534" text-anchor="middle">🎯 Best for Legacy DB Write Throttling</text>
        </g>
      </g>

      <!-- Bottom Takeaway -->
      <g transform="translate(45, 530)">
        <rect width="870" height="115" rx="12" fill="#FEF9C3" stroke="#0F172A" stroke-width="2" />
        <rect x="385" y="-10" width="100" height="20" rx="2" fill="rgba(226, 232, 240, 0.85)" stroke="#94A3B8" stroke-width="1" stroke-dasharray="4,3" />
        
        <text x="35" y="45" font-size="26">📌</text>
        <text x="75" y="42" font-family="Kalam, cursive" font-size="22" font-weight="700" fill="#0F172A">The 10-Second Interview Rule of Thumb:</text>
        <text x="75" y="75" font-family="'Plus Jakarta Sans', sans-serif" font-size="16" font-weight="600" fill="#1E293B">Need to tolerate traffic bursts without dropping requests? Pick Token Bucket. Need to protect a fragile legacy database from melting down under any spike? Pick Leaky Bucket.</text>
      </g>
    </svg>
    '''

