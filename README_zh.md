# 🔱 SwingFish | 深海交易终端 (中文)

![SwingFish Showcase](./assets/video_muestra_3.gif)

**SwingFish** 是一款专为机构级波段交易设计的高级自动化分析终端。它通过将量化金融模型与多代理逻辑委员会结合，克服了通用人工智能的局限性。

## 💡 核心问题：通用 LLM vs. SwingFish
标准 LLM 依赖网页抓取（web-scraping）来“总结”市场，这往往导致财务幻觉和肤浅的分析。
**SwingFish 通过以下方式对抗这些问题：**
1.  **数据与推理分离**：我们使用专用引擎预先获取原始事实。
2.  **专业委员会**：代理基于特定领域（风险、技术、宏观）处理数据，而非生成通用文本。
3.  **审计追踪**：每个分析结论都包含一份深度报告，对比原始输入与推理过程。

## 🔱 三大分析支柱
### 1. 数据提供引擎 (Dashboard)
扮演“声呐”角色，从 Yahoo Finance、FRED 和 COT 提取数据。
*   **方法论**: [阅读更多](./backend/Dashboard/METODOLOGY_dashboard_zh.md)

### 2. 深海探测 (多代理委员会)
通过 **LangGraph** 协调运行，由 6 个代理（技术、基本面、风险、期权、情绪、宏观）分析资产。由**投资组合经理**综合报告以消除偏见。
*   **方法论**: [阅读更多](./backend/multiagent_analysis/METODOLOGY_multiagent_zh.md)

### 3. 标普 500 评分引擎
基于 Piotroski、Altman、Beneish 和 魔法公式（Magic Formula）模型，使用加权公式 (0-100) 过滤标普 500 成分股。
*   **方法论**: [阅读更多](./backend/Filter_sp500/METODOLOGY_filter_sp500_zh.md)

## 🔄 波段交易者的理想流程
1.  **宏观检查**：使用宏观仪表盘识别市场制度（风险偏好/规避）。
2.  **资产扫描**：通过标普 500 筛选器识别具有动量的优质流动资产。
3.  **深度研究**：针对特定代码运行**深海探测**，获取机构级的审计报告和判决。

## ⚠️ 重要警告
本终端严格针对**北美市场（美国）的个股**进行优化。将其用于指数或其他资产类别可能导致数据映射不完整。

## 🗺️ 路线图 (Roadmap)
1.  **强健的期权策略**：集成专业的 [OptionStrat-AI](https://github.com/EconomiaUNMSM/OptionStrat-AI) 模块。
2.  **资产类别扩展**：支持大宗商品和 ETF。
3.  **期货集成**：深海期货合约分析。
4.  **多模型支持**：兼容 Anthropic (Claude)、DeepSeek 和本地 LLM。
5.  **交互式自定义**：实时调整理代理角色和工具。
6.  **高级量化模型**：集成经过回测的机器学习和深度学习策略。
7.  **动态权重**：自定义标普 500 评分系统的权重配置。

## 🚀 快速入门指南

### 必要条件
- **Python 3.10+**
- **Node.js 18+**
- **Git**

### 1. 后端设置
在项目根目录下：
```bash
cd backend
# 创建虚拟环境
python -m venv venv
# 激活虚拟环境 (Windows)
venv\Scripts\activate
# 安装依赖
pip install -r requirements.txt
# 启动服务器 (API 运行在 http://localhost:8000)
uvicorn api.main:app --reload
```

### 2. 前端设置
在项目根目录下：
```bash
cd frontend
# 安装依赖
npm install
# 启动开发模式 (应用运行在 http://localhost:3000)
npm run dev
```

## 🔄 仓库更新命令
让你的终端始终保持最新：
```bash
# 1. 拉取最新更改
git pull origin main

# 2. 更新后端依赖
cd backend
# (确保虚拟环境已激活)
pip install -r requirements.txt
cd ..

# 3. 更新前端依赖
cd frontend
npm install
cd ..
```


## 👨‍💻 作者
**Luis Fabio Yoplac Cortez**
- [GitHub](https://github.com/EconomiaUNMSM)
- [LinkedIn](https://www.linkedin.com/in/luis-yoplac-cortez-10397328b)
