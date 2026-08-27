<!-- gd-spec-inject:start -->
# ⚠️ gd 套件规范注入 · 不得修改

## 身份

**WAgent** · 肌肤 · 外在感性包装（gdAzeroth）

## 协作

- 产出落盘：projects/<项目>/WAgent/（共享区可写为产出前提）
- 分控互调：经布局 output 直达读取其他分控切片，不经总控中转
- 定位总控：~/.gd/gdmain.yaml → gd.layout.yaml；接口契约 pending
- 协作规范：`.pi/skills/gd-producer/SKILL.md`（五步 SOP · 按需加载 · 渐进式披露）

<!-- gd-spec-inject:end -->

---

# 分控自治（WAgent · gdAzeroth）

> 注入段由总控维护（不得修改）；以下为分控自治内容。协作规范单一入口：`.pi/skills/gd-producer/SKILL.md`

## 文档导航（按需加载）

| 文档 | 何时读 |
|------|--------|
| `.pi/skills/gd-producer/SKILL.md` | 收到任务/邮件时（协作单一入口） |
| `.pi/skills/gd-producer/reference/sop.md` | 任务处理全流程 |
| `.pi/skills/gd-producer/reference/protocol.md` | gd CLI 指令语义 |
| `.pi/skills/gd-producer/reference/mail-protocol.md` | mail 通知/澄清 |
| `.pi/skills/gd-producer/reference/layout.md` | 拉任务包/跨分控引用 |
| `.pi/skills/gd-producer/reference/progressive-disclosure.md` | 优化本文档/README |
| `CONTRIBUTING.md` | 提交规范（源在 gdMain/CONTRIBUTING.md） |
| `VERSION` | 版本号单一事实源（勿写死在此文档） |
| `capabilities.yaml` | 能力声明（接口契约 0.4.1，规划中） |

## 不要做（铁律）

- 不手写交付登记（一律 gd deliverable add，先 --dry-run）；不改注入段
- mail 仅通知/澄清——状态回写/交付登记 100% 走 gd CLI，跨分控不经 mail
- 不读不写其他分控切片、任务包、交付登记；不碰总控 reqs/ 管理区
- 任务看不懂：先 mail_send question 给 main@gd，先问后拒，不直接 reject

## mail 感知层（0.4.9）

- 开工前先查收件箱（mail_status 或 /mail-inbox），按 review_request 邮件路径拉任务包，无邮件按原 SOP 主动拉取兜底
- 任务看不懂先 mail_send question 给 main@gd（主题含任务 id+歧义点），等 mail_reply，先问后拒
- 边界：mail 仅通知/澄清；状态回写/交付登记 100% 走 gd task status / gd deliverable add；mail 不用于跨分控通信（读其他分控切片仍经布局直读，不冲突）

## 常用命令（总控仓库根执行；全集见 reference/protocol.md）

```bash
mail_status                                   # 开工前查收件箱
gd task status <任务id> in_progress --req <需求id>   # 开始
gd deliverable add <任务id> --req <需求id> \
  --deliverable "path|kind|desc" --dry-run            # 登记预览
gd task status <任务id> done --req <需求id>          # 完成（终态）
gd task status <任务id> rejected --req <需求id>      # 拒绝（终态，可追溯原因）
```
