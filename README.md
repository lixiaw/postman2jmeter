# Postman2JMeter

将 Postman/ApiPost 导出的 JSON 文件转换为 JMeter 测试计划。

## 功能特性

- 支持 Postman Collection v2.1 格式
- 支持 ApiPost 导出的 JSON 格式
- 支持文件夹嵌套结构
- 自动转换为 JMeter ThreadGroup

## 使用方法

1. 选择转换模式（Postman/ApiPost）
2. 选择输入文件
3. 选择输出路径
4. 点击转换按钮

## 安装


## 代码使用

1. 安装开发依赖
```bash
pip install -r requirements.txt
```

2. 运行
```bash
py src/main.py
```

3. 安装项目

```bash
pip install -e .
```

4. 打包
```bash
python build_exe.py
```