import json
import re
import pyperclip
import os
import sys
import tkinter as tk
from tkinter import ttk, scrolledtext
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

class InteractiveCodeObfuscator:
    def __init__(self, config_file='obfuscator_config.json', mapping_file='obfuscator_mapping.json'):
        # Get package directory
        base_dir = Path(__file__).parent
        
        # Use full paths
        self.config_file = base_dir / config_file
        self.mapping_file = base_dir / mapping_file
        
        self.config = self.load_config()
        self.mapping = self.load_mapping()
        self.counters = self.calculate_counters()
        self.original_text = ""
        self.current_text = ""
        self.in_multiline_comment = False
        # GUI elements
        self.root = None
        self.text_widget = None
        self.undo_history = []
        self.pattern_select_mode = False
        print(f"📂 Loaded {len(self.mapping)} existing mappings")

    def load_config(self):
        """Load configuration from JSON file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️ Error loading config: {e}")
        return {
            "sensitive_words": [],
            "rules": []
        }

    def load_mapping(self):
        """Load existing mappings from file (safe)"""
        try:
            if os.path.exists(self.mapping_file):
                with open(self.mapping_file, 'r') as f:
                    content = f.read().strip()
                    if content:  # Check if file is not empty
                        return json.loads(content)
                    else:
                        print("📄 Mapping file is empty, starting fresh")
                        return {}
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️ Error loading mappings: {e}")
            print("🔄 Starting with fresh mappings")
        return {}

    def on_text_modified(self, event=None):
        """Handle text modifications and save to undo history"""
        # Get the new text
        new_text = self.text_widget.get(1.0, tk.END).rstrip('\n')

        # Only save to undo if text actually changed
        if new_text != self.current_text:
            # Save state for undo
            self.undo_history.append({
                'text': self.current_text,  # Save the OLD text
                'mapping': self.mapping.copy(),
                'counters': self.counters.copy(),
                'word': '[Text Edit]'
            })

            if len(self.undo_history) > 50:
                self.undo_history.pop(0)

            # Update current text
            self.current_text = new_text

            # Re-highlight placeholders after edit
            self.highlight_placeholders()

            # Update status
            self.status_label.config(text="✏️ Text edited - Press Ctrl+Z to undo")

    def on_key_release(self, event):
        """Handle key release for text updates"""
        # Don't track undo operations
        if event.keysym == 'z' and event.state & 0x4:  # Ctrl+Z
            return

        # Schedule text update to capture the change after key processing
        self.root.after(10, self.on_text_modified)

    def on_delete_key(self, event):
        """Handle delete key press"""
        try:
            # Check if there's a selection
            sel_start = self.text_widget.index(tk.SEL_FIRST)
            sel_end = self.text_widget.index(tk.SEL_LAST)

            # Delete selected text
            self.text_widget.delete(sel_start, sel_end)
            self.on_text_modified()
            return "break"  # Prevent default delete behavior
        except tk.TclError:
            # No selection, let default delete work
            self.root.after(10, self.on_text_modified)
            return None

    def on_key_press(self, event):
        """Handle any key press for editing"""
        # Schedule text update after the key press is processed
        self.root.after(10, self.on_text_modified)

    def toggle_edit_mode(self):
        """Toggle between edit and obfuscate mode"""
        if not hasattr(self, 'edit_mode'):
            self.edit_mode = False

        self.edit_mode = not self.edit_mode

        self.edit_btn.config(text="🔒 Mode: Editing")
        self.text_widget.config(bg="white", cursor="xterm")
        self.status_label.config(text="✏️ Edit mode - Type to edit, select to delete")

    def calculate_counters(self):
        """Calculate counters from existing mappings (safe)"""
        counters = {}
        try:
            for placeholder in self.mapping.values():
                # Extract prefix and number from placeholder
                match = re.match(r'([A-Z_]+)(\d+)', placeholder)
                if match:
                    prefix = match.group(1)
                    number = int(match.group(2))
                    if prefix not in counters or number >= counters[prefix]:
                        counters[prefix] = number + 1
        except Exception as e:
            print(f"⚠️ Error calculating counters: {e}")
            counters = {}
        return counters

    def save_mapping(self):
        """Save obfuscation mappings to file (safe)"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.mapping_file), exist_ok=True)

            with open(self.mapping_file, 'w') as f:
                json.dump(self.mapping, f, indent=2)
        except Exception as e:
            print(f"⚠️ Error saving mappings: {e}")
            # Try to save to current directory as backup
            try:
                backup_file = "obfuscation_mapping_backup.json"
                with open(backup_file, 'w') as f:
                    json.dump(self.mapping, f, indent=2)
                print(f"💾 Saved backup to {backup_file}")
            except:
                print("❌ Could not save mappings!")

    def get_or_create_placeholder(self, text, prefix='PLACEHOLDER'):
        """Get existing placeholder or create new one"""
        if text in self.mapping:
            return self.mapping[text]

        if prefix not in self.counters:
            self.counters[prefix] = 1

        placeholder = f"{prefix}{self.counters[prefix]}"
        self.mapping[text] = placeholder
        self.counters[prefix] += 1
        return placeholder

    def close_and_copy(self):
        """Copy to clipboard and close"""
        pyperclip.copy(self.current_text)
        print("✅ Copied to clipboard & closing!")
        self.root.quit()

    def remove_comments(self, line):
        """Remove C# comments from line"""
        # 🧹 Handle multi-line comment state
        if self.in_multiline_comment:
            end_pos = line.find('*/')
            if end_pos != -1:
                line = line[end_pos + 2:]
                self.in_multiline_comment = False
            else:
                return ''  # Entire line is in comment

        # 🔍 Process line for comments
        result = []
        i = 0
        in_string = False
        string_char = None

        while i < len(line):
            # Handle string literals
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
            # Handle comments outside strings
            elif not in_string:
                # XML doc comments ///
                if i + 2 < len(line) and line[i:i+3] == '///':
                    break  # Rest of line is comment
                # Single-line comments //
                elif i + 1 < len(line) and line[i:i+2] == '//':
                    break  # Rest of line is comment
                # Multi-line comments /*
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

    def obfuscate_lambda_props(self):
        """Obfuscate properties in lambda expressions like x => x.Property"""
        # Save state for undo
        self.undo_history.append({
            'text': self.current_text,
            'mapping': self.mapping.copy(),
            'counters': self.counters.copy(),
            'word': '[Lambda Properties]'
        })

        if len(self.undo_history) > 50:
            self.undo_history.pop(0)

        count = 0

        # Pattern to match lambda properties
        # Matches: x => x.Property, item=>item.Name, etc.
        pattern = r'(\w+)\s*=>\s*\1\.(\w+)'

        matches = list(re.finditer(pattern, self.current_text))

        for match in reversed(matches):
            lambda_var = match.group(1)  # The variable (x, item, etc.)
            prop_name = match.group(2)   # The property name

            # Create placeholder for property
            placeholder = self.get_or_create_placeholder(prop_name, 'LAMBDA_PROP')

            # Replace just the property name
            start = match.start(2)
            end = match.end(2)
            self.current_text = self.current_text[:start] + placeholder + self.current_text[end:]
            count += 1

        # Update GUI
        scroll_pos = self.text_widget.yview()
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(1.0, self.current_text)
        self.highlight_placeholders()
        self.text_widget.yview_moveto(scroll_pos[0])

        self.save_mapping()
        self.status_label.config(text=f"✅ Obfuscated {count} lambda properties")

    def obfuscate_all_strings(self):
        """Obfuscate all string literals"""
        # Save state for undo
        self.undo_history.append({
            'text': self.current_text,
            'mapping': self.mapping.copy(),
            'counters': self.counters.copy(),
            'word': '[All Strings]'
        })

        if len(self.undo_history) > 50:
            self.undo_history.pop(0)

        count = 0
        result = []
        i = 0

        while i < len(self.current_text):
            # Check if we're starting a string
            if self.current_text[i] in ['"', "'"]:
                quote_char = self.current_text[i]
                string_start = i
                i += 1
                string_content = ""

                # Collect string content
                while i < len(self.current_text):
                    if self.current_text[i] == '\\' and i + 1 < len(self.current_text):
                        # Handle escape sequences
                        string_content += self.current_text[i:i+2]
                        i += 2
                    elif self.current_text[i] == quote_char:
                        # End of string found
                        i += 1

                        # Don't obfuscate empty strings or single characters
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
                    # Unterminated string - add as is
                    result.append(self.current_text[string_start:i])
            else:
                result.append(self.current_text[i])
                i += 1

        self.current_text = ''.join(result)

        # Update GUI
        scroll_pos = self.text_widget.yview()
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(1.0, self.current_text)
        self.highlight_placeholders()
        self.text_widget.yview_moveto(scroll_pos[0])

        self.save_mapping()
        self.status_label.config(text=f"✅ Obfuscated {count} strings")

    def apply_existing_mappings(self):
        """Apply all existing mappings to current text"""
        if not self.mapping:
            return

        count = 0
        # Sort by length (longest first) to avoid partial replacements
        sorted_mappings = sorted(self.mapping.items(),
                                 key=lambda x: len(x[0]),
                                 reverse=True)

        for original, placeholder in sorted_mappings:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(original) + r'\b'
            matches = len(re.findall(pattern, self.current_text))
            if matches > 0:
                self.current_text = re.sub(pattern, placeholder, self.current_text)
                count += matches

        return count

    def obfuscate_line(self, line):
        """Apply obfuscation rules to a single line"""
        # 🧹 Remove comments first
        line = self.remove_comments(line)
        if not line.strip():  # Return None for empty lines
            return None

        # Obfuscate sensitive words FIRST
        for word in self.config.get('sensitive_words', []):
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            matches = list(pattern.finditer(line))

            for match in reversed(matches):
                original = match.group(0)
                placeholder = self.get_or_create_placeholder(original.lower(), 'SENSITIVE')
                line = line[:match.start()] + placeholder + line[match.end():]

        # Apply other rules
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

                    # Check if this is a URL inside a string
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
            except re.error as e:
                print(f"⚠️ Regex error in pattern '{pattern}': {e}")
                continue

            for original, placeholder in replacements:
                line = line.replace(original, placeholder)

        return line

    def obfuscate(self, text):
        """Obfuscate text line by line"""
        self.in_multiline_comment = False  # 🔧 Reset state
        lines = text.split('\n')
        obfuscated_lines = []

        for line in lines:
            obfuscated_line = self.obfuscate_line(line)
            if obfuscated_line is not None:  # 🚫 Skip empty lines
                obfuscated_lines.append(obfuscated_line)

        return '\n'.join(obfuscated_lines)

    def on_single_click(self, event):
        """Auto-obfuscate word on single click OR obfuscate similar patterns OR de-obfuscate"""
        # Don't obfuscate if user is selecting text
        if hasattr(self, 'has_selection') and self.has_selection:
            self.has_selection = False
            return None  # Allow normal selection

        # Get click position
        index = self.text_widget.index(f"@{event.x},{event.y}")

        # Get the line content
        line_start = index.split('.')[0] + '.0'
        line_end = index.split('.')[0] + '.end'
        line_content = self.text_widget.get(line_start, line_end)

        # Get character position in line
        char_pos = int(index.split('.')[1])

        # 🆕 First, check if we're clicking on a placeholder pattern
        # Look ahead and behind to see if this looks like a placeholder
        temp_start = max(0, char_pos - 20)
        temp_end = min(len(line_content), char_pos + 20)
        surrounding_text = line_content[temp_start:temp_end]

        # Check if we're in a placeholder-like pattern
        placeholder_pattern = r'(SENSITIVE|URL|STRING|ANONYMIZED|PATTERN|GUID|EMAIL|IP|DATE|NUMBER|ID|PATH|CLASS|NAMESPACE|LOG_CONTENT|METHOD|LAMBDA_PROP|PLACEHOLDER)\d+'

        # Define separators - conditionally include underscore
        is_likely_placeholder = bool(re.search(placeholder_pattern, surrounding_text))

        if is_likely_placeholder:
            # Don't treat underscore as separator for placeholders
            separators = '.,-/\\()[]{}\'\"<>:;=+*&|!?#@$%^~\t\n '
        else:
            # Normal separators including underscore
            separators = '.,-_/\\()[]{}\'\"<>:;=+*&|!?#@$%^~\t\n '

        # Find word boundaries
        start = char_pos
        end = char_pos

        # Search backward for word start
        while start > 0 and line_content[start - 1] not in separators:
            start -= 1

        # Search forward for word end
        while end < len(line_content) and line_content[end] not in separators:
            end += 1

        # Get the word
        if start < end:
            word_start = f"{index.split('.')[0]}.{start}"
            word_end = f"{index.split('.')[0]}.{end}"

            # Get the word
            word = self.text_widget.get(word_start, word_end)

            if word and word.strip():
                # Check if it's a complete placeholder - FIXED: removed AUTO_ prefix
                if re.match(r'^(SENSITIVE|URL|STRING|ANONYMIZED|PATTERN|GUID|EMAIL|IP|DATE|NUMBER|ID|PATH|CLASS|NAMESPACE|LOG_CONTENT|METHOD|LAMBDA_PROP|PLACEHOLDER)\d+$', word):
                    # It's a placeholder - de-obfuscate it
                    self.deobfuscate_placeholder(word)  # 🔧 Call directly without after_idle
                elif self.pattern_select_mode:
                    # Pattern selection mode
                    self.obfuscate_similar_direct(word)
                else:
                    # Normal obfuscation mode
                    self.obfuscate_selected_word(word)

        return "break"

    def obfuscate_similar_direct(self, sample):
        """Directly obfuscate all strings with similar structure to clicked word"""
        if not sample.strip():
            return

        # Save state for undo
        self.undo_history.append({
            'text': self.current_text,
            'mapping': self.mapping.copy(),
            'counters': self.counters.copy(),
            'word': f'[Pattern: {sample}]'
        })

        if len(self.undo_history) > 50:
            self.undo_history.pop(0)

        # Build pattern based on character types (similar structure)
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

        # Find and replace matches
        count = 0
        try:
            matches = list(re.finditer(pattern, self.current_text))

            for match in reversed(matches):
                original = match.group(0)
                placeholder = self.get_or_create_placeholder(original, 'PATTERN')
                start, end = match.span()
                self.current_text = self.current_text[:start] + placeholder + self.current_text[end:]
                count += 1

            # Update text widget
            scroll_pos = self.text_widget.yview()
            self.text_widget.delete(1.0, tk.END)
            self.text_widget.insert(1.0, self.current_text)
            self.highlight_placeholders()
            self.text_widget.yview_moveto(scroll_pos[0])

            # Save mapping
            self.save_mapping()

            # Update status
            if count > 0:
                self.status_label.config(text=f"✅ Pattern '{sample}' → obfuscated {count} similar matches")
            else:
                self.status_label.config(text=f"⚠️ No similar patterns found for '{sample}'")

        except re.error as e:
            self.status_label.config(text=f"❌ Pattern error: {e}")

    def obfuscate_selected_word(self, word):
        """Obfuscate all occurrences of selected word"""
        if not word.strip():
            return

        # 🔄 Save current state for undo
        self.undo_history.append({
            'text': self.current_text,
            'mapping': self.mapping.copy(),
            'counters': self.counters.copy(),
            'word': word
        })

        # Limit undo history to 50 operations
        if len(self.undo_history) > 50:
            self.undo_history.pop(0)

        # Save current scroll position 📍
        scroll_pos = self.text_widget.yview()

        # Create placeholder for this word
        placeholder = self.get_or_create_placeholder(word, 'ANONYMIZED')

        # Replace all occurrences (case-sensitive)
        self.current_text = self.current_text.replace(word, placeholder)

        # Update text widget
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(1.0, self.current_text)

        # Highlight the newly obfuscated placeholders
        self.highlight_placeholders()

        # Restore scroll position 🎯
        self.text_widget.yview_moveto(scroll_pos[0])

        # Save mapping
        self.save_mapping()

        # Update status
        self.status_label.config(text=f"✅ Obfuscated '{word}' → {placeholder}")

    def undo_last_obfuscation(self):
        """🔄 Undo the last obfuscation"""
        if not self.undo_history:
            self.status_label.config(text="⚠️ Nothing to undo")
            return

        # Pop last state
        last_state = self.undo_history.pop()

        # Restore state
        self.current_text = last_state['text']
        self.mapping = last_state['mapping']
        self.counters = last_state['counters']

        # Update text widget
        scroll_pos = self.text_widget.yview()
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(1.0, self.current_text)
        self.highlight_placeholders()
        self.text_widget.yview_moveto(scroll_pos[0])

        # Save mapping
        self.save_mapping()

        # Update status
        self.status_label.config(text=f"↩️ Undid obfuscation of '{last_state['word']}'")

    def highlight_placeholders(self):
        """Highlight all placeholders in the text"""
        self.text_widget.tag_remove("placeholder", 1.0, tk.END)

        # Define colors for different placeholder types
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
            'METHOD': '#00b894',      # NEW - green for methods
            'PLACEHOLDER': '#95a5a6'
        }

        # Find and highlight all placeholders
        for prefix, color in colors.items():
            pattern = f"{prefix}\\d+"
            start = 1.0
            while True:
                pos = self.text_widget.search(pattern, start, tk.END, regexp=True)
                if not pos:
                    break
                # Get the actual length of the matched text
                match_text = self.text_widget.get(pos, f'{pos} wordend')
                match = re.match(f'{prefix}\\d+', match_text)
                if match:
                    end = f"{pos}+{len(match.group(0))}c"
                    self.text_widget.tag_add(f"placeholder_{prefix}", pos, end)
                    self.text_widget.tag_config(f"placeholder_{prefix}", background=color, foreground="white")
                start = f"{pos}+1c"

    def toggle_pattern_mode(self):
        """Toggle between exact and pattern mode"""
        self.pattern_select_mode = not self.pattern_select_mode

        if self.pattern_select_mode:
            self.mode_btn.config(text="🎯 Mode: Similar Pattern")
            self.status_label.config(text="🎯 Click any word to obfuscate similar patterns")
            self.text_widget.config(cursor="hand2")
        else:
            self.mode_btn.config(text="🔐 Mode: Exact Word")
            self.status_label.config(text="🔐 Click any word to obfuscate exact matches")
            self.text_widget.config(cursor="xterm")

    def on_click_handler(self, event):
        """Handle clicks based on current mode"""
        if hasattr(self, 'edit_mode') and self.edit_mode:
            # In edit mode, just allow normal text selection
            return None
        else:
            # In obfuscate mode, use existing behavior
            return self.on_single_click(event)

    def check_selection(self, event):
        """Check if user made a selection"""
        try:
            # If there's a selection, set a flag
            self.text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.has_selection = True
        except tk.TclError:
            self.has_selection = False

    def undo_last_action(self):
        """🔄 Undo the last action (obfuscation or edit)"""
        if not self.undo_history:
            self.status_label.config(text="⚠️ Nothing to undo")
            return "break"

        # Pop last state
        last_state = self.undo_history.pop()

        # Save current state in case user wants to redo (optional)
        # self.redo_history.append({
        #     'text': self.current_text,
        #     'mapping': self.mapping.copy(),
        #     'counters': self.counters.copy(),
        #     'word': 'Redo'
        # })

        # Restore state
        self.current_text = last_state['text']
        self.mapping = last_state['mapping']
        self.counters = last_state['counters']

        # Update text widget
        scroll_pos = self.text_widget.yview()
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(1.0, self.current_text)
        self.highlight_placeholders()
        self.text_widget.yview_moveto(scroll_pos[0])

        # Save mapping
        self.save_mapping()

        # Update status
        action_type = last_state['word']
        if action_type == '[Text Edit]':
            self.status_label.config(text="↩️ Undid text edit")
        else:
            self.status_label.config(text=f"↩️ Undid obfuscation of '{action_type}'")

        return "break"  # Prevent default Ctrl+Z behavior

    def create_gui(self):
        """Create the GUI window"""
        self.root = tk.Tk()
        self.root.title("🔐 Interactive Code Obfuscator")
        self.root.geometry("900x700")

        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Title
        title_label = ttk.Label(main_frame, text="🔐 Interactive Code Obfuscator", font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=10)

        # Instructions WITHOUT edit mode toggle
        instruction_frame = ttk.Frame(main_frame)
        instruction_frame.grid(row=1, column=0, columnspan=3, pady=5)

        instructions = ttk.Label(instruction_frame, text="📝 Click any word to obfuscate", font=('Arial', 10))
        instructions.pack(side=tk.LEFT, padx=10)

        # 🎯 Mode toggle button (pattern mode only)
        self.mode_btn = ttk.Button(instruction_frame, text="🔐 Mode: Exact Word",
                                   command=self.toggle_pattern_mode, width=25)
        self.mode_btn.pack(side=tk.LEFT, padx=10)

        # Text area
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)

        self.text_widget = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, width=100, height=25, font=('Consolas', 10))
        self.text_widget.pack(fill=tk.BOTH, expand=True)

        # 🎯 PATTERN OBFUSCATION SECTION
        pattern_frame = ttk.LabelFrame(main_frame, text="🎯 Quick Pattern Obfuscation", padding="10")
        pattern_frame.grid(row=3, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))

        # Pattern buttons only - NO custom_frame!
        patterns = [
            ("🔑 GUIDs", self.obfuscate_guids),
            ("🔧 Methods", self.obfuscate_methods),
            ("λ Props", self.obfuscate_lambda_props),
            ("📋 All Strings", self.obfuscate_all_strings)
        ]

        for i, (label, command) in enumerate(patterns):
            row = i // 5  # 5 buttons per row
            col = i % 5
            btn = ttk.Button(pattern_frame, text=label, command=command)
            btn.grid(row=row, column=col, padx=5, pady=5)

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=10)

        # 🔄 Add UNDO button
        undo_btn = ttk.Button(button_frame, text="↩️ UNDO",
                              command=self.undo_last_obfuscation)
        undo_btn.pack(side=tk.LEFT, padx=5)

        save_btn = ttk.Button(button_frame, text="💾 Save Mapping",
                              command=self.save_mapping)
        save_btn.pack(side=tk.LEFT, padx=5)

        show_btn = ttk.Button(button_frame, text="📋 Show Mappings",
                              command=self.show_mappings_window)
        show_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = ttk.Button(button_frame, text="🗑️ Clear Mappings",
                               command=self.clear_mappings)
        clear_btn.pack(side=tk.LEFT, padx=5)

        close_btn = ttk.Button(button_frame, text="✅ Close & Copy",
                               command=self.close_and_copy)
        close_btn.pack(side=tk.LEFT, padx=5)

        # Status bar
        self.status_label = ttk.Label(main_frame, text=f"Ready ({len(self.mapping)} mappings loaded)", relief=tk.SUNKEN)
        self.status_label.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # Bind events
        self.text_widget.bind("<Button-1>", self.on_single_click)
        self.text_widget.bind("<ButtonRelease-1>", self.check_selection)
        self.text_widget.bind("<Motion>", self.on_mouse_motion)
        self.text_widget.bind("<Leave>", self.on_mouse_leave)
        self.text_widget.bind("<KeyRelease>", self.on_key_release)

        # 🎯 CTRL+Z for undo (works for both obfuscation and text edits)
        self.text_widget.bind("<Control-z>", lambda e: self.undo_last_action())
        self.root.bind("<Control-z>", lambda e: self.undo_last_action())

    def show_mappings_window(self):
        """Show mappings in a new window"""
        mappings_window = tk.Toplevel(self.root)
        mappings_window.title("📋 Current Mappings")
        mappings_window.geometry("600x400")

        # Create text widget
        text_widget = scrolledtext.ScrolledText(mappings_window, wrap=tk.WORD, font=('Consolas', 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Add mappings
        text_widget.insert(1.0, f"Total mappings: {len(self.mapping)}\n\n")
        for original, placeholder in sorted(self.mapping.items(), key=lambda x: x[1]):
            text_widget.insert(tk.END, f"{placeholder:<20} → {original}\n")

        text_widget.config(state=tk.DISABLED)

    def obfuscate_methods(self):
        """Obfuscate all C# method names"""
        # Save state for undo
        self.undo_history.append({
            'text': self.current_text,
            'mapping': self.mapping.copy(),
            'counters': self.counters.copy(),
            'word': '[Method Names]'
        })

        if len(self.undo_history) > 50:
            self.undo_history.pop(0)

        count = 0
        found_methods = set()  # Track found methods to replace all occurrences

        # Patterns for different method declarations
        patterns = [
            # Standard method declarations with modifiers
            # Matches: public void MethodName(params), private async Task<T> MethodName(), etc.
            r'(?:public\s+|private\s+|protected\s+|internal\s+|static\s+|virtual\s+|override\s+|async\s+|sealed\s+|abstract\s+|extern\s+|partial\s+)*(?:(?:void|Task|ValueTask|[\w<>\[\]?]+)\s+)(\w+)\s*(?:<[^>]+>)?\s*\(',

            # Constructor declarations (same name as class)
            r'(?:public\s+|private\s+|protected\s+|internal\s+|static\s+)(\w+)\s*\(\s*(?:[^)]*)?\s*\)\s*(?::\s*(?:base|this)\s*\([^)]*\))?\s*{',

            # Property getter/setter methods
            r'(?:public\s+|private\s+|protected\s+|internal\s+|static\s+|virtual\s+|override\s+)*[\w<>\[\]?]+\s+(\w+)\s*\{\s*(?:get|set)',

            # Interface method declarations (no modifiers)
            r'^\s*(?:Task|ValueTask|void|[\w<>\[\]?]+)\s+(\w+)\s*(?:<[^>]+>)?\s*\(',

            # Expression-bodied methods
            r'(?:public\s+|private\s+|protected\s+|internal\s+|static\s+)*(?:[\w<>\[\]?]+)\s+(\w+)\s*(?:<[^>]+>)?\s*\([^)]*\)\s*=>',

            # Local functions inside methods
            r'(?:static\s+)?(?:async\s+)?(?:void|Task|ValueTask|[\w<>\[\]?]+)\s+(\w+)\s*\([^)]*\)\s*(?:{|=>)'
        ]

        # First pass: collect all method names
        for pattern in patterns:
            try:
                matches = re.finditer(pattern, self.current_text, re.MULTILINE)
                for match in matches:
                    method_name = match.group(1)
                    # Skip common framework methods and constructors that match class names
                    if method_name not in ['Main', 'Dispose', 'Equals', 'GetHashCode', 'ToString', 'OnConfiguring', 'OnModelCreating']:
                        found_methods.add(method_name)
            except re.error as e:
                print(f"⚠️ Regex error in pattern: {e}")
                continue

        # Second pass: replace all occurrences of found method names
        temp_text = self.current_text
        for method_name in found_methods:
            # Skip if it's already a placeholder
            if re.match(r'METHOD\d+', method_name):
                continue

            placeholder = self.get_or_create_placeholder(method_name, 'METHOD')

            # Replace method declarations and calls
            # Use word boundaries to avoid partial matches
            temp_text = re.sub(
                r'\b' + re.escape(method_name) + r'\b',
                placeholder,
                temp_text
            )
            count += 1

        self.current_text = temp_text

        # Update GUI
        scroll_pos = self.text_widget.yview()
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(1.0, self.current_text)
        self.highlight_placeholders()
        self.text_widget.yview_moveto(scroll_pos[0])

        self.save_mapping()
        self.status_label.config(text=f"✅ Obfuscated {count} method names")

    def obfuscate_logs(self):
        """Obfuscate content inside logging method calls"""
        # Save state for undo
        self.undo_history.append({
            'text': self.current_text,
            'mapping': self.mapping.copy(),
            'counters': self.counters.copy(),
            'word': '[Log Content]'
        })

        if len(self.undo_history) > 50:
            self.undo_history.pop(0)

        count = 0

        # Common logging methods
        log_methods = [
            'LogDebug', 'LogInformation', 'LogWarning', 'LogError',
            'LogCritical', 'LogTrace', 'Log',
            'Console.WriteLine', 'Debug.WriteLine', 'Trace.WriteLine',
            'logger.Debug', 'logger.Info', 'logger.Warn', 'logger.Error',
            '_logger.LogDebug', '_logger.LogInformation', '_logger.LogWarning', '_logger.LogError'
        ]

        # Build pattern for all log methods
        methods_pattern = '|'.join(re.escape(method) for method in log_methods)

        # Pattern to match log calls and capture content
        # This handles nested parentheses and multi-line content
        pattern = rf'({methods_pattern})\s*\('

        temp_text = self.current_text
        pos = 0

        while True:
            match = re.search(pattern, temp_text[pos:])
            if not match:
                break

            method_name = match.group(1)
            start_pos = pos + match.end()

            # Find matching closing parenthesis
            paren_count = 1
            i = start_pos
            in_string = False
            string_char = None
            escape_next = False

            while i < len(temp_text) and paren_count > 0:
                char = temp_text[i]

                # Handle escape sequences
                if escape_next:
                    escape_next = False
                    i += 1
                    continue

                if char == '\\':
                    escape_next = True
                    i += 1
                    continue

                # Handle strings
                if not in_string and (char == '"' or char == "'"):
                    in_string = True
                    string_char = char
                elif in_string and char == string_char:
                    in_string = False
                    string_char = None

                # Count parentheses only outside strings
                if not in_string:
                    if char == '(':
                        paren_count += 1
                    elif char == ')':
                        paren_count -= 1

                i += 1

            if paren_count == 0:
                # Extract content between parentheses
                content = temp_text[start_pos:i-1]

                if content.strip():  # Only obfuscate non-empty content
                    # Create placeholder
                    placeholder = self.get_or_create_placeholder(content, 'LOG_CONTENT')

                    # Replace in current_text
                    full_match_start = pos + match.start()
                    full_match_end = i

                    self.current_text = (
                            self.current_text[:full_match_start] +
                            method_name + '(' + placeholder + ')' +
                            self.current_text[full_match_end:]
                    )

                    count += 1

            pos = i if paren_count == 0 else pos + match.end()

        # Update GUI
        scroll_pos = self.text_widget.yview()
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(1.0, self.current_text)
        self.highlight_placeholders()
        self.text_widget.yview_moveto(scroll_pos[0])

        self.save_mapping()
        self.status_label.config(text=f"✅ Obfuscated {count} log messages")

    def obfuscate_pattern(self, pattern, prefix, description):
        """Generic pattern obfuscation method"""
        # Save state for undo
        self.undo_history.append({
            'text': self.current_text,
            'mapping': self.mapping.copy(),
            'counters': self.counters.copy(),
            'word': f'[{description}]'
        })

        if len(self.undo_history) > 50:
            self.undo_history.pop(0)

        # Find and replace all matches
        count = 0
        temp_text = self.current_text

        try:
            matches = list(re.finditer(pattern, temp_text))

            # Replace in reverse order to maintain positions
            for match in reversed(matches):
                original = match.group(0)
                placeholder = self.get_or_create_placeholder(original, prefix)
                start, end = match.span()
                self.current_text = self.current_text[:start] + placeholder + self.current_text[end:]
                count += 1

            # Update text widget
            scroll_pos = self.text_widget.yview()
            self.text_widget.delete(1.0, tk.END)
            self.text_widget.insert(1.0, self.current_text)
            self.highlight_placeholders()
            self.text_widget.yview_moveto(scroll_pos[0])

            # Save mapping
            self.save_mapping()

            # Update status
            self.status_label.config(text=f"✅ Obfuscated {count} {description}")
        except re.error as e:
            self.status_label.config(text=f"❌ Pattern error: {e}")

    def obfuscate_guids(self):
        """Obfuscate all GUIDs"""
        pattern = r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'
        self.obfuscate_pattern(pattern, 'GUID', 'GUIDs')

    def obfuscate_emails(self):
        """Obfuscate all email addresses"""
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        self.obfuscate_pattern(pattern, 'EMAIL', 'emails')

    def obfuscate_ips(self):
        """Obfuscate all IP addresses"""
        pattern = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
        self.obfuscate_pattern(pattern, 'IP', 'IP addresses')

    def obfuscate_dates(self):
        """Obfuscate common date formats"""
        patterns = [
            r'\b\d{4}-\d{2}-\d{2}\b',  # YYYY-MM-DD
            r'\b\d{2}/\d{2}/\d{4}\b',  # MM/DD/YYYY
            r'\b\d{2}-\d{2}-\d{4}\b',  # DD-MM-YYYY
        ]
        count = 0
        for pattern in patterns:
            matches = len(re.findall(pattern, self.current_text))
            if matches > 0:
                self.obfuscate_pattern(pattern, 'DATE', 'dates')
                count += matches
        if count == 0:
            self.status_label.config(text="⚠️ No dates found")

    def obfuscate_numbers(self):
        """Obfuscate standalone numbers (3+ digits)"""
        pattern = r'\b\d{3,}\b'
        self.obfuscate_pattern(pattern, 'NUMBER', 'numbers')

    def obfuscate_classes(self):
        """Obfuscate C# class and interface names"""
        # Save state for undo
        self.undo_history.append({
            'text': self.current_text,
            'mapping': self.mapping.copy(),
            'counters': self.counters.copy(),
            'word': '[Classes/Interfaces]'
        })

        if len(self.undo_history) > 50:
            self.undo_history.pop(0)

        count = 0

        # Pattern for class/interface declarations
        patterns = [
            # Classes: class Name, public class Name, internal class Name : Base
            r'(?:public\s+|private\s+|internal\s+|protected\s+|abstract\s+|sealed\s+|static\s+|partial\s+)*class\s+(\w+)(?:\s*:\s*[\w\s,<>]+)?',
            # Interfaces: interface IName, public interface IName
            r'(?:public\s+|private\s+|internal\s+|protected\s+)*interface\s+(\w+)(?:\s*:\s*[\w\s,<>]+)?',
            # Structs (bonus)
            r'(?:public\s+|private\s+|internal\s+|readonly\s+)*struct\s+(\w+)',
            # Enums (bonus)
            r'(?:public\s+|private\s+|internal\s+)*enum\s+(\w+)'
        ]

        temp_text = self.current_text

        for pattern in patterns:
            matches = list(re.finditer(pattern, temp_text))

            for match in reversed(matches):
                class_name = match.group(1)
                placeholder = self.get_or_create_placeholder(class_name, 'CLASS')

                # Replace all occurrences of this class name
                self.current_text = re.sub(r'\b' + re.escape(class_name) + r'\b',
                                           placeholder, self.current_text)
                count += 1

        # Update GUI
        scroll_pos = self.text_widget.yview()
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(1.0, self.current_text)
        self.highlight_placeholders()
        self.text_widget.yview_moveto(scroll_pos[0])

        self.save_mapping()
        self.status_label.config(text=f"✅ Obfuscated {count} classes/interfaces")

    def obfuscate_namespaces(self):
        """Obfuscate C# namespace declarations"""
        # Save state for undo
        self.undo_history.append({
            'text': self.current_text,
            'mapping': self.mapping.copy(),
            'counters': self.counters.copy(),
            'word': '[Namespaces]'
        })

        if len(self.undo_history) > 50:
            self.undo_history.pop(0)

        count = 0

        # Pattern for namespace declarations
        pattern = r'namespace\s+([\w\.]+)'

        matches = list(re.finditer(pattern, self.current_text))

        for match in reversed(matches):
            namespace = match.group(1)

            # Option 1: Obfuscate entire namespace
            placeholder = self.get_or_create_placeholder(namespace, 'NAMESPACE')

            # Option 2: Obfuscate each part separately (uncomment if preferred)
            # parts = namespace.split('.')
            # obfuscated_parts = []
            # for part in parts:
            #     part_placeholder = self.get_or_create_placeholder(part, 'NAMESPACE_PART')
            #     obfuscated_parts.append(part_placeholder)
            # placeholder = '.'.join(obfuscated_parts)

            # Replace in the namespace declaration
            start, end = match.span(1)
            self.current_text = self.current_text[:start] + placeholder + self.current_text[end:]

            # Also replace all using statements with this namespace
            self.current_text = re.sub(r'using\s+' + re.escape(namespace) + r'(?:\s*;|\s*\.\w+)',
                                       'using ' + placeholder, self.current_text)
            count += 1

        # Update GUI
        scroll_pos = self.text_widget.yview()
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(1.0, self.current_text)
        self.highlight_placeholders()
        self.text_widget.yview_moveto(scroll_pos[0])

        self.save_mapping()
        self.status_label.config(text=f"✅ Obfuscated {count} namespaces")

    def obfuscate_ids(self):
        """Obfuscate common ID patterns"""
        patterns = [
            (r'\b[A-Z]{2,}-\d+\b', 'ID'),  # PREFIX-123
            (r'\b\d+[A-Z]+\d+\b', 'ID'),   # 123ABC456
            (r'\b[A-Z]+\d{4,}\b', 'ID'),   # ABC1234
        ]
        count = 0
        for pattern, prefix in patterns:
            matches = len(re.findall(pattern, self.current_text))
            if matches > 0:
                self.obfuscate_pattern(pattern, prefix, 'IDs')
                count += matches
        if count == 0:
            self.status_label.config(text="⚠️ No IDs found")

    def obfuscate_paths(self):
        """Obfuscate file paths"""
        patterns = [
            r'[A-Za-z]:\\[\w\\.-]+',  # Windows paths
            r'/[\w/.-]+\.\w+',        # Unix paths with extension
            r'\.{1,2}/[\w/.-]+',      # Relative paths
        ]
        count = 0
        for pattern in patterns:
            matches = len(re.findall(pattern, self.current_text))
            if matches > 0:
                self.obfuscate_pattern(pattern, 'PATH', 'paths')
                count += matches
        if count == 0:
            self.status_label.config(text="⚠️ No paths found")

    def obfuscate_urls(self):
        """Obfuscate URLs"""
        pattern = r'https?://[^\s\'"<>\])]+'
        self.obfuscate_pattern(pattern, 'URL', 'URLs')

    def obfuscate_similar_pattern(self):
        """Obfuscate all strings similar to the entered pattern"""
        if not hasattr(self, 'pattern_entry') or not hasattr(self, 'status_label'):
            print("⚠️ GUI not fully initialized")
            return

        sample = self.pattern_entry.get().strip()

        if not sample:
            self.status_label.config(text="⚠️ Please enter a pattern")
            return

        # Save state for undo
        self.undo_history.append({
            'text': self.current_text,
            'mapping': self.mapping.copy(),
            'counters': self.counters.copy(),
            'word': f'[Pattern: {sample}]'
        })

        if len(self.undo_history) > 50:
            self.undo_history.pop(0)

        # Determine pattern based on sample
        pattern_mode = self.pattern_type.get()

        # 🔍 Debug info
        print(f"🔍 Pattern mode: {pattern_mode}")
        print(f"🔍 Sample: '{sample}' (length: {len(sample)})")

        if pattern_mode == "exact":
            pattern = re.escape(sample)

        elif pattern_mode == "length":
            # Same length as sample
            length = len(sample)
            if sample.isdigit():
                pattern = r'\b\d{' + str(length) + r'}\b'
            elif sample.isalpha():
                pattern = r'\b[A-Za-z]{' + str(length) + r'}\b'
            else:
                # Mixed content - match any non-whitespace of same length
                pattern = r'\b\S{' + str(length) + r'}\b'

            print(f"🔍 Generated pattern: {pattern}")

        else:  # similar structure
            # Build pattern based on character types
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
                        # Mixed case
                        pattern_parts.append(r'[A-Za-z]{' + str(j-i) + '}')
                    i = j
                else:
                    pattern_parts.append(re.escape(sample[i]))
                    i += 1

            pattern = r'\b' + ''.join(pattern_parts) + r'\b'

        # Find and replace matches
        count = 0
        found_matches = []

        try:
            matches = list(re.finditer(pattern, self.current_text))

            # 🔍 Debug: show what we found
            for match in matches:
                found_matches.append(match.group(0))

            if found_matches:
                print(f"🔍 Found {len(found_matches)} matches: {found_matches[:10]}...")  # Show first 10

            # Replace in reverse order
            for match in reversed(matches):
                original = match.group(0)
                placeholder = self.get_or_create_placeholder(original, 'PATTERN')
                start, end = match.span()
                self.current_text = self.current_text[:start] + placeholder + self.current_text[end:]
                count += 1

            # Update text widget
            scroll_pos = self.text_widget.yview()
            self.text_widget.delete(1.0, tk.END)
            self.text_widget.insert(1.0, self.current_text)
            self.highlight_placeholders()
            self.text_widget.yview_moveto(scroll_pos[0])

            # Save mapping
            self.save_mapping()

            # Update status with more detail
            if count > 0:
                examples = ', '.join(found_matches[:3])
                if len(found_matches) > 3:
                    examples += '...'
                self.status_label.config(text=f"✅ Obfuscated {count} matches: {examples}")
            else:
                self.status_label.config(text=f"⚠️ No matches found for pattern '{sample}' (length {len(sample)})")

        except re.error as e:
            self.status_label.config(text=f"❌ Invalid pattern: {e}")

    def clear_mappings(self):
        """Clear all mappings after confirmation"""
        from tkinter import messagebox
        if messagebox.askyesno("Clear Mappings", f"Are you sure you want to clear all {len(self.mapping)} mappings?"):
            # 🔄 Save state before clearing
            self.undo_history.append({
                'text': self.current_text,
                'mapping': self.mapping.copy(),
                'counters': self.counters.copy(),
                'word': '[ALL MAPPINGS]'
            })

            self.mapping = {}
            self.counters = {}
            self.save_mapping()
            self.status_label.config(text="✅ All mappings cleared!")
            print("🗑️ All mappings cleared!")

    def copy_to_clipboard(self):
        """Copy current text to clipboard"""
        pyperclip.copy(self.current_text)
        self.status_label.config(text="✅ Copied to clipboard!")

    def deobfuscate_placeholder(self, placeholder):
        """Replace placeholder with original value and remove mapping"""
        # Find original value by searching through mappings
        original_value = None
        for orig, placehold in self.mapping.items():
            if placehold == placeholder:
                original_value = orig
                break

        if not original_value:
            self.status_label.config(text=f"⚠️ No mapping found for {placeholder}")
            return

        # Save state for undo
        self.undo_history.append({
            'text': self.current_text,
            'mapping': self.mapping.copy(),
            'counters': self.counters.copy(),
            'word': f'[De-obfuscate: {placeholder}]'
        })

        if len(self.undo_history) > 50:
            self.undo_history.pop(0)

        # Replace all occurrences of placeholder with original
        count = self.current_text.count(placeholder)
        self.current_text = self.current_text.replace(placeholder, original_value)

        # Remove from mapping
        del self.mapping[original_value]

        # Update GUI
        scroll_pos = self.text_widget.yview()
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(1.0, self.current_text)
        self.highlight_placeholders()
        self.text_widget.yview_moveto(scroll_pos[0])

        # Save updated mapping
        self.save_mapping()

        # Update status
        self.status_label.config(text=f"🔓 De-obfuscated {placeholder} → '{original_value}' ({count} occurrences)")

    def run_interactive(self, initial_text):
        """Run the interactive obfuscator"""
        self.original_text = initial_text

        # Initial obfuscation
        print("🔐 Running initial obfuscation...")
        self.current_text = self.obfuscate(initial_text)

        # 🆕 AUTO-OBFUSCATE IPs, EMAILS, PATHS, and NAMESPACES
        print("🔍 Auto-obfuscating IPs, emails, paths, and namespaces...")

        # Store original mapping count to track new additions
        original_mapping_count = len(self.mapping)

        # Auto-obfuscate emails
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_matches = list(re.finditer(email_pattern, self.current_text))
        for match in reversed(email_matches):
            original = match.group(0)
            placeholder = self.get_or_create_placeholder(original, 'EMAIL')
            start, end = match.span()
            self.current_text = self.current_text[:start] + placeholder + self.current_text[end:]

        # Auto-obfuscate IPs
        ip_pattern = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
        ip_matches = list(re.finditer(ip_pattern, self.current_text))
        for match in reversed(ip_matches):
            original = match.group(0)
            placeholder = self.get_or_create_placeholder(original, 'IP')
            start, end = match.span()
            self.current_text = self.current_text[:start] + placeholder + self.current_text[end:]

        # Auto-obfuscate paths
        path_patterns = [
            r'[A-Za-z]:\\[\w\\.-]+',  # Windows paths
            r'/[\w/.-]+\.\w+',        # Unix paths with extension
            r'\.{1,2}/[\w/.-]+',      # Relative paths
        ]
        for pattern in path_patterns:
            path_matches = list(re.finditer(pattern, self.current_text))
            for match in reversed(path_matches):
                original = match.group(0)
                placeholder = self.get_or_create_placeholder(original, 'PATH')
                start, end = match.span()
                self.current_text = self.current_text[:start] + placeholder + self.current_text[end:]

        # 🆕 Auto-obfuscate namespaces (except Microsoft.*)
        print("📦 Auto-obfuscating namespaces...")
        found_namespaces = set()

        # Find namespace declarations
        namespace_pattern = r'namespace\s+([\w\.]+)'
        namespace_matches = re.finditer(namespace_pattern, self.current_text)
        for match in namespace_matches:
            namespace = match.group(1)  # Only captures the namespace name, not "namespace" keyword
            if not namespace.startswith('Microsoft.'):
                found_namespaces.add(namespace)

        # Find using statements
        using_pattern = r'using\s+([\w\.]+)\s*;'
        using_matches = re.finditer(using_pattern, self.current_text)
        for match in using_matches:
            namespace = match.group(1)  # Only captures the namespace name, not "using" keyword
            if not namespace.startswith('Microsoft.') and not namespace.startswith('System.'):
                found_namespaces.add(namespace)

        # Replace all found namespaces
        for namespace in sorted(found_namespaces, key=len, reverse=True):  # Longest first
            placeholder = self.get_or_create_placeholder(namespace, 'NAMESPACE')
            # This only replaces the namespace name, not keywords
            self.current_text = re.sub(r'\b' + re.escape(namespace) + r'\b',
                                       placeholder, self.current_text)

        auto_obfuscated = len(self.mapping) - original_mapping_count
        print(f"✅ Auto-obfuscated {auto_obfuscated} items (IPs, emails, paths, namespaces)")

        # 🆕 Apply existing mappings automatically
        replaced_count = 0
        if self.mapping:
            print(f"📂 Applying {len(self.mapping)} existing mappings...")
            replaced_count = self.apply_existing_mappings()
            print(f"✅ Auto-replaced {replaced_count} occurrences")

        # Create and setup GUI
        self.create_gui()

        # Insert obfuscated text
        self.text_widget.insert(1.0, self.current_text)

        # Highlight existing placeholders
        self.highlight_placeholders()

        # Save initial mapping
        self.save_mapping()

        # 🆕 Update status to show auto-replacements
        status_text = f"✅ Ready - {len(self.mapping)} mappings"
        if auto_obfuscated > 0:
            status_text += f", auto-obfuscated {auto_obfuscated} items"
        if replaced_count > 0:
            status_text += f", replaced {replaced_count} items"

        self.status_label.config(text=status_text)

        # Run GUI
        self.root.mainloop()

    def on_mouse_motion(self, event):
        """Highlight word on hover - show different cursor for placeholders"""
        # Remove previous hover highlight
        self.text_widget.tag_remove("hover", 1.0, tk.END)

        # Get mouse position
        index = self.text_widget.index(f"@{event.x},{event.y}")

        # Get the line content
        line_start = index.split('.')[0] + '.0'
        line_end = index.split('.')[0] + '.end'
        line_content = self.text_widget.get(line_start, line_end)

        # Get character position in line
        char_pos = int(index.split('.')[1])

        # 🆕 Check if we're hovering over a placeholder
        temp_start = max(0, char_pos - 20)
        temp_end = min(len(line_content), char_pos + 20)
        surrounding_text = line_content[temp_start:temp_end]

        placeholder_pattern = r'(SENSITIVE|URL|STRING|ANONYMIZED|PATTERN|GUID|EMAIL|IP|DATE|NUMBER|ID|PATH|CLASS|NAMESPACE|LOG_CONTENT|METHOD|LAMBDA_PROP|PLACEHOLDER)\d+'
        is_likely_placeholder = bool(re.search(placeholder_pattern, surrounding_text))

        if is_likely_placeholder:
            separators = '.,-/\\()[]{}\'\"<>:;=+*&|!?#@$%^~\t\n '
        else:
            separators = '.,-_/\\()[]{}\'\"<>:;=+*&|!?#@$%^~\t\n '

        # Find word boundaries
        start = char_pos
        end = char_pos

        # Search backward for word start
        while start > 0 and line_content[start - 1] not in separators:
            start -= 1

        # Search forward for word end
        while end < len(line_content) and line_content[end] not in separators:
            end += 1

        # Highlight the word
        if start < end:
            word_start = f"{index.split('.')[0]}.{start}"
            word_end = f"{index.split('.')[0]}.{end}"

            word = line_content[start:end]

            # Check if it's a complete placeholder
            if re.match(r'^(SENSITIVE|URL|STRING|ANONYMIZED|PATTERN|GUID|EMAIL|IP|DATE|NUMBER|ID|PATH|CLASS|NAMESPACE|LOG_CONTENT|METHOD|LAMBDA_PROP|PLACEHOLDER)\d+$', word):
                # It's a placeholder - use different hover style
                self.text_widget.tag_add("hover", word_start, word_end)
                self.text_widget.tag_config("hover", background="#ff9999", foreground="black")
                self.text_widget.config(cursor="exchange")  # Different cursor
            else:
                # Regular word
                self.text_widget.tag_add("hover", word_start, word_end)
                self.text_widget.tag_config("hover", background="#e0e0e0", foreground="black")
                self.text_widget.config(cursor="hand2" if self.pattern_select_mode else "xterm")

    def on_mouse_leave(self, event):
        """Remove hover highlight when mouse leaves"""
        self.text_widget.tag_remove("hover", 1.0, tk.END)

def main():
    obfuscator = InteractiveCodeObfuscator()

    clipboard_content = pyperclip.paste()

    if not clipboard_content:
        print("❌ Clipboard is empty!")
        return

    print("🔐 Starting interactive obfuscator...")
    obfuscator.run_interactive(clipboard_content)

if __name__ == "__main__":
    main()