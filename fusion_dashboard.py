import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np
from fpdf import FPDF
import tempfile
import os

# Set Streamlit page configuration
st.set_page_config(page_title="Fusion Energy Dashboard", page_icon="☀️", layout="wide")

# Load CSV data
@st.cache_data
def load_data():
    df = pd.read_csv('fusion_project_data.csv')
    return df

# Load dataset
data = load_data()

# Country-specific report texts
reports = {
    "USA": "USA Fusion Project Overview: Achieved ignition multiple times with significant energy gain.",
    "France": "France Fusion Project Overview: Set world record for plasma duration.",
    "Germany": "Germany Fusion Project Overview: Developing next-gen stellarator concept.",
    "China": "China Fusion Project Overview: Record-breaking plasma temperature and duration."
}

# Prepare machine learning model
ml_data = data[['Plasma Duration (seconds)', 'Plasma Temperature (°C)', 'Energy Gain']].fillna(0)
X = ml_data.values
y = np.array([2038, 2042, 2040, 2035])  # Hypothetical commercialization years
model = LinearRegression()
model.fit(X, y)

def predict_year(row):
    features = np.array([[row['Plasma Duration (seconds)'] or 0,
                          row['Plasma Temperature (°C)'] or 0,
                          row['Energy Gain'] or 0]])
    year = model.predict(features)[0]
    return int(round(year))

# Create a styled PDF report with cover page and user name
class PDF(FPDF):
    def header(self):
        if self.page_no() != 1:
            self.set_font('Arial', 'B', 14)
            self.cell(0, 10, 'Fusion Energy Global Report', ln=True, align='C')
            self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

def create_pdf_with_graph(country, report_text, prediction_year, fig_path, username):
    pdf = PDF()
    # Cover page
    pdf.add_page()
    pdf.set_font("Arial", 'B', 24)
    pdf.cell(0, 80, "Fusion Energy Global Report", ln=True, align='C')
    pdf.set_font("Arial", size=16)
    pdf.cell(0, 10, f"Prepared for: {username}", ln=True, align='C')
    pdf.ln(20)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, "Country Focus: " + country, ln=True, align='C')

    # Content page
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"Fusion Energy Report - {country}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Project Overview", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 8, report_text)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Predicted Commercialization Year", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.cell(0, 10, f"{prediction_year}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Plasma Duration Graph", ln=True)
    pdf.image(fig_path, x=10, w=190)
    pdf.ln(5)
    return pdf

# Country selection dropdown
country = st.selectbox("Select a Country to Explore", data['Country'].unique())

# Filter data based on selection
data_filtered = data[data['Country'] == country].iloc[0]

# Intro section with energy news links
st.title("Fusion Energy Global Dashboard")

# Plasma duration visualization
st.subheader("Plasma Duration Comparison")
fig, ax = plt.subplots()
plot_data = data.dropna(subset=['Plasma Duration (seconds)'])
ax.bar(plot_data['Country'], plot_data['Plasma Duration (seconds)'])
ax.set_ylabel("Duration (seconds)")
ax.set_title("Plasma Sustained Time by Country")
st.pyplot(fig)

# Save graph temporarily
with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
    fig.savefig(tmpfile.name)
    temp_graph_path = tmpfile.name

# Machine learning commercialization prediction
st.subheader("Commercialization Prediction")
predicted_year = predict_year(data_filtered)
st.success(f"Predicted Commercialization Year: {predicted_year}")

# Investment strategy recommendation
st.subheader("Investment Strategy Recommendation")
plasma_temp = data_filtered['Plasma Temperature (°C)']
if pd.notnull(plasma_temp) and plasma_temp > 100_000_000:
    st.info("High Potential: Focus on high-temperature superconducting tokamak technologies.")
else:
    st.info("Medium Potential: Monitor plasma duration and stability progress.")

# Downloadable PDF report with graph and user name input
st.subheader("Download Your Report")
username = st.text_input("Enter your name for the report:", "Juhee")
if st.button("Generate PDF Report"):
    pdf = create_pdf_with_graph(country, reports[country], predicted_year, temp_graph_path, username)
    pdf_output = f"{country}_Fusion_Report.pdf"
    pdf.output(pdf_output)
    with open(pdf_output, "rb") as f:
        st.download_button("Click to download your report", f, file_name=pdf_output)

# Clean up temp graph file
if os.path.exists(temp_graph_path):
    os.remove(temp_graph_path)

# Custom report options (future features)
st.subheader("🌐 Custom Report Options (Coming Soon)")
st.checkbox("Include Plasma Duration Graph")
st.checkbox("Include Commercialization Prediction")
st.checkbox("Include Investment Strategy")
