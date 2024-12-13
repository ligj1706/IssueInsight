from flask import Flask, render_template, request, jsonify
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
from collections import Counter
from typing import Dict, List, Any
import re
import json
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitHubAPI:
    def __init__(self, token: str = None):
        self.session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=3,  # 最多重试3次
            backoff_factor=1,  # 重试间隔
            status_forcelist=[429, 500, 502, 503, 504],  # 需要重试的HTTP状态码
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        
        # 设置默认headers
        self.session.headers.update({
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {token}" if token else None,
            "User-Agent": "IssueInsight-App"
        })

    def get(self, url: str, params: Dict = None) -> Dict:
        """执行GET请求并处理错误"""
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise

class GitHubAnalyzer:
    def __init__(self, owner: str, repo: str, token: str = None):
        """初始化分析器"""
        self.owner = owner
        self.repo = repo
        self.api = GitHubAPI(token)
        self.base_url = f"https://api.github.com/repos/{owner}/{repo}"

    def get_issues(self) -> List[Dict]:
        """获取所有issues"""
        issues = []
        page = 1
        
        while True:
            try:
                url = f"{self.base_url}/issues"
                params = {
                    "state": "all",
                    "per_page": 100,
                    "page": page,
                    "sort": "created",
                    "direction": "desc"
                }
                
                response = self.api.get(url, params)
                if not response:
                    break
                    
                # 过滤出真正的issues（排除PRs）
                real_issues = [issue for issue in response if "pull_request" not in issue]
                issues.extend(real_issues)
                
                logger.info(f"Fetched page {page}, got {len(real_issues)} issues")
                
                if len(response) < 100:
                    break
                    
                page += 1
                time.sleep(1)  # 避免触发限制
                
            except Exception as e:
                logger.error(f"Error fetching issues: {str(e)}")
                break
                
        return issues

    def analyze_issues(self, issues: List[Dict]) -> Dict:
        """分析issues数据"""
        try:
            # 基础统计
            total_issues = len(issues)
            open_issues = len([i for i in issues if i["state"] == "open"])
            closed_issues = total_issues - open_issues
            
            # 计算响应时间
            response_times = []
            for issue in issues:
                if issue["closed_at"]:
                    created = datetime.strptime(issue["created_at"], "%Y-%m-%dT%H:%M:%SZ")
                    closed = datetime.strptime(issue["closed_at"], "%Y-%m-%dT%H:%M:%SZ")
                    response_times.append((closed - created).total_seconds() / 3600)
            
            # 时间分布
            created_times = [
                datetime.strptime(issue["created_at"], "%Y-%m-%dT%H:%M:%SZ")
                for issue in issues
            ]
            
            # 按月统计
            monthly_counts = {}
            for dt in created_times:
                month_key = dt.strftime("%Y-%m")
                monthly_counts[month_key] = monthly_counts.get(month_key, 0) + 1
            
            # 计算增长率
            sorted_months = sorted(monthly_counts.keys())
            if len(sorted_months) >= 2:
                current_month = monthly_counts[sorted_months[-1]]
                prev_month = monthly_counts[sorted_months[-2]]
                growth_rate = ((current_month - prev_month) / prev_month * 100) if prev_month > 0 else 0
            else:
                growth_rate = 0
            
            # 统计标签
            labels = []
            for issue in issues:
                labels.extend([label["name"] for label in issue["labels"]])
            label_counts = Counter(labels)
            
            # 提取关键词
            titles = [issue["title"] for issue in issues]
            descriptions = [issue.get("body", "") for issue in issues]
            
            # 简单的关键词提取（可以根据需要改进）
            words = []
            for text in titles + descriptions:
                if text:
                    # 移除特殊字符，分割成单词
                    cleaned = re.sub(r'[^\w\s]', ' ', text.lower())
                    words.extend(cleaned.split())
            
            # 过滤掉常见词和空字符串
            common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
            filtered_words = [word for word in words if word and word not in common_words and len(word) > 2]
            word_counts = Counter(filtered_words)

            return {
                "basic_stats": {
                    "total_issues": total_issues,
                    "open_issues": open_issues,
                    "closed_issues": closed_issues,
                    "resolution_rate": round((closed_issues / total_issues * 100) if total_issues > 0 else 0, 1),
                    "contributors_count": len(set(issue["user"]["login"] for issue in issues))
                },
                "time_analysis": {
                    "monthly": dict(sorted(monthly_counts.items())),
                    "avg_resolution_time": np.mean(response_times) if response_times else 0,
                    "median_resolution_time": np.median(response_times) if response_times else 0,
                    "weekly_pattern": self._calculate_weekly_pattern(created_times)
                },
                "labels": {
                    "top_labels": dict(label_counts.most_common(10)),
                    "total_labels": len(set(labels))
                },
                "response_analysis": {
                    "response_distribution": self._calculate_time_distribution(response_times),
                    "median_response_time": np.median(response_times) if response_times else 0,
                    "quick_response_rate": len([t for t in response_times if t <= 24]) / len(response_times) if response_times else 0
                },
                "engagement": {
                    "engagement_rate": len(set(issue["user"]["login"] for issue in issues)) / total_issues if total_issues > 0 else 0
                },
                "trends": {
                    "growth_rate": round(growth_rate, 1),
                    "resolution_rate_change": 0,
                    "response_time_change": 0,
                    "engagement_change": 0
                },
                "content_analysis": {
                    "top_keywords": dict(word_counts.most_common(30)),  
                    "title_length": {
                        "avg": np.mean([len(title.split()) for title in titles]),
                        "min": min(len(title.split()) for title in titles) if titles else 0,
                        "max": max(len(title.split()) for title in titles) if titles else 0
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing issues: {str(e)}")
            raise

    def _calculate_time_distribution(self, times: List[float]) -> Dict[str, int]:
        """计算时间分布"""
        if not times:
            return {}
            
        bins = [0, 1, 3, 6, 12, 24, float('inf')]
        labels = ['<1h', '1-3h', '3-6h', '6-12h', '12-24h', '>24h']
        
        hist, _ = np.histogram(times, bins=bins)
        return dict(zip(labels, hist.tolist()))

    def _calculate_weekly_pattern(self, times: List[datetime]) -> List[int]:
        """计算每周各天的活动分布"""
        if not times:
            return [0] * 7
            
        # 统计每个工作日的数量（0=周一，6=周日）
        weekday_counts = [0] * 7
        for dt in times:
            # datetime的weekday()返回0-6，其中0是周一
            weekday_counts[dt.weekday()] += 1
            
        return weekday_counts

app = Flask(__name__)

@app.route('/')
def index():
    """渲染主页"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """分析仓库"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        github_url = data.get('url', '').strip()
        token = data.get('token', '').strip()
        
        if not github_url or not token:
            return jsonify({"error": "Missing required parameters"}), 400
            
        # 提取owner和repo
        match = re.match(r'https?://github\.com/([^/]+)/([^/]+)', github_url)
        if not match:
            return jsonify({"error": "Invalid GitHub URL"}), 400
            
        owner, repo = match.groups()
        repo = repo.replace('.git', '').split('/')[0]  # 移除.git和其他路径
        
        # 验证token
        try:
            test_url = f"https://api.github.com/user"
            headers = {"Authorization": f"token {token}"}
            response = requests.get(test_url, headers=headers)
            response.raise_for_status()
        except Exception as e:
            return jsonify({"error": "Invalid GitHub token"}), 401
        
        # 执行分析
        analyzer = GitHubAnalyzer(owner, repo, token)
        issues = analyzer.get_issues()
        
        if not issues:
            return jsonify({"error": "No issues found or repository is not accessible"}), 404
            
        results = analyzer.analyze_issues(issues)
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)