# 使用playwright操作浏览器

## 包管理
使用uv

## 安装依赖
clone项目后，使用uv安装依赖：
```bash
uv sync
```

执行代码前激活虚拟环境：
```bash
source .venv/bin/activate
```

安装三方包:
```bash
uv add playwright==1.51.0
```


## Tools调试

启动mcp调试工具：
```bash
uv run mcp dev src/office_assistant_mcp/mcp_server.py
```
打开调试：http://127.0.0.1:6274 

## 开发

为了能执行examples/下的文件，需要在根目录下安装office_assistant_mcp包：
```bash
uv pip install -e .
```

## 打包

```bash
uv build
```

## 发布
上传到pypi，X替换为最新版本号
```bash
uv run twine upload dist/office_assistant_mcp-0.0.X*
```




