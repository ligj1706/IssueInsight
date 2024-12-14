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
import os
import shutil
import sys
from flask_frozen import Freezer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitHubAPI:
    def __init__(self, token: str = None):
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,  # Maximum number of retries
            backoff_factor=1,  # Retry interval
            status_forcelist=[429, 500, 502, 503, 504],  # HTTP status codes to retry
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        
        # Set default headers
        self.session.headers.update({
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {token}" if token else None,
            "User-Agent": "IssueInsight-App"
        })

    def get(self, url: str, params: Dict = None) -> Dict:
        """Execute GET request and handle errors"""
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise

class GitHubAnalyzer:
    def __init__(self, owner: str, repo: str, token: str = None):
        """Initialize analyzer with repository information"""
        self.owner = owner
        self.repo = repo
        self.api = GitHubAPI(token)
        self.base_url = f"https://api.github.com/repos/{owner}/{repo}"

    def get_issues(self) -> List[Dict]:
        """Fetch all issues from the repository"""
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
                    
                # Filter out pull requests
                real_issues = [issue for issue in response if "pull_request" not in issue]
                issues.extend(real_issues)
                
                logger.info(f"Fetched page {page}, got {len(real_issues)} issues")
                
                if len(response) < 100:
                    break
                    
                page += 1
                time.sleep(1)  # Avoid hitting rate limits
                
            except Exception as e:
                logger.error(f"Error fetching issues: {str(e)}")
                break
                
        return issues

    def analyze_issues(self, issues: List[Dict]) -> Dict:
        """Analyze issues and generate insights"""
        try:
            # Basic statistics
            total_issues = len(issues)
            open_issues = len([i for i in issues if i["state"] == "open"])
            closed_issues = total_issues - open_issues
            
            # Calculate resolution rate
            resolution_rate = (closed_issues / total_issues * 100) if total_issues > 0 else 0
            
            # Response time analysis
            response_times = []
            for issue in issues:
                if issue["closed_at"]:
                    created = datetime.strptime(issue["created_at"], "%Y-%m-%dT%H:%M:%SZ")
                    closed = datetime.strptime(issue["closed_at"], "%Y-%m-%dT%H:%M:%SZ")
                    response_times.append((closed - created).total_seconds() / 3600)
            
            # Time-based analysis
            created_times = [
                datetime.strptime(issue["created_at"], "%Y-%m-%dT%H:%M:%SZ")
                for issue in issues
            ]
            
            # Monthly statistics
            monthly_counts = {}
            for dt in created_times:
                month_key = dt.strftime("%Y-%m")
                monthly_counts[month_key] = monthly_counts.get(month_key, 0) + 1
            
            # Calculate growth rate
            sorted_months = sorted(monthly_counts.keys())
            if len(sorted_months) >= 2:
                current_month = monthly_counts[sorted_months[-1]]
                prev_month = monthly_counts[sorted_months[-2]]
                growth_rate = ((current_month - prev_month) / prev_month * 100) if prev_month > 0 else 0
            else:
                growth_rate = 0
            
            # Label analysis
            labels = []
            for issue in issues:
                labels.extend([label["name"] for label in issue["labels"]])
            label_counts = Counter(labels)
            
            # Extract keywords from titles and bodies
            titles = [issue["title"] for issue in issues]
            descriptions = [issue.get("body", "") for issue in issues]
            
            # Simple keyword extraction (can be improved)
            words = []
            for text in titles + descriptions:
                if text:
                    # Remove special characters, split into words
                    cleaned = re.sub(r'[^\w\s]', ' ', text.lower())
                    words.extend(cleaned.split())
            
            # Filter out common words and empty strings
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
        """Calculate time distribution"""
        if not times:
            return {}
            
        bins = [0, 1, 3, 6, 12, 24, float('inf')]
        labels = ['<1h', '1-3h', '3-6h', '6-12h', '12-24h', '>24h']
        
        hist, _ = np.histogram(times, bins=bins)
        return dict(zip(labels, hist.tolist()))

    def _calculate_weekly_pattern(self, times: List[datetime]) -> List[int]:
        """Calculate weekly activity pattern"""
        if not times:
            return [0] * 7
            
        # Count activity by day of the week
        weekday_counts = [0] * 7
        for dt in times:
            # datetime's weekday() returns 0-6, where 0 is Monday
            weekday_counts[dt.weekday()] += 1
            
        return weekday_counts

app = Flask(__name__)
freezer = Freezer(app)

@app.route('/')
def index():
    """Render the main dashboard page"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST', 'GET'])
def analyze():
    """Analyze GitHub repository issues"""
    try:
        # 如果是在生成静态文件时
        if request.method == 'GET':
            return jsonify({"message": "This endpoint accepts POST requests"}), 200
            
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        github_url = data.get('url', '').strip()
        token = data.get('token', '').strip()
        
        if not github_url or not token:
            return jsonify({"error": "Missing required parameters"}), 400
            
        # Extract owner and repo from URL
        match = re.match(r'https?://github\.com/([^/]+)/([^/]+)', github_url)
        if not match:
            return jsonify({"error": "Invalid GitHub repository URL"}), 400
            
        owner, repo = match.groups()
        repo = repo.replace('.git', '').split('/')[0]  # Remove .git and other paths
        
        # Validate token
        try:
            test_url = f"https://api.github.com/user"
            headers = {"Authorization": f"token {token}"}
            response = requests.get(test_url, headers=headers)
            response.raise_for_status()
        except Exception as e:
            return jsonify({"error": "Invalid GitHub token"}), 401
        
        # Analyze issues
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
    if len(sys.argv) > 1 and sys.argv[1] == 'build':
        # 创建 build 目录
        if os.path.exists('build'):
            shutil.rmtree('build')
        os.makedirs('build')
        
        # 冻结 Flask 应用为静态文件
        freezer.freeze()
        
        print("静态文件已生成到 build 目录")
    else:
        # 正常运行 Flask 应用
        app.run(debug=True)