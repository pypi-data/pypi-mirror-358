DFUai is a Python package that utilizes AI to assist clinicians in diagnosing the severity of diabetic foot (DF).
By simply inputting a file with the grouped information of eight clinical features (PAD, CRP, HbA1c, DKD, ESR, ALB, SBP, and X25OHD),
DFUai predicts whether the diabetic foot condition is mild/moderate or severe.

Feature Grouping Criteria:
- PAD (Peripheral Artery Disease): Grouped according to clinical guidelines.
- DKD (Diabetic Kidney Disease): Grouped based on clinical guidelines.
- CRP (C-Reactive Protein): Grouped as 1 if greater than 16.34 mg/L, otherwise 0.
- ESR (Erythrocyte Sedimentation Rate): Grouped as 1 if greater than 44.5 mm/h, otherwise 0.
- ALB (Albumin): Grouped as 1 if greater than 41.55 g/L, otherwise 0.
- SBP (Systolic Blood Pressure): Grouped as 1 if greater than 136.5 mmHg, otherwise 0.
- X25OHD (25-Hydroxyvitamin D): Grouped as 1 if greater than 12.945 ng/mL, otherwise 0.
- HbA1c (Glycated Hemoglobin): Grouped as 1 if greater than 8.05%, otherwise 0.

The input format has rows as sample names, columns as variable feature names, and the cells filled with the grouped information of the variable features.

