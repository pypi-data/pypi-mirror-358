import tkinter as tk
from tkinter import scrolledtext
from clyp.transpiler import parse_clyp
import sys
import io

def main():
    root = tk.Tk()
    root.title("Clyp Runner")
    root.geometry("800x600")

    editor = scrolledtext.ScrolledText(root, height=15)
    editor.pack(fill='both', expand=True, padx=5, pady=5)
    editor.insert('1.0', '# Enter your clyp code here')

    output = scrolledtext.ScrolledText(root, height=10)
    output.pack(fill='both', expand=True, padx=5, pady=5)
    output.config(state='disabled')

    def run_code():
        output.config(state='normal')
        output.delete('1.0', 'end')
        code = editor.get('1.0', 'end-1c')
        
        old_stdout = sys.stdout
        redirected_output = io.StringIO()
        sys.stdout = redirected_output

        try:
            python_code = parse_clyp(code, "clyp_ui")
            exec(python_code, {'__name__': '__main__'})
        except Exception as e:
            output.insert('end', f"Error: {e}\n")
        
        sys.stdout = old_stdout
        output.insert('end', redirected_output.getvalue())
        output.config(state='disabled')

    run_button = tk.Button(root, text="Run", command=run_code)
    run_button.pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()