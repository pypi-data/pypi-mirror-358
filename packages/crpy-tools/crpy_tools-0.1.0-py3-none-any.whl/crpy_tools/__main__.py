#!/usr/bin/env python
"""
Python Comment Remover
Removes all comments from Python files while preserving indentation and code structure.
"""

import re
import sys
import argparse
import os
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QLabel, QLineEdit, QPushButton, QTextEdit, QCheckBox, QGroupBox,
                              QFileDialog, QProgressBar, QStatusBar, QMessageBox)
from PySide6.QtCore import Qt, QThread, Signal, QSettings
from PySide6.QtGui import QFont, QTextOption

class CommentRemoverWorker(QThread):
    """Worker thread for processing files to avoid freezing the GUI"""
    progress_signal = Signal(str, int)
    finished_signal = Signal()
    error_signal = Signal(str)

    def __init__(self, input_path, output_path, suffix, remove_docstrings, recursive):
        super().__init__()
        self.input_path = Path(input_path)
        self.output_path = Path(output_path) if output_path else None
        self.suffix = suffix
        self.remove_docstrings = remove_docstrings
        self.recursive = recursive
        self.cancel_requested = False

    def run(self):
        """Main processing method"""
        try:
            if self.input_path.is_file():
                # Determine output path for single file
                if self.output_path:
                    if self.output_path.is_dir():
                        output_file = self.output_path / self.input_path.name
                    else:
                        output_file = self.output_path
                else:
                    # Add suffix to filename in same directory
                    output_file = self.input_path.parent / f"{self.input_path.stem}{self.suffix}{self.input_path.suffix}"
                
                self.process_file(self.input_path, output_file, self.remove_docstrings)
                self.progress_signal.emit(f"Processed: {self.input_path} -> {output_file}", 100)
                
            elif self.input_path.is_dir():
                pattern = '**/*.py' if self.recursive else '*.py'
                files = list(self.input_path.glob(pattern))
                total = len(files)
                
                if total == 0:
                    self.error_signal.emit("No Python files found in the specified directory")
                    return
                
                for i, py_file in enumerate(files):
                    if self.cancel_requested:
                        self.progress_signal.emit("Processing canceled", 0)
                        return
                    
                    if self.output_path:
                        # Create output directory structure
                        rel_path = py_file.relative_to(self.input_path)
                        output_file = self.output_path / rel_path
                        output_file.parent.mkdir(parents=True, exist_ok=True)
                    else:
                        # Add suffix to filename in same directory
                        output_file = py_file.parent / f"{py_file.stem}{self.suffix}{py_file.suffix}"
                    
                    self.process_file(py_file, output_file, self.remove_docstrings)
                    self.progress_signal.emit(f"Processed: {py_file}", int((i+1)/total*100))
            else:
                self.error_signal.emit(f"Error: {self.input_path} is not a valid file or directory")
        except Exception as e:
            self.error_signal.emit(f"Error during processing: {str(e)}")
        finally:
            self.finished_signal.emit()

    def process_file(self, input_path, output_path, remove_docstrings):
        """Process a single file with error handling"""
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            processed_content = remove_comments_from_text(content, remove_docstrings)
            
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(processed_content)
        except Exception as e:
            self.error_signal.emit(f"Error processing {input_path}: {e}")

    def cancel(self):
        """Request cancellation of processing"""
        self.cancel_requested = True


def remove_comments_from_line(line):
    """
    Remove comments from a single line while handling strings properly.
    Preserves the original indentation.
    """
    # Track if we're inside a string
    in_single_quote = False
    in_double_quote = False
    in_triple_single = False
    in_triple_double = False
    escaped = False
    i = 0
    
    while i < len(line):
        char = line[i]
        
        # Handle escape sequences
        if escaped:
            escaped = False
            i += 1
            continue
            
        if char == '\\' and (in_single_quote or in_double_quote):
            escaped = True
            i += 1
            continue
        
        # Check for triple quotes first
        if i <= len(line) - 3:
            if line[i:i+3] == '"""':
                if not in_single_quote and not in_triple_single:
                    in_triple_double = not in_triple_double
                    i += 3
                    continue
            elif line[i:i+3] == "'''":
                if not in_double_quote and not in_triple_double:
                    in_triple_single = not in_triple_single
                    i += 3
                    continue
        
        # Handle single character quotes
        if char == '"' and not in_single_quote and not in_triple_single and not in_triple_double:
            in_double_quote = not in_double_quote
        elif char == "'" and not in_double_quote and not in_triple_double and not in_triple_single:
            in_single_quote = not in_single_quote
        elif char == '#' and not (in_single_quote or in_double_quote or in_triple_single or in_triple_double):
            # Found a comment outside of strings - remove everything from here
            return line[:i].rstrip() + '\n' if line.endswith('\n') else line[:i].rstrip()
        
        i += 1
    
    return line

def is_docstring_line(line, prev_lines, remove_docstrings):
    """
    Check if a line is likely part of a docstring.
    Simple heuristic: if it's a string literal at the beginning of a function/class/module.
    """
    if not remove_docstrings:
        return False
    
    stripped = line.strip()
    if not (stripped.startswith('"""') or stripped.startswith("'''")):
        return False
    
    # If this is the very first content line (module docstring)
    if not prev_lines or all(not prev_line.strip() for prev_line in prev_lines):
        return True
    
    # Look at previous non-empty, non-comment lines to see if this could be a docstring
    code_lines_seen = 0
    for prev_line in reversed(prev_lines):
        prev_stripped = prev_line.strip()
        if not prev_stripped or prev_stripped.startswith('#'):
            continue
        
        code_lines_seen += 1
        
        # Check if previous line indicates start of function, class, or module
        if (prev_stripped.startswith('def ') or 
            prev_stripped.startswith('class ') or 
            prev_stripped.startswith('async def ') or
            prev_stripped.endswith(':')):
            return True
        
        # If this is the first real code line after imports/shebang, it could be module docstring
        if code_lines_seen == 1 and (
            prev_stripped.startswith('import ') or
            prev_stripped.startswith('from ') or
            prev_stripped.startswith('#!')  # shebang
        ):
            return True
        
        # If we hit other actual code, this is probably not a docstring
        if code_lines_seen >= 2:
            break
    
    return False

def clean_excessive_whitespace(lines):
    """
    Remove unnecessary whitespace but add strategic blank lines for readability.
    Add blank lines before: classes, functions, methods (except first in class).
    """
    if not lines:
        return lines
        
    cleaned = []
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Only process lines that have actual content
        if not stripped:
            continue
            
        # Check if we need to add a blank line before this line
        should_add_blank = False
        
        if i > 0:  # Don't add blank line before first line
            # Add blank line before class definitions
            if stripped.startswith('class '):
                should_add_blank = True
            
            # Add blank line before function definitions (but not methods immediately after class)
            elif stripped.startswith('def ') or stripped.startswith('async def '):
                # Check if this is a method (inside a class) or a standalone function
                # Look at previous non-blank lines to determine context
                prev_line_found = False
                for j in range(i-1, -1, -1):
                    prev_stripped = lines[j].strip()
                    if prev_stripped:
                        prev_line_found = True
                        # If previous line is class definition, don't add blank (first method)
                        if prev_stripped.startswith('class '):
                            should_add_blank = False
                        else:
                            should_add_blank = True
                        break
                
                if not prev_line_found:
                    should_add_blank = True
        
        # Add blank line if needed
        if should_add_blank:
            cleaned.append('\n')
        
        # Add the actual line
        cleaned.append(line)
    
    return cleaned

def remove_comments_from_text(text, remove_docstrings=False):
    """
    Remove comments from Python code text while preserving indentation.
    Handles multi-line strings and various comment scenarios.
    """
    lines = text.splitlines(keepends=True)
    result_lines = []
    in_multiline_string = False
    in_docstring = False
    multiline_delimiter = None
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Skip empty lines entirely for minification
        if not stripped:
            continue
        
        # Handle multi-line string/docstring detection
        if not in_multiline_string and not in_docstring:
            # Check if this line starts a multi-line string
            for delimiter in ['"""', "'''"]:
                if delimiter in line:
                    # Count occurrences to see if string is closed on same line
                    count = line.count(delimiter)
                    if count % 2 == 1:  # Odd count means string is opened but not closed
                        # Check if this is a docstring
                        if is_docstring_line(line, result_lines, remove_docstrings):
                            in_docstring = True
                        else:
                            in_multiline_string = True
                        multiline_delimiter = delimiter
                        break
            
            # Handle single-line docstrings
            if remove_docstrings and not in_multiline_string and not in_docstring:
                for delimiter in ['"""', "'''"]:
                    if line.count(delimiter) >= 2:  # Single line docstring
                        if is_docstring_line(line, result_lines, remove_docstrings):
                            # Skip this line entirely
                            continue
        
        elif in_docstring:
            # We're in a docstring, check if it's closed
            if multiline_delimiter in line:
                count = line.count(multiline_delimiter)
                if count % 2 == 1:  # Odd count means string is closed
                    in_docstring = False
                    multiline_delimiter = None
            # Skip docstring lines
            continue
            
        elif in_multiline_string:
            # We're in a multi-line string, check if it's closed
            if multiline_delimiter in line:
                count = line.count(multiline_delimiter)
                if count % 2 == 1:  # Odd count means string is closed
                    in_multiline_string = False
                    multiline_delimiter = None
            # Keep multi-line string content
            result_lines.append(line)
        
        # Process regular lines (not in docstring or multiline string)
        if not in_multiline_string and not in_docstring:
            # Process line for comment removal
            processed_line = remove_comments_from_line(line)
            
            # Only add lines that have content after processing
            if processed_line.strip():
                result_lines.append(processed_line)
    
    # Add strategic blank lines for readability
    result_lines = clean_excessive_whitespace(result_lines)
    
    return ''.join(result_lines)


class PythonCommentRemoverGUI(QMainWindow):
    """Main GUI window for the Python Comment Remover"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python Comment Remover")
        self.resize(800, 600)
        
        # Load settings
        self.settings = QSettings("PythonCommentRemover", "Settings")
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        
        # Create input section
        input_group = QGroupBox("Input Options")
        input_layout = QVBoxLayout(input_group)
        
        # Input file/directory selection
        input_path_layout = QHBoxLayout()
        input_path_layout.addWidget(QLabel("Input File/Directory:"))
        self.input_path_edit = QLineEdit()
        self.input_path_edit.setPlaceholderText("Select a file or directory...")
        input_path_layout.addWidget(self.input_path_edit, 3)
        
        self.browse_input_btn = QPushButton("Browse...")
        self.browse_input_btn.clicked.connect(self.browse_input)
        input_path_layout.addWidget(self.browse_input_btn)
        
        input_layout.addLayout(input_path_layout)
        
        # Output options
        output_path_layout = QHBoxLayout()
        output_path_layout.addWidget(QLabel("Output Directory:"))
        self.output_path_edit = QLineEdit()
        self.output_path_edit.setPlaceholderText("Select output directory (optional)...")
        output_path_layout.addWidget(self.output_path_edit, 3)
        
        self.browse_output_btn = QPushButton("Browse...")
        self.browse_output_btn.clicked.connect(self.browse_output)
        output_path_layout.addWidget(self.browse_output_btn)
        
        input_layout.addLayout(output_path_layout)
        
        # Suffix option
        suffix_layout = QHBoxLayout()
        suffix_layout.addWidget(QLabel("Output File Suffix:"))
        self.suffix_edit = QLineEdit("_no_comments")
        suffix_layout.addWidget(self.suffix_edit)
        input_layout.addLayout(suffix_layout)
        
        # Options checkboxes
        options_layout = QHBoxLayout()
        self.recursive_cb = QCheckBox("Process Subdirectories")
        self.remove_docstrings_cb = QCheckBox("Remove Docstrings")
        options_layout.addWidget(self.recursive_cb)
        options_layout.addWidget(self.remove_docstrings_cb)
        input_layout.addLayout(options_layout)
        
        main_layout.addWidget(input_group)
        
        # Create action buttons
        button_layout = QHBoxLayout()
        self.run_btn = QPushButton("Run Processing")
        self.run_btn.setFixedHeight(40)
        self.run_btn.clicked.connect(self.start_processing)
        button_layout.addWidget(self.run_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setFixedHeight(40)
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.cancel_processing)
        button_layout.addWidget(self.cancel_btn)
        
        main_layout.addLayout(button_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(True)
        main_layout.addWidget(self.progress_bar)
        
        # Log output
        log_group = QGroupBox("Processing Log")
        log_layout = QVBoxLayout(log_group)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Courier New", 10))
        self.log_text.setWordWrapMode(QTextOption.NoWrap)
        log_layout.addWidget(self.log_text)
        
        main_layout.addWidget(log_group, 1)  # Give log area more space
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready to process files")
        
        # Initialize worker thread
        self.worker_thread = None
        
        # Load saved settings
        self.load_settings()
    
    def load_settings(self):
        """Load saved settings from previous session"""
        # Load input path
        input_path = self.settings.value("input_path", "")
        if input_path:
            self.input_path_edit.setText(input_path)
            
        # Load output path
        output_path = self.settings.value("output_path", "")
        if output_path:
            self.output_path_edit.setText(output_path)
            
        # Load suffix
        suffix = self.settings.value("suffix", "_no_comments")
        self.suffix_edit.setText(suffix)
            
        # Load options
        self.recursive_cb.setChecked(self.settings.value("recursive", False, type=bool))
        self.remove_docstrings_cb.setChecked(self.settings.value("remove_docstrings", False, type=bool))
    
    def save_settings(self):
        """Save current settings for next session"""
        self.settings.setValue("input_path", self.input_path_edit.text())
        self.settings.setValue("output_path", self.output_path_edit.text())
        self.settings.setValue("suffix", self.suffix_edit.text())
        self.settings.setValue("recursive", self.recursive_cb.isChecked())
        self.settings.setValue("remove_docstrings", self.remove_docstrings_cb.isChecked())
    
    def closeEvent(self, event):
        """Handle window close event"""
        self.save_settings()
        event.accept()
    
    def browse_input(self):
        """Open dialog to select input file or directory"""
        path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Python File", 
            self.input_path_edit.text() or "", 
            "Python Files (*.py);;All Files (*)"
        )
        
        if not path:
            # If file dialog canceled, try directory dialog
            path = QFileDialog.getExistingDirectory(
                self, 
                "Select Directory", 
                self.input_path_edit.text() or ""
            )
        
        if path:
            self.input_path_edit.setText(path)
    
    def browse_output(self):
        """Open dialog to select output directory"""
        path = QFileDialog.getExistingDirectory(
            self, 
            "Select Output Directory", 
            self.output_path_edit.text() or ""
        )
        
        if path:
            self.output_path_edit.setText(path)
    
    def start_processing(self):
        """Start the comment removal process"""
        input_path = self.input_path_edit.text().strip()
        if not input_path:
            QMessageBox.warning(self, "Input Required", "Please select an input file or directory.")
            return
        
        output_path = self.output_path_edit.text().strip() or None
        suffix = self.suffix_edit.text().strip()
        remove_docstrings = self.remove_docstrings_cb.isChecked()
        recursive = self.recursive_cb.isChecked()
        
        # Clear log
        self.log_text.clear()
        self.log_text.append("Starting processing...")
        self.log_text.append("-" * 80)
        
        # Validate output path if specified
        if output_path and not os.path.exists(output_path):
            try:
                os.makedirs(output_path, exist_ok=True)
            except Exception as e:
                QMessageBox.critical(self, "Output Error", f"Cannot create output directory: {str(e)}")
                return
        
        # Create and start worker thread
        self.worker_thread = CommentRemoverWorker(
            input_path,
            output_path,
            suffix,
            remove_docstrings,
            recursive
        )
        
        # Connect signals
        self.worker_thread.progress_signal.connect(self.update_progress)
        self.worker_thread.finished_signal.connect(self.processing_finished)
        self.worker_thread.error_signal.connect(self.handle_error)
        
        # Update UI
        self.run_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.status_bar.showMessage("Processing files...")
        self.progress_bar.setValue(0)
        
        # Start thread
        self.worker_thread.start()
    
    def cancel_processing(self):
        """Request cancellation of the current processing"""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.cancel()
            self.cancel_btn.setEnabled(False)
            self.status_bar.showMessage("Canceling...")
    
    def update_progress(self, message, progress):
        """Update progress bar and log"""
        self.log_text.append(message)
        self.progress_bar.setValue(progress)
        self.status_bar.showMessage(message)
    
    def processing_finished(self):
        """Handle completion of processing"""
        self.log_text.append("-" * 80)
        self.log_text.append("Processing complete!")
        self.progress_bar.setValue(100)
        self.run_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.status_bar.showMessage("Processing complete")
        
        # Save settings
        self.save_settings()
        
        # Show completion message
        QMessageBox.information(self, "Processing Complete", "Comment removal process has finished successfully.")
    
    def handle_error(self, error_message):
        """Display error messages"""
        self.log_text.append(f"ERROR: {error_message}")
        self.log_text.append("-" * 80)
        self.log_text.append("Processing stopped due to errors")
        self.progress_bar.setValue(0)
        self.run_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.status_bar.showMessage("Processing stopped due to errors")
        
        # Show error message
        QMessageBox.critical(self, "Processing Error", error_message)

def print_help():
    """Print detailed help information for CLI usage"""
    help_text = """
Python Comment Remover - CLI Usage

This tool removes comments from Python files while preserving code structure.

Basic Usage:
  python comment_remover.py [OPTIONS] INPUT

Required Arguments:
  INPUT              Path to input Python file or directory

Options:
  -o, --output PATH  Output file or directory (default: add suffix to filename)
  -r, --recursive    Process directory recursively (only for directory input)
  -d, --remove-docstrings
                     Also remove docstrings
  --suffix SUFFIX    Suffix for output files (default: '_no_comments')
  -h, --help         Show this help message and exit

Examples:
  1. Process a single file:
     python comment_remover.py input.py -o output.py
     
  2. Process a directory recursively, removing docstrings:
     python comment_remover.py my_project/ -o cleaned_project/ -r -d
     
  3. Process all files in current directory with custom suffix:
     python comment_remover.py . --suffix "_clean"
"""
    print(help_text)

def main_cli():
    """Command line interface entry point"""
    parser = argparse.ArgumentParser(
        description="Remove comments from Python files while preserving indentation",
        add_help=False  # We'll handle help manually to show extended help
    )
    parser.add_argument('input', nargs='?', help='Input Python file or directory')
    parser.add_argument('-o', '--output', help='Output file (if not specified, prints to stdout)')
    parser.add_argument('-r', '--recursive', action='store_true', help='Process directory recursively')
    parser.add_argument('-d', '--remove-docstrings', action='store_true', help='Also remove docstrings')
    parser.add_argument('--suffix', default='_no_comments', help='Suffix for output files when processing directories')
    parser.add_argument('-h', '--help', action='store_true', help='Show extended help information')
    
    args = parser.parse_args()
    
    if args.help or not args.input:
        print_help()
        if not args.input:
            sys.exit(1)
        else:
            sys.exit(0)
    
    input_path = Path(args.input)
    
    if input_path.is_file():
        # Process single file
        if args.output:
            output_path = Path(args.output)
            # If output is a directory, use input filename
            if output_path.is_dir():
                output_path = output_path / input_path.name
        else:
            # Add suffix to filename in same directory
            output_path = input_path.parent / f"{input_path.stem}{args.suffix}{input_path.suffix}"
            
        process_file(input_path, output_path, args.remove_docstrings)
        
    elif input_path.is_dir():
        # Process directory
        pattern = '**/*.py' if args.recursive else '*.py'
        
        for py_file in input_path.glob(pattern):
            if args.output:
                # Create output directory structure
                rel_path = py_file.relative_to(input_path)
                output_dir = Path(args.output)
                output_file = output_dir / rel_path
                output_file.parent.mkdir(parents=True, exist_ok=True)
            else:
                # Add suffix to filename in same directory
                output_file = py_file.parent / f"{py_file.stem}{args.suffix}{py_file.suffix}"
            
            process_file(py_file, output_file, args.remove_docstrings)
    else:
        print(f"Error: {input_path} is not a valid file or directory", file=sys.stderr)
        sys.exit(1)

def process_file(input_path, output_path=None, remove_docstrings=False):
    """
    Process a single Python file to remove comments.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        processed_content = remove_comments_from_text(content, remove_docstrings)
        
        if output_path:
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(processed_content)
            print(f"Processed: {input_path} -> {output_path}")
        else:
            # Output to stdout
            print(processed_content)
            
    except Exception as e:
        print(f"Error processing {input_path}: {e}", file=sys.stderr)

if __name__ == "__main__":
    # Check if we should run CLI or GUI
    if len(sys.argv) > 1:
        main_cli()
    else:
        app = QApplication(sys.argv)
        window = PythonCommentRemoverGUI()
        window.show()
        sys.exit(app.exec())