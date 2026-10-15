# LabMateAI 🧪

**Your AI lab companion for biotechnology learning, calculations, and report drafting.**

LabMateAI is a student-built Streamlit prototype that combines a Groq-hosted language model with small utilities for biotechnology coursework.

## Features

- **Lab Assistant:** Ask questions about biotechnology, genetics, microbiology, biochemistry, and laboratory concepts.
- **PCR Calculator:** Calculate reagent volumes for a user-specified reaction count and excess percentage; export the mix as CSV.
- **Report Builder:** Draft a structured lab report from your own notes and download it as Markdown.
- **Safety-conscious prompting:** The report builder is instructed not to invent observations or references.

## Tech stack

- Python
- Streamlit
- Groq API
- Llama 3.3 70B Versatile

## Run locally

1. Install Python 3.10 or later.
2. Clone the repository and open the project folder.
3. Create and activate a virtual environment:

   **Windows (PowerShell)**
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   **macOS/Linux**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Set your Groq API key as an environment variable.

   **Windows (PowerShell; current terminal only)**
   ```powershell
   $env:GROQ_API_KEY="your_actual_key"
   ```

   **macOS/Linux**
   ```bash
   export GROQ_API_KEY="your_actual_key"
   ```

   Alternatively, for Streamlit, create `.streamlit/secrets.toml` locally with:

   ```toml
   GROQ_API_KEY = "your_actual_key"
   ```

   Do not commit the secrets file or share your key.

6. Start the app:

   ```bash
   streamlit run app.py
   ```

## Deploy with Streamlit Community Cloud

1. Create a new app from this GitHub repository.
2. Select `app.py` as the main file.
3. In the app's **Settings → Secrets**, add:

   ```toml
   GROQ_API_KEY = "your_actual_key"
   ```

4. Deploy or reboot the app.

## Project structure

```text
LabMateAI/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Important limitations

- This repository contains a reconstructed starter implementation based on the project's described features; it may not match every detail of the earlier local version.
- AI answers can be incorrect. Verify scientific statements and follow approved institutional protocols.
- The PCR calculator does arithmetic only; it does not recommend or validate a protocol.
- The report builder must use real observations supplied by the user. Review, edit, and verify all generated text before academic use.
- Do not enter patient information, confidential research data, or other sensitive information into the app.

## Future improvements

- Add automated tests for volume calculations.
- Add input validation and a downloadable PDF report.
- Add structured conversation export and clearer model error handling.
- Add validated, user-configurable reagent templates.
