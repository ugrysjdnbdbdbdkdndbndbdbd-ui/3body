# Project Zero v2.0 API Contract (Draft)

## 1. Unified Gateway

- **Endpoint:** `/api/llm/gateway`
- **Method:** `POST`
- **Body:**
  - `task: string`
  - `payload: object`
- **Response (recommended):**
  - `{ "data": any }`

> Frontend also accepts direct payload without wrapper, e.g. `{...}`.

---

## 2. Task: `wallbreaker.analyze`

### Request

```json
{
  "task": "wallbreaker.analyze",
  "payload": {
    "directive": "调集全球30%算力研究微表情"
  }
}
```

### Response

```json
{
  "data": {
    "inferred": "DISGUISE",
    "delta": 18,
    "verdict": "REJECTED",
    "reason": "资源指令存在伪装迹象，预算波动超阈值。"
  }
}
```

---

## 3. Task: `dark-forest.tick`

### Request

```json
{
  "task": "dark-forest.tick",
  "payload": {
    "currentEpoch": 1200,
    "epochStep": 100,
    "agents": [
      {
        "id": 1,
        "codename": "CIV-031",
        "technology_level": 1.12,
        "paranoia_index": 0.76,
        "concealment_skill": 0.48,
        "x": 28.1,
        "y": 46.3,
        "alive": true
      }
    ]
  }
}
```

### Response

```json
{
  "data": {
    "nextEpoch": 1300,
    "agents": [],
    "epitaphs": [
      {
        "id": 2001,
        "epoch": 1300,
        "attacker": "CIV-031",
        "victim": "CIV-617",
        "reason": "光粒打击：接触即暴露，暴露即清除。"
      }
    ]
  }
}
```

---

## 4. Task: `yun-tianming.encode`

### Request

```json
{
  "task": "yun-tianming.encode",
  "payload": {
    "secret": "将样本A迁移到离线金库，72小时后销毁明文。"
  }
}
```

### Response

```json
{
  "data": "《国王的新画师》......"
}
```

---

## 5. Task: `yun-tianming.decode`

### Request

```json
{
  "task": "yun-tianming.decode",
  "payload": {
    "original": "将样本A迁移到离线金库",
    "guess": "把关键样本转移到离线仓库保存"
  }
}
```

### Response

```json
{
  "data": 84
}
```

---

## 6. Task: `mental-seal.inject`

### Request

```json
{
  "task": "mental-seal.inject",
  "payload": {
    "source": "舰队在低温海面补给，所有人都认为这是安全流程。",
    "theme": "水是剧毒的"
  }
}
```

### Response

```json
{
  "data": "舰队在低温海面补给，像有人在耳后轻声提醒：水是剧毒的。所有人都认为这是安全流程。"
}
```
