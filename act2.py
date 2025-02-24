import streamlit as st
import pandas as pd
import random

st.set_page_config(layout="wide")

def recalculate_all_probabilities(entries):
    cumulative_probability = 0
    for i, entry in enumerate(entries):
        probability = entry["Days"] / st.session_state.total_days
        cumulative_probability += probability
        entry["Probability"] = probability
        entry["Cumulative Probability"] = cumulative_probability
        start_range = sum(entries[j]['Days'] for j in range(i))
        end_range = start_range + entry['Days'] - 1
        day_range = f"{start_range} to {end_range}" if start_range != end_range else f"{start_range}"
        entry["RNI"] = day_range

@st.dialog("Edit entries")
def edit_dialog(df_entries):
    st.session_state.edited_entries = [entry.copy() for entry in st.session_state.entries]

    for i in range(len(st.session_state.edited_entries)):
        col1_edit, col2_edit = st.columns(2)
        with col1_edit:
            st.number_input(f"Customers (Row {i+1}):", min_value=0, step=1, key=f"customers_{i}", value=st.session_state.edited_entries[i]['Customers'] if st.session_state.edited_entries else 0)
        with col2_edit:
            st.number_input(f"Days (Row {i+1}):", min_value=1, step=1, key=f"days_{i}", value=st.session_state.edited_entries[i]['Days'] if st.session_state.edited_entries else 1)

    if st.button("Save Changes"):
        temp_total_days = 0
        for i in range(len(df_entries)):
            st.session_state.edited_entries[i]['Customers'] = st.session_state[f"customers_{i}"]
            st.session_state.edited_entries[i]['Days'] = st.session_state[f"days_{i}"]
            temp_total_days += st.session_state.edited_entries[i]['Days']
        if temp_total_days > 100:
            st.error("Total number of days cannot exceed 100. Changes rejected.")
        else:
            st.session_state.entries = [entry.copy() for entry in st.session_state.edited_entries]
            recalculate_all_probabilities(st.session_state.entries)
            st.session_state.total_days = sum(entry['Days'] for entry in st.session_state.entries)
            st.session_state.pop('edited_entries')
            st.rerun()

    if st.button("Cancel"):
        st.session_state.pop('edited_entries')
        st.rerun()

def main():
    col1, col2 = st.columns(2)
    if 'total_days' not in st.session_state:
        st.session_state.total_days = 0
    if 'entries' not in st.session_state:
        st.session_state.entries = []
    if 'last_range' not in st.session_state:
        st.session_state.last_range = -1
    if 'random_results' not in st.session_state:
        st.session_state.random_results = []
    if 'error_message' not in st.session_state:
        st.session_state.error_message = ""

    with col1:
        st.subheader("Input")
        num_customers = st.number_input("Number of customers:", min_value=0, step=1, value=0)
        num_days = 1
        num_days = st.number_input("Number of days:", min_value=1, step=1, value=1)

        col1_btn1, col1_btn2, col1_btn3 = st.columns(3)

        with col1_btn1:
            if st.button("Submit Entry"):
                if st.session_state.total_days + num_days > 100:
                    st.session_state.error_message = "Total number of days cannot exceed 100. Entry rejected."
                else:
                    st.session_state.error_message = ""
                    start_range = st.session_state.total_days
                    end_range = start_range + num_days - 1
                    day_range = f"{start_range} to {end_range}" if start_range != end_range else f"{start_range}"

                    if st.session_state.total_days == 0:
                        probability = 1.0 
                    else:
                        probability = num_days / st.session_state.total_days
                    
                    if st.session_state.entries:
                        cumulative_probability = st.session_state.entries[-1]['Cumulative Probability'] + probability
                    else:
                        cumulative_probability = probability

                    st.session_state.entries.append({
                        "Customers": num_customers,
                        "Days": num_days,
                        "Probability": probability,
                        "Cumulative Probability": cumulative_probability,
                        "RNI": day_range,
                    })
                    
                    st.session_state.total_days += num_days
                    st.session_state.last_range = end_range

        with col1_btn2:
            if st.session_state.entries:
                if st.button("Edit Entries"):
                    edit_dialog(st.session_state.entries)

        with col1_btn3:
            if st.session_state.entries:
                if st.button("Clear Entries"):
                    st.session_state.entries = []
                    st.session_state.total_days = 0
                    st.session_state.last_range = -1
                    st.session_state.random_results = []
                    st.rerun()

        if st.session_state.error_message:
            st.error(st.session_state.error_message)
            st.session_state.error_message = ""
        if st.session_state.total_days == 100:
            st.success("Total number of days has reached 100.")
        else:
            st.info(f"Total days inputted: {st.session_state.total_days}. Days available: {100 - st.session_state.total_days}.")

    with col2:
        st.subheader("Entries")
        recalculate_all_probabilities(st.session_state.entries)
        if st.session_state.entries:
            df_entries = pd.DataFrame(st.session_state.entries)
            df_entries.index = range(1, len(st.session_state.entries) + 1)
            df_entries = df_entries.rename_axis("")
            pd.set_option('display.float_format', lambda x: '%.2f' % x)
            st.dataframe(df_entries, use_container_width=True)
        else:
            st.warning("There are no current entries.")

    st.divider()
    st.subheader("Simulation")
    # Input for number of days to simulate
    num_sim_days = st.number_input("Number of days to simulate:", min_value=1, step=1, value=1)
    
    # Simulate Random Days
    if st.button("Simulate"):
        if not st.session_state.entries:
            st.warning("No entries to simulate. Please add entries first.")
        else: 
            st.session_state.random_results = []
            for _ in range(num_sim_days):
                random_day = random.randint(0, st.session_state.total_days -1) if st.session_state.total_days > 0 else None # Corrected random day generation
                assigned_customers = None

                if st.session_state.total_days > 0:
                    for entry in st.session_state.entries:
                        range_parts = entry["RNI"].split(" to ")
                        start = int(range_parts[0])
                        end = int(range_parts[1]) if len(range_parts) > 1 else start

                        if start <= random_day <= end:
                            assigned_customers = entry["Customers"]
                            break

                st.session_state.random_results.append({"Random Number": random_day, "Number of Customers": assigned_customers})

    # Display random results
    if st.session_state.random_results:
        df_random_results = pd.DataFrame(st.session_state.random_results)
        df_random_results.index = range(1, len(df_random_results) + 1)
        df_random_results = df_random_results.rename_axis("Day")

        st.dataframe(df_random_results, use_container_width=True)

        # Calculate and display totals and averages
        total_customers = df_random_results["Number of Customers"].sum()
        num_rows = len(df_random_results)
        average_customers = total_customers / num_rows if num_rows > 0 else 0
        col1_sim, col2_sim = st.columns(2)

        with col1_sim:
            st.write(f"**Total Customers:** {total_customers}")

        with col2_sim:
            st.write(f"**Average Customers:** {average_customers:.4f}")

if __name__ == "__main__":
    main()
