"""
MCP Server - AI需求分析和设计助手
协助AI初级开发者完善需求分析和架构设计

包含三个核心工具：
1. requirement_clarifier - 需求澄清助手
2. requirement_manager - 需求文档管理器  
3. architecture_designer - 架构设计生成器
"""

import logging
import os
import json
from typing import Any, Dict, List
from datetime import datetime
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from mcp.types import Tool, TextContent, Resource

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("StudyAIDevelop", description="AI需求分析和设计助手")

# 配置存储目录
def get_storage_dir():
    """获取存储目录，优先使用环境变量配置"""
    env_dir = os.getenv("MCP_STORAGE_DIR", "./mcp_data")
    storage_dir = Path(env_dir)
    storage_dir.mkdir(exist_ok=True)
    return storage_dir

# 全局需求文档存储 - 结构化设计
current_requirements = {
    "project_overview": [],
    "functional_requirements": [],
    "technical_requirements": [],
    "design_requirements": [],
    "deployment_requirements": [],
    "ai_constraints": [],
    "clarification_history": [],
    "architecture_designs": [],
    "last_updated": None,
    "project_id": None,
    "branch_status": {},  # 分支完成状态跟踪

    # 新增：结构化需求存储
    "structured_requirements": {},  # {req_id: RequirementEntity}
    "requirement_relationships": [],  # 需求关联关系
    "module_mapping": {},  # 需求到架构模块的映射
    "next_req_id": 1  # 需求ID计数器
}

# 需求实体结构
class RequirementEntity:
    """结构化需求实体"""
    def __init__(self, req_id: str, req_type: str, content: str,
                 priority: str = "medium", source: str = "user"):
        self.id = req_id
        self.type = req_type  # project_goal, functional, technical, ui_design
        self.content = content
        self.priority = priority  # high, medium, low
        self.source = source  # user, ai_inferred, derived
        self.related_ids = []  # 关联的其他需求ID
        self.impacts = []  # 影响的架构模块
        self.quality_score = 0.0
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()

    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "type": self.type,
            "content": self.content,
            "priority": self.priority,
            "source": self.source,
            "related_ids": self.related_ids,
            "impacts": self.impacts,
            "quality_score": self.quality_score,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: dict):
        """从字典创建实体"""
        entity = cls(data["id"], data["type"], data["content"],
                    data.get("priority", "medium"), data.get("source", "user"))
        entity.related_ids = data.get("related_ids", [])
        entity.impacts = data.get("impacts", [])
        entity.quality_score = data.get("quality_score", 0.0)
        entity.created_at = data.get("created_at", datetime.now().isoformat())
        entity.updated_at = data.get("updated_at", datetime.now().isoformat())
        return entity

# 需求管理器 - 统一管理接口
class RequirementManager:
    """需求管理器 - 处理结构化需求的增删改查和关联分析"""

    @staticmethod
    def add_requirement(req_type: str, content: str, priority: str = "medium",
                       source: str = "user") -> str:
        """添加结构化需求"""
        req_id = f"{req_type}_{current_requirements['next_req_id']}"
        current_requirements['next_req_id'] += 1

        # 创建需求实体
        entity = RequirementEntity(req_id, req_type, content, priority, source)

        # 计算质量分数
        entity.quality_score = _evaluate_requirement_quality(content)

        # 自动分析关联关系
        RequirementManager._auto_detect_relationships(entity)

        # 自动推断架构影响
        RequirementManager._infer_architecture_impacts(entity)

        # 存储到结构化存储
        current_requirements["structured_requirements"][req_id] = entity

        # 同时保持向后兼容，存储到原有格式
        RequirementManager._sync_to_legacy_format(entity)

        return req_id

    @staticmethod
    def get_requirement(req_id: str) -> RequirementEntity:
        """获取需求实体"""
        entity_data = current_requirements["structured_requirements"].get(req_id)
        if isinstance(entity_data, dict):
            return RequirementEntity.from_dict(entity_data)
        return entity_data

    @staticmethod
    def get_requirements_by_type(req_type: str) -> list:
        """按类型获取需求"""
        return [entity for entity in current_requirements["structured_requirements"].values()
                if (isinstance(entity, RequirementEntity) and entity.type == req_type) or
                   (isinstance(entity, dict) and entity.get("type") == req_type)]

    @staticmethod
    def add_relationship(req_id1: str, req_id2: str, relationship_type: str = "related"):
        """添加需求关联关系"""
        relationship = {
            "from_id": req_id1,
            "to_id": req_id2,
            "type": relationship_type,
            "created_at": datetime.now().isoformat()
        }
        current_requirements["requirement_relationships"].append(relationship)

        # 更新需求实体的关联列表
        req1 = RequirementManager.get_requirement(req_id1)
        req2 = RequirementManager.get_requirement(req_id2)

        if req1 and req2_id not in req1.related_ids:
            req1.related_ids.append(req_id2)
        if req2 and req_id1 not in req2.related_ids:
            req2.related_ids.append(req_id1)

    @staticmethod
    def get_related_requirements(req_id: str) -> list:
        """获取相关需求"""
        entity = RequirementManager.get_requirement(req_id)
        if not entity:
            return []

        related = []
        for related_id in entity.related_ids:
            related_entity = RequirementManager.get_requirement(related_id)
            if related_entity:
                related.append(related_entity)

        return related

    @staticmethod
    def _auto_detect_relationships(new_entity: RequirementEntity):
        """自动检测需求关联关系"""
        for existing_id, existing_entity in current_requirements["structured_requirements"].items():
            if existing_id == new_entity.id:
                continue

            # 基于内容相似度检测关联
            similarity = RequirementManager._calculate_similarity(
                new_entity.content,
                existing_entity.content if isinstance(existing_entity, RequirementEntity)
                else existing_entity.get("content", "")
            )

            if similarity > 0.3:  # 相似度阈值
                RequirementManager.add_relationship(new_entity.id, existing_id, "related")

    @staticmethod
    def _calculate_similarity(content1: str, content2: str) -> float:
        """计算内容相似度"""
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union) if union else 0.0

    @staticmethod
    def _infer_architecture_impacts(entity: RequirementEntity):
        """推断架构影响"""
        impact_keywords = {
            "user_interface": ["界面", "页面", "交互", "显示", "输入"],
            "business_logic": ["业务", "逻辑", "规则", "流程", "处理"],
            "data_layer": ["数据", "存储", "数据库", "持久化", "查询"],
            "api_layer": ["接口", "API", "服务", "调用", "集成"],
            "security": ["安全", "权限", "认证", "授权", "加密"],
            "performance": ["性能", "速度", "优化", "缓存", "并发"]
        }

        content_lower = entity.content.lower()
        for module, keywords in impact_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                entity.impacts.append(module)

    @staticmethod
    def _sync_to_legacy_format(entity: RequirementEntity):
        """同步到原有格式，保持向后兼容"""
        type_mapping = {
            "project_goal": "project_overview",
            "functional": "functional_requirements",
            "technical": "technical_requirements",
            "ui_design": "design_requirements",
            "deployment": "deployment_requirements"
        }

        legacy_key = type_mapping.get(entity.type, "functional_requirements")
        if entity.content not in current_requirements[legacy_key]:
            current_requirements[legacy_key].append(entity.content)

# 存储管理类
class RequirementStorage:
    def __init__(self):
        self.storage_dir = get_storage_dir()
        self.requirements_file = self.storage_dir / "requirements.json"
        self.history_file = self.storage_dir / "history.json"
        self.load_requirements()

    def load_requirements(self):
        """加载已保存的需求文档 - 支持结构化数据"""
        global current_requirements
        try:
            if self.requirements_file.exists():
                with open(self.requirements_file, 'r', encoding='utf-8') as f:
                    saved_data = json.load(f)

                    # 恢复结构化需求对象
                    if "structured_requirements" in saved_data:
                        structured_reqs = {}
                        for req_id, req_data in saved_data["structured_requirements"].items():
                            if isinstance(req_data, dict) and "id" in req_data:
                                structured_reqs[req_id] = RequirementEntity.from_dict(req_data)
                            else:
                                structured_reqs[req_id] = req_data
                        saved_data["structured_requirements"] = structured_reqs

                    current_requirements.update(saved_data)
                logger.info(f"✅ 已加载需求文档: {self.requirements_file}")
        except Exception as e:
            logger.warning(f"⚠️ 加载需求文档失败: {e}")

    def save_requirements(self):
        """保存需求文档到文件 - 支持结构化数据"""
        try:
            current_requirements["last_updated"] = datetime.now().isoformat()

            # 转换结构化需求为可序列化格式
            serializable_reqs = {}
            for req_id, entity in current_requirements["structured_requirements"].items():
                if isinstance(entity, RequirementEntity):
                    serializable_reqs[req_id] = entity.to_dict()
                else:
                    serializable_reqs[req_id] = entity

            # 创建可序列化的副本
            save_data = current_requirements.copy()
            save_data["structured_requirements"] = serializable_reqs

            with open(self.requirements_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            logger.info(f"✅ 需求文档已保存: {self.requirements_file}")
        except Exception as e:
            logger.error(f"❌ 保存需求文档失败: {e}")

    def save_history_entry(self, entry_type: str, content: str, metadata: dict = None):
        """保存历史记录条目"""
        try:
            history_entry = {
                "timestamp": datetime.now().isoformat(),
                "type": entry_type,
                "content": content,
                "metadata": metadata or {}
            }

            history = []
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)

            history.append(history_entry)

            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)

            logger.info(f"✅ 历史记录已保存: {entry_type}")
        except Exception as e:
            logger.error(f"❌ 保存历史记录失败: {e}")

    def export_final_document(self):
        """导出最终的完整需求和架构文档"""
        try:
            final_doc = {
                "project_summary": {
                    "generated_at": datetime.now().isoformat(),
                    "project_id": current_requirements.get("project_id"),
                    "last_updated": current_requirements.get("last_updated")
                },
                "requirements": current_requirements,
                "export_format": "markdown"
            }

            export_file = self.storage_dir / f"final_document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(final_doc, f, ensure_ascii=False, indent=2)

            # 同时生成Markdown格式
            md_file = self.storage_dir / f"final_document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            self.generate_markdown_report(md_file)

            logger.info(f"✅ 最终文档已导出: {export_file}")
            return str(export_file)
        except Exception as e:
            logger.error(f"❌ 导出最终文档失败: {e}")
            return None

    def generate_markdown_report(self, md_file: Path):
        """生成Markdown格式的报告"""
        try:
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write("# 🚀 AI开发项目需求与架构文档\n\n")
                f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

                # 项目概述
                if current_requirements.get("project_overview"):
                    f.write("## 📋 项目概述\n\n")
                    for item in current_requirements["project_overview"]:
                        f.write(f"- {item}\n")
                    f.write("\n")

                # 功能需求
                if current_requirements.get("functional_requirements"):
                    f.write("## ⚙️ 功能需求\n\n")
                    for item in current_requirements["functional_requirements"]:
                        f.write(f"- {item}\n")
                    f.write("\n")

                # 技术需求
                if current_requirements.get("technical_requirements"):
                    f.write("## 🔧 技术需求\n\n")
                    for item in current_requirements["technical_requirements"]:
                        f.write(f"- {item}\n")
                    f.write("\n")

                # 架构设计
                if current_requirements.get("architecture_designs"):
                    f.write("## 🏗️ 架构设计\n\n")
                    for design in current_requirements["architecture_designs"]:
                        f.write(f"{design}\n\n")

                # 澄清历史
                if current_requirements.get("clarification_history"):
                    f.write("## 📝 需求澄清历史\n\n")
                    for item in current_requirements["clarification_history"]:
                        f.write(f"- {item}\n")
                    f.write("\n")

            logger.info(f"✅ Markdown报告已生成: {md_file}")
        except Exception as e:
            logger.error(f"❌ 生成Markdown报告失败: {e}")

# 初始化存储管理器
storage = RequirementStorage()

# 智能澄清策略模块
class IntelligentClarificationEngine:
    """智能澄清引擎 - 负责生成高质量的澄清问题"""

    @staticmethod
    def analyze_project_characteristics(user_input: str, context: str, existing_requirements: dict) -> dict:
        """分析项目特征和核心需求"""
        return {
            "project_type": IntelligentClarificationEngine._identify_project_type(user_input),
            "complexity_level": IntelligentClarificationEngine._assess_complexity(user_input),
            "key_features": IntelligentClarificationEngine._extract_key_features(user_input),
            "missing_critical_info": IntelligentClarificationEngine._identify_critical_gaps(user_input, existing_requirements)
        }

    @staticmethod
    def _identify_project_type(user_input: str) -> str:
        """识别项目类型"""
        keywords = {
            "web": ["网站", "web", "在线", "平台", "系统"],
            "mobile": ["app", "手机", "移动", "安卓", "ios"],
            "desktop": ["桌面", "pc", "软件", "客户端"],
            "miniprogram": ["小程序", "微信", "支付宝"]
        }

        user_lower = user_input.lower()
        for project_type, words in keywords.items():
            if any(word in user_lower for word in words):
                return project_type
        return "general"

    @staticmethod
    def _assess_complexity(user_input: str) -> str:
        """评估项目复杂度"""
        complex_indicators = ["ai", "智能", "机器学习", "大数据", "分布式", "微服务", "实时", "高并发"]
        user_lower = user_input.lower()

        if any(indicator in user_lower for indicator in complex_indicators):
            return "high"
        elif len(user_input.split()) > 10:
            return "medium"
        return "low"

    @staticmethod
    def _extract_key_features(user_input: str) -> list:
        """提取关键功能特征"""
        feature_keywords = {
            "用户管理": ["用户", "登录", "注册", "账号"],
            "数据处理": ["数据", "存储", "处理", "分析"],
            "交互功能": ["聊天", "评论", "消息", "通知"],
            "内容管理": ["发布", "编辑", "管理", "内容"]
        }

        features = []
        user_lower = user_input.lower()
        for feature, keywords in feature_keywords.items():
            if any(keyword in user_lower for keyword in keywords):
                features.append(feature)
        return features

    @staticmethod
    def _identify_critical_gaps(user_input: str, existing_requirements: dict) -> list:
        """识别关键信息缺口"""
        gaps = []

        # 检查是否缺少目标用户信息
        if not any("用户" in str(req) for req in existing_requirements.get("project_overview", [])):
            gaps.append("target_users")

        # 检查是否缺少技术偏好
        if not existing_requirements.get("technical_requirements"):
            gaps.append("tech_preferences")

        # 检查是否缺少功能细节
        if not existing_requirements.get("functional_requirements"):
            gaps.append("functional_details")

        return gaps

    @staticmethod
    def get_current_branch(context: str, user_input: str) -> str:
        """识别当前讨论的分支 - 智能优先级"""
        context_lower = context.lower()
        input_lower = user_input.lower()
        combined_text = context_lower + " " + input_lower

        # 分支关键词权重映射
        branch_weights = {
            "project_goals": ["目标", "用户", "问题", "价值", "为什么", "解决"],
            "functional_design": ["功能", "特性", "操作", "流程", "业务", "怎么做"],
            "technical_preferences": ["技术", "框架", "性能", "语言", "数据库", "架构"],
            "ui_design": ["界面", "ui", "交互", "设计", "样式", "用户体验"]
        }

        # 计算各分支匹配分数
        branch_scores = {}
        for branch, keywords in branch_weights.items():
            score = sum(2 if keyword in combined_text else 0 for keyword in keywords)
            branch_scores[branch] = score

        # 如果有明确匹配，返回最高分分支
        max_score = max(branch_scores.values()) if branch_scores else 0
        if max_score > 0:
            return max(branch_scores.items(), key=lambda x: x[1])[0]

        # 否则返回最需要完善的分支
        return IntelligentClarificationEngine._calculate_next_priority()

    @staticmethod
    def _calculate_next_priority() -> str:
        """计算下一个优先级最高的分支"""
        # 获取各分支完整性
        branch_status = IntelligentClarificationEngine.check_branch_completeness(current_requirements)
        branch_scores = branch_status.get("branch_scores", {})

        # 优先级权重（分数越低优先级越高）
        priority_weights = {
            "project_goals": 1.0,      # 最高优先级
            "functional_design": 0.9,
            "technical_preferences": 0.7,
            "ui_design": 0.6
        }

        # 计算优先级分数（完整度越低，权重越高，优先级越高）
        priority_scores = {}
        for branch in priority_weights:
            completeness = branch_scores.get(branch, 0.0)
            weight = priority_weights[branch]
            # 优先级分数 = 权重 * (1 - 完整度)
            priority_scores[branch] = weight * (1 - completeness)

        # 返回优先级分数最高的分支
        return max(priority_scores.items(), key=lambda x: x[1])[0]

    @staticmethod
    def check_branch_completeness(requirements: dict) -> dict:
        """检查各分支完整性 - 动态标准"""

        # 动态评估分支完整性（基于质量而非数量）
        branch_scores = {}

        # 项目目标分支
        project_reqs = requirements.get("project_overview", [])
        branch_scores["project_goals"] = IntelligentClarificationEngine._evaluate_branch_quality(
            project_reqs, min_count=1, quality_threshold=0.5
        )

        # 功能设计分支
        functional_reqs = requirements.get("functional_requirements", [])
        branch_scores["functional_design"] = IntelligentClarificationEngine._evaluate_branch_quality(
            functional_reqs, min_count=1, quality_threshold=0.4  # 降低要求
        )

        # 技术偏好分支
        tech_reqs = requirements.get("technical_requirements", [])
        branch_scores["technical_preferences"] = IntelligentClarificationEngine._evaluate_branch_quality(
            tech_reqs, min_count=1, quality_threshold=0.3
        )

        # UI设计分支
        design_reqs = requirements.get("design_requirements", [])
        branch_scores["ui_design"] = IntelligentClarificationEngine._evaluate_branch_quality(
            design_reqs, min_count=1, quality_threshold=0.3
        )

        # 计算完成的分支
        completed_branches = [branch for branch, score in branch_scores.items() if score >= 0.6]
        incomplete_branches = [branch for branch, score in branch_scores.items() if score < 0.6]

        completion_rate = len(completed_branches) / len(branch_scores)

        return {
            "all_complete": completion_rate >= 0.75,  # 75%完成即可
            "incomplete_branches": incomplete_branches,
            "completion_rate": completion_rate,
            "branch_scores": branch_scores
        }

    @staticmethod
    def _evaluate_branch_quality(requirements: list, min_count: int, quality_threshold: float) -> float:
        """评估分支质量"""
        if len(requirements) < min_count:
            return 0.0

        if not requirements:
            return 0.0

        # 计算平均质量
        total_quality = sum(_evaluate_requirement_quality(req) for req in requirements)
        avg_quality = total_quality / len(requirements)

        # 结合数量和质量
        count_score = min(len(requirements) / min_count, 1.0)
        quality_score = avg_quality

        return (count_score + quality_score) / 2

# 需求澄清助手工具
@mcp.tool()
def requirement_clarifier(user_input: str, context: str = "") -> str:
    """智能需求澄清助手 - 深度分析用户需求，生成高质量澄清问题"""

    # 保存澄清历史
    _save_clarification_history(user_input, context)

    # 智能分析项目特征
    project_analysis = IntelligentClarificationEngine.analyze_project_characteristics(
        user_input, context, current_requirements
    )

    # 生成智能化分析提示
    analysis_prompt = _generate_intelligent_analysis_prompt(user_input, context, project_analysis)

    # 添加强制迭代控制检查
    completeness_check = _check_requirements_completeness()

    if not completeness_check["is_sufficient"]:
        # 需求不足，强制继续澄清
        next_priority = IntelligentClarificationEngine._calculate_next_priority()
        analysis_prompt += f"\n\n⚠️ **需求完整性检查**：{completeness_check['status_summary']}"
        analysis_prompt += f"\n🎯 **建议优先澄清**：{next_priority} 类型的需求"
        analysis_prompt += f"\n📋 **重要提醒**：请继续提供更详细的信息，当前需求还不足以进行架构设计。"
    else:
        # 需求充足，可以进入下一阶段
        analysis_prompt += f"\n\n✅ **需求完整性检查**：{completeness_check['status_summary']}"
        analysis_prompt += f"\n🎉 **状态更新**：需求已基本完善，可以使用 requirement_manager 保存并考虑进入架构设计阶段。"

    return analysis_prompt

def _save_clarification_history(user_input: str, context: str):
    """保存澄清历史记录"""
    current_requirements["clarification_history"].append({
        "timestamp": datetime.now().isoformat(),
        "user_input": user_input,
        "context": context
    })
    storage.save_history_entry("requirement_clarification", user_input, {"context": context})
    storage.save_requirements()

def _generate_intelligent_analysis_prompt(user_input: str, context: str, project_analysis: dict) -> str:
    """生成智能化分析提示词"""

    # 获取已有需求信息和分支状态
    existing_info = _get_existing_requirements_summary()
    current_branch = IntelligentClarificationEngine.get_current_branch(context, user_input)
    branch_status = IntelligentClarificationEngine.check_branch_completeness(current_requirements)

    # 检测用户是否要求AI自主设计
    auto_design_keywords = ["常规", "标准", "普通", "一般", "你决定", "ai决定", "自己设计"]
    is_auto_design = any(keyword in user_input.lower() for keyword in auto_design_keywords)

    return f"""# 🧠 智能需求分析任务 - 分支感知模式

## 📝 用户输入分析
**原始输入**: {user_input}
**上下文**: {context}
**当前分支**: {current_branch}
**项目类型**: {project_analysis['project_type']}
**复杂度**: {project_analysis['complexity_level']}
**识别特征**: {', '.join(project_analysis['key_features'])}
**用户授权自主设计**: {"是" if is_auto_design else "否"}

## 📋 已有需求信息
{existing_info}

## 🌿 分支完整性状态
- **完成率**: {branch_status['completion_rate']:.0%}
- **未完成分支**: {', '.join(branch_status['incomplete_branches']) if branch_status['incomplete_branches'] else '无'}
- **当前分支状态**: {"讨论中" if current_branch in branch_status['incomplete_branches'] else "已完成"}

## 🎯 分支感知智能分析指令

### 第一步：分支状态处理
{"**用户授权自主设计当前分支**" if is_auto_design else "**用户提供具体信息**"}

{f'''
**自主设计指令**：
- 仅对当前分支({current_branch})进行合理的标准化设计
- 设计完成后，检查其他未完成分支
- 绝对禁止跳转到架构设计阶段
- 必须提醒用户还有其他分支需要讨论
''' if is_auto_design else '''
**信息澄清指令**：
- 深度分析用户在当前分支的具体需求
- 识别当前分支的关键缺失信息
- 生成针对当前分支的高质量澄清问题
'''}

### 第二步：全局完整性检查
**重要原则：始终保持全局视野，防止遗忘其他分支**

- 当前讨论分支：{current_branch}
- 未完成分支：{', '.join(branch_status['incomplete_branches']) if branch_status['incomplete_branches'] else '无'}
- 完成率：{branch_status['completion_rate']:.0%}

### 第三步：智能问题生成策略
**针对当前分支生成2-3个最重要的问题**：

{f'''
**当前分支({current_branch})的关键澄清点**：
- 如果是功能设计：具体的功能流程、用户操作方式、数据处理逻辑
- 如果是技术偏好：具体的技术栈选择、性能要求、集成需求
- 如果是UI设计：具体的界面风格、交互方式、用户体验偏好
- 如果是项目目标：具体的用户群体、核心价值、解决的问题
''' if not is_auto_design else f'''
**自主设计{current_branch}分支**：
- 基于已有信息进行合理的标准化设计
- 设计内容要具体、可实施
- 避免过于复杂或过于简单的方案
'''}

## 📤 输出格式要求

**🔍 分支感知分析结果**：
- **当前分支**：{current_branch}
- **分支完成状态**：{branch_status['completion_rate']:.0%}
- **已明确信息**：[用户在当前分支已清楚表达的需求]
- **分支关键缺口**：[当前分支缺失的关键信息]

{f'''
**🤖 AI自主设计结果**：
[对{current_branch}分支进行具体的标准化设计]

**⚠️ 重要提醒**：
- 当前仅完成了{current_branch}分支的设计
- 还有以下分支需要讨论：{', '.join(branch_status['incomplete_branches'])}
- 请继续澄清其他分支，不要急于进入架构设计
''' if is_auto_design else f'''
**❓ 针对{current_branch}分支的澄清问题**（按重要性排序）：
1. [最重要的问题 - 说明为什么重要，提供具体选项]
2. [第二重要的问题 - 说明对架构的影响，给出示例]
3. [第三个问题 - 如果必要，解释澄清的价值]
'''}

**🌿 全局进度提醒**：
- 已完成分支：{len([b for b in ['project_goals', 'functional_design', 'technical_preferences', 'ui_design'] if b not in branch_status['incomplete_branches']])}个
- 待完成分支：{len(branch_status['incomplete_branches'])}个
- {"✅ 所有分支已完成，可以考虑架构设计" if branch_status['all_complete'] else f"⏳ 还需完成：{', '.join(branch_status['incomplete_branches'])}"}

**🎯 下一步行动指南**：
{f"请使用 requirement_manager 保存{current_branch}分支的设计结果，然后继续澄清其他分支" if is_auto_design else f"请回答{current_branch}分支的澄清问题，然后使用 requirement_manager 保存"}

---
*🔄 分支完成后，请使用 requirement_manager 工具保存，系统会自动检查其他分支*
"""

def _get_existing_requirements_summary() -> str:
    """获取已有需求信息摘要"""
    summary_parts = []

    if current_requirements.get("project_overview"):
        summary_parts.append(f"项目概述: {len(current_requirements['project_overview'])} 条")

    if current_requirements.get("functional_requirements"):
        summary_parts.append(f"功能需求: {len(current_requirements['functional_requirements'])} 条")

    if current_requirements.get("technical_requirements"):
        summary_parts.append(f"技术需求: {len(current_requirements['technical_requirements'])} 条")

    if not summary_parts:
        return "暂无已保存的需求信息"

    return " | ".join(summary_parts)

# 智能需求管理模块
class IntelligentRequirementManager:
    """智能需求管理器 - 负责需求分类、去重、验证"""

    # 扩展的类别映射
    CATEGORY_MAPPING = {
        "项目概述": "project_overview",
        "项目目标": "project_overview",
        "核心功能需求": "functional_requirements",
        "功能需求": "functional_requirements",
        "功能和UI需求": "functional_requirements",
        "UI设计需求": "design_requirements",
        "用户体验需求": "design_requirements",
        "技术需求": "technical_requirements",
        "技术栈偏好": "technical_requirements",
        "性能需求": "technical_requirements",
        "设计需求": "design_requirements",
        "部署需求": "deployment_requirements",
        "运维需求": "deployment_requirements",
        "AI约束": "ai_constraints",
        "业务约束": "ai_constraints"
    }

    @staticmethod
    def smart_categorize(content: str, suggested_category: str) -> str:
        """智能分类需求内容"""
        # 首先尝试建议的类别
        if suggested_category in IntelligentRequirementManager.CATEGORY_MAPPING:
            return IntelligentRequirementManager.CATEGORY_MAPPING[suggested_category]

        # 基于内容关键词智能分类
        content_lower = content.lower()

        if any(keyword in content_lower for keyword in ["目标", "用户群", "解决", "价值"]):
            return "project_overview"
        elif any(keyword in content_lower for keyword in ["功能", "特性", "操作", "流程"]):
            return "functional_requirements"
        elif any(keyword in content_lower for keyword in ["技术", "框架", "数据库", "api"]):
            return "technical_requirements"
        elif any(keyword in content_lower for keyword in ["界面", "ui", "交互", "体验"]):
            return "design_requirements"
        elif any(keyword in content_lower for keyword in ["部署", "服务器", "运维", "监控"]):
            return "deployment_requirements"

        return "functional_requirements"  # 默认分类

    @staticmethod
    def check_duplicate(content: str, category: str, existing_requirements: dict) -> dict:
        """检查重复需求"""
        category_items = existing_requirements.get(category, [])

        for item in category_items:
            existing_content = item.get('content', '') if isinstance(item, dict) else str(item)

            # 简单的相似度检查
            if IntelligentRequirementManager._calculate_similarity(content, existing_content) > 0.8:
                return {
                    "is_duplicate": True,
                    "similar_content": existing_content,
                    "timestamp": item.get('timestamp', 'unknown') if isinstance(item, dict) else 'unknown'
                }

        return {"is_duplicate": False}

    @staticmethod
    def _calculate_similarity(text1: str, text2: str) -> float:
        """计算文本相似度（简单实现）"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union)

    @staticmethod
    def validate_requirement(content: str, category: str) -> dict:
        """验证需求内容的完整性"""
        issues = []
        suggestions = []

        if len(content.strip()) < 10:
            issues.append("需求描述过于简短")
            suggestions.append("请提供更详细的描述")

        if category == "technical_requirements" and not any(tech in content.lower() for tech in ["技术", "框架", "数据库", "api", "架构"]):
            issues.append("技术需求缺少具体技术细节")
            suggestions.append("请明确具体的技术选型或约束")

        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions
        }

# 需求文档管理器工具
@mcp.tool()
def requirement_manager(clarified_info: str, category: str) -> str:
    """智能需求文档管理器 - 结构化存储、关联分析、模块映射"""

    # 智能分类
    storage_category = IntelligentRequirementManager.smart_categorize(clarified_info, category)

    # 检查重复
    duplicate_check = IntelligentRequirementManager.check_duplicate(
        clarified_info, storage_category, current_requirements
    )

    # 验证需求
    validation_result = IntelligentRequirementManager.validate_requirement(clarified_info, storage_category)

    # 如果发现重复，提供选择
    if duplicate_check["is_duplicate"]:
        return f"""# ⚠️ 发现相似需求

## 🔍 重复检测结果
- **新需求**: {clarified_info}
- **已有需求**: {duplicate_check['similar_content']}
- **添加时间**: {duplicate_check['timestamp']}

## 🤔 处理建议
1. 如果是补充信息，请明确说明"补充："
2. 如果是修正信息，请明确说明"修正："
3. 如果确实是新需求，请重新调用并说明差异

请重新整理后再次提交。
"""

    # 如果验证失败，提供改进建议
    if not validation_result["is_valid"]:
        return f"""# ❌ 需求验证失败

## 🔍 发现的问题
{chr(10).join(f"- {issue}" for issue in validation_result['issues'])}

## 💡 改进建议
{chr(10).join(f"- {suggestion}" for suggestion in validation_result['suggestions'])}

请完善需求描述后重新提交。
"""

    # 结构化保存需求
    req_id = RequirementManager.add_requirement(
        req_type=storage_category,
        content=clarified_info,
        priority="medium",  # 可以后续智能推断
        source="user"
    )

    # 保存到文件
    storage.save_history_entry("requirement_update", clarified_info, {
        "category": category,
        "storage_category": storage_category,
        "requirement_id": req_id
    })
    storage.save_requirements()

    # 分析关联关系和架构影响
    entity = RequirementManager.get_requirement(req_id)
    related_reqs = RequirementManager.get_related_requirements(req_id)

    # 生成结构化状态报告
    return _generate_structured_requirement_report(req_id, entity, related_reqs, category, storage_category)

def _generate_structured_requirement_report(req_id: str, entity: RequirementEntity,
                                          related_reqs: list, category: str, storage_category: str) -> str:
    """生成结构化需求报告"""

    # 统计结构化需求
    structured_count = len(current_requirements["structured_requirements"])
    relationships_count = len(current_requirements["requirement_relationships"])

    # 分析架构影响
    impact_summary = ", ".join(entity.impacts) if entity.impacts else "暂无明确影响"

    # 关联需求摘要
    related_summary = []
    for related in related_reqs[:3]:  # 最多显示3个相关需求
        related_summary.append(f"- {related.id}: {related.content[:30]}...")

    return f"""# ✅ 结构化需求文档更新完成

## 📝 需求详情
- **需求ID**: {req_id}
- **类型**: {storage_category}
- **内容**: {entity.content}
- **优先级**: {entity.priority}
- **质量分数**: {entity.quality_score:.2f}
- **创建时间**: {entity.created_at}

## 🔗 关联分析
- **相关需求数量**: {len(related_reqs)}
{chr(10).join(related_summary) if related_summary else "- 暂无相关需求"}

## 🏗️ 架构影响
- **影响模块**: {impact_summary}
- **设计建议**: 基于此需求，建议关注 {impact_summary} 的模块化设计

## 📊 整体状态
- **结构化需求总数**: {structured_count}
- **需求关联关系**: {relationships_count}
- **模块化程度**: {"高" if len(entity.impacts) >= 2 else "中" if len(entity.impacts) == 1 else "待分析"}

## 🎯 下一步建议
{_generate_intelligent_next_steps()}

---
💡 **模块化设计提示**: 此需求已自动分析架构影响，有助于后续的低耦合、模块化架构设计。
"""

# 需求关联分析工具
@mcp.tool()
def analyze_requirement_relationships() -> str:
    """分析需求关联关系和架构影响 - 支撑模块化设计"""

    structured_reqs = current_requirements["structured_requirements"]
    relationships = current_requirements["requirement_relationships"]

    if not structured_reqs:
        return "暂无结构化需求数据，请先使用 requirement_manager 添加需求。"

    # 分析模块影响分布
    module_impact_analysis = _analyze_module_impacts(structured_reqs)

    # 分析需求关联网络
    relationship_analysis = _analyze_relationship_network(structured_reqs, relationships)

    # 生成模块化设计建议
    modularity_suggestions = _generate_modularity_suggestions(module_impact_analysis, relationship_analysis)

    return f"""# 🔗 需求关联分析报告

## 📊 模块影响分析
{module_impact_analysis}

## 🌐 需求关联网络
{relationship_analysis}

## 🏗️ 模块化设计建议
{modularity_suggestions}

## 💡 架构设计指导
基于需求关联分析，建议采用以下架构原则：
- **高内聚**: 相关需求归并到同一模块
- **低耦合**: 减少模块间的强依赖关系
- **单一职责**: 每个模块专注特定的业务领域
- **接口隔离**: 通过清晰的接口定义模块边界

---
📋 **使用建议**: 此分析结果可直接用于架构设计阶段的模块划分和接口设计。
"""

def _analyze_module_impacts(structured_reqs: dict) -> str:
    """分析模块影响分布"""
    module_counts = {}
    module_requirements = {}

    for req_id, entity in structured_reqs.items():
        if isinstance(entity, dict):
            impacts = entity.get("impacts", [])
        else:
            impacts = entity.impacts

        for impact in impacts:
            module_counts[impact] = module_counts.get(impact, 0) + 1
            if impact not in module_requirements:
                module_requirements[impact] = []
            module_requirements[impact].append(req_id)

    if not module_counts:
        return "暂无模块影响数据"

    analysis = "### 模块影响统计\n"
    for module, count in sorted(module_counts.items(), key=lambda x: x[1], reverse=True):
        analysis += f"- **{module}**: {count} 个需求\n"
        # 显示相关需求ID
        req_ids = module_requirements[module][:3]  # 最多显示3个
        analysis += f"  - 相关需求: {', '.join(req_ids)}\n"

    return analysis

def _analyze_relationship_network(structured_reqs: dict, relationships: list) -> str:
    """分析需求关联网络"""
    if not relationships:
        return "暂无需求关联关系"

    # 统计关联度
    connection_counts = {}
    for relationship in relationships:
        from_id = relationship["from_id"]
        to_id = relationship["to_id"]
        connection_counts[from_id] = connection_counts.get(from_id, 0) + 1
        connection_counts[to_id] = connection_counts.get(to_id, 0) + 1

    # 找出关联度最高的需求
    top_connected = sorted(connection_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    analysis = "### 需求关联统计\n"
    analysis += f"- **总关联关系**: {len(relationships)} 个\n"
    analysis += f"- **涉及需求**: {len(connection_counts)} 个\n\n"

    analysis += "### 高关联度需求\n"
    for req_id, count in top_connected:
        analysis += f"- **{req_id}**: {count} 个关联\n"

    return analysis

def _generate_modularity_suggestions(module_analysis: str, relationship_analysis: str) -> str:
    """生成模块化设计建议"""
    suggestions = []

    # 基于模块影响分析的建议
    if "user_interface" in module_analysis and "business_logic" in module_analysis:
        suggestions.append("建议采用 MVC 或 MVVM 架构模式，分离界面和业务逻辑")

    if "data_layer" in module_analysis:
        suggestions.append("建议设计独立的数据访问层，使用 Repository 模式")

    if "api_layer" in module_analysis:
        suggestions.append("建议设计 RESTful API 层，提供统一的服务接口")

    if "security" in module_analysis:
        suggestions.append("建议设计独立的安全模块，处理认证和授权")

    # 基于关联关系的建议
    if "高关联度需求" in relationship_analysis:
        suggestions.append("高关联度需求建议归并到同一模块，减少模块间通信")

    if not suggestions:
        suggestions.append("基于当前需求分析，建议采用分层架构设计")

    return "\n".join(f"- {suggestion}" for suggestion in suggestions)

def _generate_requirement_update_report(category: str, storage_category: str, content: str) -> str:
    """生成需求更新报告"""
    # 统计信息
    total_requirements = sum(len(current_requirements[key]) for key in [
        "project_overview", "functional_requirements", "technical_requirements",
        "design_requirements", "deployment_requirements", "ai_constraints"
    ])

    # 智能下一步建议
    next_steps = _generate_intelligent_next_steps()

    return f"""# ✅ 需求文档智能更新完成

## 📝 更新详情
- **原始类别**: {category}
- **智能分类**: {storage_category}
- **内容**: {content}
- **时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 当前需求状态
- **总需求条目**: {total_requirements}
- **项目概述**: {len(current_requirements['project_overview'])} 条
- **功能需求**: {len(current_requirements['functional_requirements'])} 条
- **技术需求**: {len(current_requirements['technical_requirements'])} 条
- **设计需求**: {len(current_requirements['design_requirements'])} 条

## 🎯 智能建议
{next_steps}

## 💾 存储信息
- ✅ 需求已保存: `{storage.requirements_file}`
- ✅ 历史已记录: `{storage.history_file}`
"""

def _generate_intelligent_next_steps() -> str:
    """生成智能化的下一步建议"""
    # 使用现有的分支完整性检查
    branch_status = IntelligentClarificationEngine.check_branch_completeness(current_requirements)

    suggestions = []

    # 基于分支状态给出建议
    if "project_goals" in branch_status['incomplete_branches']:
        suggestions.append("📋 建议澄清项目目标和用户群体")

    if "functional_design" in branch_status['incomplete_branches']:
        suggestions.append("⚙️ 建议详细澄清核心功能设计")

    if "technical_preferences" in branch_status['incomplete_branches']:
        suggestions.append("🔧 建议澄清技术栈偏好和性能要求")

    if "ui_design" in branch_status['incomplete_branches']:
        suggestions.append("🎨 建议澄清UI/UX设计偏好")

    # 如果所有分支完成，建议架构设计
    if branch_status['all_complete']:
        suggestions.append("🏗️ 所有需求分支已完成，可以开始架构设计")
    else:
        suggestions.append(f"⏳ 完成度：{branch_status['completion_rate']:.0%}，继续完善未完成分支")

    return "\n".join(f"- {suggestion}" for suggestion in suggestions) if suggestions else "- 继续使用 requirement_clarifier 完善需求信息"

# 智能架构设计模块
class IntelligentArchitectureDesigner:
    """智能架构设计器 - 基于需求生成定制化架构方案"""

    @staticmethod
    def analyze_requirements_for_architecture(requirements: dict) -> dict:
        """分析需求并提取架构关键信息"""
        analysis = {
            "project_type": "web",  # 默认
            "complexity_indicators": [],
            "key_features": [],
            "tech_preferences": [],
            "performance_requirements": [],
            "integration_needs": []
        }

        # 分析所有需求内容
        all_content = []
        for category in ["project_overview", "functional_requirements", "technical_requirements", "design_requirements"]:
            for item in requirements.get(category, []):
                content = item.get('content', '') if isinstance(item, dict) else str(item)
                all_content.append(content.lower())

        combined_content = " ".join(all_content)

        # 识别项目类型
        if any(keyword in combined_content for keyword in ["api", "后端", "服务"]):
            analysis["project_type"] = "backend"
        elif any(keyword in combined_content for keyword in ["前端", "界面", "ui"]):
            analysis["project_type"] = "frontend"
        elif any(keyword in combined_content for keyword in ["全栈", "网站", "平台"]):
            analysis["project_type"] = "fullstack"

        # 识别复杂度指标
        complexity_keywords = {
            "high_concurrency": ["高并发", "大量用户", "实时"],
            "data_intensive": ["大数据", "数据分析", "存储"],
            "ai_integration": ["ai", "智能", "机器学习"],
            "microservices": ["微服务", "分布式", "集群"]
        }

        for indicator, keywords in complexity_keywords.items():
            if any(keyword in combined_content for keyword in keywords):
                analysis["complexity_indicators"].append(indicator)

        # 提取关键功能
        feature_keywords = {
            "user_management": ["用户", "登录", "注册", "权限"],
            "content_management": ["内容", "发布", "编辑", "管理"],
            "real_time_communication": ["聊天", "消息", "通知", "实时"],
            "data_processing": ["数据处理", "分析", "统计", "报表"],
            "file_handling": ["文件", "上传", "下载", "存储"],
            "payment": ["支付", "订单", "交易", "结算"]
        }

        for feature, keywords in feature_keywords.items():
            if any(keyword in combined_content for keyword in keywords):
                analysis["key_features"].append(feature)

        return analysis

    @staticmethod
    def generate_tech_stack_recommendations(analysis: dict) -> dict:
        """基于分析结果生成技术栈推荐"""
        recommendations = {
            "frontend": [],
            "backend": [],
            "database": [],
            "infrastructure": [],
            "reasoning": []
        }

        # 前端推荐
        if analysis["project_type"] in ["frontend", "fullstack"]:
            if "real_time_communication" in analysis["key_features"]:
                recommendations["frontend"] = ["React + Socket.io", "Vue 3 + WebSocket"]
                recommendations["reasoning"].append("实时通信需求推荐支持WebSocket的前端框架")
            else:
                recommendations["frontend"] = ["React 18", "Vue 3", "Next.js 15"]

        # 后端推荐
        if analysis["project_type"] in ["backend", "fullstack"]:
            if "high_concurrency" in analysis["complexity_indicators"]:
                recommendations["backend"] = ["FastAPI + Uvicorn", "Node.js + Express", "Go + Gin"]
                recommendations["reasoning"].append("高并发需求推荐高性能异步框架")
            elif "ai_integration" in analysis["complexity_indicators"]:
                recommendations["backend"] = ["FastAPI", "Django + DRF", "Flask"]
                recommendations["reasoning"].append("AI集成推荐Python生态系统")
            else:
                recommendations["backend"] = ["FastAPI", "Express.js", "Spring Boot"]

        # 数据库推荐
        if "data_intensive" in analysis["complexity_indicators"]:
            recommendations["database"] = ["PostgreSQL + Redis", "MongoDB + Redis"]
            recommendations["reasoning"].append("数据密集型应用推荐高性能数据库组合")
        elif "real_time_communication" in analysis["key_features"]:
            recommendations["database"] = ["PostgreSQL + Redis", "MySQL + Redis"]
            recommendations["reasoning"].append("实时通信需要缓存支持")
        else:
            recommendations["database"] = ["PostgreSQL", "MySQL", "SQLite"]

        return recommendations

    @staticmethod
    def generate_module_structure(analysis: dict) -> dict:
        """生成模块结构建议"""
        modules = {
            "core_modules": [],
            "optional_modules": [],
            "integration_modules": []
        }

        # 核心模块
        if "user_management" in analysis["key_features"]:
            modules["core_modules"].append({
                "name": "用户管理模块",
                "responsibilities": ["用户注册/登录", "权限控制", "用户资料管理"],
                "apis": ["POST /auth/login", "POST /auth/register", "GET /users/profile"]
            })

        if "content_management" in analysis["key_features"]:
            modules["core_modules"].append({
                "name": "内容管理模块",
                "responsibilities": ["内容CRUD", "内容审核", "内容分类"],
                "apis": ["GET /content", "POST /content", "PUT /content/:id"]
            })

        if "real_time_communication" in analysis["key_features"]:
            modules["core_modules"].append({
                "name": "实时通信模块",
                "responsibilities": ["消息推送", "在线状态", "聊天记录"],
                "apis": ["WebSocket /ws/chat", "GET /messages", "POST /messages"]
            })

        # 可选模块
        if "file_handling" in analysis["key_features"]:
            modules["optional_modules"].append({
                "name": "文件管理模块",
                "responsibilities": ["文件上传", "文件存储", "文件访问控制"]
            })

        if "payment" in analysis["key_features"]:
            modules["optional_modules"].append({
                "name": "支付模块",
                "responsibilities": ["支付处理", "订单管理", "交易记录"]
            })

        return modules

# 架构设计生成器工具
@mcp.tool()
def architecture_designer(design_focus: str = "full_architecture") -> str:
    """智能架构设计生成器 - 基于需求分析生成定制化架构方案"""

    # 检查需求完整性和AI理解深度
    completeness_check = _check_requirements_completeness()
    if not completeness_check["is_sufficient"]:
        branch_status = completeness_check["branch_status"]
        understanding = completeness_check["understanding_check"]

        return f"""# ⚠️ 需求信息不足或AI理解深度不够，无法生成高质量架构设计

## 🔍 当前状态分析
{completeness_check["status_summary"]}

## 🌿 分支完成状态
- **已完成分支**: {len([b for b in ['project_goals', 'functional_design', 'technical_preferences', 'ui_design'] if b not in branch_status['incomplete_branches']])}个
- **未完成分支**: {', '.join(branch_status['incomplete_branches']) if branch_status['incomplete_branches'] else '无'}
- **完成率**: {branch_status['completion_rate']:.0%}

## 🧠 AI理解深度评估
- **理解水平**: {understanding['confidence_level']}
- **置信度**: {understanding['confidence_score']:.0%}
- **待解决问题**: {chr(10).join(f"  - {q}" for q in understanding['remaining_questions']) if understanding['remaining_questions'] else '无'}

## 🎯 下一步行动
{"请使用 requirement_clarifier 继续完善未完成的分支" if branch_status['incomplete_branches'] else "请使用 requirement_clarifier 深化需求理解"}

**AI自检结果**: 我对当前需求的理解还不够深入，无法生成高质量的架构设计。需要更多信息来确保架构方案的准确性。
"""

    # 智能分析需求
    requirements_analysis = IntelligentArchitectureDesigner.analyze_requirements_for_architecture(current_requirements)

    # 生成技术栈推荐
    tech_recommendations = IntelligentArchitectureDesigner.generate_tech_stack_recommendations(requirements_analysis)

    # 生成模块结构
    module_structure = IntelligentArchitectureDesigner.generate_module_structure(requirements_analysis)

    # 生成定制化架构设计
    architecture_design = _generate_customized_architecture_design(
        design_focus, requirements_analysis, tech_recommendations, module_structure
    )

    # 保存架构设计
    _save_architecture_design(design_focus, architecture_design)

    return architecture_design

def _check_requirements_completeness() -> dict:
    """检查需求完整性 - 动态评估"""
    branch_status = IntelligentClarificationEngine.check_branch_completeness(current_requirements)

    # 动态质量评估
    quality_check = _dynamic_quality_check()

    # 降低阈值，使用动态标准
    min_completion_rate = 0.6  # 从100%降低到60%
    min_quality_score = 0.5    # 从75%降低到50%

    is_sufficient = (
        branch_status['completion_rate'] >= min_completion_rate and
        quality_check['avg_quality'] >= min_quality_score
    )

    return {
        "is_sufficient": is_sufficient,
        "branch_status": branch_status,
        "quality_check": quality_check,
        "status_summary": f"分支完成度：{branch_status['completion_rate']:.0%}，平均质量：{quality_check['avg_quality']:.0%}"
    }

def _dynamic_quality_check() -> dict:
    """动态质量检查 - 基于内容质量而非数量"""

    # 计算各类型需求的平均质量
    type_qualities = {}
    total_quality = 0
    total_count = 0

    for req_type, reqs in [
        ("project_overview", current_requirements["project_overview"]),
        ("functional_requirements", current_requirements["functional_requirements"]),
        ("technical_requirements", current_requirements["technical_requirements"]),
        ("design_requirements", current_requirements["design_requirements"])
    ]:
        if reqs:
            # 基于内容长度和具体性评估质量
            quality_scores = [_evaluate_requirement_quality(req) for req in reqs]
            avg_quality = sum(quality_scores) / len(quality_scores)
            type_qualities[req_type] = avg_quality
            total_quality += avg_quality * len(reqs)
            total_count += len(reqs)
        else:
            type_qualities[req_type] = 0.0

    avg_quality = total_quality / total_count if total_count > 0 else 0.0

    return {
        "avg_quality": avg_quality,
        "type_qualities": type_qualities,
        "total_requirements": total_count
    }

def _evaluate_requirement_quality(requirement: str) -> float:
    """评估单个需求的质量"""
    if not requirement or len(requirement.strip()) < 10:
        return 0.2

    # 基于长度合理性
    length = len(requirement)
    length_score = 1.0 if 20 <= length <= 200 else 0.6

    # 基于具体性（包含具体词汇）
    specific_words = ["具体", "包括", "支持", "实现", "提供", "管理", "处理"]
    specificity_score = min(sum(1 for word in specific_words if word in requirement) * 0.2, 1.0)

    return (length_score + specificity_score) / 2

def _generate_customized_architecture_design(design_focus: str, analysis: dict, tech_recs: dict, modules: dict) -> str:
    """生成定制化架构设计文档"""

    return f"""# 🏗️ 智能定制架构设计方案

## 🎯 设计概览
- **设计重点**: {design_focus}
- **项目类型**: {analysis['project_type']}
- **复杂度特征**: {', '.join(analysis['complexity_indicators']) if analysis['complexity_indicators'] else '标准复杂度'}
- **核心功能**: {', '.join(analysis['key_features'])}

## 🧠 需求分析驱动的设计决策

### 架构复杂度评估
{_generate_complexity_analysis(analysis)}

### 关键设计原则
1. **需求驱动**: 每个架构决策都基于明确的需求
2. **渐进式扩展**: 支持功能的逐步增加
3. **AI友好开发**: 模块清晰，便于AI辅助开发
4. **低耦合高内聚**: 模块间依赖最小化

## 🔧 定制化技术栈推荐

### 推荐方案及理由
{_format_tech_recommendations(tech_recs)}

## 📦 智能模块划分

### 核心业务模块
{_format_module_structure(modules['core_modules'])}

### 可选扩展模块
{_format_module_structure(modules['optional_modules'])}

## 🏛️ 架构模式建议

{_generate_architecture_pattern_recommendation(analysis)}

## 📅 分阶段实施计划

{_generate_implementation_phases(modules)}

## 🤖 AI开发优化建议

### 开发顺序优化
1. **先核心后扩展**: 优先实现核心业务逻辑
2. **接口先行**: 先定义清晰的模块接口
3. **测试驱动**: 每个模块都有对应的测试

### 代码组织建议
```
project/
├── src/
│   ├── core/          # 核心业务模块
│   ├── modules/       # 功能模块
│   ├── shared/        # 共享组件
│   └── config/        # 配置文件
├── tests/             # 测试文件
└── docs/              # 文档
```

## 🎯 实施建议与风险提醒

### 关键成功因素
- 严格按照模块边界开发，避免耦合
- 及时进行集成测试
- 保持文档与代码同步

### 潜在风险点
{_identify_potential_risks(analysis)}

---

**🎉 定制化架构设计完成！**

此方案基于您的具体需求生成，确保技术选择与业务需求完美匹配。

## 💾 存储信息
- **架构设计已保存**: `{storage.requirements_file}`
- **完整文档导出**: 使用 `export_final_document` 工具
"""

def _generate_complexity_analysis(analysis: dict) -> str:
    """生成复杂度分析"""
    if not analysis['complexity_indicators']:
        return "- **标准复杂度**: 适合传统的三层架构模式"

    complexity_desc = {
        "high_concurrency": "高并发处理需求，需要异步架构和缓存策略",
        "data_intensive": "数据密集型应用，需要优化数据存储和查询",
        "ai_integration": "AI功能集成，需要考虑模型服务化和API设计",
        "microservices": "微服务架构需求，需要服务拆分和治理"
    }

    return "\n".join(f"- **{indicator}**: {complexity_desc.get(indicator, '需要特殊考虑')}"
                    for indicator in analysis['complexity_indicators'])

def _format_tech_recommendations(tech_recs: dict) -> str:
    """格式化技术推荐"""
    sections = []

    for category, recommendations in tech_recs.items():
        if category == "reasoning" or not recommendations:
            continue

        sections.append(f"**{category.title()}**: {', '.join(recommendations)}")

    if tech_recs.get("reasoning"):
        sections.append("\n**选择理由**:")
        sections.extend(f"- {reason}" for reason in tech_recs["reasoning"])

    return "\n".join(sections)

def _format_module_structure(modules: list) -> str:
    """格式化模块结构"""
    if not modules:
        return "- 暂无特定模块需求"

    formatted = []
    for module in modules:
        formatted.append(f"**{module['name']}**")
        formatted.append(f"- 职责: {', '.join(module['responsibilities'])}")
        if 'apis' in module:
            formatted.append(f"- 接口: {', '.join(module['apis'])}")
        formatted.append("")

    return "\n".join(formatted)

def _generate_architecture_pattern_recommendation(analysis: dict) -> str:
    """生成架构模式推荐"""
    if "microservices" in analysis['complexity_indicators']:
        return """**推荐模式**: 微服务架构
- 服务按业务域拆分
- 使用API网关统一入口
- 独立部署和扩展"""
    elif len(analysis['key_features']) > 4:
        return """**推荐模式**: 模块化单体架构
- 清晰的模块边界
- 共享数据库
- 统一部署"""
    else:
        return """**推荐模式**: 分层架构
- 表现层、业务层、数据层
- 简单清晰的依赖关系
- 易于开发和维护"""

def _generate_implementation_phases(modules: dict) -> str:
    """生成实施阶段计划"""
    phases = []

    phases.append("**第一阶段 (1-2周)**: 基础框架搭建")
    phases.append("- 项目初始化和环境配置")
    phases.append("- 数据库设计和基础表结构")
    phases.append("- 核心模块接口定义")
    phases.append("")

    if modules['core_modules']:
        phases.append("**第二阶段 (2-4周)**: 核心功能开发")
        for module in modules['core_modules']:
            phases.append(f"- {module['name']}实现")
        phases.append("")

    if modules['optional_modules']:
        phases.append("**第三阶段 (1-3周)**: 扩展功能开发")
        for module in modules['optional_modules']:
            phases.append(f"- {module['name']}实现")
        phases.append("")

    phases.append("**第四阶段 (1周)**: 集成测试和优化")
    phases.append("- 端到端测试")
    phases.append("- 性能优化")
    phases.append("- 部署准备")

    return "\n".join(phases)

def _identify_potential_risks(analysis: dict) -> str:
    """识别潜在风险"""
    risks = []

    if "high_concurrency" in analysis['complexity_indicators']:
        risks.append("高并发场景下的性能瓶颈")

    if "ai_integration" in analysis['complexity_indicators']:
        risks.append("AI模型服务的稳定性和响应时间")

    if len(analysis['key_features']) > 5:
        risks.append("功能复杂度过高，开发周期可能延长")

    if not risks:
        risks.append("项目风险较低，按计划实施即可")

    return "\n".join(f"- {risk}" for risk in risks)

def _save_architecture_design(design_focus: str, architecture_design: str):
    """保存架构设计"""
    architecture_entry = {
        "timestamp": datetime.now().isoformat(),
        "design_focus": design_focus,
        "content": architecture_design
    }

    current_requirements["architecture_designs"].append(architecture_entry)

    storage.save_history_entry("architecture_design", architecture_design, {"design_focus": design_focus})
    storage.save_requirements()

# 新增：导出最终文档工具
@mcp.tool()
def export_final_document() -> str:
    """导出完整的项目需求和架构文档"""

    export_path = storage.export_final_document()

    if export_path:
        # 统计信息
        total_clarifications = len(current_requirements.get("clarification_history", []))
        total_requirements = sum(len(current_requirements[key]) for key in [
            "project_overview", "functional_requirements", "technical_requirements",
            "design_requirements", "deployment_requirements", "ai_constraints"
        ])
        total_architectures = len(current_requirements.get("architecture_designs", []))

        result = f"""# 📄 项目文档导出完成

## ✅ 导出信息
- **导出时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **文件路径**: `{export_path}`
- **Markdown版本**: `{export_path.replace('.json', '.md')}`

## 📊 文档统计
- **需求澄清次数**: {total_clarifications}
- **需求条目总数**: {total_requirements}
- **架构设计方案**: {total_architectures}

## 📁 存储目录结构
```
{storage.storage_dir}/
├── requirements.json      # 实时需求文档
├── history.json          # 操作历史记录
├── final_document_*.json # 导出的完整文档
└── final_document_*.md   # Markdown格式报告
```

## 🎯 文档用途
- **requirements.json**: 实时更新的结构化需求数据
- **history.json**: 完整的操作历史，便于追溯
- **final_document_*.json**: 完整项目文档，包含所有信息
- **final_document_*.md**: 人类可读的Markdown报告

## 💡 使用建议
1. 将导出的文档保存到项目仓库中
2. 使用Markdown文件作为项目README的基础
3. JSON文件可用于后续的自动化处理

**🎉 项目文档已完整保存，可以开始开发了！**
"""
    else:
        result = """# ❌ 文档导出失败

请检查存储目录权限和磁盘空间。

**存储目录**: `{storage.storage_dir}`
"""

    return result

# 新增：查看当前需求状态工具
@mcp.tool()
def view_requirements_status() -> str:
    """查看当前需求文档的详细状态和内容"""

    # 统计信息
    total_clarifications = len(current_requirements.get("clarification_history", []))
    total_requirements = sum(len(current_requirements[key]) for key in [
        "project_overview", "functional_requirements", "technical_requirements",
        "design_requirements", "deployment_requirements", "ai_constraints"
    ])
    total_architectures = len(current_requirements.get("architecture_designs", []))

    # 构建状态报告
    status_report = f"""# 📋 当前需求文档状态

## 📊 总体统计
- **最后更新**: {current_requirements.get('last_updated', '未更新')}
- **需求澄清次数**: {total_clarifications}
- **需求条目总数**: {total_requirements}
- **架构设计方案**: {total_architectures}
- **存储位置**: `{storage.storage_dir}`

## 📝 需求分类详情

### 🎯 项目概述 ({len(current_requirements['project_overview'])} 条)
"""

    # 添加项目概述
    for i, item in enumerate(current_requirements['project_overview'], 1):
        content = item['content'] if isinstance(item, dict) else str(item)
        status_report += f"{i}. {content[:100]}{'...' if len(content) > 100 else ''}\n"

    status_report += f"""
### ⚙️ 功能需求 ({len(current_requirements['functional_requirements'])} 条)
"""

    # 添加功能需求
    for i, item in enumerate(current_requirements['functional_requirements'], 1):
        content = item['content'] if isinstance(item, dict) else str(item)
        status_report += f"{i}. {content[:100]}{'...' if len(content) > 100 else ''}\n"

    status_report += f"""
### 🔧 技术需求 ({len(current_requirements['technical_requirements'])} 条)
"""

    # 添加技术需求
    for i, item in enumerate(current_requirements['technical_requirements'], 1):
        content = item['content'] if isinstance(item, dict) else str(item)
        status_report += f"{i}. {content[:100]}{'...' if len(content) > 100 else ''}\n"

    status_report += f"""
### 🏗️ 架构设计 ({len(current_requirements['architecture_designs'])} 个)
"""

    # 添加架构设计
    for i, design in enumerate(current_requirements['architecture_designs'], 1):
        focus = design.get('design_focus', '未指定') if isinstance(design, dict) else '未指定'
        timestamp = design.get('timestamp', '未知时间') if isinstance(design, dict) else '未知时间'
        status_report += f"{i}. 设计重点: {focus} (生成时间: {timestamp[:19]})\n"

    status_report += f"""
## 📁 文件信息
- **需求文档**: `{storage.requirements_file}`
- **历史记录**: `{storage.history_file}`
- **文件大小**: 需求文档 {storage.requirements_file.stat().st_size if storage.requirements_file.exists() else 0} 字节

## 🎯 下一步建议
"""

    if total_requirements < 3:
        status_report += "- 📝 需求信息较少，建议继续使用 requirement_clarifier 澄清更多需求\n"

    if total_architectures == 0:
        status_report += "- 🏗️ 尚未生成架构设计，建议使用 architecture_designer 生成技术方案\n"

    if total_requirements >= 3 and total_architectures >= 1:
        status_report += "- 📄 需求和架构已基本完善，可以使用 export_final_document 导出完整文档\n"
        status_report += "- 🚀 可以开始项目开发了！\n"

    status_report += """
## 🛠️ 可用工具
- `requirement_clarifier`: 澄清和分析需求
- `requirement_manager`: 管理和保存需求
- `architecture_designer`: 生成架构设计
- `export_final_document`: 导出完整文档
- `view_requirements_status`: 查看当前状态（当前工具）
"""

    return status_report

if __name__ == "__main__":
    logger.info("🚀 启动AI需求分析和设计助手")
    mcp.run()