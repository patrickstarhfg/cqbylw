# GitHub 大文件上传脚本 (Git LFS)
# ---------------------------------------------------------
# 此脚本将帮助你将 sjys_data 中的所有数据文件推送到仓库中。
# 它使用 Git LFS 来处理大的 .xlsx 和 .pdf 文件。

# 1. 进入工作目录
Set-Location "d:\重庆工商毕业论文"

# 2. 初始化 Git 仓库 (如果尚未初始化)
if (!(Test-Path ".git")) {
    git init
    git remote add origin https://github.com/patrickstarhfg/cqbylw.git
}

# 3. 初始化 Git LFS (处理大文件)
git lfs install

# 4. 追踪大文件类型
git lfs track "*.xlsx"
git lfs track "*.pdf"
git lfs track "*.zip"

# 5. 添加配置文件 (.gitattributes 是 LFS 追踪的关键)
git add .gitattributes

# 6. 添加所有解压后的数据文件
git add sjys_data/extracted/

# 7. 提交更改
git commit -m "Add large data files using Git LFS"

# 8. 推送到主分支
# 注意：这可能会提示你输入 GitHub 账号和密码/Token
git push -u origin main

Write-Host "大文件上传完成！" -ForegroundColor Green
