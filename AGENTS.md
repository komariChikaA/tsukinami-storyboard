# 工作规则

GitHub Issues 是本项目的持久任务与验收记录。开始修改前查看对应 Issue、提交和交付记录，不只依靠聊天历史。

生命周期：Graveyard → Idle → Pending → WIP → Qualified → Ranked。类型与优先级独立记录。实现和技术检查完成后标记 Qualified；用户正式验收后才标记 Ranked 并关闭 Issue。

发生中断时保存代码并尽可能推送，在 Issue 留下完成项、待办、分支、成品位置、已做与未做的检查、具体续做步骤。不得把完成的渲染和生成大文件重新提交到源码仓库。

仅通过本机已有 GitHub CLI / Git Credential Manager / SSH agent 进行认证，不在输出、代码或提交里泄漏密钥。若执行环境启用 sandbox，认证 GitHub 操作应在宿主机执行；遵守环境本身允许的权限方式。

保持仓库整洁：只提交本 storyboard 实际使用的脚本、配置和素材。纹理必须与脚本引用一致；不加入编辑器接入、识别模型、通用压制工具或制作日志。`output/`、`work/`、模型、编译文件均忽略；视频与可移植 storyboard 包发布到 Release。

歌词不得固定在同一位置。四角交替、适量漂移，避开角色脸部；长句按语义分行。保留用户给出的日文词句，不采用 ASR 错词。

本项目任务完成或等待用户操作时，应发送中文邮件到 hiralove1c@yandex.com。默认本机通道：`powershell -NoProfile -ExecutionPolicy Bypass -File C:\Users\hiral\.codex\scripts\send-email.ps1 -Subject ... -BodyText ...`。密钥从本机私有配置读取，禁止打印和提交；通道不可用时在交付说明里明确告知。
