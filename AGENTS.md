# 分控自治（WAgent · gdAzeroth）

> 协作规范单一事实源：gdMain 仓库 `skills/gd-producer/`（本仓库经 `.pi/settings.json` 引用，**勿建本地副本**）

## 文档导航（按需加载）

| 文档 | 何时读 |
|------|--------|
| `.pi/skills/gd-producer/SKILL.md` | 收到任务/邮件时（协作单一入口） |
| `.pi/skills/gd-producer/reference/sop.md` | 任务处理全流程 |
| `.pi/skills/gd-producer/reference/protocol.md` | gd CLI 指令语义 |

提交规范由 pi-commit 扩展自动注入；能力声明见 `capabilities.yaml`（仓库根）。

## 不要做（铁律）

- 不手写交付登记（一律 gd deliverable add，先 --dry-run）；不改注入段
- mail 仅通知/澄清——状态回写/交付登记 100% 走 gd CLI，跨分控不经 mail
- 不读不写其他分控切片、任务包、交付登记；不碰总控 reqs/ 管理区
- 任务看不懂：先 mail_send question 给 main@gd；**0.5.0 无 rejected**——不接 = 保持 new + mail question

## 常用命令（总控仓库根执行；全集见 reference/protocol.md）

```bash
mail_status                                   # 开工前查收件箱
gd task status <任务id> accepted --req <需求id>     # 认领（0.5.0：读 task-list 标记 accepted，取代拉取任务包）
gd task status <任务id> in_progress --req <需求id>  # 开始
gd deliverable add <任务id> --req <需求id> \
  --deliverable "deliver_wa/xxx.md|kind|desc" --dry-run   # 登记预览（0.5.0：产出 deliver_wa/）
gd task status <任务id> done --req <需求id>          # 交付完成
# 不接 = 保持 new + mail question（0.5.0 无 rejected）
```
