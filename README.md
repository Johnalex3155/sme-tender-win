# 🚀 SME Tender-Win AI

SME Tender-Win is an AI-powered procurement agent designed to democratize government tendering for Small and Medium-sized Enterprises (SMEs). It automates the tedious process of finding, filtering, and analyzing government opportunities, allowing small businesses to compete on a level playing field.

## 🌟 Key Features
- **🎯 Targeted Discovery**: Instead of broad searches, the agent performs targeted queries across a curated list of government portals to ensure 100% source coverage.
- **🌐 Direct Portal Crawling**: Bypasses search engine noise by crawling official procurement portals directly.
- **🤖 AI-Driven Analysis**: Integrated with Large Language Models (LLMs) to analyze tender requirements against a company's specific SME profile.
- **✍️ Automated Proposal Drafting**: Generates initial technical approach drafts and compliance checklists to accelerate the bidding process.
- **📊 Win Probability**: Provides a heuristic-based win probability score based on capability matching.

## 🛠️ Tech Stack
- **Frontend**: Streamlit
- **Discovery**: Serper.dev API (Google Search)
- **Extraction**: Firecrawl (Markdown-based web scraping)
- **Intelligence**: Local LLMs via Ollama (e.g., Gemma 4)
- **Language**: Python 3.11+


## 🚀 Getting Started

### 🛠️ Prerequisites
Before running the app, ensure you have the following installed:
- **Python 3.11+**
- **Docker & Docker Compose** (Required to run Firecrawl locally)
- **Ollama** (For local LLM execution)
- **Serper.dev API Key** (For Google Search discovery)

### 📦 Service Setup

#### 1. Install & Run Firecrawl (Self-Hosted)
The agent requires a Firecrawl instance to scrape government portals.
```bash
# Clone the Firecrawl repository
git clone https://github.com/mendableai/firecrawl.git
cd firecrawl

# Start the services using Docker
docker compose up -d
```
*The instance will be available at `http://localhost:3002` by default.*

#### 2. Setup Ollama
Install Ollama from [ollama.com](https://ollama.com) and pull the required model:
```bash
ollama pull gemma4:31b
```
*If running in a VM, ensure `OLLAMA_HOST=0.0.0.0` is set to allow external connections.*

### 💻 Application Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/[your-username]/sme-tender-win.git
   cd sme-tender-win
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the App**:
   ```bash
   streamlit run src/app.py
   ```
## ⚙️ Configuration
In the sidebar, you can:
- Configure your **SME Profile** (capabilities, niche, etc.).
- Set your **Ollama Server URL** and **API Key**.
- Manage your **Target Portals** (add/remove government URLs).

## 📄 License
This project is licensed under the MIT License.
