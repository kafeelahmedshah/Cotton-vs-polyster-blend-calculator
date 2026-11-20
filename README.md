# Advanced Cotton vs. Polyester Blend Calculator

**Student ID:** 25TE006  
**Department:** Textile Engineering

A GitHub-ready Streamlit application for exploring cotton/polyester blend ratios, estimating fabric material and production costs, comparing blend scenarios, and exporting calculation reports.

## Advanced features

- Cotton slider from 0–100%; polyester automatically adjusts to keep the blend at 100%.
- Interactive composition chart and live dashboard.
- User-defined cotton and polyester prices per kg.
- Fabric GSM and usable width inputs.
- Fiber waste allowance, processing cost, and overhead assumptions.
- Detailed cost breakdown for cotton, polyester, processing, and overhead.
- Illustrative comfort and durability indicators with clear limitations.
- Standard and custom blend comparison table.
- Cost comparison chart and CSV export.
- Target-cost blend explorer based on the current linear costing model.
- Downloadable PDF report.
- Educational cotton/polyester fiber guide.
- Responsive Streamlit layout.

## Project files

```text
cotton_polyester_blend_calculator_advanced/
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Cost model

All calculations are estimates per meter of fabric.

Let:

- `C` = cotton percentage
- `P` = polyester percentage (`100 - C`)
- `Pc` = cotton price per kg
- `Pp` = polyester price per kg
- `GSM` = fabric mass in grams per square meter
- `W` = usable fabric width in meters
- `w` = fiber waste fraction (for example, 5% = 0.05)
- `Proc` = processing cost per meter
- `O` = overhead percentage

### 1. Net fabric mass per meter

`Net mass (kg/m) = GSM × W ÷ 1000`

### 2. Gross fiber input with waste

`Gross fiber input (kg/m) = Net mass ÷ (1 − w)`

This treats the waste allowance as the fraction of gross input that does not become finished fabric.

### 3. Fiber costs

`Cotton cost = Gross fiber input × C/100 × Pc`

`Polyester cost = Gross fiber input × P/100 × Pp`

`Raw fiber cost = Cotton cost + Polyester cost`

### 4. Processing and overhead

`Overhead = (Raw fiber cost + Proc) × O/100`

`Estimated total cost/m = Raw fiber cost + Proc + Overhead`

The processing and overhead fields are user-entered assumptions. The application does not infer factory-specific production costs.

## Ratings: important limitation

Comfort and durability scores are simplified, illustrative blend-based teaching indicators. They are **not laboratory test results**, validated predictive models, or certified product-performance claims. Real fabric behavior depends on fiber grade, yarn count and twist, spinning system, fabric structure, density, finishing, and test conditions. Use standardized laboratory tests for technical or commercial decisions.

## Run locally

Python 3.9 or newer is recommended.

### 1. Clone the repository

Replace the placeholder with your own GitHub repository URL:

```bash
git clone https://github.com/YOUR-USERNAME/cotton-polyester-blend-calculator.git
cd cotton-polyester-blend-calculator
```

Or download the ZIP from GitHub and extract it.

### 2. (Optional) Create a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
streamlit run app.py
```

Open the local URL shown in the terminal, usually `http://localhost:8501`.

## Publish to GitHub

1. Sign in to GitHub and create a new repository.
2. Use a repository name such as `cotton-polyester-blend-calculator`.
3. Keep the repository public if you want easy sharing (or private if preferred).
4. Upload `app.py`, `requirements.txt`, `README.md`, and `.gitignore` to the repository root.
5. Commit the files.

### Git command-line option

From inside the project directory:

```bash
git init
git add .
git commit -m "Build advanced cotton polyester blend calculator"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/cotton-polyester-blend-calculator.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your GitHub username and use the repository URL GitHub gives you.

## Deploy with Streamlit Community Cloud

1. Push the project to GitHub.
2. Open Streamlit Community Cloud and sign in.
3. Choose **Create app**.
4. Select your repository and `main` branch.
5. Set the main file path to `app.py`.
6. Select **Deploy**.
7. Wait for the app to build; Streamlit installs packages from `requirements.txt`.

## Suggested demonstration workflow

1. Enter cotton and polyester market prices in the sidebar.
2. Set GSM, usable width, waste allowance, processing cost and overhead.
3. Move the cotton slider and observe the polyester percentage adjust automatically.
4. Review the composition, cost breakdown and performance indicators.
5. Compare standard and custom blend ratios.
6. Enter a target cost to see the blend percentage estimated by the current cost model.
7. Export the comparison CSV and current calculation PDF.

## Disclaimer

This is an educational costing and comparison tool. Results depend on input accuracy and simplified assumptions. It is not a replacement for supplier quotations, production costing systems, engineering validation, or standardized textile laboratory testing.
