Offline C Code Generator
An application to generate C code using a local, offline Code Llama LLM.

The application generates clean, complete, and runnable C programs based on your requests. All code generation happens fully offline on your machine.

Setup Guide
1. Install Python Dependencies
You need Python 3.8+. Install the core library:

pip install llama-cpp-python[server]

2. Model Requirement
Download a Code Llama 7B Instruct GGUF file.

Rename it to: codellama-7b-instruct.Q4_K_M.gguf

Place it in the same directory as your Python script.

3. Run the App
python CGEN.py

How to Use
Wait for the Status Bar (bottom) to turn green ("Model loaded successfully. Ready.").

Enter your C code request in the top box.

Click Generate C Code.

Use the Save to .c file button to save the output.
