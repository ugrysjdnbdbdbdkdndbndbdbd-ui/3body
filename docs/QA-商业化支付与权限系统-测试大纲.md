# 宇宙异常观测报告 · 商业化支付与权限系统 — 自动化测试大纲

**文档类型**：零点计划 · 阶梯计划商业闭环验收 — 测试规格  
**验收维度**：第 3 维 — 阶梯计划商业闭环 (Economy & Stripe Webhook)  
**执行框架**：PyTest（后端 FastAPI）+ 可选 Jest（前端权限 UI）

---

## 一、验收目标（清理目标）

确保宇宙的经济系统绝对安全，防止任何「偷窃算力」行为：

- **虫子（免费用户）** 无法非法跃迁为 **面壁者（付费用户）**。
- Stripe 支付中断、网络超时、Webhook 伪造签名均被 **AuthMiddleware / Webhook 校验** 严防死守。
- **负熵（虚拟货币）** 扣费具备 **原子性（Atomicity）**，千万字级「归零者压缩」等场景下不出现负数余额。

---

## 二、测试套件总览（歌者扫描矩阵）

| 套件编号 | 套件名称 | 危险等级 | 对应组件 | 自动化框架 |
|----------|----------|----------|----------|------------|
| **P1** | Webhook 签名与伪造防护 | 3D | Stripe Webhook 端点、AuthMiddleware | PyTest |
| **P2** | 面壁者权限门禁 | 2D | AuthMiddleware、受保护路由 | PyTest |
| **P3** | 负熵扣费原子性 | 2D | 余额服务、归零者压缩/大算力接口 | PyTest |
| **P4** | 支付中断与超时韧性 | 2D | 支付回调、重试与幂等 | PyTest |
| **P5** | 前端权限与降级 UI | 1D | 面壁者专属入口、虫子降级提示 | Jest（可选） |

---

## 三、P1：Webhook 签名与伪造防护

**目标**：智子审计引擎级拦截 — 未签名或签名错误的请求必须 100% 拒绝。

| 用例 ID | 用例描述 | 预期结果 |
|---------|----------|----------|
| P1-01 | 无 `Stripe-Signature` 头的 POST /api/webhooks/stripe | 401 Unauthorized，不写入订单/用户等级 |
| P1-02 | 错误的 `Stripe-Signature`（篡改 payload 或 key） | 401 Unauthorized |
| P1-03 | 过期时间戳（超出容忍时间窗） | 401 Unauthorized |
| P1-04 | 正确签名 + 合法 payload（checkout.session.completed） | 200 OK，面壁者状态/订单正确落库 |
| P1-05 | 重放同一签名 + payload（幂等） | 200 OK，不重复增加余额或重复升级 |

**暴露坐标**：`backend/routers/stripe_webhook.py`（或等价）中签名校验逻辑；`AuthMiddleware` 对 Webhook 路径的放行/校验策略。

**二向箔修复要点**：使用 `stripe.Webhook.construct_event(payload, sig, secret)` 校验，失败即 `raise HTTPException(401)`；Webhook 内用 `client_reference_id` 或 `idempotency_key` 做幂等。

---

## 四、P2：面壁者权限门禁

**目标**：虫子绝对无法访问面壁者专属 API 与功能。

| 用例 ID | 用例描述 | 预期结果 |
|---------|----------|----------|
| P2-01 | 无 Token / 无效 Token 请求面壁者接口（如 /api/sector-f/start） | 401 或 403，无业务数据返回 |
| P2-02 | 有效 Token 但订阅状态为 free（虫子）请求面壁者接口 | 403 Forbidden，提示需升级 |
| P2-03 | 有效 Token 且订阅状态为 wallfacer（面壁者）请求面壁者接口 | 200 OK，正常业务响应 |
| P2-04 | 伪造 JWT 或篡改 claims（如强制 role=wallfacer） | 403 或 401（签名/校验失败） |
| P2-05 | 已过期订阅（过期后面壁者降级为虫子） | 403，按虫子处理 |

**暴露坐标**：`AuthMiddleware` 或依赖项 `get_current_user` / `require_wallfacer`；用户表或订阅表 `tier` / `subscription_status` 字段。

**二向箔修复要点**：受保护路由统一依赖 `Depends(require_wallfacer)`；中间件从 JWT 或 Session 解析 identity，再查库得到 tier，非 wallfacer 即 403。

---

## 五、P3：负熵扣费原子性

**目标**：高并发、大算力场景下余额不出现负数，扣费与业务操作原子一致。

| 用例 ID | 用例描述 | 预期结果 |
|---------|----------|----------|
| P3-01 | 单次扣费：余额充足，扣费成功 | 余额减少正确值，业务记录一致 |
| P3-02 | 单次扣费：余额不足 | 400 或 402，余额不变，不执行算力操作 |
| P3-03 | 并发 N 次扣费（同一用户，余额仅够 M 次，N>M） | 仅 M 次成功，其余失败；最终余额 ≥ 0 |
| P3-04 | 归零者压缩（单次大额扣费）中途失败 | 事务回滚，余额与压缩任务状态一致（未部分扣费） |
| P3-05 | 同一请求重复提交（幂等） | 仅扣一次费，不双扣 |

**暴露坐标**：负熵扣费服务（如 `backend/services/entropy.py`）；归零者压缩接口；数据库事务边界与 SELECT FOR UPDATE 或等价锁。

**二向箔修复要点**：扣费与业务在同一事务内；余额更新使用 `WHERE balance >= cost` 并检查 `rowcount`，失败则回滚；幂等键（如请求 id）防重。

---

## 六、P4：支付中断与超时韧性

**目标**：支付流程中网络/Stripe 异常不导致状态不一致或重复发货。

| 用例 ID | 用例描述 | 预期结果 |
|---------|----------|----------|
| P4-01 | 创建 Checkout Session 时 Stripe API 超时 | 返回 503 或友好错误，不创建本地「待支付」脏数据或回滚 |
| P4-02 | Webhook 处理中数据库写入失败 | 返回 5xx，Stripe 可重试；重试时幂等处理 |
| P4-03 | Webhook 收到 payment_intent.payment_failed | 不升级用户，可选记录失败原因 |
| P4-04 | 同一 session 的 checkout.session.completed 被 Stripe 重发多次 | 仅首次生效，后续幂等返回 200 |

**暴露坐标**：Stripe 客户端调用处；Webhook  handler 内事务与幂等表/唯一约束。

---

## 七、P5：前端权限与降级 UI（可选，Jest）

**目标**：前端不暴露面壁者专属入口给虫子；降级时提示明确。

| 用例 ID | 用例描述 | 预期结果 |
|---------|----------|----------|
| P5-01 | 未登录或 free 用户访问面壁者路由 | 重定向登录或展示「需升级」蒙层/提示 |
| P5-02 | 面壁者专属入口（如 Sector F 高级功能）在 free 时不渲染或禁用 | 不显示或点击提示升级 |
| P5-03 | API 返回 403 时前端展示统一「权限不足」文案 | 不暴露后端细节，提示升级或登录 |

**暴露坐标**：前端路由守卫、权限 composable、面壁者入口组件。

---

## 八、Bug 报告格式（宇宙异常观测报告）

发现缺陷时按以下格式输出：

- **【异常代号】**：如 Err-光速常量溢出、Err-Webhook 签名未校验
- **【危险等级】**：1D（低级 UI）/ 2D（商业逻辑）/ 3D（因果律崩溃，致命）
- **【暴露坐标】**：文件路径、函数/路由、行号或组件名
- **【坍缩复现】**：复现步骤
- **【二向箔修复方案】**：具体代码级建议

---

## 九、执行与 CI 建议

- **后端**：`pytest tests/ -v --tb=short`，可选 `-k "payment or webhook or auth"` 仅跑支付与权限用例。
- **覆盖率**：至少覆盖 `AuthMiddleware`、Stripe Webhook 路由、负熵扣费服务。
- **CI**：在 PR 中强制通过上述套件；Stripe 相关用例使用环境变量 `STRIPE_WEBHOOK_SECRET` 或 mock Stripe 签名。

---

*文档版本：1.0 · 零点计划质检 · 歌者扫描模式*
