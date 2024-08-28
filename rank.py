import pandas as pd
import os

# Define the TDP penalty, L3 cache bonus, single core score weight, and multi core score weight
tdp_penalty_factor = 1.24
l3_cache_bonus_factor = 0.68
weight_single = 0.66
weight_multi = 0.34

# Get the list of all CSV files in the current directory
csv_files = [os.path.join('CPUs', file) for file in os.listdir('CPUs') if file.endswith('.csv')]

# Create a list to store all results
all_results_list = []

# Process each CSV file
for file in csv_files:
    try:
        print(f"Processing file: {file}")

        # Read the CSV file into a DataFrame
        df = pd.read_csv(file)
        print(f"Data read from file: {file}")

        # Ensure that the CSV file has the required columns
        if 'single' not in df.columns or 'multi' not in df.columns:
            print(f"File {file} does not contain 'single' or 'multi' columns.")
            continue

        # Extract the values for L2 cache, L3 cache, cores, threads, TDP, and release year
        l2_cache = df['single'].iloc[-3]  # L2 cache is the third last value in 'single' column
        l3_cache = df['multi'].iloc[-3]  # L3 cache is the third last value in 'multi' column
        cores = df['single'].iloc[-2]  # Cores is the second last value in 'single' column
        threads = df['multi'].iloc[-2]  # Threads is the second last value in 'multi' column
        tdp = df['single'].iloc[-1]  # TDP is the last value in 'single' column
        release_year = df['multi'].iloc[-1]  # Release year is the last value in 'multi' column

        # Remove the last six lines which contain L2 cache, L3 cache, cores, threads, TDP, and release year
        df = df.iloc[:-6]

        # Sort the scores and exclude the best and worst
        df_sorted_single = df['single'].sort_values().iloc[1:-1]
        df_sorted_multi = df['multi'].sort_values().iloc[1:-1]

        # Calculate the average scores excluding the best and worst
        avg_single = df_sorted_single.mean()
        avg_multi = df_sorted_multi.mean()
        print(f"Averages calculated for file: {file}")

        # Calculate the penalty based on TDP
        tdp_penalty = tdp * tdp_penalty_factor

        # Calculate the bonus based on L3 cache
        l3_cache_bonus = l3_cache * l3_cache_bonus_factor

        # Extract the processor name from the file name
        processor_name = os.path.basename(file).replace('.csv', '')

        # Append the results to the list, but exclude the TDP penalty and L3 cache bonus from being saved in the CSV
        all_results_list.append({
            'Processor': processor_name,
            'Cores': cores,
            'Threads': threads,
            'L2_Cache': l2_cache,
            'L3_Cache': l3_cache,
            'TDP': tdp,  # Include TDP in the CSV
            'Release_Year': release_year,
            'Single': avg_single,
            'Multi': avg_multi,
        })
        print(f"Results appended for file: {file}")

    except Exception as e:
        print(f"Error processing file {file}: {e}")
        continue

# Convert the list to a DataFrame
all_results = pd.DataFrame(all_results_list)
print(f"All results combined into DataFrame")

# Ensure there are results to rank
if all_results.empty:
    print("No valid results to rank.")
else:
    print("Ranking processors based on combined performance")

    # Calculate the combined score including the TDP penalty and L3 cache bonus
    all_results['Combined_Score'] = (
            (weight_single * all_results['Single']) +
            (weight_multi * all_results['Multi']) -
            (all_results['TDP'] * tdp_penalty_factor) +  # Apply the TDP penalty in score calculation
            (all_results['L3_Cache'] * l3_cache_bonus_factor)  # Apply the L3 cache bonus in score calculation
    )

    # Rank the processors based on the combined score
    final_rankings = all_results.sort_values(by='Combined_Score', ascending=False).reset_index(drop=True)
    final_rankings['Rank'] = final_rankings.index + 1

    # Create the 'Out' directory if it doesn't exist
    output_dir = 'Out'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    # Save the rankings to a CSV file in the 'Out' directory
    output_file = os.path.join(output_dir, 'processor_rankings.csv')
    final_rankings.to_csv(output_file, index=False)
    print(f"Rankings saved to '{output_file}'")

input("Press Enter to exit.")
