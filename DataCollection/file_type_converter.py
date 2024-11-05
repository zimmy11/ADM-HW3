import csv

def tsv_to_csv(tsv_file, csv_file):
    """
    Converts a TSV file to a CSV file.
    
    Parameters:
        tsv_file (str): The input TSV file path.
        csv_file (str): The output CSV file path.
    """
    with open(tsv_file, 'r', encoding='utf-8') as tsv, open(csv_file, 'w', encoding='utf-8', newline='') as csv_f:
        tsv_reader = csv.reader(tsv, delimiter='\t')
        csv_writer = csv.writer(csv_f, delimiter=',')
        
        for row in tsv_reader:
            csv_writer.writerow(row)
    print(f"Conversion complete: {csv_file}")

#tsv_to_csv('michelin_restaurants_data.tsv', 'michelin_restaurants_data.csv')
