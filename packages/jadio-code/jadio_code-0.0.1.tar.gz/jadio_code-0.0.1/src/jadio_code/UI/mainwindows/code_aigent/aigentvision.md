🧭 AIGENT VISION DOCUMENT
This document defines exactly how the Code.AIGent system is structured in my VS Code-like IDE.

It is not optional, not approximate — it is THE design.

✅ Overview
Code.AIGent is the entire persistent right-side panel of my IDE.

It is always present, always visible.

It is one unified module, split visually and logically into strict subcomponents:

sql
Copy
Edit
-----------------------------------------------------
| AIGENT_MENU   (top blue bar)                      |
|---------------------------------------------------|
| TOPBOX                                           |
| - AI_MODEL_SETTINGS                              |
| - LAN_SETTINGS                                   |
| - AI_TOOL_SET                                    |
| - LONG_CONTEXT                                   |
|---------------------------------------------------|
| CHAT WINDOW                                      |
|---------------------------------------------------|
| BOTTOMBOX                                        |
|---------------------------------------------------|
| AIGENT_SIDEBAR (vertical grey bar of buttons)    |
-----------------------------------------------------
✅ 1️⃣ AIGENT CONTROLLER
File:

bash
Copy
Edit
code_aigent/aigent_controller.py
Purpose:
⭐ The master QWidget that assembles all parts.
⭐ Always loaded.
⭐ Defines the layout for the entire AIGent panel.

Layout:

sql
Copy
Edit
QHBoxLayout
├── MainContent (LEFT) = QVBoxLayout
│   ├── AigentMenu
│   ├── TopBox
│   ├── ChatWindow
│   └── BottomBox
└── AigentSidebar (RIGHT)
✅ Left = Vertical stack of the 4 main sections.
✅ Right = Sidebar (grey vertical button bar).

✅ Imported by ui_backend to embed in the IDE.

✅ 2️⃣ AIGENT MENU
File:

bash
Copy
Edit
code_aigent/aigent_menu.py
Purpose:
⭐ Top horizontal blue bar.
⭐ Always present.
⭐ Contains buttons for:

Refresh Chat

New Chat

Old Chats

Etc.

✅ The first item in the vertical layout.

✅ 3️⃣ TOPBOX
Folder:

bash
Copy
Edit
code_aigent/topbox/
Controller:

Copy
Edit
topbox_controller.py
Purpose:
⭐ The orange area under the menu.
⭐ Contains 4 modes:

AI_MODEL_SETTINGS (topbox_modelsettings.py)

LAN_SETTINGS (topbox_lan.py)

AI_TOOL_SET (topbox_tools.py)

LONG_CONTEXT (topbox_context.py)

Behavior:
✅ Only one of these is visible at a time.
✅ When you click a button, its full panel fills the TopBox.

Layout inside TopBox:

pgsql
Copy
Edit
Button List (on left or top)
→ Clicking swaps central stacked widget.
✅ Note:
⭐ This is a tab system or stacked widget.
⭐ Must support dynamic switching.

✅ 4️⃣ CHAT WINDOW
Folder:

bash
Copy
Edit
code_aigent/chatwindow/
Controller:

Copy
Edit
aigent_chat_controller.py
Purpose:
⭐ The yellow middle section.
⭐ Always present.
⭐ Contains:

Scrollable chat history.

Summaries (via aigent_summary.py).

Behavior:
✅ Expands vertically.
✅ Shrinks if BottomBox terminal expands.
✅ Supports dynamic resizing.

✅ Layout:

diff
Copy
Edit
QVBoxLayout
- Chat history
- Summaries
✅ 5️⃣ BOTTOMBOX
Folder:

bash
Copy
Edit
code_aigent/bottombox/
Controller:

Copy
Edit
bottombox_controller.py
Purpose:
⭐ The blue bottom section.
⭐ Always present.
⭐ Contains:

✅ A) MINI TERMINAL STRIP

diff
Copy
Edit
- Current Context
- Quick Summary
✅ B) INPUT AREA

diff
Copy
Edit
- Start typing field
- Expand Terminal Button
- Hot-Swap Model Button
- Send Button
Behavior:
✅ If "Expand Terminal" is pressed, terminal expands upward.
✅ ChatWindow moves up accordingly.

✅ Layout:

diff
Copy
Edit
QVBoxLayout
- Mini Terminal
- Input Area
✅ 6️⃣ AIGENT SIDEBAR
File:

bash
Copy
Edit
code_aigent/aigent_sidebar.py
Purpose:
⭐ Always present vertical sidebar attached to the right edge of the AIGENT panel.
⭐ Fixed width.
⭐ Contains 4-5 vertical buttons/icons.

✅ Mirrors VS Code's Activity Bar.

Layout:

css
Copy
Edit
QVBoxLayout
- Button 1
- Button 2
- Button 3
- Button 4
...
Usage:
✅ Quick switches
✅ Tools
✅ Plugins
✅ Mode changes

✅ 7️⃣ FILE TREE MAPPING
css
Copy
Edit
code_aigent/
├── bottombox/
│   ├── bottombox_chat.py
│   ├── bottombox_context.py
│   ├── bottombox_controller.py
│   ├── bottombox_settings.py
│   └── bottombox_terminal.py
│
├── chatwindow/
│   ├── aigent_chat_controller.py
│   └── aigent_summary.py
│
├── topbox/
│   ├── topbox_context.py
│   ├── topbox_controller.py
│   ├── topbox_lan.py
│   ├── topbox_modelsettings.py
│   └── topbox_tools.py
│
├── aigent_controller.py  ← ROOT
├── aigent_menu.py        ← Top blue bar
└── aigent_sidebar.py     ← Grey vertical buttons
✅ Each controller manages its own section.

✅ aigent_controller.py is the only top-level "god" that assembles it all.

✅ 8️⃣ BEHAVIOR NOTES
✅ Nothing here is optional.
✅ Always renders all regions:

✅ Order matters:

scss
Copy
Edit
AigentMenu (light blue)
↓
TopBox (orange)
↓
ChatWindow (yellow, stretch)
↓
BottomBox (blue)
↓
AigentSidebar (grey)
✅ If BottomBox expands, ChatWindow resizes.

✅ TopBox swaps panels when buttons are clicked.

✅ Sidebar always visible.

✅ 9️⃣ UI-BACKEND INTEGRATION
✅ ui_backend.py will simply:

python
Copy
Edit
from code_aigent.aigent_controller import AigentController

aigent_panel = AigentController()
horizontal_splitter.addWidget(aigent_panel)
✅ ui_backend does not control any layout details inside Code.AIGent.

✅ 10️⃣ TL;DR SUMMARY
✅ Entire right side = Code.AIGent.
✅ Always present, always loaded.
✅ Modular by folders.
✅ 1:1 match with design diagram:

css
Copy
Edit
AigentMenu (Top)
→ TopBox
→ ChatWindow
→ BottomBox
→ AigentSidebar
✅ Master controller = aigent_controller.py

✅ Clean. Strict. Modular. No guesswork.

This document is the official blueprint for Code.AIGent. Any implementation must match it.