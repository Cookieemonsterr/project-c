import streamlit as st
import pandas as pd

def compare_menus(careem_file, talabat_file):
    # Load CSV files
    careem_menu = pd.read_csv(careem_file)
    talabat_menu = pd.read_csv(talabat_file)

    # Normalize column names
    careem_menu.columns = careem_menu.columns.str.lower()
    talabat_menu.columns = talabat_menu.columns.str.lower()

    careem_menu.rename(columns={'item': 'item_name', 'price': 'item_price'}, inplace=True)
    talabat_menu.rename(columns={'item': 'item_name', 'price': 'item_price'}, inplace=True)

    # Exclusive to Talabat
    talabat_items = set(talabat_menu['item_name'].str.lower())
    careem_items = set(careem_menu['item_name'].str.lower())
    exclusive_to_talabat = talabat_items - careem_items

    # Lower Priced on Talabat
    talabat_prices = talabat_menu.groupby('item_name')['item_price'].mean()
    careem_prices = careem_menu.groupby('item_name')['item_price'].mean()
    common_items = talabat_prices.index.intersection(careem_prices.index)
    lower_priced_items = [
        item for item in common_items if talabat_prices[item] < careem_prices[item]
    ]

    # Missing Descriptions
    missing_descriptions = []
    if 'description' in talabat_menu.columns and 'description' in careem_menu.columns:
        for item in common_items:
            talabat_description = talabat_menu[talabat_menu['item_name'].str.lower() == item].get('description').iloc[0]
            careem_description = careem_menu[careem_menu['item_name'].str.lower() == item].get('description').iloc[0]
            if pd.isna(careem_description) and not pd.isna(talabat_description):
                missing_descriptions.append({'Item': item, 'Talabat Description': talabat_description})

    # Output Results
    return {
        "Exclusive to Talabat": list(exclusive_to_talabat),
        "Lower Priced Items": lower_priced_items,
        "Missing Descriptions": missing_descriptions,
    }

# Streamlit Web App
st.title("Menu Comparison Tool 🍴")
st.write("Upload the Careem and Talabat menus as CSV files to compare them.")

# File Uploads
careem_file = st.file_uploader("Upload Careem Menu CSV", type=["csv"])
talabat_file = st.file_uploader("Upload Talabat Menu CSV", type=["csv"])

if careem_file and talabat_file:
    st.success("Files uploaded successfully! Click 'Compare Menus' to proceed.")
    
    if st.button("Compare Menus"):
        # Perform the comparison
        results = compare_menus(careem_file, talabat_file)
        
        # Display results
        st.header("Results:")
        st.subheader("Exclusive to Talabat")
        st.write(results["Exclusive to Talabat"])
        
        st.subheader("Lower Priced Items")
        st.write(results["Lower Priced Items"])
        
        st.subheader("Missing Descriptions")
        st.write(pd.DataFrame(results["Missing Descriptions"]))
        
        # Option to download results
        st.download_button(
            label="Download Results as CSV",
            data=pd.DataFrame(results["Missing Descriptions"]).to_csv(index=False),
            file_name="menu_comparison_results.csv",
            mime="text/csv"
        )
