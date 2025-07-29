import json
import re
import pyperclip
import os
import tkinter as tk
from tkinter import ttk, scrolledtext
from pathlib import Path

class SecureObfuscator:
    def __init__(self, config_file='config.json', mapping_file='mapping.json'):
        self.config_file = config_file
        self.mapping_file = mapping_file
        self.config = self._load_json_safe(self.config_file, {"sensitive_words": [], "rules": []})
        self.mapping = self._load_json_safe(self.mapping_file, {})
        self.counters = self._init_counters()
        self.original_text = ""
        self.current_text = ""
        self.in_multiline_comment = False
        self.root = None
        self.text_widget = None
        self.undo_history = []
        self.pattern_select_mode = False
        self.max_text_size = 1048576
        self.max_undo_history = 50

    def _load_json_safe(self, filename, default):
        try:
            if os.path.exists(filename) and os.path.getsize(filename) > 0:
                with open(filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return default

    def _save_json_safe(self, filename, data):
        try:
            os.makedirs(os.path.dirname(filename) or '.', exist_ok=True)
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return True
        except:
            try:
                backup_file = f"backup_{os.path.basename(filename)}"
                with open(backup_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                return True
            except:
                return False

    def _init_counters(self):
        counters = {}
        try:
            for placeholder in self.mapping.values():
                match = re.match(r'([A-Z_]+)(\d+)', placeholder)
                if match:
                    prefix = match.group(1)
                    number = int(match.group(2))
                    if prefix not in counters or number >= counters[prefix]:
                        counters[prefix] = number + 1
        except:
            counters = {}
        return counters

    def _validate_input(self, text):
        if not text or len(text) > self.max_text_size:
            return False
        return True

    def get_or_create_placeholder(self, text, prefix='PLACEHOLDER'):
        if text in self.mapping:
            return self.mapping[text]
        if prefix not in self.counters:
            self.counters[prefix] = 1
        placeholder = f"{prefix}{self.counters[prefix]}"
        self.mapping[text] = placeholder
        self.counters[prefix] += 1
        return placeholder

    def save_mapping(self):
        self._save_json_safe(self.mapping_file, self.mapping)

    def remove_comments(self, line):
        if self.in_multiline_comment:
            end_pos = line.find('*/')
            if end_pos != -1:
                line = line[end_pos + 2:]
                self.in_multiline_comment = False
            else:
                return ''
        
        result = []
        i = 0
        in_string = False
        string_char = None
        
        while i < len(line):
            if not in_string and (line[i] == '"' or line[i] == "'"):
                in_string = True
                string_char = line[i]
                result.append(line[i])
                i += 1
            elif in_string:
                if line[i] == '\\' and i + 1 < len(line):
                    result.append(line[i:i+2])
                    i += 2
                elif line[i] == string_char:
                    in_string = False
                    result.append(line[i])
                    i += 1
                else:
                    result.append(line[i])
                    i += 1
            elif not in_string:
                if i + 2 < len(line) and line[i:i+3] == '///':
                    break
                elif i + 1 < len(line) and line[i:i+2] == '//':
                    break
                elif i + 1 < len(line) and line[i:i+2] == '/*':
                    end_pos = line.find('*/', i + 2)
                    if end_pos != -1:
                        i = end_pos + 2
                    else:
                        self.in_multiline_comment = True
                        break
                else:
                    result.append(line[i])
                    i += 1
            else:
                result.append(line[i])
                i += 1
        
        return ''.join(result).rstrip()

    def deobfuscate_all(self):
        """Deobfuscate entire text and close"""
        if not self.mapping:
            return
        
        reverse_mapping = {v: k for k, v in self.mapping.items()}
        sorted_placeholders = sorted(reverse_mapping.keys(), key=len, reverse=True)
        
        for placeholder in sorted_placeholders:
            original = reverse_mapping[placeholder]
            self.current_text = self.current_text.replace(placeholder, original)
        
        pyperclip.copy(self.current_text)
        self.root.quit()
        
    def obfuscate_line(self, line):
        line = self.remove_comments(line)
        if not line.strip():
            return None
            
        for word in self.config.get('sensitive_words', []):
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            matches = list(pattern.finditer(line))
            
            for match in reversed(matches):
                original = match.group(0)
                placeholder = self.get_or_create_placeholder(original.lower(), 'SENSITIVE')
                line = line[:match.start()] + placeholder + line[match.end():]
        
        for rule in self.config.get('rules', []):
            pattern = rule.get('pattern', '')
            prefix = rule.get('prefix', 'PLACEHOLDER')
            whole_match = rule.get('whole_match', False)
            
            replacements = []
            
            try:
                for match in re.finditer(pattern, line):
                    if whole_match:
                        original = match.group(0)
                    else:
                        if match.groups():
                            original = match.group(1)
                        else:
                            continue
                    
                    if prefix == "STRING" and re.search(r'https?://', original):
                        url_pattern = r'https?://[^\s\"\'<>\]\)]+'
                        for url_match in re.finditer(url_pattern, original):
                            url = url_match.group(0)
                            url_placeholder = self.get_or_create_placeholder(url, 'URL')
                            original = original.replace(url, url_placeholder)
                        
                        placeholder = self.get_or_create_placeholder(original, prefix)
                    else:
                        placeholder = self.get_or_create_placeholder(original, prefix)
                    
                    replacements.append((original, placeholder))
            except re.error:
                continue
            
            for original, placeholder in replacements:
                line = line.replace(original, placeholder)
        
        return line

    def obfuscate(self, text):
        self.in_multiline_comment = False
        lines = text.split('\n')
        obfuscated_lines = []
        
        for line in lines:
            obfuscated_line = self.obfuscate_line(line)
            if obfuscated_line is not None:
                obfuscated_lines.append(obfuscated_line)
        
        return '\n'.join(obfuscated_lines)

    def apply_existing_mappings(self):
        if not self.mapping:
            return 0
            
        count = 0
        sorted_mappings = sorted(self.mapping.items(), key=lambda x: len(x[0]), reverse=True)
        
        for original, placeholder in sorted_mappings:
            pattern = r'\b' + re.escape(original) + r'\b'
            matches = len(re.findall(pattern, self.current_text))
            if matches > 0:
                self.current_text = re.sub(pattern, placeholder, self.current_text)
                count += matches
        
        return count

    def _save_undo_state(self, action_label):
        self.undo_history.append({
            'text': self.current_text,
            'mapping': self.mapping.copy(),
            'counters': self.counters.copy(),
            'word': action_label
        })
        
        if len(self.undo_history) > self.max_undo_history:
            self.undo_history.pop(0)

    def undo_last_action(self):
        if not self.undo_history:
            self.status_label.config(text="Nothing to undo")
            return "break"
            
        last_state = self.undo_history.pop()
        self.current_text = last_state['text']
        self.mapping = last_state['mapping']
        self.counters = last_state['counters']
        
        scroll_pos = self.text_widget.yview()
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(1.0, self.current_text)
        self.highlight_placeholders()
        self.text_widget.yview_moveto(scroll_pos[0])
        
        self.save_mapping()
        self.status_label.config(text="Action undone")
        return "break"

    def on_text_modified(self, event=None):
        new_text = self.text_widget.get(1.0, tk.END).rstrip('\n')
        
        if new_text != self.current_text:
            self._save_undo_state('[Text Edit]')
            self.current_text = new_text
            self.highlight_placeholders()
            self.status_label.config(text="Text edited")

    def on_key_release(self, event):
        if event.keysym == 'z' and event.state & 0x4:
            return
        self.root.after(10, self.on_text_modified)

    def on_single_click(self, event):
        if hasattr(self, 'has_selection') and self.has_selection:
            self.has_selection = False
            return None
            
        index = self.text_widget.index(f"@{event.x},{event.y}")
        line_start = index.split('.')[0] + '.0'
        line_end = index.split('.')[0] + '.end'
        line_content = self.text_widget.get(line_start, line_end)
        char_pos = int(index.split('.')[1])
        
        temp_start = max(0, char_pos - 20)
        temp_end = min(len(line_content), char_pos + 20)
        surrounding_text = line_content[temp_start:temp_end]
        
        placeholder_pattern = r'(SENSITIVE|URL|STRING|ANONYMIZED|PATTERN|GUID|EMAIL|IP|DATE|NUMBER|ID|PATH|CLASS|NAMESPACE|LOG_CONTENT|METHOD|LAMBDA_PROP|PLACEHOLDER)\d+'
        is_likely_placeholder = bool(re.search(placeholder_pattern, surrounding_text))
        
        if is_likely_placeholder:
            separators = '.,-/\\()[]{}\'\"<>:;=+*&|!?#@$%^~\t\n '
        else:
            separators = '.,-_/\\()[]{}\'\"<>:;=+*&|!?#@$%^~\t\n '
        
        start = char_pos
        end = char_pos
        
        while start > 0 and line_content[start - 1] not in separators:
            start -= 1
            
        while end < len(line_content) and line_content[end] not in separators:
            end += 1
        
        if start < end:
            word_start = f"{index.split('.')[0]}.{start}"
            word_end = f"{index.split('.')[0]}.{end}"
            word = self.text_widget.get(word_start, word_end)
            
            if word and word.strip():
                if re.match(r'^(SENSITIVE|URL|STRING|ANONYMIZED|PATTERN|GUID|EMAIL|IP|DATE|NUMBER|ID|PATH|CLASS|NAMESPACE|LOG_CONTENT|METHOD|LAMBDA_PROP|PLACEHOLDER)\d+$', word):
                    self.deobfuscate_placeholder(word)
                elif self.pattern_select_mode:
                    self.obfuscate_similar_direct(word)
                else:
                    self.obfuscate_selected_word(word)
        
        return "break"

    def deobfuscate_placeholder(self, placeholder):
        original_value = None
        for orig, placehold in self.mapping.items():
            if placehold == placeholder:
                original_value = orig
                break
                
        if not original_value:
            self.status_label.config(text="No mapping found")
            return
            
        self._save_undo_state(f'[De-obfuscate: {placeholder}]')
        
        count = self.current_text.count(placeholder)
        self.current_text = self.current_text.replace(placeholder, original_value)
        del self.mapping[original_value]
        
        scroll_pos = self.text_widget.yview()
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(1.0, self.current_text)
        self.highlight_placeholders()
        self.text_widget.yview_moveto(scroll_pos[0])
        
        self.save_mapping()
        self.status_label.config(text=f"De-obfuscated {count} occurrences")

    def obfuscate_selected_word(self, word):
        if not word.strip():
            return
            
        self._save_undo_state(word)
        
        scroll_pos = self.text_widget.yview()
        placeholder = self.get_or_create_placeholder(word, 'ANONYMIZED')
        self.current_text = self.current_text.replace(word, placeholder)
        
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(1.0, self.current_text)
        self.highlight_placeholders()
        self.text_widget.yview_moveto(scroll_pos[0])
        
        self.save_mapping()
        self.status_label.config(text="Word obfuscated")

    def obfuscate_similar_direct(self, sample):
        if not sample.strip():
            return
            
        self._save_undo_state(f'[Pattern: {sample}]')
        
        pattern_parts = []
        i = 0
        while i < len(sample):
            if sample[i].isdigit():
                j = i
                while j < len(sample) and sample[j].isdigit():
                    j += 1
                pattern_parts.append(r'\d{' + str(j-i) + '}')
                i = j
            elif sample[i].isalpha():
                j = i
                while j < len(sample) and sample[j].isalpha():
                    j += 1
                if sample[i:j].isupper():
                    pattern_parts.append(r'[A-Z]{' + str(j-i) + '}')
                elif sample[i:j].islower():
                    pattern_parts.append(r'[a-z]{' + str(j-i) + '}')
                else:
                    pattern_parts.append(r'[A-Za-z]{' + str(j-i) + '}')
                i = j
            else:
                pattern_parts.append(re.escape(sample[i]))
                i += 1
        
        pattern = r'\b' + ''.join(pattern_parts) + r'\b'
        
        count = 0
        try:
            matches = list(re.finditer(pattern, self.current_text))
            
            for match in reversed(matches):
                original = match.group(0)
                placeholder = self.get_or_create_placeholder(original, 'PATTERN')
                start, end = match.span()
                self.current_text = self.current_text[:start] + placeholder + self.current_text[end:]
                count += 1
            
            scroll_pos = self.text_widget.yview()
            self.text_widget.delete(1.0, tk.END)
            self.text_widget.insert(1.0, self.current_text)
            self.highlight_placeholders()
            self.text_widget.yview_moveto(scroll_pos[0])
            
            self.save_mapping()
            
            if count > 0:
                self.status_label.config(text=f"Obfuscated {count} similar patterns")
            else:
                self.status_label.config(text="No similar patterns found")
                
        except re.error:
            self.status_label.config(text="Pattern error")

    def highlight_placeholders(self):
        self.text_widget.tag_remove("placeholder", 1.0, tk.END)
        
        colors = {
            'SENSITIVE': '#ff6b6b',
            'URL': '#4ecdc4',
            'STRING': '#45b7d1',
            'ANONYMIZED': '#f39c12',
            'PATTERN': '#9b59b6',
            'GUID': '#2ecc71',
            'EMAIL': '#e74c3c',
            'IP': '#34495e',
            'DATE': '#16a085',
            'NUMBER': '#d35400',
            'ID': '#8e44ad',
            'PATH': '#27ae60',
            'CLASS': '#3498db',
            'NAMESPACE': '#e67e22',
            'LOG_CONTENT': '#9b59b6',
            'METHOD': '#00b894',
            'LAMBDA_PROP': '#1abc9c',
            'PLACEHOLDER': '#95a5a6'
        }
        
        for prefix, color in colors.items():
            pattern = f"{prefix}\\d+"
            start = 1.0
            while True:
                pos = self.text_widget.search(pattern, start, tk.END, regexp=True)
                if not pos:
                    break
                match_text = self.text_widget.get(pos, f'{pos} wordend')
                match = re.match(f'{prefix}\\d+', match_text)
                if match:
                    end = f"{pos}+{len(match.group(0))}c"
                    self.text_widget.tag_add(f"placeholder_{prefix}", pos, end)
                    self.text_widget.tag_config(f"placeholder_{prefix}", background=color, foreground="white")
                start = f"{pos}+1c"

    def toggle_pattern_mode(self):
        self.pattern_select_mode = not self.pattern_select_mode
        
        if self.pattern_select_mode:
            self.mode_btn.config(text="Mode: Pattern")
            self.status_label.config(text="Click to obfuscate similar patterns")
            self.text_widget.config(cursor="hand2")
        else:
            self.mode_btn.config(text="Mode: Exact")
            self.status_label.config(text="Click to obfuscate exact matches")
            self.text_widget.config(cursor="xterm")

    def obfuscate_pattern(self, pattern, prefix, description):
        self._save_undo_state(f'[{description}]')
        
        count = 0
        temp_text = self.current_text
        
        try:
            matches = list(re.finditer(pattern, temp_text))
            
            for match in reversed(matches):
                original = match.group(0)
                placeholder = self.get_or_create_placeholder(original, prefix)
                start, end = match.span()
                self.current_text = self.current_text[:start] + placeholder + self.current_text[end:]
                count += 1
            
            scroll_pos = self.text_widget.yview()
            self.text_widget.delete(1.0, tk.END)
            self.text_widget.insert(1.0, self.current_text)
            self.highlight_placeholders()
            self.text_widget.yview_moveto(scroll_pos[0])
            
            self.save_mapping()
            self.status_label.config(text=f"Obfuscated {count} {description}")
        except re.error:
            self.status_label.config(text="Pattern error")

    def obfuscate_guids(self):
        pattern = r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'
        self.obfuscate_pattern(pattern, 'GUID', 'GUIDs')

    def obfuscate_methods(self):
        self._save_undo_state('[Method Names]')
        
        count = 0
        found_methods = set()
        
        patterns = [
            r'(?:public\s+|private\s+|protected\s+|internal\s+|static\s+|virtual\s+|override\s+|async\s+|sealed\s+|abstract\s+|extern\s+|partial\s+)*(?:(?:void|Task|ValueTask|[\w<>\[\]?]+)\s+)(\w+)\s*(?:<[^>]+>)?\s*\(',
            r'(?:public\s+|private\s+|protected\s+|internal\s+|static\s+)(\w+)\s*\(\s*(?:[^)]*)?\s*\)\s*(?::\s*(?:base|this)\s*\([^)]*\))?\s*{',
            r'(?:public\s+|private\s+|protected\s+|internal\s+|static\s+|virtual\s+|override\s+)*[\w<>\[\]?]+\s+(\w+)\s*\{\s*(?:get|set)',
            r'^\s*(?:Task|ValueTask|void|[\w<>\[\]?]+)\s+(\w+)\s*(?:<[^>]+>)?\s*\(',
            r'(?:public\s+|private\s+|protected\s+|internal\s+|static\s+)*(?:[\w<>\[\]?]+)\s+(\w+)\s*(?:<[^>]+>)?\s*\([^)]*\)\s*=>',
            r'(?:static\s+)?(?:async\s+)?(?:void|Task|ValueTask|[\w<>\[\]?]+)\s+(\w+)\s*\([^)]*\)\s*(?:{|=>)'
        ]
        
        for pattern in patterns:
            try:
                matches = re.finditer(pattern, self.current_text, re.MULTILINE)
                for match in matches:
                    method_name = match.group(1)
                    if method_name not in ['Main', 'Dispose', 'Equals', 'GetHashCode', 'ToString', 'OnConfiguring', 'OnModelCreating']:
                        found_methods.add(method_name)
            except re.error:
                continue
        
        temp_text = self.current_text
        for method_name in found_methods:
            if re.match(r'METHOD\d+', method_name):
                continue
                
            placeholder = self.get_or_create_placeholder(method_name, 'METHOD')
            temp_text = re.sub(r'\b' + re.escape(method_name) + r'\b', placeholder, temp_text)
            count += 1
        
        self.current_text = temp_text
        
        scroll_pos = self.text_widget.yview()
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(1.0, self.current_text)
        self.highlight_placeholders()
        self.text_widget.yview_moveto(scroll_pos[0])
        
        self.save_mapping()
        self.status_label.config(text=f"Obfuscated {count} methods")

    def obfuscate_lambda_props(self):
        self._save_undo_state('[Lambda Properties]')
        
        count = 0
        pattern = r'(\w+)\s*=>\s*\1\.(\w+)'
        matches = list(re.finditer(pattern, self.current_text))
        
        for match in reversed(matches):
            lambda_var = match.group(1)
            prop_name = match.group(2)
            placeholder = self.get_or_create_placeholder(prop_name, 'LAMBDA_PROP')
            start = match.start(2)
            end = match.end(2)
            self.current_text = self.current_text[:start] + placeholder + self.current_text[end:]
            count += 1
        
        scroll_pos = self.text_widget.yview()
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(1.0, self.current_text)
        self.highlight_placeholders()
        self.text_widget.yview_moveto(scroll_pos[0])
        
        self.save_mapping()
        self.status_label.config(text=f"Obfuscated {count} lambda properties")

    def obfuscate_all_strings(self):
        self._save_undo_state('[All Strings]')
        
        count = 0
        result = []
        i = 0
        
        while i < len(self.current_text):
            if self.current_text[i] in ['"', "'"]:
                quote_char = self.current_text[i]
                string_start = i
                i += 1
                string_content = ""
                
                while i < len(self.current_text):
                    if self.current_text[i] == '\\' and i + 1 < len(self.current_text):
                        string_content += self.current_text[i:i+2]
                        i += 2
                    elif self.current_text[i] == quote_char:
                        i += 1
                        
                        if len(string_content) > 1:
                            placeholder = self.get_or_create_placeholder(string_content, 'STRING')
                            result.append(quote_char + placeholder + quote_char)
                            count += 1
                        else:
                            result.append(quote_char + string_content + quote_char)
                        break
                    else:
                        string_content += self.current_text[i]
                        i += 1
                else:
                    result.append(self.current_text[string_start:i])
            else:
                result.append(self.current_text[i])
                i += 1
        
        self.current_text = ''.join(result)
        
        scroll_pos = self.text_widget.yview()
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(1.0, self.current_text)
        self.highlight_placeholders()
        self.text_widget.yview_moveto(scroll_pos[0])
        
        self.save_mapping()
        self.status_label.config(text=f"Obfuscated {count} strings")

    def show_mappings_window(self):
        mappings_window = tk.Toplevel(self.root)
        mappings_window.title("Current Mappings")
        mappings_window.geometry("600x400")
        
        text_widget = scrolledtext.ScrolledText(mappings_window, wrap=tk.WORD, font=('Consolas', 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget.insert(1.0, f"Total mappings: {len(self.mapping)}\n\n")
        for original, placeholder in sorted(self.mapping.items(), key=lambda x: x[1]):
            text_widget.insert(tk.END, f"{placeholder:<20} → {original}\n")
        
        text_widget.config(state=tk.DISABLED)

    def clear_mappings(self):
        from tkinter import messagebox
        if messagebox.askyesno("Clear Mappings", f"Clear all {len(self.mapping)} mappings?"):
            self._save_undo_state('[ALL MAPPINGS]')
            self.mapping = {}
            self.counters = {}
            self.save_mapping()
            self.status_label.config(text="Mappings cleared")

    def close_and_copy(self):
        pyperclip.copy(self.current_text)
        self.root.quit()

    def check_selection(self, event):
        try:
            self.text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.has_selection = True
        except tk.TclError:
            self.has_selection = False

    def on_mouse_motion(self, event):
        self.text_widget.tag_remove("hover", 1.0, tk.END)
        
        index = self.text_widget.index(f"@{event.x},{event.y}")
        line_start = index.split('.')[0] + '.0'
        line_end = index.split('.')[0] + '.end'
        line_content = self.text_widget.get(line_start, line_end)
        char_pos = int(index.split('.')[1])
        
        temp_start = max(0, char_pos - 20)
        temp_end = min(len(line_content), char_pos + 20)
        surrounding_text = line_content[temp_start:temp_end]
        
        placeholder_pattern = r'(SENSITIVE|URL|STRING|ANONYMIZED|PATTERN|GUID|EMAIL|IP|DATE|NUMBER|ID|PATH|CLASS|NAMESPACE|LOG_CONTENT|METHOD|LAMBDA_PROP|PLACEHOLDER)\d+'
        is_likely_placeholder = bool(re.search(placeholder_pattern, surrounding_text))
        
        if is_likely_placeholder:
            separators = '.,-/\\()[]{}\'\"<>:;=+*&|!?#@$%^~\t\n '
        else:
            separators = '.,-_/\\()[]{}\'\"<>:;=+*&|!?#@$%^~\t\n '
        
        start = char_pos
        end = char_pos
        
        while start > 0 and line_content[start - 1] not in separators:
            start -= 1
            
        while end < len(line_content) and line_content[end] not in separators:
            end += 1
        
        if start < end:
            word_start = f"{index.split('.')[0]}.{start}"
            word_end = f"{index.split('.')[0]}.{end}"
            word = line_content[start:end]
            
            if re.match(r'^(SENSITIVE|URL|STRING|ANONYMIZED|PATTERN|GUID|EMAIL|IP|DATE|NUMBER|ID|PATH|CLASS|NAMESPACE|LOG_CONTENT|METHOD|LAMBDA_PROP|PLACEHOLDER)\d+$', word):
                self.text_widget.tag_add("hover", word_start, word_end)
                self.text_widget.tag_config("hover", background="#ff9999", foreground="black")
                self.text_widget.config(cursor="exchange")
            else:
                self.text_widget.tag_add("hover", word_start, word_end)
                self.text_widget.tag_config("hover", background="#e0e0e0", foreground="black")
                self.text_widget.config(cursor="hand2" if self.pattern_select_mode else "xterm")

    def on_mouse_leave(self, event):
        self.text_widget.tag_remove("hover", 1.0, tk.END)

    def create_gui(self):
        self.root = tk.Tk()
        self.root.title("Code Obfuscator")
        self.root.geometry("900x700")
        
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        title_label = ttk.Label(main_frame, text="Interactive Code Obfuscator", font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        instruction_frame = ttk.Frame(main_frame)
        instruction_frame.grid(row=1, column=0, columnspan=3, pady=5)
        
        instructions = ttk.Label(instruction_frame, text="Click any word to obfuscate", font=('Arial', 10))
        instructions.pack(side=tk.LEFT, padx=10)
        
        self.mode_btn = ttk.Button(instruction_frame, text="Mode: Exact", command=self.toggle_pattern_mode, width=25)
        self.mode_btn.pack(side=tk.LEFT, padx=10)
        
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        self.text_widget = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, width=100, height=25, font=('Consolas', 10))
        self.text_widget.pack(fill=tk.BOTH, expand=True)
        
        pattern_frame = ttk.LabelFrame(main_frame, text="Pattern Obfuscation", padding="10")
        pattern_frame.grid(row=3, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))
        
        patterns = [
            ("GUIDs", self.obfuscate_guids),
            ("Methods", self.obfuscate_methods),
            ("Lambda Props", self.obfuscate_lambda_props),
            ("All Strings", self.obfuscate_all_strings)
        ]
        
        for i, (label, command) in enumerate(patterns):
            row = i // 5
            col = i % 5
            btn = ttk.Button(pattern_frame, text=label, command=command)
            btn.grid(row=row, column=col, padx=5, pady=5)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=10)
        
        undo_btn = ttk.Button(button_frame, text="UNDO", command=self.undo_last_action)
        undo_btn.pack(side=tk.LEFT, padx=5)
        
        save_btn = ttk.Button(button_frame, text="Save Mapping", command=self.save_mapping)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        show_btn = ttk.Button(button_frame, text="Show Mappings", command=self.show_mappings_window)
        show_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = ttk.Button(button_frame, text="Clear Mappings", command=self.clear_mappings)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        deobfuscate_btn = ttk.Button(button_frame, text="Deobfuscate All", command=self.deobfuscate_all)
        deobfuscate_btn.pack(side=tk.LEFT, padx=5)

        close_btn = ttk.Button(button_frame, text="Close & Copy", command=self.close_and_copy)
        close_btn.pack(side=tk.LEFT, padx=5)
        
        self.status_label = ttk.Label(main_frame, text=f"Ready ({len(self.mapping)} mappings loaded)", relief=tk.SUNKEN)
        self.status_label.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        self.text_widget.bind("<Button-1>", self.on_single_click)
        self.text_widget.bind("<ButtonRelease-1>", self.check_selection)
        self.text_widget.bind("<Motion>", self.on_mouse_motion)
        self.text_widget.bind("<Leave>", self.on_mouse_leave)
        self.text_widget.bind("<KeyRelease>", self.on_key_release)
        self.text_widget.bind("<Control-z>", lambda e: self.undo_last_action())
        self.root.bind("<Control-z>", lambda e: self.undo_last_action())

    def auto_obfuscate_patterns(self):
        patterns = [
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'EMAIL'),
            (r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b', 'IP'),
            (r'[A-Za-z]:\\[\w\\.-]+', 'PATH'),
            (r'/[\w/.-]+\.\w+', 'PATH'),
            (r'\.{1,2}/[\w/.-]+', 'PATH')
        ]
        
        for pattern, prefix in patterns:
            matches = list(re.finditer(pattern, self.current_text))
            for match in reversed(matches):
                original = match.group(0)
                placeholder = self.get_or_create_placeholder(original, prefix)
                start, end = match.span()
                self.current_text = self.current_text[:start] + placeholder + self.current_text[end:]
        
        found_namespaces = set()
        
        namespace_pattern = r'namespace\s+([\w\.]+)'
        namespace_matches = re.finditer(namespace_pattern, self.current_text)
        for match in namespace_matches:
            namespace = match.group(1)
            if not namespace.startswith('Microsoft.'):
                found_namespaces.add(namespace)
        
        using_pattern = r'using\s+([\w\.]+)\s*;'
        using_matches = re.finditer(using_pattern, self.current_text)
        for match in using_matches:
            namespace = match.group(1)
            if not namespace.startswith('Microsoft.') and not namespace.startswith('System.'):
                found_namespaces.add(namespace)
        
        for namespace in sorted(found_namespaces, key=len, reverse=True):
            placeholder = self.get_or_create_placeholder(namespace, 'NAMESPACE')
            self.current_text = re.sub(r'\b' + re.escape(namespace) + r'\b', placeholder, self.current_text)

    def run_interactive(self, initial_text):
        if not self._validate_input(initial_text):
            return
            
        self.original_text = initial_text
        self.current_text = self.obfuscate(initial_text)
        
        self.auto_obfuscate_patterns()
        
        if self.mapping:
            self.apply_existing_mappings()
        
        self.create_gui()
        self.text_widget.insert(1.0, self.current_text)
        self.highlight_placeholders()
        self.save_mapping()
        
        status_text = f"Ready - {len(self.mapping)} mappings"
        self.status_label.config(text=status_text)
        
        self.root.mainloop()

def main():
    obfuscator = SecureObfuscator()
    clipboard_content = pyperclip.paste()
    
    if not clipboard_content:
        return
        
    obfuscator.run_interactive(clipboard_content)

if __name__ == "__main__":
    main()