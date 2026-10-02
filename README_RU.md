# SpaceClaim Named Selection Namer

Полуавтоматическая подготовка, проверка и исправление Named Selections для **ANSYS SpaceClaim 2021 R1 / Script API V19 / IronPython 2.7**.

**Текущая стабильная версия: v0.15.8**

Инженер по-прежнему сам выбирает геометрию, а инструмент автоматизирует имена, подсветку, QA и контролируемое исправление четырёх типов групп:

| Назначение | Геометрия | Последовательность | Подсветка |
| --- | --- | --- | --- |
| Weld pair | Faces или Edges | `w1a`, `w1b`, `w2a`, `w2b`, ... | A синяя, B красная |
| Bolt pair | Edges | `f1a`, `f1b`, `f2a`, `f2b`, ... | A синяя, B красная |
| Face Meshing | Faces | `fm1`, `fm2`, ... | синяя |
| Contact pair | только Faces | `ctkt1a`, `ctkt1b`, `ctkt2a`, `ctkt2b`, ... | A приглушённо-синяя, B песочная |

> Это скрипт для SpaceClaim Script Editor, а не ACT Extension и не DLL.

## Что нового в v0.15.8

Для `Contact pair (ctkt)` добавлен тот же контролируемый QA / Repair workflow, который используется для Weld pair. Для выбранной пары можно независимо по стороне A или B выполнить **Replace**, **Add**, **Remove** или **Create Missing**. Для `ctkt` ремонт намеренно ограничен **только Faces**. После изменения группа заново читается из модели и проверяется до обновления таблицы.

Сохранена схема цветов v0.15.7: Weld и Bolt — синий/красный, Face Meshing — синий, Contact — приглушённо-синий/песочный.

Подробности: [RELEASE_NOTES.md](RELEASE_NOTES.md) и [CHANGELOG.md](CHANGELOG.md).

## Скриншоты интерфейса

Ниже используются реальные изображения из рабочего SpaceClaim 2021 R1. Weld, Bolt и Face Meshing сняты на v0.15.7; Contact — уже на финальной v0.15.8 после проверки нового Contact QA / Repair workflow непосредственно в SpaceClaim.

### Weld pair

Главное окно Weld на реальной модели:

![Weld window v0.15.7](docs/images/v0157_weld_window.png)

Сине-красная подсветка Weld pair:

![Weld highlight v0.15.7](docs/images/v0157_weld_highlight.png)

QA / Repair Manager с таблицей и кнопками Add/Remove/Replace/Create Missing:

![Weld QA Repair](docs/images/v0157_weld_qa_repair.png)

### Bolt pair

Bolt mode после проверки существующих пар:

![Bolt window v0.15.7](docs/images/v0157_bolt_window.png)

Подсветка текущей A/B-пары:

![Bolt pair highlight](docs/images/v0157_bolt_pair_highlight.png)

Подсветка всех Bolt groups:

![Bolt all highlight](docs/images/v0157_bolt_all_highlight.png)

### Face Meshing

Face Meshing и кнопка аудита существующих групп:

![Face Meshing window v0.15.7](docs/images/v0157_face_meshing_window.png)

Пример Face Meshing surfaces в модели:

![Face Meshing model](docs/images/v0157_face_meshing_model.png)

### Contact pair

Финальный Contact mode v0.15.8 с активной кнопкой Contact QA / Repair Manager:

![Contact window v0.15.8](docs/images/v0158_contact_window.png)

Contact QA / Repair Manager на реальных группах `ctkt`. На скриншоте **Add to B** увеличивает `ctkt37b` до 8 Faces, после чего пара автоматически перечитывается и повторно валидируется:

![Contact QA Repair v0.15.8](docs/images/v0158_contact_qa_repair.png)

Старые подтверждённые скриншоты также оставлены в `docs/images/` как история разработки.

## Быстрый старт

1. Открыть модель в SpaceClaim и активировать **root component / root part**.
2. Открыть `Weld_Namer.py` в Script Editor.
3. Выбрать **API V19** и выполнить весь скрипт.
4. Выбрать нужный **Group purpose**.
5. Выделить геометрию в модели.
6. Нажать **Create Next**.
7. Использовать подсветку, audit или QA для выбранного режима.
8. Для Weld и Contact pair открыть **Named Selection QA / Repair Manager**, если группу нужно исправить.

Лог:

```text
%TEMP%\SpaceClaim_Weld_Namer_v012.log
```

## Кнопки главного окна

Полное описание каждой кнопки — в **[docs/USER_GUIDE_RU.md](docs/USER_GUIDE_RU.md)**. Краткая таблица:

| Элемент | Назначение |
| --- | --- |
| **Group purpose** | Переключает Weld, Bolt, Face Meshing и Contact. Для каждого режима своя независимая нумерация. |
| **Selection type** | Edges/Faces там, где это допускается. Bolt — только Edges; Face Meshing и Contact — только Faces. |
| **Create Next** | Создаёт первое свободное корректное имя. Существующие группы не перезаписываются. |
| **Check Next Name** | Показывает следующее имя без изменения модели. |
| **Auto highlight after Create** | После создания автоматически подсвечивает созданную пару/группу. |
| **Show names of highlighted Named Selections** | Добавляет временные подписи к подсвеченной геометрии. |
| **Label size (%)** | Масштаб временных подписей; CAD-геометрию не меняет. |
| **Bolt axis tolerance (degrees)** | Допуск проверки оси Bolt pair. По умолчанию 1°. |
| **Highlight Current Pair / Group** | Подсвечивает текущую логическую пару/группу. |
| **Highlight All ...** | Подсвечивает все группы активного режима. |
| **Clear Highlight** | Убирает подсветку пар, подписи и оранжевые QA-overlay. |
| **Weld / Contact QA / Repair Manager** | Табличный QA, навигация, CSV и контролируемое исправление. |
| **Check Existing Bolt Pairs** | Read-only проверка уже существующих Bolt pair. |
| **Check Existing Face Meshing** | Read-only проверка повторного использования Faces в `fm`. |
| **Find Groups for Selected Geometry** | Показывает группы активного режима, содержащие текущую выбранную геометрию. |

## QA / Repair Manager

Менеджер доступен для **Weld pair** и, начиная с v0.15.8, для **Contact pair**. В нём есть:

- таблица пар A/B с типом геометрии, количеством объектов, относительным отличием метрики, статусом и причиной;
- **Validate All** и **Show Problems Only**;
- **Highlight Problems** / **Clear Problem Highlight** — оранжевая подсветка проблем;
- **Previous Problem / Next Problem**;
- **Highlight Selected Pair** и **Zoom Selected Pair**;
- **Export CSV**;
- исправление по текущему primary selection SpaceClaim:
  - **Replace A / Replace B**;
  - **Add to A / Add to B**;
  - **Remove from A / Remove from B**;
  - **Create Missing A / Create Missing B**;
  - **Highlight Conflict**.

Для Contact pair ремонт принимает **только Faces**. Удаление блокируется, если после него Named Selection станет пустым. Любая мутация требует подтверждения, для существующей группы использует V19 `NamedSelection.Replace(...)`, затем повторно читает результат и запускает QA для пары.

QA здесь — проверка подготовки геометрии/модели, а **не** инженерный расчёт приемлемости сварного шва, болта или контакта.

## Поведение по режимам

### Weld pair (`w`)

- нумерация без учёта регистра, пропуски заполняются;
- Faces или Edges;
- одна сторона может содержать несколько объектов;
- A/B — синий/красный;
- QA проверяет отсутствующие/пустые группы, тип геометрии, повторное использование A/B, использование в других weld-группах, дубли имён, пропуски последовательности, отличие длины/площади;
- разница количества объектов A/B выводится как информация.

### Bolt pair (`f`)

- только Edges;
- ожидается одна полная круговая кромка отверстия на сторону;
- первая сторона может иметь статус **PENDING**, пока противоположная сторона не создана;
- завершённая пара проверяется относительно нормалей прилегающих плоских пластин;
- допуск по умолчанию 1°;
- **Check Existing Bolt Pairs** выдаёт OK / ERROR / INCOMPLETE и не меняет группы.

### Face Meshing (`fm`)

- только Faces;
- Create Next останавливается, если выбранная поверхность уже входит в другую `fm`-группу;
- **Check Existing Face Meshing** проверяет существующие группы и подсвечивает пересечения;
- audit ничего не изменяет.

### Contact pair (`ctkt`)

- только Faces;
- последовательное создание A/B;
- приглушённо-синий/песочный специально отделяет Contact от Weld/Bolt;
- поддерживаются временные подписи и поиск групп по выделенной геометрии;
- v0.15.8 добавляет Contact QA / Repair Manager с контролируемыми Add/Remove/Replace/Create Missing;
- инструмент создаёт и обслуживает Named Selections. Contact/Target и свойства контакта назначаются отдельно в Mechanical.

## Статус проверки

Стабильный Weld workflow проверен на реальной установке **SpaceClaim 2021 R1 / API V19 / IronPython 2.7**: большая Edge-based модель, A/B-подсветка, QA и Repair workflow.

Для v0.15.8 проходят **23 локальных regression test**: 16 тестов Bolt geometry/mutation guard и 7 статических тестов маршрутизации Contact Repair. После этого Contact QA / Repair workflow был проверен пользователем непосредственно в **SpaceClaim 2021 R1 / API V19**. На присланном скриншоте `Add to B` обновляет `ctkt37b` до 8 Faces, после чего пара автоматически перечитывается и повторно валидируется. Поэтому v0.15.8 публикуется как стабильная версия.

Подробнее: [docs/VALIDATION.md](docs/VALIDATION.md).

## Требования

- ANSYS SpaceClaim **2021 R1**
- Script API **V19**
- встроенный **IronPython 2.7**
- активная корневая деталь / root part при создании и исправлении

Другие версии SpaceClaim могут работать, но не заявлены как проверенные этой версией.

## Структура репозитория

```text
SpaceClaim-Weld-Namer/
├── Weld_Namer.py
├── README.md
├── README_RU.md
├── CHANGELOG.md
├── RELEASE_NOTES.md
├── VERSION
├── LICENSE
├── SUPPORT.md
├── docs/
│   ├── USER_GUIDE.md
│   ├── USER_GUIDE_RU.md
│   ├── ARCHITECTURE.md
│   ├── VALIDATION.md
│   ├── RELEASE_CHECKLIST.md
│   ├── DEVELOPMENT_NOTES.md
│   └── images/
├── tests/
└── tools/
```

## Связанный проект

**MPC184 Viewer:** https://github.com/maximofflove/MPC184Viewer

Weld mode подготавливает пары `wNa / wNb` для дальнейшего workflow в Mechanical.

## Лицензия

GNU General Public License v3.0. См. [LICENSE](LICENSE).

## Поддержка

Проект бесплатный и open source. Добровольная поддержка:

**https://boosty.to/ansys2021/donate**
