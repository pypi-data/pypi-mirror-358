![Documiner](https://documiner.ai/_static/documiner_readme_header.png "Documiner - Advanced tool designed for text analysis and data mining in documents")

# Documiner: Advanced tool designed for text analysis and data mining in documents

[![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/sabih-urrehman/6203e5026a3b4c613e78e95c00420e13/raw/99b05a21ebeb05ab53cccc8c83a91e6135e8e414/gistfile1.txt)](https://github.com/sabih-urrehman/documiner/actions)
[![docs](https://github.com/sabih-urrehman/documiner/actions/workflows/docs.yml/badge.svg?branch=main)](https://github.com/sabih-urrehman/documiner/actions/workflows/docs.yml)
[![documentation](https://img.shields.io/badge/docs-latest-blue.svg)](https://sabih-urrehman.github.io/documiner/)
[![License](https://img.shields.io/badge/License-Apache_2.0-bright.svg)](https://opensource.org/licenses/Apache-2.0)
![PyPI](https://img.shields.io/pypi/v/documiner)
[![Python Versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)](https://www.python.org/downloads/)
[![CodeQL](https://github.com/sabih-urrehman/documiner/actions/workflows/codeql.yml/badge.svg?branch=main)](https://github.com/sabih-urrehman/documiner/actions/workflows/codeql.yml)
[![bandit security](https://github.com/sabih-urrehman/documiner/actions/workflows/bandit-security.yml/badge.svg?branch=main)](https://github.com/sabih-urrehman/documiner/actions/workflows/bandit-security.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat)](https://pycqa.github.io/isort/)
[![Pydantic v2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json)](https://pydantic.dev)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](CODE_OF_CONDUCT.md)
[![DeepWiki](https://img.shields.io/static/v1?label=DeepWiki&message=Chat%20with%20Code&labelColor=%23283593&color=%237E57C2&style=flat-square)](https://deepwiki.com/sabih-urrehman/documiner)
[![GitHub latest commit](https://img.shields.io/github/last-commit/sabih-urrehman/documiner?label=latest%20commit)](https://github.com/sabih-urrehman/documiner/commits/main)

<br/><br/>

Documiner is a free, open-source LLM framework that makes it radically easier to extract structured data and insights from documents — with minimal code.

---


## 💎 Why Documiner?

Most popular LLM frameworks for extracting structured data from documents require extensive boilerplate code to extract even basic information. This significantly increases development time and complexity.

Documiner addresses this challenge by providing a flexible, intuitive framework that extracts structured data and insights from documents with minimal effort. Complex, most time-consuming parts are handled with **powerful abstractions**, eliminating boilerplate code and reducing development overhead.


## ⭐ Key features

<table>
    <thead>
        <tr style="text-align: left; opacity: 0.8;">
            <th style="width: 75%">Built-in abstractions</th>
            <th style="width: 10%"><strong>Documiner</strong></th>
            <th style="width: 15%">Other LLM frameworks*</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>
                Automated dynamic prompts
            </td>
            <td>🟢</td>
            <td>◯</td>
        </tr>
        <tr>
            <td>
                Automated data modelling and validators
            </td>
            <td>🟢</td>
            <td>◯</td>
        </tr>
        <tr>
            <td>
                Precise granular reference mapping (paragraphs & sentences)
            </td>
            <td>🟢</td>
            <td>◯</td>
        </tr>
        <tr>
            <td>
                Justifications (reasoning backing the extraction)
            </td>
            <td>🟢</td>
            <td>◯</td>
        </tr>
        <tr>
            <td>
                Neural segmentation (SaT)
            </td>
            <td>🟢</td>
            <td>◯</td>
        </tr>
        <tr>
            <td>
                Multilingual support (I/O without prompting)
            </td>
            <td>🟢</td>
            <td>◯</td>
        </tr>
        <tr>
            <td>
                Single, unified extraction pipeline (declarative, reusable, fully serializable)
            </td>
            <td>🟢</td>
            <td>🟡</td>
        </tr>
        <tr>
            <td>
                Grouped LLMs with role-specific tasks
            </td>
            <td>🟢</td>
            <td>🟡</td>
        </tr>
        <tr>
            <td>
                Nested context extraction
            </td>
            <td>🟢</td>
            <td>🟡</td>
        </tr>
        <tr>
            <td>
                Unified, fully serializable results storage model (document)
            </td>
            <td>🟢</td>
            <td>🟡</td>
        </tr>
        <tr>
            <td>
                Extraction task calibration with examples
            </td>
            <td>🟢</td>
            <td>🟡</td>
        </tr>
        <tr>
            <td>
                Built-in concurrent I/O processing
            </td>
            <td>🟢</td>
            <td>🟡</td>
        </tr>
        <tr>
            <td>
                Automated usage & costs tracking
            </td>
            <td>🟢</td>
            <td>🟡</td>
        </tr>
        <tr>
            <td>
                Fallback and retry logic
            </td>
            <td>🟢</td>
            <td>🟢</td>
        </tr>
        <tr>
            <td>
                Multiple LLM providers
            </td>
            <td>🟢</td>
            <td>🟢</td>
        </tr>
    </tbody>
</table>

🟢 - fully supported - no additional setup required<br>
🟡 - partially supported - requires additional setup<br>
◯ - not supported - requires custom logic

\* See [descriptions](https://documiner.ai/motivation.html#the-documiner-solution) of Documiner abstractions and [comparisons](https://documiner.ai/vs_other_frameworks.html) of specific implementation examples using Documiner and other popular open-source LLM frameworks.

## 💡 What you can build

With **minimal code**, you can:

- **Extract structured data** from documents (text, images)
- **Identify and analyze key aspects** (topics, themes, categories) within documents ([learn more](https://documiner.ai/aspects/aspects.html))
- **Extract specific concepts** (entities, facts, conclusions, assessments) from documents ([learn more](https://documiner.ai/concepts/supported_concepts.html))
- **Build complex extraction workflows** through a simple, intuitive API
- **Create multi-level extraction pipelines** (aspects containing concepts, hierarchical aspects)

<br/>

![Documiner extraction example](https://documiner.ai/_static/readme_code_snippet.png "Documiner extraction example")


## 📦 Installation

```bash
pip install -U documiner
```

> **⚡ v0.5.0+**: Documiner now installs 7.5x faster with minimal dependencies (no torch/transformers required), making it easier to integrate into existing ML environments.


## 🚀 Quick start

```python
# Quick Start Example - Extracting anomalies from a document, with source references and justifications

import os

from documiner import Document, DocumentLLM, StringConcept

# Sample document text (shortened for brevity)
doc = Document(
    raw_text=(
        "Consultancy Agreement\n"
        "This agreement between Company A (Supplier) and Company B (Customer)...\n"
        "The term of the agreement is 1 year from the Effective Date...\n"
        "The Supplier shall provide consultancy services as described in Annex 2...\n"
        "The Customer shall pay the Supplier within 30 calendar days of receiving an invoice...\n"
        "The purple elephant danced gracefully on the moon while eating ice cream.\n"  # 💎 anomaly
        "Time-traveling dinosaurs will review all deliverables before acceptance.\n"  # 💎 another anomaly
        "This agreement is governed by the laws of Norway...\n"
    ),
)

# Attach a document-level concept
doc.concepts = [
    StringConcept(
        name="Anomalies",  # in longer contexts, this concept is hard to capture with RAG
        description="Anomalies in the document",
        add_references=True,
        reference_depth="sentences",
        add_justifications=True,
        justification_depth="brief",
        # see the docs for more configuration options
    )
    # add more concepts to the document, if needed
    # see the docs for available concepts: StringConcept, JsonObjectConcept, etc.
]
# Or use `doc.add_concepts([...])`

# Define an LLM for extracting information from the document
llm = DocumentLLM(
    model="openai/gpt-4o-mini",  # or another provider/LLM
    api_key=os.environ.get(
        "DOCUMINER_OPENAI_API_KEY"
    ),  # your API key for the LLM provider
    # see the docs for more configuration options
)

# Extract information from the document
doc = llm.extract_all(doc)  # or use async version `await llm.extract_all_async(doc)`

# Access extracted information in the document object
anomalies_concept = doc.concepts[0]
# or `doc.get_concept_by_name("Anomalies")`
for item in anomalies_concept.extracted_items:
    print(f"Anomaly:")
    print(f"  {item.value}")
    print(f"Justification:")
    print(f"  {item.justification}")
    print("Reference paragraphs:")
    for p in item.reference_paragraphs:
        print(f"  - {p.raw_text}")
    print("Reference sentences:")
    for s in item.reference_sentences:
        print(f"  - {s.raw_text}")
    print()

```
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sabih-urrehman/documiner/blob/main/dev/notebooks/readme/quickstart_concept.ipynb)

---

### 📚 More Examples

**Basic usage:**
- [Aspect Extraction from Document](https://documiner.ai/quickstart.html#aspect-extraction-from-document)
- [Extracting Aspect with Sub-Aspects](https://documiner.ai/quickstart.html#extracting-aspect-with-sub-aspects)
- [Concept Extraction from Aspect](https://documiner.ai/quickstart.html#concept-extraction-from-aspect)
- [Concept Extraction from Document (text)](https://documiner.ai/quickstart.html#concept-extraction-from-document-text)
- [Concept Extraction from Document (vision)](https://documiner.ai/quickstart.html#concept-extraction-from-document-vision)
- [LLM chat interface](https://documiner.ai/quickstart.html#lightweight-llm-chat-interface)

**Advanced usage:**
- [Extracting Aspects Containing Concepts](https://documiner.ai/advanced_usage.html#extracting-aspects-with-concepts)
- [Extracting Aspects and Concepts from a Document](https://documiner.ai/advanced_usage.html#extracting-aspects-and-concepts-from-a-document)
- [Using a Multi-LLM Pipeline to Extract Data from Several Documents](https://documiner.ai/advanced_usage.html#using-a-multi-llm-pipeline-to-extract-data-from-several-documents)


## 🔄 Document converters

To create a Documiner document for LLM analysis, you can either pass raw text directly, or use built-in converters that handle various file formats.

### 📄 DOCX converter

Documiner provides built-in converter to easily transform DOCX files into LLM-ready data.

- **Comprehensive extraction of document elements**: paragraphs, headings, lists, tables, comments, footnotes, textboxes, headers/footers, links, embedded images, and inline formatting
- **Document structure preservation** with rich metadata for improved LLM analysis
- **Built-in converter** that directly processes Word XML

```python
# Using Documiner's DocxConverter

from documiner import DocxConverter

converter = DocxConverter()

# Convert a DOCX file to an LLM-ready Documiner Document
# from path
document = converter.convert("path/to/document.docx")
# or from file object
with open("path/to/document.docx", "rb") as docx_file_object:
    document = converter.convert(docx_file_object)

# Perform data extraction on the resulting Document object
# document.add_aspects(...)
# document.add_concepts(...)
# llm.extract_all(document)

# You can also use DocxConverter instance as a standalone text extractor
docx_text = converter.convert_to_text_format(
    "path/to/document.docx",
    output_format="markdown",  # or "raw"
)

```

📖 Learn more about [DOCX converter features](https://documiner.ai/converters/docx.html) in the documentation.

## 🎯 Focused document analysis

Documiner leverages LLMs' long context windows to deliver superior extraction accuracy from individual documents. Unlike RAG approaches that often [struggle with complex concepts and nuanced insights](https://www.linkedin.com/pulse/raging-contracts-pitfalls-rag-contract-review-sabih-urrehman-ptg3f), Documiner capitalizes on continuously expanding context capacity, evolving LLM capabilities, and decreasing costs. This focused approach enables direct information extraction from complete documents, eliminating retrieval inconsistencies while optimizing for in-depth single-document analysis. While this delivers higher accuracy for individual documents, Documiner does not currently support cross-document querying or corpus-wide retrieval - for these use cases, modern RAG systems (e.g., LlamaIndex, Haystack) remain more appropriate.

📖 Read more on [how Documiner works](https://documiner.ai/how_it_works.html) in the documentation.

## 🤖 Supported LLMs

Documiner supports both cloud-based and local LLMs through [LiteLLM](https://github.com/BerriAI/litellm) integration:
- **Cloud LLMs**: OpenAI, Anthropic, Google, Azure OpenAI, and more
- **Local LLMs**: Run models locally using providers like Ollama, LM Studio, etc.
- **Model Architectures**: Works with both reasoning/CoT-capable (e.g. o4-mini) and non-reasoning models (e.g. gpt-4.1)
- **Simple API**: Unified interface for all LLMs with easy provider switching

> **💡 Model Selection Note:** For reliable structured extraction, we recommend using models with performance equivalent to or exceeding `gpt-4o-mini`. Smaller models (such as 8B parameter models) may struggle with Documiner's detailed extraction instructions. If you encounter issues with smaller models, see our [troubleshooting guide](https://documiner.ai/optimizations/optimization_small_llm_troubleshooting.html) for potential solutions.

📖 Learn more about [supported LLM providers and models](https://documiner.ai/llms/supported_llms.html), how to [configure LLMs](https://documiner.ai/llms/llm_config.html), and [LLM extraction methods](https://documiner.ai/llms/llm_extraction_methods.html) in the documentation.

## ⚡ Optimizations

Documiner documentation offers guidance on optimization strategies to maximize performance, minimize costs, and enhance extraction accuracy:

- [Optimizing for Accuracy](https://documiner.ai/optimizations/optimization_accuracy.html)
- [Optimizing for Speed](https://documiner.ai/optimizations/optimization_speed.html)
- [Optimizing for Cost](https://documiner.ai/optimizations/optimization_cost.html)
- [Dealing with Long Documents](https://documiner.ai/optimizations/optimization_long_docs.html)
- [Choosing the Right LLM(s)](https://documiner.ai/optimizations/optimization_choosing_llm.html)
- [Troubleshooting Issues with Small Models](https://documiner.ai/optimizations/optimization_small_llm_troubleshooting.html)


## 💾 Serializing results

Documiner allows you to save and load Document objects, pipelines, and LLM configurations with built-in serialization methods:

- Save processed documents to avoid repeating expensive LLM calls
- Transfer extraction results between systems
- Persist pipeline and LLM configurations for later reuse

📖 Learn more about [serialization options](https://documiner.ai/serialization.html) in the documentation.

## 📚 Documentation

📖 **Full documentation:** [documiner.ai](https://documiner.ai)

📄 **Raw documentation for LLMs:** Available at [`docs/docs-raw-for-llm.txt`](https://github.com/sabih-urrehman/documiner/blob/main/docs/docs-raw-for-llm.txt) - automatically generated, optimized for LLM ingestion.

🤖 **AI-powered code exploration:** [DeepWiki](https://deepwiki.com/sabih-urrehman/documiner) provides visual architecture maps and natural language Q&A for the codebase.

📈 **Change history:** See the [CHANGELOG](https://github.com/sabih-urrehman/documiner/blob/main/CHANGELOG.md) for version history, improvements, and bug fixes.

## 💬 Community

🐛 **Found a bug or have a feature request?** [Open an issue](https://github.com/sabih-urrehman/documiner/issues/new) on GitHub.

💭 **Need help or want to discuss?** Start a thread in [GitHub Discussions](https://github.com/sabih-urrehman/documiner/discussions/new/).

## 🤝 Contributing

We welcome contributions from the community - whether it's fixing a typo or developing a completely new feature! 

📋 **Get started:** Check out our [Contributor Guidelines](https://github.com/sabih-urrehman/documiner/blob/main/CONTRIBUTING.md).

## 🔐 Security

This project is automatically scanned for security vulnerabilities using multiple security tools:

- **[CodeQL](https://codeql.github.com/)** - GitHub's semantic code analysis engine for vulnerability detection
- **[Bandit](https://github.com/PyCQA/bandit)** - Python security linter for common security issues  
- **[Snyk](https://snyk.io)** - Dependency vulnerability monitoring (used as needed)

🛡️ **Security policy:** See [SECURITY](https://github.com/sabih-urrehman/documiner/blob/main/SECURITY.md) file for details.

## 💖 Acknowledgements

Documiner relies on these excellent open-source packages:

- [aiolimiter](https://github.com/mjpieters/aiolimiter): Powerful rate limiting for async operations
- [Jinja2](https://github.com/pallets/jinja): Fast, expressive template engine that powers our dynamic prompt rendering
- [litellm](https://github.com/BerriAI/litellm): Unified interface to multiple LLM providers with seamless provider switching
- [loguru](https://github.com/Delgan/loguru): Simple yet powerful logging that enhances debugging and observability
- [lxml](https://github.com/lxml/lxml): High-performance XML processing library for parsing DOCX document structure
- [pydantic](https://github.com/pydantic/pydantic): The gold standard for data validation
- [python-ulid](https://github.com/mdomke/python-ulid): Efficient ULID generation
- [wtpsplit-lite](https://github.com/superlinear-ai/wtpsplit-lite): Lightweight version of [wtpsplit](https://github.com/segment-any-text/wtpsplit) for state-of-the-art text segmentation using wtpsplit's SaT models


## 🌱 Support the project

Documiner is just getting started, and your support means the world to us! 

⭐ **Star the project** if you find Documiner useful  
📢 **Share it** with others who might benefit  
🔧 **Contribute** with feedback, issues, or code improvements

Your engagement is what makes this project grow!

## 📄 License & Contact

**License:** Apache 2.0 License - see the [LICENSE](https://github.com/sabih-urrehman/documiner/blob/main/LICENSE) and [NOTICE](https://github.com/sabih-urrehman/documiner/blob/main/NOTICE) files for details.

**Copyright:** © 2025 [Documiner](https://shcherbak.ai), an AI engineering company building tools for AI/ML/NLP developers.

**Connect:** [LinkedIn](https://www.linkedin.com/in/sergii-shcherbak-10068866/) or [X](https://x.com/seshch) for questions or collaboration ideas.

Built with ❤️ in Oslo, Norway.
