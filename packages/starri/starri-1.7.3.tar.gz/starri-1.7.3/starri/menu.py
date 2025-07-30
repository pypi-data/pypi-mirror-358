from blessed import Terminal
import re
import gradify
import os

term = Terminal()

def cls():
    print(term.home + term.clear_eos, end="")

def option(label, onselect):
    return {"type": "option", "label": label, "onselect": onselect}

def spacer():
    return {"type": "spacer"}

def checkbox(label, checked=False):
    return {"type": "checkbox", "label": label, "checked": checked}

def text(label):
    return {"type": "text", "label": label}

def starri(title, content):
    selectable_indices = [i for i, item in enumerate(content) if item.get("type") in ("option", "checkbox")]
    if not selectable_indices:
        cls()
        print(title)
        for item in content:
            if item.get("type") == "text":
                print(item["label"])
            elif item.get("type") == "spacer":
                print()
        return

    selected_idx = 0
    scroll_offset = 0
    MARGIN = 1

    def visible_length(txt):
        return len(re.sub(r'\x1b\[[0-9;]*m', '', txt))

    title_lines = title.splitlines()
    header_height = len(title_lines) + 2

    prev_size = (term.height, term.width)
    needs_render = True

    def render():
        nonlocal scroll_offset
        print(term.home + term.clear_eos, end="")
        height, width = term.height, term.width

        for i, line in enumerate(title_lines):
            vis_w = visible_length(line)
            x = (width - vis_w) // 2
            print(term.move_xy(x, i) + line)

        displayable = [(i, item) for i, item in enumerate(content)]
        total = len(displayable)
        max_vis = height - header_height

        sel_real = selectable_indices[selected_idx]
        sel_disp = next(idx for idx, (ri, _) in enumerate(displayable) if ri == sel_real)

        if selected_idx == 0:
            scroll_offset = 0
        elif selected_idx == len(selectable_indices) - 1:
            scroll_offset = max(total - max_vis, 0)
        else:
            if sel_disp - MARGIN < scroll_offset:
                scroll_offset = sel_disp - MARGIN
            elif sel_disp + MARGIN >= scroll_offset + max_vis:
                scroll_offset = sel_disp + MARGIN - max_vis + 1
            scroll_offset = max(0, min(scroll_offset, max(total - max_vis, 0)))

        window = displayable[scroll_offset:scroll_offset + max_vis]
        for idx, (ri, item) in enumerate(window):
            y = header_height + idx
            if item['type'] == 'spacer':
                line = ""
            elif item['type'] == 'text':
                line = f"  {item['label']}"
            elif item['type'] == 'checkbox':
                box = '[X]' if item['checked'] else '[ ]'
                line = f"{box} - {item['label']}"
            else:
                prefix = '> ' if ri == sel_real else '  '
                line = f"{prefix}{item['label']}"
            if ri == sel_real and item['type'] in ('option', 'checkbox'):
                line = term.reverse(line)
            x = (width - visible_length(line)) // 2
            print(term.move_xy(x, y) + line)

    def move_selection(delta):
        nonlocal selected_idx, needs_render
        new = selected_idx + delta
        new = max(0, min(new, len(selectable_indices) - 1))
        if new != selected_idx:
            selected_idx = new
            needs_render = True

    print(term.enter_fullscreen(), end="")
    try:
        with term.cbreak(), term.hidden_cursor():
            while True:
                current_size = (term.height, term.width)
                if current_size != prev_size:
                    prev_size = current_size
                    needs_render = True
                if needs_render:
                    render()
                    needs_render = False
                key = term.inkey(timeout=0.1)
                if not key:
                    continue
                if key.name == 'KEY_UP':
                    move_selection(-1)
                elif key.name == 'KEY_DOWN':
                    move_selection(1)
                elif key == ' ':
                    ri = selectable_indices[selected_idx]
                    if content[ri]['type'] == 'checkbox':
                        content[ri]['checked'] = not content[ri]['checked']
                        needs_render = True
                elif key.name in ('KEY_ENTER',) or key == '\n':
                    ri = selectable_indices[selected_idx]
                    itm = content[ri]
                    if itm['type'] == 'checkbox':
                        itm['checked'] = not itm['checked']
                        needs_render = True
                    else:
                        cls()
                        itm.get('onselect', lambda: None)()
                        break
    finally:
        print(term.exit_fullscreen(), end="")
