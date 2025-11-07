# Pack2Skill Architecture Design

**Version:** 2.0 (Next Generation)
**Date:** January 2025
**Status:** Design Phase

## Executive Summary

This document outlines the architectural redesign of pack2skill to incorporate advanced features from [pack](https://github.com/GeneralUserModels/pack) while maintaining our unique value proposition: generating production-ready Claude Skills.

**Key Goals:**
1. Plugin-based VLM backend system (support BLIP, Gemini, Qwen, Claude)
2. Intelligent burst detection for better event grouping
3. Modular output generation (Skills, Manuals, Documentation)
4. Backward compatibility with v0.1.0
5. Scalable architecture for team collaboration
6. Extensible for future features

---

## Current Architecture (v0.1.0)

### Overview

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Record    │─────▶│   Analyze    │─────▶│  Generate   │
│  Workflows  │      │   Workflows  │      │   Skills    │
└─────────────┘      └──────────────┘      └─────────────┘
      │                     │                      │
      │                     │                      │
   FFmpeg              BLIP + OCR           SKILL.md
   Pynput              OpenCV              REFERENCE.md
```

### Components

1. **Recorder** (pack2skill/core/recorder/)
   - `screen_recorder.py` - FFmpeg video capture
   - `event_recorder.py` - Pynput keyboard/mouse events
   - `workflow_recorder.py` - Orchestrator

2. **Analyzer** (pack2skill/core/analyzer/)
   - `workflow_analyzer.py` - Frame extraction + VLM captioning
   - Uses: BLIP (Hugging Face), Tesseract OCR, OpenCV

3. **Generator** (pack2skill/core/generator/)
   - `skill_generator.py` - Orchestrator
   - `skill_formatter.py` - Claude Skills format
   - Outputs: SKILL.md, REFERENCE.md, scripts/

4. **Quality** (pack2skill/quality/)
   - `confidence.py` - Multi-factor scoring
   - `description.py` - Description optimization
   - `robustness.py` - Issue detection

5. **CLI** (pack2skill/cli/)
   - `main.py` - Click-based commands

### Limitations

❌ Single VLM backend (BLIP only)
❌ No burst detection (simple scene change detection)
❌ No vLLM support
❌ Fixed output format (Skills only)
❌ No plugin system
❌ Limited model choices

---

## Proposed Architecture (v2.0)

### High-Level Design

```
┌──────────────────────────────────────────────────────────┐
│                     Pack2Skill v2.0                      │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────┐   ┌──────────────┐   ┌─────────────┐ │
│  │   Capture   │──▶│   Analyze    │──▶│   Output    │ │
│  │   Module    │   │   Module     │   │   Module    │ │
│  └─────────────┘   └──────────────┘   └─────────────┘ │
│         │                  │                   │        │
│         ▼                  ▼                   ▼        │
│  ┌─────────────┐   ┌──────────────┐   ┌─────────────┐ │
│  │  Recording  │   │  VLM Backend │   │   Skills    │ │
│  │   Backends  │   │   Plugins    │   │  Generators │ │
│  └─────────────┘   └──────────────┘   └─────────────┘ │
│         │                  │                   │        │
│  • Video (FFmpeg)   • BLIP (local)      • Claude Skills│
│  • Screenshots      • Gemini (API)      • Manuals      │
│  • Hybrid           • Qwen (vLLM)       • Docs         │
│                     • Claude (API)                     │
│                                                          │
├──────────────────────────────────────────────────────────┤
│              Cross-Cutting Concerns                      │
├──────────────────────────────────────────────────────────┤
│  • Event Processing (Burst Detection)                    │
│  • Quality Assessment (Confidence Scoring)               │
│  • Storage & Caching                                     │
│  • Configuration Management                              │
│  • Team Collaboration (Git, Distribution)                │
└──────────────────────────────────────────────────────────┘
```

### Core Principles

1. **Plugin Architecture** - Extensible backends for capture, analysis, output
2. **Separation of Concerns** - Clear module boundaries
3. **Configuration over Code** - User-selectable backends
4. **Backward Compatibility** - v0.1.0 workflows still work
5. **Performance First** - Async, caching, efficient processing
6. **Test-Driven** - Comprehensive test coverage

---

## Module Design

### 1. Capture Module

**Purpose:** Record user activity through multiple strategies

#### Architecture

```python
# pack2skill/core/capture/base.py

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pathlib import Path

class CaptureBackend(ABC):
    """Base class for capture backends"""

    @abstractmethod
    def start_capture(self, config: Dict[str, Any]) -> str:
        """Start capturing, return session_id"""
        pass

    @abstractmethod
    def stop_capture(self) -> Dict[str, Any]:
        """Stop and return capture data"""
        pass

    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return capabilities: ['video', 'screenshots', 'events', ...]"""
        pass

class CaptureManager:
    """Manages capture backends and orchestrates recording"""

    def __init__(self):
        self._backends: Dict[str, CaptureBackend] = {}
        self._active_backend: CaptureBackend | None = None

    def register_backend(self, name: str, backend: CaptureBackend):
        """Register a capture backend"""
        self._backends[name] = backend

    def start_recording(
        self,
        backend: str = "video",
        config: Dict[str, Any] | None = None
    ) -> str:
        """Start recording with specified backend"""
        pass
```

#### Backends

**1. Video Backend** (Current - FFmpeg)
```python
# pack2skill/core/capture/video_backend.py

class VideoBackend(CaptureBackend):
    """Continuous video recording with FFmpeg"""

    capabilities = ["video", "events", "audio"]

    pros:
        - Smooth playback
        - Audio capture
        - Standard format

    cons:
        - Large file sizes
        - Less efficient for long sessions
        - Harder to seek to specific events
```

**2. Screenshot Backend** (New - from pack)
```python
# pack2skill/core/capture/screenshot_backend.py

class ScreenshotBackend(CaptureBackend):
    """Periodic screenshot capture with cyclic buffer"""

    capabilities = ["screenshots", "events"]

    features:
        - Configurable frame rate
        - Cyclic buffer (memory efficient)
        - Easy frame access
        - Faster random access

    pros:
        - Memory efficient
        - Easy to process individual frames
        - Better for long sessions

    cons:
        - No smooth video
        - May miss rapid changes
        - No audio
```

**3. Hybrid Backend** (New - best of both)
```python
# pack2skill/core/capture/hybrid_backend.py

class HybridBackend(CaptureBackend):
    """
    Screenshots for normal activity + video bursts for rapid changes
    """

    capabilities = ["screenshots", "video", "events"]

    strategy:
        - Default: Screenshots at 1-2 fps
        - Detect rapid activity → switch to video
        - After burst ends → back to screenshots

    pros:
        - Efficient storage
        - Captures rapid sequences
        - Best for variable activity

    cons:
        - More complex
        - Requires burst detection
```

#### Decision: Default Backend

**Choice:** Start with **Video Backend** (backward compatible), add **Screenshot Backend** in v2.1

**Rationale:**
- Maintains v0.1.0 compatibility
- Users already familiar with video workflow
- Screenshot backend can be added without breaking changes
- Hybrid backend deferred to v2.2 (added complexity)

---

### 2. Analysis Module

**Purpose:** Extract meaningful information from captured data

#### Architecture

```python
# pack2skill/core/analysis/base.py

from abc import ABC, abstractmethod
from typing import Dict, Any, List

class VLMBackend(ABC):
    """Base class for Vision-Language Model backends"""

    @abstractmethod
    def analyze_frame(
        self,
        frame: np.ndarray,
        context: Dict[str, Any] | None = None
    ) -> Dict[str, Any]:
        """Analyze a single frame, return caption and metadata"""
        pass

    @abstractmethod
    def analyze_sequence(
        self,
        frames: List[np.ndarray],
        events: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Analyze a sequence of frames with events"""
        pass

    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return capabilities: ['captioning', 'ocr', 'object_detection', ...]"""
        pass

class AnalysisManager:
    """Manages VLM backends and orchestrates analysis"""

    def __init__(self):
        self._vlm_backends: Dict[str, VLMBackend] = {}
        self._event_processor: EventProcessor | None = None

    def register_vlm_backend(self, name: str, backend: VLMBackend):
        """Register a VLM backend"""
        self._vlm_backends[name] = backend

    def analyze_workflow(
        self,
        capture_data: Dict[str, Any],
        vlm_backend: str = "gemini",
        use_burst_detection: bool = True
    ) -> Dict[str, Any]:
        """Analyze captured workflow"""
        pass
```

#### VLM Backends

**1. BLIP Backend** (Current - Local)
```python
# pack2skill/core/analysis/vlm/blip_backend.py

class BLIPBackend(VLMBackend):
    """Local BLIP model via Hugging Face"""

    model: Salesforce/blip-image-captioning-large

    pros:
        - Works offline
        - No API costs
        - Privacy (local only)
        - Fast for single frames

    cons:
        - Limited capabilities
        - Older technology
        - No multimodal reasoning
        - Less accurate than newer models

    use_cases:
        - Offline environments
        - Privacy-sensitive workflows
        - Budget-constrained users
```

**2. Gemini Backend** (New - API)
```python
# pack2skill/core/analysis/vlm/gemini_backend.py

class GeminiBackend(VLMBackend):
    """Google Gemini 2.5 API"""

    models:
        - gemini-2.5-flash (fast, cheap)
        - gemini-2.5-pro (powerful, expensive)

    pros:
        - State-of-the-art accuracy
        - Multimodal reasoning
        - Low latency
        - Video understanding

    cons:
        - Requires API key
        - Costs per request
        - Requires internet
        - Privacy concerns (cloud)

    use_cases:
        - Best quality needed
        - Complex workflows
        - Video analysis
```

**3. Qwen3-VL Backend** (New - vLLM)
```python
# pack2skill/core/analysis/vlm/qwen_backend.py

class Qwen3VLBackend(VLMBackend):
    """Qwen3-VL via vLLM (local)"""

    models:
        - Qwen/Qwen3-VL-8B-Thinking-FP8
        - Qwen/Qwen3-VL-30B-A3B-Thinking-FP8

    pros:
        - High quality (near Gemini)
        - Local inference
        - No API costs
        - Fast with vLLM

    cons:
        - Requires GPU
        - Large model downloads
        - Setup complexity
        - Memory intensive

    use_cases:
        - High-quality local processing
        - Batch processing
        - Privacy requirements + quality needs
```

**4. Claude Backend** (New - API)
```python
# pack2skill/core/analysis/vlm/claude_backend.py

class ClaudeBackend(VLMBackend):
    """Anthropic Claude 3.5 Sonnet API"""

    models:
        - claude-3-5-sonnet-20241022
        - claude-3-5-haiku (when available)

    pros:
        - Excellent reasoning
        - Good at following instructions
        - Lower cost than GPT-4V
        - Strong at structured output

    cons:
        - API costs
        - Requires internet
        - Rate limits

    use_cases:
        - Structured workflow analysis
        - Complex reasoning needed
        - Integration with Claude ecosystem
```

#### VLM Backend Selection Strategy

```python
# pack2skill/core/analysis/vlm/strategy.py

class VLMStrategy:
    """Intelligent VLM backend selection"""

    @staticmethod
    def select_backend(
        requirements: Dict[str, Any]
    ) -> str:
        """
        Select best VLM backend based on requirements

        Requirements:
            - quality: 'low' | 'medium' | 'high'
            - cost_constraint: 'free' | 'low' | 'medium' | 'unlimited'
            - privacy: 'local_only' | 'ok_cloud'
            - speed: 'fast' | 'medium' | 'slow_ok'
            - batch_size: int
        """

        # Local only + high quality → Qwen3-VL (if GPU)
        if requirements['privacy'] == 'local_only':
            if requirements['quality'] == 'high' and has_gpu():
                return 'qwen'
            return 'blip'

        # High quality + cost OK → Gemini 2.5
        if requirements['quality'] == 'high':
            if requirements['cost_constraint'] in ['medium', 'unlimited']:
                return 'gemini-pro'
            return 'gemini-flash'

        # Structured analysis → Claude
        if requirements.get('structured_output'):
            return 'claude'

        # Default fallback
        return 'blip'
```

#### Event Processing with Burst Detection

```python
# pack2skill/core/analysis/event_processor.py

class EventProcessor:
    """Process events with burst detection (from pack)"""

    def __init__(
        self,
        burst_threshold: float = 0.5,  # seconds
        burst_min_events: int = 3
    ):
        self.burst_threshold = burst_threshold
        self.burst_min_events = burst_min_events

    def detect_bursts(
        self,
        events: List[Dict[str, Any]]
    ) -> List[List[Dict[str, Any]]]:
        """
        Group events into bursts

        Burst: sequence of events within threshold time

        Example:
            Events: [e1(t=0), e2(t=0.1), e3(t=0.2), e4(t=2.0), e5(t=2.1)]
            Bursts: [[e1, e2, e3], [e4, e5]]

        Benefits:
            - Better step segmentation
            - Identifies rapid sequences
            - Reduces noise from individual events
        """
        bursts = []
        current_burst = []

        for i, event in enumerate(events):
            if not current_burst:
                current_burst.append(event)
                continue

            time_since_last = event['t'] - current_burst[-1]['t']

            if time_since_last <= self.burst_threshold:
                current_burst.append(event)
            else:
                if len(current_burst) >= self.burst_min_events:
                    bursts.append(current_burst)
                current_burst = [event]

        if len(current_burst) >= self.burst_min_events:
            bursts.append(current_burst)

        return bursts

    def burst_to_step(
        self,
        burst: List[Dict[str, Any]],
        frame_captions: List[str]
    ) -> Dict[str, Any]:
        """Convert a burst of events into a workflow step"""

        # Aggregate burst information
        step = {
            'timestamp': burst[0]['t'],
            'duration': burst[-1]['t'] - burst[0]['t'],
            'event_count': len(burst),
            'event_types': list(set(e['type'] for e in burst)),
            'events': burst,
            'frame_caption': frame_captions[0] if frame_captions else None
        }

        # Generate step description from burst
        step['text'] = self._generate_step_text(step)
        step['action'] = self._infer_action(step)

        return step
```

#### Decision: Default VLM Backend

**Choice:** **Gemini 2.5 Flash** (with BLIP fallback if no API key)

**Rationale:**
- Best balance of quality/cost/speed
- Easy setup (just API key)
- Significantly better than BLIP
- Falls back gracefully to BLIP if no key
- Qwen3-VL available for GPU users

**Configuration:**
```yaml
# ~/.pack2skill/config.yaml

analysis:
  vlm_backend: "gemini"  # or "blip", "qwen", "claude"

  gemini:
    api_key: "${GEMINI_API_KEY}"
    model: "gemini-2.5-flash"

  qwen:
    model: "Qwen/Qwen3-VL-8B-Thinking-FP8"
    device: "cuda"  # or "cpu"

  claude:
    api_key: "${ANTHROPIC_API_KEY}"
    model: "claude-3-5-sonnet-20241022"

  blip:
    device: "cpu"  # fallback only

event_processing:
  use_burst_detection: true
  burst_threshold: 0.5  # seconds
  burst_min_events: 3
```

---

### 3. Output Module

**Purpose:** Generate various outputs from analyzed workflows

#### Architecture

```python
# pack2skill/core/output/base.py

from abc import ABC, abstractmethod
from typing import Dict, Any
from pathlib import Path

class OutputGenerator(ABC):
    """Base class for output generators"""

    @abstractmethod
    def generate(
        self,
        analysis: Dict[str, Any],
        output_dir: Path,
        config: Dict[str, Any]
    ) -> Path:
        """Generate output, return path to output"""
        pass

    @abstractmethod
    def get_output_type(self) -> str:
        """Return output type: 'skill', 'manual', 'doc', etc."""
        pass

class OutputManager:
    """Manages output generators"""

    def __init__(self):
        self._generators: Dict[str, OutputGenerator] = {}

    def register_generator(self, name: str, generator: OutputGenerator):
        """Register an output generator"""
        self._generators[name] = generator

    def generate_output(
        self,
        analysis: Dict[str, Any],
        output_type: str = "skill",
        output_dir: Path,
        config: Dict[str, Any] | None = None
    ) -> Path:
        """Generate specified output type"""
        pass
```

#### Output Generators

**1. Skill Generator** (Current)
```python
# pack2skill/core/output/skill_generator.py

class SkillGenerator(OutputGenerator):
    """Generate Claude Skills"""

    output_type = "skill"

    structure:
        skill-name/
        ├── SKILL.md          # Main skill file
        ├── REFERENCE.md      # Detailed reference
        └── scripts/          # Helper scripts
            └── helper.py

    format:
        - YAML frontmatter (name, description, version)
        - Markdown instructions
        - Claude Skills specification compliant

    features:
        - Name sanitization
        - Description optimization
        - Confidence scoring
        - Robustness checking
```

**2. Manual Generator** (New - Manus-style)
```python
# pack2skill/core/output/manual_generator.py

class ManualGenerator(OutputGenerator):
    """Generate image-embedded documentation"""

    output_type = "manual"

    structure:
        manual-name/
        ├── index.md          # Main manual
        ├── images/           # Extracted frames
        │   ├── step-1.png
        │   ├── step-2.png
        │   └── ...
        └── manual.pdf        # Optional PDF export

    features:
        - Markdown with embedded images
        - Step-by-step with screenshots
        - PDF export via pandoc
        - Web-friendly HTML export

    use_cases:
        - Documentation
        - Tutorials
        - Onboarding materials
        - Knowledge base articles
```

**3. Documentation Generator** (New)
```python
# pack2skill/core/output/doc_generator.py

class DocGenerator(OutputGenerator):
    """Generate structured documentation"""

    output_type = "documentation"

    formats:
        - README.md
        - API documentation
        - User guides
        - Architecture docs

    features:
        - Template-based generation
        - Multiple output formats
        - Integration with docs sites (MkDocs, Sphinx)
```

#### Decision: Output Priority

**Phase 1 (v2.0):** Skill Generator (current, enhanced)
**Phase 2 (v2.1):** Manual Generator (Manus-style)
**Phase 3 (v2.2):** Documentation Generator

**Rationale:**
- Maintain core value proposition (Skills)
- Add manual generation as differentiator
- Documentation generator nice-to-have

---

## Cross-Cutting Concerns

### Configuration Management

```python
# pack2skill/core/config/manager.py

class ConfigManager:
    """Centralized configuration management"""

    locations:
        1. ~/.pack2skill/config.yaml (user global)
        2. ./.pack2skill/config.yaml (project local)
        3. Environment variables (PACK2SKILL_*)
        4. CLI arguments (highest priority)

    features:
        - Hierarchical configuration
        - Environment variable interpolation
        - Validation and defaults
        - Hot reload support
```

### Storage & Caching

```python
# pack2skill/core/storage/cache.py

class CacheManager:
    """Intelligent caching for expensive operations"""

    cache_types:
        - VLM results (frame captions)
        - OCR results
        - Model downloads
        - Analysis intermediates

    storage:
        ~/.pack2skill/cache/
        ├── vlm/              # VLM results
        ├── ocr/              # OCR results
        ├── models/           # Downloaded models
        └── analysis/         # Analysis intermediates

    eviction:
        - LRU policy
        - Size limits (configurable)
        - TTL for API results
```

### Quality Assessment

```python
# pack2skill/core/quality/assessment.py

class QualityAssessment:
    """Enhanced quality assessment"""

    metrics:
        - Confidence scoring (multi-factor)
        - Completeness (step coverage)
        - Accuracy (VLM agreement)
        - Robustness (hardcoded values, edge cases)

    features:
        - Per-step scoring
        - Overall workflow score
        - Quality report generation
        - Improvement suggestions
```

---

## Performance Considerations

### Async Processing

```python
# pack2skill/core/async_processing.py

import asyncio
from concurrent.futures import ProcessPoolExecutor

class AsyncProcessor:
    """Asynchronous processing for I/O-bound tasks"""

    async def process_frames_async(
        self,
        frames: List[np.ndarray],
        vlm_backend: VLMBackend
    ) -> List[Dict[str, Any]]:
        """Process frames concurrently"""

        tasks = [
            vlm_backend.analyze_frame_async(frame)
            for frame in frames
        ]

        return await asyncio.gather(*tasks)

class BatchProcessor:
    """Batch processing for ML models"""

    def process_frames_batch(
        self,
        frames: List[np.ndarray],
        vlm_backend: VLMBackend,
        batch_size: int = 32
    ) -> List[Dict[str, Any]]:
        """Process frames in batches for efficiency"""

        results = []
        for i in range(0, len(frames), batch_size):
            batch = frames[i:i+batch_size]
            batch_results = vlm_backend.analyze_batch(batch)
            results.extend(batch_results)

        return results
```

### Memory Management

```python
# pack2skill/core/memory/manager.py

class MemoryManager:
    """Memory-efficient processing for large videos"""

    features:
        - Streaming video processing
        - Frame buffering (cyclic)
        - On-disk intermediate storage
        - Memory-mapped arrays for large datasets
```

---

## Trade-Off Analysis

### 1. VLM Backend Selection

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| BLIP only | Simple, offline, free | Poor quality | ❌ Not sufficient |
| Gemini only | Best quality | Requires API key, costs | ❌ Too restrictive |
| **Multi-backend** | Flexibility, quality options | Complex | ✅ **Selected** |

### 2. Recording Strategy

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Video only | Current approach, smooth | Large files | ✅ Keep for v2.0 |
| Screenshots only | Efficient, from pack | No smooth video | 🔄 Add in v2.1 |
| **Hybrid** | Best of both | Complex | 🔄 Consider for v2.2 |

### 3. Event Processing

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Simple timestamps | Easy, current | Less intelligent | ❌ Upgrade needed |
| **Burst detection** | Better grouping, from pack | More complex | ✅ **Implement** |
| ML-based segmentation | Most intelligent | Heavy, slow | 🔄 Future research |

### 4. Output Generation

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Skills only | Focused, current | Limited use cases | ❌ Too narrow |
| **Multi-output** | Flexible, competitive | More code | ✅ **Selected** |
| Everything at once | Full-featured | Scope creep | ❌ Too much |

---

## Migration Strategy

### Backward Compatibility

```python
# pack2skill/compat/v1.py

class V1Compatibility:
    """Ensure v0.1.0 workflows still work"""

    features:
        - Automatic detection of v1 recordings
        - Legacy CLI command support
        - Config file migration
        - Output format compatibility

    deprecated:
        - Direct BLIP imports (use VLM backend)
        - Old config format
        - Legacy analysis output

    timeline:
        - v2.0: Full backward compat
        - v2.1: Deprecation warnings
        - v3.0: Remove legacy code
```

### Migration Path

```bash
# Automatic migration
pack2skill migrate --from 0.1.0 --to 2.0.0

# What it does:
# 1. Converts old config to new format
# 2. Updates skill files (if needed)
# 3. Migrates cache structure
# 4. Provides migration report
```

---

## Implementation Phases

### Phase 1: Core Refactoring (v2.0)
**Timeline:** 2-3 weeks

**Deliverables:**
- [ ] Plugin architecture for VLM backends
- [ ] Gemini 2.5 backend implementation
- [ ] Burst detection in event processing
- [ ] Enhanced configuration system
- [ ] Backward compatibility layer
- [ ] Migration tools

**Testing:**
- Unit tests for all backends
- Integration tests for full pipeline
- Regression tests for v1 compatibility
- Performance benchmarks

### Phase 2: Advanced VLMs (v2.1)
**Timeline:** 2 weeks

**Deliverables:**
- [ ] Qwen3-VL backend (vLLM)
- [ ] Claude backend (API)
- [ ] Screenshot capture backend
- [ ] VLM strategy selection
- [ ] Caching system

**Testing:**
- VLM backend comparison tests
- Performance profiling
- Cost analysis for API backends

### Phase 3: Extended Outputs (v2.2)
**Timeline:** 2-3 weeks

**Deliverables:**
- [ ] Manual generator (Manus-style)
- [ ] PDF export
- [ ] HTML export
- [ ] YouTube URL ingestion
- [ ] Documentation generator

**Testing:**
- Output format validation
- Multi-format generation tests
- YouTube ingestion tests

### Phase 4: Optimization (v2.3)
**Timeline:** 1-2 weeks

**Deliverables:**
- [ ] Async processing
- [ ] Batch processing optimizations
- [ ] Memory management improvements
- [ ] Performance tuning

**Testing:**
- Load testing
- Memory profiling
- Latency measurements

---

## Scalability Considerations

### Horizontal Scaling

```python
# pack2skill/distributed/worker.py

class DistributedWorker:
    """Worker for distributed processing"""

    architecture:
        ┌────────────┐
        │   Master   │
        └─────┬──────┘
              │
        ┌─────┴──────┐
        ▼            ▼
    ┌────────┐  ┌────────┐
    │Worker 1│  │Worker 2│
    └────────┘  └────────┘

    use_cases:
        - Batch processing of many workflows
        - Parallel VLM inference
        - Large-scale team repositories

    technologies:
        - Celery for task queue
        - Redis for coordination
        - S3/GCS for storage
```

### Cloud Deployment

```yaml
# docker-compose.yml

version: '3.8'

services:
  pack2skill-api:
    image: pack2skill:2.0
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - REDIS_URL=redis://redis:6379
    ports:
      - "8000:8000"

  pack2skill-worker:
    image: pack2skill:2.0
    command: celery worker
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - REDIS_URL=redis://redis:6379

  redis:
    image: redis:7-alpine

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=pack2skill
```

---

## Security Considerations

### API Key Management

```python
# pack2skill/security/credentials.py

class CredentialManager:
    """Secure credential management"""

    features:
        - Encrypted storage (keyring)
        - Environment variable support
        - Cloud secret manager integration
        - Rotation support

    storage:
        - macOS: Keychain
        - Windows: Credential Manager
        - Linux: Secret Service
```

### Privacy

```python
# pack2skill/privacy/anonymizer.py

class DataAnonymizer:
    """Anonymize sensitive data in recordings"""

    features:
        - PII detection (emails, names, etc.)
        - Screen region redaction
        - Text masking in OCR
        - Configurable anonymization rules
```

---

## Testing Strategy

### Test Pyramid

```
       ┌────────┐
       │  E2E   │  10% - Full workflow tests
       ├────────┤
       │  Integ │  20% - Module integration
       ├────────┤
       │  Unit  │  70% - Individual functions
       └────────┘
```

### Test Coverage Requirements

- **Unit Tests:** 90%+ coverage
- **Integration Tests:** Key workflows
- **E2E Tests:** CLI commands
- **Performance Tests:** Benchmarks
- **Compatibility Tests:** v1 workflows

```python
# tests/integration/test_full_workflow.py

def test_full_workflow_gemini():
    """Test complete workflow with Gemini backend"""

    # Record
    recorder = WorkflowRecorder(output_dir="./test_output")
    session = recorder.start_recording(name="test-workflow")
    # ... simulate actions ...
    data = recorder.stop_recording()

    # Analyze
    analyzer = AnalysisManager(vlm_backend="gemini")
    analysis = analyzer.analyze_workflow(data)

    # Generate
    generator = SkillGenerator()
    skill_path = generator.generate(analysis, output_dir="./test_skills")

    # Verify
    assert (skill_path / "SKILL.md").exists()
    # ... more assertions ...
```

---

## Documentation Requirements

### Developer Documentation

- [ ] Architecture overview (this document)
- [ ] API reference (updated)
- [ ] Plugin development guide
- [ ] Testing guide
- [ ] Contributing guide

### User Documentation

- [ ] Migration guide (v1 → v2)
- [ ] VLM backend selection guide
- [ ] Configuration reference
- [ ] Troubleshooting guide
- [ ] Performance tuning guide

---

## Alternatives Evaluated

### Alternative 1: Fork pack directly

**Pros:**
- Reuse all pack's code
- Get burst detection for free
- Proven architecture

**Cons:**
- Lose pack2skill's unique features
- Different goals (tracking vs skills)
- Harder to maintain separate identity

**Decision:** ❌ Rejected - Better to integrate features

### Alternative 2: Wrapper around pack

**Pros:**
- Leverage pack as library
- Minimal new code

**Cons:**
- Tight coupling
- Limited control
- Dependency on pack updates

**Decision:** ❌ Rejected - Too limiting

### Alternative 3: Complete rewrite

**Pros:**
- Clean slate
- Best architecture

**Cons:**
- Massive effort
- Break existing users
- Lose v1 code

**Decision:** ❌ Rejected - Not worth it

### Alternative 4: Incremental enhancement (Selected)

**Pros:**
- ✅ Maintain existing users
- ✅ Add features incrementally
- ✅ Learn from pack's design
- ✅ Keep pack2skill identity

**Cons:**
- More complex migration
- Technical debt from v1

**Decision:** ✅ **Selected** - Best balance

---

## Success Metrics

### Technical Metrics

- **Quality:** VLM accuracy >90% (vs BLIP ~70%)
- **Performance:** <2min analysis per 5min video
- **Reliability:** 99.9% uptime for API backends
- **Compatibility:** 100% v1 workflows work

### User Metrics

- **Adoption:** 50%+ users upgrade to v2 in 3 months
- **Retention:** <5% churn due to breaking changes
- **Satisfaction:** >4.5/5 user rating
- **Cost:** <$0.10 per workflow (Gemini)

### Business Metrics

- **Growth:** 2x user base in 6 months
- **Engagement:** 3x workflows created per user
- **Community:** 10+ community-contributed backends

---

## Open Questions

1. **Model Hosting:** Should we offer hosted VLM service?
   - Pro: Easier onboarding, monetization
   - Con: Operational complexity, costs

2. **Real-time Mode:** Should we support real-time analysis?
   - Pro: Interactive feedback
   - Con: Significant complexity

3. **Marketplace:** Should we build a skill marketplace?
   - Pro: Community value
   - Con: Moderation, quality control

4. **Multi-user:** Support collaborative recording?
   - Pro: Team workflows
   - Con: Coordination complexity

---

## Conclusion

This architecture provides a solid foundation for pack2skill v2.0 that:

✅ Incorporates pack's best features (Gemini, burst detection)
✅ Maintains pack2skill's unique value (Claude Skills)
✅ Enables future features (manuals, documentation)
✅ Scales for team and enterprise use
✅ Preserves backward compatibility

**Next Steps:**
1. Review and approve architecture
2. Create implementation tickets
3. Set up development branches
4. Begin Phase 1 implementation

**Estimated Timeline:** 8-10 weeks for full v2.0 release

---

**Document Status:** Draft
**Review Required:** Yes
**Approver:** Project Lead
**Last Updated:** January 2025
