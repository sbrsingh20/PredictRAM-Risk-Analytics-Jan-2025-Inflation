import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# File paths for uploaded data
inflation_price_index_file = "India Inflation CPI Price Index.xlsx"
inflation_income_statement_file = "India Inflation CPI IncomeStatement.xlsx"

# Load data from Excel files
inflation_price_df = pd.read_excel(inflation_price_index_file)
inflation_income_df = pd.read_excel(inflation_income_statement_file)

# Debugging: Print columns of each dataframe
st.write("Columns in inflation_price_df:", inflation_price_df.columns.tolist())
st.write("Columns in inflation_income_df:", inflation_income_df.columns.tolist())

# Risk categorization based on correlation values
def categorize_risk(value, thresholds):
    if value < thresholds[0]:
        return "High Risk"
    elif thresholds[0] <= value <= thresholds[1]:
        return "Moderate Risk"
    else:
        return "Low Risk"

# Get color for risk levels
def get_risk_color(risk_level):
    colors = {"High Risk": "red", "Moderate Risk": "orange", "Low Risk": "green"}
    return colors.get(risk_level, "gray")

# Function to calculate inflation correlation for stocks
def calculate_inflation_correlation(stock_symbols):
    inflation_results = []

    for stock_symbol in stock_symbols:
        # Extract stock-specific data
        stock_price_data = inflation_price_df[inflation_price_df['Symbol'] == stock_symbol]
        stock_income_data = inflation_income_df[inflation_income_df['Symbol'] == stock_symbol]

        # Add correlations from price index data
        if not stock_price_data.empty:
            for _, row in stock_price_data.iterrows():
                inflation_results.append({
                    'Symbol': stock_symbol,
                    'Category': 'Inflation Correlation',
                    'Parameter': row.get('Parameter', 'N/A'),
                    'Value': row.get('Correlation', 0),
                    'Risk Level': categorize_risk(row.get('Correlation', 0), (-0.5, 0.5)),
                    'Color': get_risk_color(categorize_risk(row.get('Correlation', 0), (-0.5, 0.5)))
                })

        # Add correlations from income statement data
        if not stock_income_data.empty:
            for _, row in stock_income_data.iterrows():
                inflation_results.append({
                    'Symbol': stock_symbol,
                    'Category': 'Inflation Correlation (Income)',
                    'Parameter': row.get('Parameter', 'N/A'),
                    'Value': row.get('Correlation', 0),
                    'Risk Level': categorize_risk(row.get('Correlation', 0), (-0.5, 0.5)),
                    'Color': get_risk_color(categorize_risk(row.get('Correlation', 0), (-0.5, 0.5)))
                })

    return inflation_results

# Function to plot risk pie charts
def plot_risk_pie_chart(results, category):
    data = [r for r in results if r['Category'] == category]
    risk_counts = pd.DataFrame(data)['Risk Level'].value_counts()
    fig, ax = plt.subplots()
    ax.pie(
        risk_counts,
        labels=risk_counts.index,
        autopct='%1.1f%%',
        colors=[get_risk_color(level) for level in risk_counts.index],
        startangle=90
    )
    ax.set_title(f"Risk Distribution: {category}")
    st.pyplot(fig)

# Function to plot trends of inflation parameters
def plot_inflation_trends(df, stock_symbol):
    stock_data = df[df['Symbol'] == stock_symbol]
    if stock_data.empty:
        st.write(f"No data available for {stock_symbol}")
        return

    fig, ax = plt.subplots()
    for parameter in stock_data['Parameter'].unique():
        subset = stock_data[stock_data['Parameter'] == parameter]
        ax.plot(subset['Date'], subset['Value'], label=parameter)

    ax.set_title(f"Inflation Trends for {stock_symbol}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Value")
    ax.legend()
    st.pyplot(fig)

# Streamlit interface
st.title("Comprehensive Risk Analysis with Inflation Data")

# User input: Select stocks to analyze
stock_symbols = inflation_price_df['Symbol'].unique()
selected_stocks = st.multiselect("Select Stocks for Analysis", stock_symbols)

if selected_stocks:
    # Calculate correlations
    inflation_results = calculate_inflation_correlation(selected_stocks)

    # Display risk pie charts
    st.subheader("Inflation Correlation Analysis")
    for category in ["Inflation Correlation", "Inflation Correlation (Income)"]:
        plot_risk_pie_chart(inflation_results, category)

    # Display trends for selected stocks
    st.subheader("Inflation Parameter Trends")
    for stock_symbol in selected_stocks:
        st.write(f"Inflation trends for {stock_symbol}:")
        plot_inflation_trends(inflation_price_df, stock_symbol)

    # Display summary table
    st.subheader("Inflation Impact Summary")
    for stock_symbol in selected_stocks:
        st.write(f"Inflation correlation for {stock_symbol}:")
        inflation_summary = [r for r in inflation_results if r['Symbol'] == stock_symbol]
        st.write(pd.DataFrame(inflation_summary))

else:
    st.write("Please select at least one stock to analyze.")
