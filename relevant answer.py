import pandas as pd

def find_most_popular_results(input_csv_path, output_csv_path):
    
    data = pd.read_csv(input_csv_path, delimiter='\t')
    
    
    grouped_data = data.groupby(['INPUT:id', 'OUTPUT:result']).size().reset_index(name='counts')
    
    # Find the most popular result for each task_id
    most_popular_results = grouped_data.loc[grouped_data.groupby(['INPUT:id'])['counts'].idxmax()]
    
    
    most_popular_results.to_csv(output_csv_path, index=False)


input_csv_path = 'assigments.csv'  # Update this to your actual input file path
output_csv_path = 'result1.csv'  # Update this to your desired output file path


find_most_popular_results(input_csv_path, output_csv_path)