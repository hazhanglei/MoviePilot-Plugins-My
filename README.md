# MoviePilot 媒体库封面生成插件仓库

这是一个为 MoviePilot v2 创建的第三方插件仓库，包含 Emby 媒体库封面生成插件。

## 插件列表

| 插件名称 | 描述 | 版本 |
|---------|------|------|
| Emby媒体库封面生成V2 | 生成媒体库动态/静态封面，支持 Emby/Jellyfin | 1.0.0 |

## 安装方法

### 步骤 1：创建 GitHub 仓库

1. 登录 GitHub，创建一个新的公开仓库（例如：`MoviePilot-Plugins-My`）
2. 将本目录下的以下文件上传到仓库：
   - `package.v2.json`（放在仓库根目录）
   - `plugins.v2/mediacovergenerator/` 整个目录

### 步骤 2：配置 MoviePilot 插件市场

1. 打开 MoviePilot → 设置 → 系统
2. 找到 **插件市场** 配置项
3. 在原有地址后面添加你的仓库地址（用逗号分隔）：

```
https://github.com/你的用户名/MoviePilot-Plugins-My/
```

完整配置示例：
```
https://github.com/jxxghp/MoviePilot-Plugins/,https://github.com/你的用户名/MoviePilot-Plugins-My/
```

### 步骤 3：安装插件

1. 进入 MoviePilot → 插件 → 插件市场
2. 刷新插件列表
3. 找到「Emby媒体库封面生成」插件
4. 点击安装

## 仓库目录结构

```
MoviePilot-Plugins-My/
├── package.v2.json          # 插件清单文件（必需）
├── plugins.v2/              # v2插件目录
│   └── mediacovergenerator/ # 插件目录（目录名必须与插件类名小写匹配）
│       └── __init__.py      # 插件主文件
└── README.md                # 说明文档
```

## 依赖说明

本插件依赖以下 Python 包（MoviePilot 已内置，无需额外安装）：
- pillow >= 9.1.1
- numpy >= 1.21.0

## 功能特性

- ✅ 支持三种封面风格：经典、现代、极简
- ✅ 自定义封面分辨率
- ✅ 显示媒体数量统计
- ✅ 兼容 Emby/Jellyfin

## 常见问题

### Q: 插件市场看不到我的插件？

检查以下几点：
1. 仓库必须是公开的 GitHub 仓库
2. `package.v2.json` 必须在仓库根目录
3. 插件目录名必须与插件类名的小写形式一致
4. 确保插件市场地址配置正确

### Q: 安装时提示依赖不兼容？

本插件已修复依赖版本问题，使用宽松的版本约束：
- pillow >= 9.1.1（而非固定版本）
- numpy >= 1.21.0（而非固定版本）

如果仍有问题，请检查 MoviePilot 的 Python 环境。
