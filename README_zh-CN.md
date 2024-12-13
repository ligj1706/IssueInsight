# IssueInsight

[English](./README.md) | 简体中文

GitHub Issues 智能分析面板：分析github issues数据，洞察项目需求。

![image-1](https://p.ipic.vip/dd7jo6.png)

![2-png](https://p.ipic.vip/0lbm5a.png)

## ✨ 特性

- **一键分析**：即时分析任何公开 GitHub 仓库的 issues
- **丰富可视化**：直观展示问题趋势、时间模式和社区参与度指标
- **社区洞察**：理解项目维护模式和社区健康状况
- **时间分析**：追踪活跃时段和响应模式
- **性能指标**：监控解决率和团队效率
- **用户友好**：简洁直观的 Web 仪表板，便于分析

## 🚀 快速开始

1. **环境要求**
   - Python 3.7+
   - GitHub 个人访问令牌（必需）
     - 应用需要 GitHub 令牌才能访问 API
     - 没有令牌将无法获取仓库数据
     - 令牌必须具有 `repo` 权限才能正常工作

2. **安装**
   ```bash
   # 克隆仓库
   git clone https://github.com/yourusername/IssueInsight.git
   cd IssueInsight
   
   # 安装依赖
   pip install -r requirements.txt
   ```

3. **获取 GitHub Token**
   - 访问 [GitHub Token 设置](https://github.com/settings/tokens)
   - 创建带有 `repo` 权限的 token
   - 复制你的 token

4. **运行应用**
   ```bash
   python app.py
   ```

5. **访问面板**
   - 打开 `http://localhost:5000`
   - 输入你的 GitHub token
   - 输入要分析的仓库 URL

## 📊 核心指标

- **Issues 统计**
  - 总数、开放和关闭的 issues 统计
  - 解决率和趋势
  - 平均响应时间

- **时间分析**
  - 按小时/天的活动模式
  - 贡献高峰时段
  - 响应时间分布

- **社区参与度**
  - 活跃贡献者
  - 评论频率
  - 用户互动模式

## 💡 使用场景

- **项目评估**：采用前评估仓库维护状况
- **社区分析**：了解用户参与模式
- **维护规划**：识别最佳 issue 管理时机
- **团队表现**：跟踪解决效率
- **趋势分析**：监控长期项目健康度

## 🛠️ 开发

```bash
# Fork 仓库
git clone https://github.com/yourusername/IssueInsight.git

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows 使用: venv\Scripts\activate

# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
pytest
```

## 🤝 贡献指南

贡献使开源社区成为一个令人赞叹的学习、激励和创造的地方。我们**非常感谢**任何形式的贡献。

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 📝 许可证

基于 MIT 许可证开源。详见 `LICENSE` 文件。

## 🙏 致谢

- [GitHub API](https://docs.github.com/en/rest)
- [Flask](https://flask.palletsprojects.com/)
- 所有贡献者和用户