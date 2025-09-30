import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
import threading
import os
from llama_cpp import Llama

# --- Configuration ---
# The application will look for the model in the same folder it's running from.
MODEL_NAME = "codellama-7b-instruct.Q4_K_M.gguf"
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), MODEL_NAME)

llm = None

# --- Main Application Logic ---

def initialize_model():
    """Loads the AI model into memory. Displays errors if it fails."""
    global llm
    try:
        # Check if the model file exists before trying to load it
        if not os.path.exists(MODEL_PATH):
            messagebox.showerror("Fatal Error", f"Model file not found!\n\nPlease make sure '{MODEL_NAME}' is in the same folder as the application.")
            window.destroy()
            return
            
        status_label.config(text=f"Loading model: {MODEL_NAME}...")
        window.update_idletasks() # Update UI to show the message
        
        # Load the model
        llm = Llama(
            model_path=MODEL_PATH,
            n_ctx=4096,      # Context window size
            n_gpu_layers=-1, # Offload all layers to GPU if available
            verbose=False    # Suppress verbose output
        )
        status_label.config(text="Model loaded successfully. Ready.", fg="green")
        generate_button.config(state=tk.NORMAL) # Enable the button after loading
        
    except Exception as e:
        messagebox.showerror("Model Loading Failed", f"An error occurred while loading the AI model: {e}")
        status_label.config(text="Model failed to load.", fg="red")
        window.destroy()

def start_code_generation():
    """Validates input and starts the generation in a new thread."""
    prompt_text = prompt_entry.get("1.0", tk.END).strip()
    if not prompt_text:
        messagebox.showwarning("Input Error", "The prompt box cannot be empty.")
        return
    
    # Disable UI elements during generation
    generate_button.config(state=tk.DISABLED)
    prompt_entry.config(state=tk.DISABLED)
    output_text.config(state=tk.NORMAL)
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, ">>> Generating C code... Please wait.\n\n")
    output_text.config(state=tk.DISABLED)
    
    # Run the model in a separate thread to keep the UI from freezing
    threading.Thread(target=generate_code_thread, args=(prompt_text,), daemon=True).start()

def generate_code_thread(prompt_text):
    """Handles the actual interaction with the model."""
    global llm
    try:
        # This is the "system prompt" - our strict instruction to the AI.
        # It forces the model to ONLY output C code.
        system_message = "You are a C code generation expert. Your sole purpose is to write a complete, correct, and clean C program based on the user's request. You MUST NOT provide any explanation, commentary, or text outside of the final C code block. Your entire response must be valid C code."
        
        # This combines the system instruction with the user's request.
        full_prompt = f"<s>[INST] {system_message}\n\nUser request: {prompt_text} [/INST]\n"
        
        # Call the model
        output = llm(
            prompt=full_prompt,
            max_tokens=2048,  # Max length of the generated code
            stop=["</s>"],    # Stop generation at the end token
            echo=False        # Don't repeat the prompt in the output
        )
        
        generated_code = output['choices'][0]['text'].strip()
        
        # Schedule the UI update on the main thread
        window.after(0, update_ui_with_result, generated_code)
        
    except Exception as e:
        error_message = f"An error occurred during code generation: {e}"
        window.after(0, update_ui_with_result, error_message)

def update_ui_with_result(result_text):
    """Updates the UI with the generated code or an error message."""
    output_text.config(state=tk.NORMAL)
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, result_text)
    
    # Re-enable UI elements
    generate_button.config(state=tk.NORMAL)
    prompt_entry.config(state=tk.NORMAL)

def save_code():
    """Opens a dialog to save the generated code to a .c file."""
    code = output_text.get("1.0", tk.END).strip()
    if not code or ">>> Generating" in code:
        messagebox.showwarning("Save Error", "There is no code to save.")
        return
        
    filepath = filedialog.asksaveasfilename(
        defaultextension=".c",
        filetypes=[("C Files", "*.c"), ("All Files", "*.*")]
    )
    if filepath:
        with open(filepath, 'w') as f:
            f.write(code)

# --- GUI Setup ---
window = tk.Tk()
window.title("Offline C Code Generator")
window.geometry("800x600")

main_frame = tk.Frame(window, padx=10, pady=10)
main_frame.pack(fill=tk.BOTH, expand=True)

# Top frame for prompt
prompt_frame = tk.LabelFrame(main_frame, text="1. Enter C Program Request", font=("Segoe UI", 10))
prompt_frame.pack(fill=tk.X, pady=(0, 10))
prompt_entry = scrolledtext.ScrolledText(prompt_frame, height=8, width=80, wrap=tk.WORD, font=("Consolas", 11))
prompt_entry.pack(fill=tk.X, expand=True, padx=5, pady=5)

# Middle frame for controls
control_frame = tk.Frame(main_frame)
control_frame.pack(fill=tk.X, pady=5)
generate_button = tk.Button(control_frame, text="Generate C Code", command=start_code_generation, font=("Segoe UI", 12, "bold"), state=tk.DISABLED)
generate_button.pack(side=tk.LEFT, padx=(0, 10))
save_button = tk.Button(control_frame, text="Save to .c file", command=save_code, font=("Segoe UI", 10))
save_button.pack(side=tk.RIGHT)

# Bottom frame for output
output_frame = tk.LabelFrame(main_frame, text="2. Generated C Code", font=("Segoe UI", 10))
output_frame.pack(fill=tk.BOTH, expand=True)
output_text = scrolledtext.ScrolledText(output_frame, height=20, width=80, wrap=tk.WORD, font=("Consolas", 11), state=tk.DISABLED)
output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

# Status bar
status_label = tk.Label(window, text="Initializing...", bd=1, relief=tk.SUNKEN, anchor=tk.W)
status_label.pack(side=tk.BOTTOM, fill=tk.X)

# Start model loading in a background thread so the UI is responsive
threading.Thread(target=initialize_model, daemon=True).start()

window.mainloop()
