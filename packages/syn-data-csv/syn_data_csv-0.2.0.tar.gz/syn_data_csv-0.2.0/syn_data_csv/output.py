def generate_output(df, delimiter=','):

    if not df.empty:
        df.to_csv("synthetic_data1.csv", index=False, sep=delimiter)
        print(f"✅ Synthetic data saved to synthetic_data1.csv with delimiter '{delimiter}'")
    else:
        print("❌ No valid data to save.")
