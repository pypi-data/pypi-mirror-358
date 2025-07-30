# AI Develop Assistant

协助AI开发者进行智能化需求完善、模块设计、技术架构设计的MCP工具

## 🔧 核心工具

1. **requirement_clarifier** - 需求澄清助手
2. **requirement_manager** - 需求文档管理器
3. **architecture_designer** - 架构设计生成器
4. **export_final_document** - 导出完整文档
5. **view_requirements_status** - 查看需求状态

## 📁 配置方法

### Claude Desktop配置

1. **找到配置文件位置**
   ```
   Windows: %APPDATA%\Claude\claude_desktop_config.json
   macOS: ~/Library/Application Support/Claude/claude_desktop_config.json
   Linux: ~/.config/claude/claude_desktop_config.json
   ```

2. **添加配置内容**
   ```json
   {
     "mcpServers": {
       "ai-develop-assistant": {
         "command": "uvx",
         "args": ["ai-develop-assistant@latest"],
         "env": {
           "MCP_STORAGE_DIR": "/path/to/your/storage"
         }
       }
     }
   }
   ```

3. **重启Claude Desktop**

## 📊 存储结构

配置成功后，会在指定目录生成以下文件：

```
your_storage_directory/
├── requirements.json      # 实时需求文档
├── history.json          # 操作历史记录
├── final_document_*.json # 导出的完整文档
└── final_document_*.md   # Markdown格式报告
```

## 🎯 使用说明

配置完成后，在Claude Desktop中即可使用以下工具：

- `requirement_clarifier` - 分析和澄清项目需求
- `requirement_manager` - 管理和保存需求信息
- `architecture_designer` - 生成技术架构设计
- `export_final_document` - 导出完整项目文档
- `view_requirements_status` - 查看当前分析状态

所有数据将保存在您指定的本地目录中。

## 💬 交流群

<div align="center">
<img src="./assets/qr-code.jpg" width="200" alt="交流群">
<br>
交流群
</div>


