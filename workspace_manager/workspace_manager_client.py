"""
Workspace Manager Client
管理跨 workspace 的配置、同步和註冊功能
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from github import Github
import platform


class WorkspaceManager:
    """管理 Antigravity workspace 的註冊、同步和查詢"""
    
    def __init__(
        self, 
        github_token: str, 
        command_center_repo: str = "alstonhuang/AI_Command_Center",
        skills_repo: str = "alstonhuang/shared-agent-skills"
    ):
        """
        初始化 Workspace Manager
        
        Args:
            github_token: GitHub Personal Access Token
            command_center_repo: AI Command Center 倉庫名稱
            skills_repo: Shared Skills 倉庫名稱
        """
        self.token = github_token
        self.github = Github(github_token)
        self.command_center_repo = self.github.get_repo(command_center_repo)
        self.skills_repo_name = skills_repo
        self.workspace_root = self._detect_workspace_root()
        
    def _detect_workspace_root(self) -> Path:
        """自動檢測當前 workspace 根目錄"""
        current = Path.cwd()
        
        # 向上尋找包含 .agent 目錄的路徑
        while current != current.parent:
            if (current / ".agent").exists():
                return current
            current = current.parent
        
        # 如果找不到，返回當前目錄
        return Path.cwd()
    
    def register_workspace(
        self, 
        name: str, 
        location: str = None,
        description: str = ""
    ) -> bool:
        """
        註冊 workspace 到 AI Command Center
        
        Args:
            name: Workspace 名稱
            location: Workspace 路徑（預設為當前路徑）
            description: Workspace 描述
            
        Returns:
            註冊成功返回 True
        """
        if location is None:
            location = str(self.workspace_root)
        
        # 收集 workspace 資訊
        info = {
            "name": name,
            "location": location,
            "description": description,
            "registered_at": datetime.now().isoformat(),
            "machine": {
                "hostname": platform.node(),
                "os": platform.system(),
                "os_version": platform.version(),
                "architecture": platform.machine()
            },
            "projects": self._detect_projects(),
            "skills_version": self._get_skills_version()
        }
        
        # 儲存到 Command Center
        try:
            # 檢查 workspaces/config.json 是否存在
            try:
                config_file = self.command_center_repo.get_contents("workspaces/config.json")
                config = json.loads(config_file.decoded_content.decode())
            except:
                # 不存在則創建
                config = {"workspaces": []}
            
            # 檢查是否已註冊
            existing = next((w for w in config["workspaces"] if w["name"] == name), None)
            if existing:
                # 更新現有註冊
                existing.update(info)
                message = f"Update workspace: {name}"
            else:
                # 新增註冊
                config["workspaces"].append(info)
                message = f"Register new workspace: {name}"
            
            # 提交更新
            content = json.dumps(config, indent=2, ensure_ascii=False)
            if existing:
                self.command_center_repo.update_file(
                    "workspaces/config.json",
                    message,
                    content,
                    config_file.sha
                )
            else:
                try:
                    self.command_center_repo.create_file(
                        "workspaces/config.json",
                        message,
                        content
                    )
                except:
                    # 檔案已存在，更新之
                    config_file = self.command_center_repo.get_contents("workspaces/config.json")
                    self.command_center_repo.update_file(
                        "workspaces/config.json",
                        message,
                        content,
                        config_file.sha
                    )
            
            print(f"✅ Workspace '{name}' 已成功註冊到 AI Command Center")
            return True
            
        except Exception as e:
            print(f"❌ 註冊失敗: {e}")
            return False
    
    def _detect_projects(self) -> List[str]:
        """檢測 workspace 中的專案"""
        projects = []
        projects_dir = self.workspace_root / "projects"
        
        if projects_dir.exists():
            for item in projects_dir.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    projects.append(item.name)
        
        return projects
    
    def _get_skills_version(self) -> str:
        """取得當前 skills 的版本（Git commit hash）"""
        skills_path = self.workspace_root / ".agent" / "skills"
        
        if not skills_path.exists():
            return "not-installed"
        
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=skills_path,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()[:7]  # 短版本
        except:
            pass
        
        return "unknown"
    
    def sync_skills(self, target_path: str = None) -> bool:
        """
        從 GitHub 同步最新的 skills
        
        Args:
            target_path: Skills 安裝路徑（預設為 .agent/skills）
            
        Returns:
            同步成功返回 True
        """
        if target_path is None:
            target_path = self.workspace_root / ".agent" / "skills"
        else:
            target_path = Path(target_path)
        
        print(f"🔄 正在同步 skills 到: {target_path}")
        
        try:
            if target_path.exists() and (target_path / ".git").exists():
                # 已存在 Git 倉庫，執行 pull
                result = subprocess.run(
                    ["git", "pull"],
                    cwd=target_path,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    print(f"✅ Skills 已更新到最新版本")
                    return True
                else:
                    print(f"⚠️  更新失敗: {result.stderr}")
                    return False
            else:
                # 不存在，執行 clone
                target_path.parent.mkdir(parents=True, exist_ok=True)
                result = subprocess.run(
                    ["git", "clone", f"https://github.com/{self.skills_repo_name}.git", str(target_path)],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    print(f"✅ Skills 已成功安裝")
                    return True
                else:
                    print(f"❌ 安裝失敗: {result.stderr}")
                    return False
                    
        except Exception as e:
            print(f"❌ 同步失敗: {e}")
            return False
    
    def get_workspace_info(self) -> Dict:
        """取得當前 workspace 的資訊"""
        return {
            "root": str(self.workspace_root),
            "projects": self._detect_projects(),
            "skills_version": self._get_skills_version(),
            "machine": platform.node(),
            "os": platform.system()
        }
    
    def find_project(self, project_name: str) -> Optional[Dict]:
        """
        在所有已註冊的 workspace 中搜尋專案
        
        Args:
            project_name: 專案名稱
            
        Returns:
            包含專案所在 workspace 資訊的字典，找不到返回 None
        """
        try:
            config_file = self.command_center_repo.get_contents("workspaces/config.json")
            config = json.loads(config_file.decoded_content.decode())
            
            for workspace in config.get("workspaces", []):
                if project_name in workspace.get("projects", []):
                    return {
                        "workspace_name": workspace["name"],
                        "workspace_location": workspace["location"],
                        "project_name": project_name,
                        "project_path": os.path.join(workspace["location"], "projects", project_name)
                    }
            
            return None
            
        except Exception as e:
            print(f"❌ 搜尋失敗: {e}")
            return None
    
    def list_all_workspaces(self) -> List[Dict]:
        """列出所有已註冊的 workspaces"""
        try:
            config_file = self.command_center_repo.get_contents("workspaces/config.json")
            config = json.loads(config_file.decoded_content.decode())
            return config.get("workspaces", [])
        except Exception as e:
            print(f"❌ 讀取失敗: {e}")
            return []
    
    def test_connection(self) -> bool:
        """測試與 GitHub 的連接"""
        try:
            self.github.get_user().login
            print("✅ GitHub 連接正常")
            return True
        except Exception as e:
            print(f"❌ GitHub 連接失敗: {e}")
            return False
    
    def test_github_access(self) -> bool:
        """測試是否能訪問 Command Center 倉庫"""
        try:
            self.command_center_repo.name
            print(f"✅ 可以訪問 {self.command_center_repo.full_name}")
            return True
        except Exception as e:
            print(f"❌ 無法訪問倉庫: {e}")
            return False
    
    def verify_registration(self) -> bool:
        """驗證當前 workspace 是否已註冊"""
        try:
            workspaces = self.list_all_workspaces()
            current_location = str(self.workspace_root)
            
            for ws in workspaces:
                if ws["location"] == current_location:
                    print(f"✅ 當前 workspace 已註冊為: {ws['name']}")
                    return True
            
            print(f"⚠️  當前 workspace 尚未註冊")
            return False
            
        except Exception as e:
            print(f"❌ 驗證失敗: {e}")
            return False


# ===== 命令列介面 =====

if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Workspace Manager CLI")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # register 命令
    register_parser = subparsers.add_parser("register", help="註冊 workspace")
    register_parser.add_argument("--name", required=True, help="Workspace 名稱")
    register_parser.add_argument("--location", help="Workspace 路徑")
    register_parser.add_argument("--description", default="", help="描述")
    
    # sync-skills 命令
    subparsers.add_parser("sync-skills", help="同步 skills")
    
    # info 命令
    subparsers.add_parser("info", help="顯示 workspace 資訊")
    
    # list 命令
    subparsers.add_parser("list", help="列出所有 workspaces")
    
    # find 命令
    find_parser = subparsers.add_parser("find", help="搜尋專案")
    find_parser.add_argument("project", help="專案名稱")
    
    args = parser.parse_args()
    
    # 讀取 GitHub token
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        token_file = Path(".gh_token")
        if token_file.exists():
            token = token_file.read_text().strip()
        else:
            print("❌ 找不到 GitHub token")
            print("   請設定 GITHUB_TOKEN 環境變數或創建 .gh_token 檔案")
            sys.exit(1)
    
    # 初始化 manager
    manager = WorkspaceManager(token)
    
    # 執行命令
    if args.command == "register":
        manager.register_workspace(args.name, args.location, args.description)
    
    elif args.command == "sync-skills":
        manager.sync_skills()
    
    elif args.command == "info":
        info = manager.get_workspace_info()
        print(json.dumps(info, indent=2, ensure_ascii=False))
    
    elif args.command == "list":
        workspaces = manager.list_all_workspaces()
        print(f"\n📋 已註冊的 Workspaces ({len(workspaces)}):\n")
        for ws in workspaces:
            print(f"  • {ws['name']}")
            print(f"    位置: {ws['location']}")
            print(f"    專案: {', '.join(ws.get('projects', []))}")
            print(f"    機器: {ws.get('machine', {}).get('hostname', 'unknown')}")
            print()
    
    elif args.command == "find":
        result = manager.find_project(args.project)
        if result:
            print(f"\n✅ 找到專案: {args.project}")
            print(f"   Workspace: {result['workspace_name']}")
            print(f"   路徑: {result['project_path']}\n")
        else:
            print(f"\n❌ 找不到專案: {args.project}\n")
    
    else:
        parser.print_help()
