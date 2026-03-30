Designing with BUILD123D Scripts

This workflow outlines how to reconstruct a parametric CAD model using build123d from an existing STL reference.

🚀 Workflow
Generate G-code
Slice the reference STL file to obtain G-code.
Import into AI Tool
Load the generated G-code into Antigravity (or similar AI tooling).
Setup Environment
Prompt the AI tool to install all required dependencies:
build123d
Python libraries and supporting scripts
Capture Dimensions
Manually measure as many dimensions as possible from the original CAD/STL.

Generate Parametric Script
Provide the following to the AI tool:
1. G-code file
2. Measured dimensions

Then prompt it to generate a parametric build123d script capable of recreating the model and exporting an STL.

Enforce Parametric Design
Explicitly instruct the AI:
Do not include any G-code references in the script
Use only extracted and measured dimensions
Ensure the script is fully parametric
Iterate & Refine
Manually tweak and rerun the script until the output matches the desired geometry.
✅ Validation
Compare the generated model against the original reference STL
Use CAD tools to visually and dimensionally verify accuracy
🛠️ Tooling
Slicer (G-code generation): ideaMaker
AI Tool: Antigravity
Validation CAD Software: Fusion 360
