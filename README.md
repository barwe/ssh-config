默认的 SSH 主机列表存放在 `~/.ssh/config` 里面，不方便也不直观，因此写个 ssh-config 来管理 SSH 主机。

默认配置文件为 `$HOME/.config/ssh-config/ssh-config.tsv`

首先设置主密码：`ssh-config passwd <password>`

执行命令时可在子命令之前或者之后使用 `-p` 传递主密码，例如 `ssh-config -p <password> ps` 或者 `ssh-config ps -p <password>`

用法：
- `ps`: 打印所有主机信息
- `get <keyword>`: 在主机键名和主机名称中搜索
- `make`: 制作 ~/.ssh/config 文件（add/remove/update 会自动执行本操作）
- `open`: 打开 tsv 文件
- `open -t config`: 打开 ~/.ssh/config 文件
- `add`: 新建主机
- `remove <host>`: 删除主机
- `update <host> <field> <value>`: 更新主机信息
- `clean`: 清空备份
- `passwd <new_password>`: 重置密码