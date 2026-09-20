# TCM Study App — Data Schema (contract, do not change without updating all consumers)

All content is **繁體中文（台灣用字）**. Data lives in `data/*.json` (UTF-8, no BOM).
The final single-file app inlines every JSON into one `window.TCM_DATA` object via `build.py`.

Top-level keys of `window.TCM_DATA`:
`meta`, `curriculum`, `theory`, `herbs`, `formulas`, "acupoints" (meridians+points), `quiz`.

---

## data/theory.json  (~80 terms)
```json
{
  "concepts": [
    {
      "id": "t001",
      "term": "陰陽",
      "category": "陰陽",
      "definition": "一句到三句話的精確定義（繁中）。",
      "keyPoints": ["背诵要点1", "背诵要点2"]
    }
  ]
}
```
- `category` ∈ `陰陽` `五行` `藏象` `氣血津液` `經絡` `病因` `治則治法`（只用這 7 種）
- `id` 格式 `t###`，唯一。

## data/herbs.json  (~100 herbs)
```json
{
  "herbs": [
    {
      "id": "h001",
      "name": "黃芪",
      "category": "補氣藥",
      "nature": "微溫",
      "flavor": "甘",
      "channels": ["脾", "肺"],
      "dose": "9–30g",
      "efficacy": "補氣升陽，益衛固表，托毒生肌，利水退腫",
      "indications": "脾胃虛弱、中氣下陷、表虛自汗、氣虛水腫……",
      "caution": "表實邪旺、陰虛陽旺者不宜",
      "memo": "補氣長藥，氣中升陽之品"
    }
  ]
}
```
- `category` ∈ 中藥學章節：`解表藥` `清熱藥` `瀉下藥` `祛風濕藥` `化濕藥` `利水滲濕藥` `溫裡藥` `理氣藥` `消食藥` `止血藥` `活血祛瘀藥` `化痰止咳平喘藥` `安神藥` `平肝息風藥` `開竅藥` `補虛藥` `收澀藥`
- `id` 格式 `h###`；`channels` 用單字臟腑名（脾肺心腎肝膽胃小腸大腸膀胱三焦心包）。

## data/formulas.json  (~60 formulas)
```json
{
  "formulas": [
    {
      "id": "f001",
      "name": "四君子湯",
      "category": "補益劑",
      "composition": [
        {"herb": "人參", "role": "君"},
        {"herb": "白朮", "role": "臣"},
        {"herb": "茯苓", "role": "佐"},
        {"herb": "甘草", "role": "使"}
      ],
      "function": "益氣健脾",
      "indications": "脾胃氣虛證。面色㿠白，語聲低微，氣短乏力……",
      "analysis": "方中人參甘溫益氣、健脾養胃為君……（1–3 句）",
      "song": "四君子湯中和義，參朮甘草共煎成，益氣健脾基基礎，氣虛諸證效堪誇。"
    }
  ]
}
```
- `category` ∈ `解表劑` `清熱劑` `瀉下劑` `祛風濕劑` `開竅劑` `理氣劑` `消食劑` `止血劑` `理血劑` `化痰止咳平喘劑` `安神劑` `平肝息風劑` `補益劑` `固澀劑` `腫瘍劑等其他`
- `role` ∈ `君` `臣` `佐` `使`；`id` 格式 `f###`。

## data/acupoints.json
```json
{
  "meridians": [
    {"id": "m01", "name": "手太陰肺經", "short": "肺經", "count": 11, "note": "起於中焦，下絡大腸……"}
  ],
  "points": [
    {
      "id": "a001",
      "name": "中府",
      "meridian": "m01",
      "location": "鎖骨下窩外側，前正中线旁開6寸",
      "indications": "咳嗽、氣喘、胸滿、肩背痛",
      "method": "斜刺或平刺0.5–0.8寸，不可深刺",
      "special": "肺之募穴；手太陰、足太陰之會"
    }
  ]
}
```
- `meridians` 全 14 條：手三陰(肺/心包/心)、手三陽(大腸/三焦/小腸)、足三陽(胃/膽/膀胱)、足三陰(脾/肝/腎)、任脈、督脈。`id` `m01`–`m14`。
- `points` ~120 個重點穴，`meridian` 引用 meridian id。`special` 可為空字串。

## data/quiz.json  (~40 手動理論題；藥/方/穴的選擇題由 app 從資料自動生成)
```json
{
  "questions": [
    {
      "id": "q001",
      "topic": "五行",
      "stem": "「木曰曲直」體現的特性是？",
      "options": ["生長、升發、條達", "清涼、收斂", "溫熱、上升", "潤下、閉藏"],
      "answer": 0,
      "explanation": "木性喜條達，主升發……"
    }
  ]
}
```
- `answer` 為 options 的 0-based index。`topic` ∈ theory 的 7 大 category。
- 4 個 options，length 恰為 4。

## data/curriculum.json  (學習路徑 — 已由主 agent 寫好，勿改結構)
```json
{
  "stages": [
    {
      "id": "s1", "title": "中医基础理論",
      "goal": "...", "howto": "...", "duration": "4–6 週",
      "tasks": [{"label": "...", "module": "theory", "filter": "陰陽"}],
      "milestone": "..."
    }
  ]
}
```
- `module` ∈ `theory` `herbs` `formulas` `acupoints`。

---

## App modules (index.html)
1. **學習路徑**：渲染 curriculum 五階段 + 進度（localStorage）。
2. **卡片記憶**：全部資料均可翻卡（正面 name/term，背面詳情），支援分類牌組過濾 + 「記得/不記得」計數。
3. **查詢工具書**：全域搜尋（名稱/功效/主治）+ 分類瀏覽 + 詳情。
4. **測驗考試**：手動題庫 + 自動生成題（藥性/歸經/方劑組成/穴位定位），可選範圍與題數，計分 + 錯題回顧。

進度/牌組狀態存 localStorage key prefix `tcm.`。
