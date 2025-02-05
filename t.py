import pandas as pd
import json

def excel_to_json(file_path):
    """
    Reads an Excel file and converts it into a list of JSON objects.

    Parameters:
        file_path (str): Path to the Excel file.

    Returns:
        list: A list of JSON objects.
    """
    try:
        # Read the Excel file
        df = pd.read_csv(file_path)

        df["CityId"] = df["CityId"].str.lower()

        # Filter data for Leeds and London
        leeds_data = df[df["CityId"] == "leeds"].to_dict(orient="records")
        london_data = df[df["CityId"] == "london"].to_dict(orient="records")

        # Save to JSON files
        with open("leeds.json", "w", encoding="utf-8") as leeds_file:
            json.dump(leeds_data, leeds_file, indent=4)

        with open("london.json", "w", encoding="utf-8") as london_file:
            json.dump(london_data, london_file, indent=4)

        print("JSON files created successfully: leeds.json & london.json")
        # return json_list
    except Exception as e:
        print(f"Error: {e}")
        return []

# Example usage
if __name__ == "__main__":
    file_path = "Place 05.02.25 01.07.csv"  # Replace with your Excel file path
    json_data = excel_to_json(file_path)

    # Print JSON output
    print(json.dumps(json_data, indent=4))
