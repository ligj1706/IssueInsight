# IssueInsight

English | [简体中文](./README_zh-CN.md)

A powerful analytics dashboard for GitHub Issues that provides deep insights into repository health and community engagement.

[Report Bug](https://github.com/yourusername/IssueInsight/issues) · [Request Feature](https://github.com/yourusername/IssueInsight/issues)

![image-1](https://p.ipic.vip/etr59x.png)

![2-png](https://p.ipic.vip/9v5e88.png)

## ✨ Key Features

- **Instant Analysis**: One-click analysis of any public GitHub repository
- **Smart Metrics**: Comprehensive statistics on issues, responses, and community engagement
- **Visual Insights**: Beautiful charts and graphs for trend analysis
- **Time Intelligence**: Activity patterns and response time analysis
- **Community Health**: Deep understanding of community engagement and contribution patterns

## 🚀 Getting Started

1. **Prerequisites**
   - Python 3.7+
   - GitHub Personal Access Token (Required)
     - The app requires a GitHub token to access the API
     - Without a token, the app cannot fetch repository data
     - Token must have `repo` scope for full functionality

2. **Installation**
   ```bash
   # Clone the repository
   git clone https://github.com/yourusername/IssueInsight.git
   cd IssueInsight
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Configuration**
   - Get your GitHub token from [GitHub Settings](https://github.com/settings/tokens)
   - Token needs `repo` scope for repository access

4. **Launch**
   ```bash
   python app.py
   ```

5. **Usage**
   - Visit `http://localhost:5000`
   - Enter your GitHub token
   - Input a repository URL to analyze
   - Explore the insights!

## 📊 Analytics Features

### Core Metrics
- Total, open, and closed issues
- Resolution rates and trends
- Response time analysis
- Community engagement levels

### Time Analysis
- Monthly activity trends
- Weekly patterns
- Response time distribution
- Peak activity periods

### Content Analysis
- Top issue keywords
- Label distribution
- Title length statistics
- Engagement patterns

### Community Insights
- Active contributors
- Quick response rates
- Community health trends
- Engagement metrics

## 🛠️ Development

```bash
# Setup development environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [GitHub REST API](https://docs.github.com/en/rest)
- [Flask](https://flask.palletsprojects.com/)
- [ECharts](https://echarts.apache.org/)
- All contributors and users