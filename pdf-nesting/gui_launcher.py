#!/usr/bin/env python3
"""
GUI Launcher for PDF Nesting - Windows Friendly
Simple GUI interface using tkinter
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import threading
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from pdf_nesting_pipeline import PDFNestingPipeline


class PDFNestingGUI:
    """Simple GUI for PDF Nesting"""

    def __init__(self, root):
        self.root = root
        self.root.title("PDF Nesting System")
        self.root.geometry("600x500")
        self.root.resizable(False, False)

        # Variables
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
        self.sheet_width = tk.IntVar(value=1000)
        self.sheet_height = tk.IntVar(value=1000)
        self.spacing = tk.DoubleVar(value=5.0)
        self.output_format = tk.StringVar(value="pdf")
        self.rotation_enabled = tk.BooleanVar(value=True)

        self.create_widgets()

    def create_widgets(self):
        """Create GUI widgets"""

        # Title
        title = tk.Label(
            self.root,
            text="PDF Nesting System",
            font=("Arial", 16, "bold"),
            pady=10
        )
        title.pack()

        # Frame for inputs
        input_frame = ttk.LabelFrame(self.root, text="Input Settings", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Input file
        ttk.Label(input_frame, text="Input PDF:").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(input_frame, textvariable=self.input_file, width=40).grid(row=0, column=1, padx=5)
        ttk.Button(input_frame, text="Browse...", command=self.browse_input).grid(row=0, column=2)

        # Output file
        ttk.Label(input_frame, text="Output File:").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(input_frame, textvariable=self.output_file, width=40).grid(row=1, column=1, padx=5)
        ttk.Button(input_frame, text="Browse...", command=self.browse_output).grid(row=1, column=2)

        # Frame for sheet settings
        sheet_frame = ttk.LabelFrame(self.root, text="Sheet Settings", padding=10)
        sheet_frame.pack(fill="x", padx=10, pady=5)

        # Sheet width
        ttk.Label(sheet_frame, text="Sheet Width (mm):").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(sheet_frame, textvariable=self.sheet_width, width=15).grid(row=0, column=1, padx=5)

        # Sheet height
        ttk.Label(sheet_frame, text="Sheet Height (mm):").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(sheet_frame, textvariable=self.sheet_height, width=15).grid(row=1, column=1, padx=5)

        # Spacing
        ttk.Label(sheet_frame, text="Spacing (mm):").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Entry(sheet_frame, textvariable=self.spacing, width=15).grid(row=2, column=1, padx=5)

        # Options frame
        options_frame = ttk.LabelFrame(self.root, text="Options", padding=10)
        options_frame.pack(fill="x", padx=10, pady=5)

        # Output format
        ttk.Label(options_frame, text="Output Format:").grid(row=0, column=0, sticky="w", pady=5)
        format_combo = ttk.Combobox(
            options_frame,
            textvariable=self.output_format,
            values=["pdf", "svg", "ai"],
            state="readonly",
            width=12
        )
        format_combo.grid(row=0, column=1, padx=5, sticky="w")

        # Rotation checkbox
        ttk.Checkbutton(
            options_frame,
            text="Allow Rotation",
            variable=self.rotation_enabled
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=5)

        # Run button
        run_button = ttk.Button(
            self.root,
            text="▶ Run Nesting",
            command=self.run_nesting,
            style="Accent.TButton"
        )
        run_button.pack(pady=10)

        # Progress bar
        self.progress = ttk.Progressbar(
            self.root,
            mode="indeterminate",
            length=400
        )
        self.progress.pack(pady=5)

        # Status text
        self.status_text = tk.Text(self.root, height=10, width=70, state="disabled")
        self.status_text.pack(padx=10, pady=5)

    def browse_input(self):
        """Browse for input PDF file"""
        filename = filedialog.askopenfilename(
            title="Select Input PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.input_file.set(filename)

            # Auto-generate output filename
            if not self.output_file.get():
                input_path = Path(filename)
                output_path = input_path.parent / f"{input_path.stem}_nested.pdf"
                self.output_file.set(str(output_path))

    def browse_output(self):
        """Browse for output file"""
        format_ext = self.output_format.get()
        filename = filedialog.asksaveasfilename(
            title="Save Output As",
            defaultextension=f".{format_ext}",
            filetypes=[
                (f"{format_ext.upper()} files", f"*.{format_ext}"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.output_file.set(filename)

    def log(self, message):
        """Log message to status text"""
        self.status_text.config(state="normal")
        self.status_text.insert("end", message + "\n")
        self.status_text.see("end")
        self.status_text.config(state="disabled")
        self.root.update()

    def clear_log(self):
        """Clear log"""
        self.status_text.config(state="normal")
        self.status_text.delete(1.0, "end")
        self.status_text.config(state="disabled")

    def run_nesting(self):
        """Run nesting in background thread"""

        # Validate inputs
        if not self.input_file.get():
            messagebox.showerror("Error", "Please select an input PDF file")
            return

        if not self.output_file.get():
            messagebox.showerror("Error", "Please specify an output file")
            return

        if not Path(self.input_file.get()).exists():
            messagebox.showerror("Error", "Input file does not exist")
            return

        # Clear log
        self.clear_log()

        # Start progress
        self.progress.start()

        # Run in thread
        thread = threading.Thread(target=self._run_nesting_thread)
        thread.daemon = True
        thread.start()

    def _run_nesting_thread(self):
        """Run nesting in background thread"""
        try:
            self.log("🚀 Starting PDF Nesting...")
            self.log(f"📄 Input: {self.input_file.get()}")
            self.log(f"📦 Output: {self.output_file.get()}")
            self.log("")

            # Create pipeline
            pipeline = PDFNestingPipeline(
                sheet_width=self.sheet_width.get(),
                sheet_height=self.sheet_height.get(),
                spacing=self.spacing.get(),
                rotation_enabled=self.rotation_enabled.get(),
                units='mm'
            )

            # Run
            result = pipeline.run(
                self.input_file.get(),
                self.output_file.get(),
                self.output_format.get()
            )

            # Stop progress
            self.progress.stop()

            if result['success']:
                self.log("")
                self.log("✅ SUCCESS!")
                self.log(f"📊 Statistics:")
                self.log(f"   - Input shapes: {result['stats']['input_shapes']}")
                self.log(f"   - Nested: {result['stats']['nested_count']}/{result['stats']['total_count']}")
                self.log(f"   - Utilization: {result['stats']['utilization']:.2f}%")
                self.log(f"   - Output: {result['output_file']}")

                # Show success dialog
                response = messagebox.askyesno(
                    "Success",
                    f"Nesting completed!\nUtilization: {result['stats']['utilization']:.1f}%\n\nOpen output file?"
                )

                if response:
                    import os
                    os.startfile(result['output_file'])

            else:
                self.log("")
                self.log("❌ Failed!")
                messagebox.showerror("Error", "Nesting failed. Check log for details.")

        except Exception as e:
            self.progress.stop()
            self.log(f"❌ Error: {str(e)}")
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")


def main():
    """Main entry point"""
    root = tk.Tk()
    app = PDFNestingGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
