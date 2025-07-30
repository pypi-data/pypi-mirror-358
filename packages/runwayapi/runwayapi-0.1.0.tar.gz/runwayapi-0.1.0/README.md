# RunwayAPI

RunwayAPI 是一个用于与 Runway ML 平台交互的 Python 库，提供了简单易用的接口来进行图片生成、视频生成等操作。

## 特性

- 完整的 Runway API 封装
- 支持图片生成和视频生成
- 支持会话管理
- 类型提示支持
- 简单易用的 API

## 安装

```bash
pip install runwayapi
```

## 快速开始

```python
from runwayapi import login, generate_image

# 登录获取token
token = login("your_username", "your_password")

# 获取用户ID
team_id = get_user_team_id(token)

# 创建会话
session_id = create_session(token, team_id)

# 生成图片
image_urls = generate_image(
    token=token,
    team_id=team_id,
    session_id=session_id,
    prompt="一只可爱的猫咪"
)
```

## API 文档

### 认证相关

#### `login(username: str, password: str) -> str`
使用用户名和密码登录 Runway，返回 JWT token。

#### `get_user_team_id(token: str) -> str`
获取用户的团队 ID。

### 会话管理

#### `create_session(token: str, team_id: str) -> str`
创建新的会话，返回会话 ID。

#### `get_sessions(token: str, team_id: str) -> list`
获取用户最近的50个会话。

#### `get_min_session_id(token: str, team_id: str) -> str`
获取任务数最少的会话 ID。

### 内容生成

#### `generate_image(token: str, team_id: str, session_id: str, prompt: str, seed: int = None) -> list[str]`
根据文本提示生成图片，返回图片URL列表。

#### `generate_video_for_gen3a(token: str, team_id: str, session_id: str, image_url: str, prompt: str, second: int = 5, seed: int = None) -> list[str]`
使用 Gen-3 Alpha 模型生成视频，返回视频URL。

### 资源管理

#### `upload_image(token: str, file_path: str) -> Optional[str]`
上传图片文件，返回图片URL。

### 状态检查

#### `is_can_generate_image(token: str, team_id: str) -> bool`
检查是否可以生成图片。

#### `is_can_generate_video(token: str, team_id: str, model: str, second: int) -> bool`
检查是否可以生成视频。

## 示例

### 生成图片

```python
from runwayapi import login, generate_image, get_user_team_id, create_session

# 登录
token = login("your_username", "your_password")
team_id = get_user_team_id(token)
session_id = create_session(token, team_id)

# 生成图片
images = generate_image(
    token=token,
    team_id=team_id,
    session_id=session_id,
    prompt="一只在草地上奔跑的金毛犬"
)

print(f"生成的图片URL: {images}")
```

### 生成视频

```python
from runwayapi import login, generate_video_for_gen3a, upload_image

# 登录
token = login("your_username", "your_password")
team_id = get_user_team_id(token)
session_id = create_session(token, team_id)

# 上传初始图片
image_url = upload_image(token, "path/to/your/image.jpg")

# 生成视频
video_url = generate_video_for_gen3a(
    token=token,
    team_id=team_id,
    session_id=session_id,
    image_url=image_url,
    prompt="一只金毛犬在草地上奔跑",
    second=5
)

print(f"生成的视频URL: {video_url}")
```

## 注意事项

1. 所有需要token的操作都需要先调用`login()`获取token
2. 图片生成和视频生成可能需要一定时间，函数会自动等待直到生成完成
3. 确保有足够的API额度才能进行生成操作
4. 上传图片时支持的格式：jpg, jpeg, png, gif

## 开发

1. 克隆仓库
```