# Workspace Backlog

Спільний беклог для всіх проектів на Pi5. Оновлюється вручну або через `chkp`/`chkp2` (додати інтеграцію — див. Infrastructure).

---

## 🔥 P0 — Memory Chain (найвищий пріоритет)

Виявлено 2026-04-21: Sam Phase 2 залишився активним у userMemories навіть після завершення. Це структурна проблема пам'яті, не Sam-specific.

- [ ] **`chkp` формат — додати явний `DONE:` маркер.** Коли фаза/епік завершений — писати в `done` аргумент префікс `DONE: Phase X` щоб extraction бачив сигнал закриття. Зараз `chkp` дає тільки positive signal про нову активність, але не негативний про завершення старої.
- [ ] **WARM.md `status` field — enforce у memory extraction prompt.** В YAML є `status: active|done|paused`, але memory extraction на нього не дивиться. Оновити prompt щоб items зі `status: done` не потрапляли в userMemories як активні.
- [ ] **Sync userMemories ↔ HOT/WARM.** Зараз вони незалежні, userMemories живе своє життя через Anthropic memory system. Треба або явна команда "sync memory" (скидає HOT.md в Claude і просить оновити), або regular `chkp2` робить це автоматично.
- [ ] **Post-mortem extraction bug**: Phase 2 Sam був у userMemories як активний навіть після завершення. Розібратись де саме signal loss — чи в chkp логах, чи в memory extractor prompt, чи в Anthropic-side recency heuristic.

---

## Sam

- [x] **Перенести `shared/curriculum/` → `sam/curriculum/`** (high, non-blocking)
  - Курікулом — доменна модель Сема, не shared-інфраструктура. Garcia deprecated, інші боти курікулом не використовують.
  - Кроки: перенести пакет, оновити імпорти у `modules/curriculum.py`, `modules/pinned.py`, `modules/state_manager.py`, `modules/proactive.py`, `main.py`. Прогнати `grep -r "shared.curriculum"`.
  - Коли: між пунктом (1) Renderer v2 і (2) Callback handlers Phase 2 — щоб не плодити нових імпортів у старому місці.
- [ ] `/nbstatus` — команда що показує які теми мають який NotebookLM-контент за форматами.
- [ ] `add_topic` tool — протестувати live через розмову з Sem, після чого прибрати підказку `/cur_add` з pinned footer.
- [ ] Case study doc `sam/docs/AGENTIC_LOOP_CASESTUDY.md` — розбір Sam agentic loop (tool dispatch, execute_tool, pipeline integration) + тема в курікулумі "Agentic Loop & Tool Use".
- [ ] `/pin` в меню бота (BotCommand list).
- [ ] Перезапустити rate-limited NBLM podcast генерацію (10 тем) + розібратись з 2 broken notebooks (agent_architecture-2, rag_retrieval-1).
- [ ] Одноразова міграція `learning_state.json.topics[*].formats_consumed` → `curriculum.json:topics[*].formats[*].consumed`. Без цього лічильник N/7 у pinned завжди показуватиме 0.
- [ ] Перенести `sam/modules/notebooklm.py` → `shared/` коли знадобиться іншому агенту (Garcia deprecated — можливо зняти пункт взагалі).
- [x] ~~Прибрати `Test Topic For Cleanup` з `sam/data/curriculum.json`~~ — видалено 2026-04-20.

## InSilver v3

- [ ] **При старті v4 — ПЕРШЕ ДІЛО**: оновити `insilver-v4-implementation-guide_v003.md` → v004.
  - Виправити `send_photo` → `photo`
  - Прибрати ручні `echo '{}' >handoff_state.json` між блоками (reset_command з `config/bots.yaml` робить це автоматом)
  - Додати реальний список assertions (`text_contains`, `admin_received`, `no_bot_response`, `order_saved`)
  - Переписати `09_handoff.json` і `10_order_funnel.json` з assertions замість покладатись на Haiku judge
  - Без цього плутанина між старою докою і реальністю гарантована.
- [ ] **Bug handoff**: PTB `Chat not found` коли бот перезапущений і peer не в кеші → `ctx.bot.send_message(admin_id)` падає. Потрібен fallback або warm-up peer cache при старті.

## Infrastructure

- [x] ~~**`chkp2.sh` bug:** не комітить зміни у `shared/`~~ — **закрито структурно 2026-04-20**: untrack sam/ з workspace-репо, тепер workspace і sam — два незалежні git-репо, комітяться окремо. Workspace-репо комітиться вручну (не через chkp2), sam — через chkp2.
- [x] ~~**`chkp2.sh` — прибрати інтерактивний `read -p`**~~ — **закрито 2026-04-20** (kit commit 4ade28a). Guard на існування файлів залишено, trust-модель: Claude оновлює 3 яруси ДО виклику chkp2 (див. sam/MEMORY.md секцію "One-shot template").
- [ ] **Об'єднати master→main** у workspace-репо: `git branch -m master main; git push -u origin main; git push origin --delete master` + перемкнути default у GitHub UI.
- [ ] **Великий catch-up commit** у workspace-репо: Phase 29 cleanup (`curriculum_engine.py`, `gen_queue.py`, `hub_renderer.py`), `shared/curriculum/` модифікації, ~30 untracked backup-файлів у sam/data/ і shared/. Ревізувати, пачками закомітити.
- [ ] Pi5 SD card backup strategy (high, non-blocking): rsync + Backblaze + dd-image.
- [ ] Автоматизувати file transfer Claude↔Pi5: MCP server / git branch / HTTP через Cloudflare tunnel. Обговорити після Sam curriculum v2.
- [ ] `chkp.sh` / `chkp2.sh` — додати append до `BACKLOG.md` коли Саша каже "в беклог: ...".
- [ ] **HOT.md чистка — 3 проекти** (abby-v2, garcia, sam показали оновлення, решта — abby, ed, household_agent, insilver-v3 — згадок `kit/projects.yaml` у HOT не було, скоріше у WARM). Перевірити WARM цих проектів і замінити `kit/projects.yaml` → `meta/chkp/projects.yaml`.
- [ ] **chkp3 template HOT.md** — перевірити чи шаблон `meta/chkp/templates/HOT.md` не містить старих згадок `kit/projects.yaml`. Інакше нові проекти через `--init` одразу мітимуть застарілі шляхи.
- [ ] **Abby-v2**: баг кнопки Image 4 (платне генерування не спрацьовує). Діагностувати при наступній роботі з Abby.

## Ed

### Прискорення тестів (дослідження + план)

**Проблема:** Ed funnel-тести йдуть довго (10-крокова воронка ~60-120с). Основний жерун — `MULTI_MESSAGE_DELAY=2.0s` після кожного повідомлення бота × Telethon round-trip.

**Що НЕ спрацює:**
- Direct transport у теперішньому вигляді — він викликає тільки `core.ai.ask_ai()` / `GarciaBrain.run()`, не бачить ConversationHandler, не підтримує команди/кнопки/фото/admin. Для funnel-тестів принципово не підходить. Адаптація під v2 ≈ написати mini-PTB-симулятор (15-25 год роботи, високий ризик розсинхрону з реальним ботом).
- Зменшення `MULTI_MESSAGE_DELAY` нижче 2.0s — ризик false-negative коли бот шле 3+ повідомлень поспіль.

**Що ДАСТЬ прискорення в рази:**
1. **Паралельний запуск блоків (P1)** — різні блоки одночасно через окремі Telethon-сесії або окремі target-боти. Очікуваний виграш: x2-4 на повній регресії. Обмеження: rate limits TG при одному target-боті, race conditions на shared state (handoff_state.json, orders.json). Рішення: або окремі тестові боти-клони, або послідовний запуск блоків що ділять стан + паралельний для незалежних.
2. **Pre-warm intent cache (P2)** — batch-виклик Haiku для всіх `click_intent` кроків тест-кейсу перед прогоном. Виграш: -500-1500ms на кожен новий intent. Допомагає тільки на перших прогонах нових тестів.
3. **Smarter silence detection (P3)** — адаптивний `MULTI_MESSAGE_DELAY`: якщо бот за останні N запитів завжди укладався в 0.8s — знижувати до 0.8s, якщо бував 2s+ — тримати 2.0s. Виграш: ~20-30%, це саме той "20%", який не влаштовує. Робити тільки якщо (1) не працює або не дає достатньо.

**План:** Починати з паралельного запуску (найбільший ROI, найнижчий ризик). Перед стартом — домовитись як боротись з shared state (handoff, orders). Естімейт: 4-6 год на MVP паралелізатора на рівні `main.py run --parallel` для незалежних блоків.

**Що direct ВСЕ Ж годиться робити:** блоки де тестується тільки AI-відповідь без воронки/кнопок (напр. `07_prompt_guardrails`). Там direct вже зараз швидший за telegram в рази. Можна явно мапити блоки→транспорт у suite config.

## Garcia

(deprecated, див. HOT/WARM Sam)

## Abby-v2

(порожньо)

## Meggy

(порожньо)

## Kit

(порожньо)
