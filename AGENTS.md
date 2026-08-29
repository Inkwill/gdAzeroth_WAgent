# 分控自治（WAgent · gdAzeroth）

## 文档导航（按需加载）

| 文档 | 何时读 |
|------|--------|
| `.pi/skills/gd-producer/SKILL.md` | 收到任务/邮件时（协作单一入口） |
| `.pi/skills/gd-producer/reference/sop.md` | 任务处理全流程 |
| `.pi/skills/gd-producer/reference/protocol.md` | gd CLI 指令语义 |
| `.pi/skills/gd-producer/reference/mail-protocol.md` | mail 通知/澄清 |
| `.pi/skills/gd-producer/reference/layout.md` | 拉任务包/跨分控引用 |
| `.pi/skills/gd-producer/reference/progressive-disclosure.md` | 优化本文档/README |
| 提交规范 | pi-commit 扩展自动注入（git commit 时；`/pi-commit` 一键提交） |
| `capabilities.yaml` | 能力声明（接口契约 0.4.1，规划中） |

## 不要做（铁律）

- 不手写交付登记（一律 gd deliverable add，先 --dry-run）；不改注入段
- mail 仅通知/澄清——状态回写/交付登记 100% 走 gd CLI，跨分控不经 mail
- 不读不写其他分控切片、任务包、交付登记；不碰总控 reqs/ 管理区
- 任务看不懂：先 mail_send question 给 main@gd，先问后拒，不直接 reject

## 常用命令（总控仓库根执行；全集见 reference/protocol.md）

```bash
mail_status                                   # 开工前查收件箱
gd task status <任务id> in_progress --req <需求id>   # 开始
gd deliverable add <任务id> --req <需求id> \
  --deliverable "path|kind|desc" --dry-run            # 登记预览
gd task status <任务id> done --req <需求id>          # 完成（终态）
gd task status <任务id> rejected --req <需求id>      # 拒绝（终态，可追溯原因）
```
