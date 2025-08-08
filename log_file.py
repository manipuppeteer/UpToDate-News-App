import os
import pandas as pd
from collections import Counter
def get_log_files(directory):
    """Return list of all .log files in the directory."""
    return [f for f in os.listdir(directory) if f.endswith(".log")]


def parse_log(file_path, info):
    """Parse a single log file and return structured data."""
    with open(file_path, 'r') as f:
        for lines in f:
            info['Date'].append(lines.split()[0])
            info['Time'].append(lines.split()[1])
            info['Message'].append(' '.join(lines.split()[2:]))
    return info


def summarize_logs(parsed_data):
    """Summarize logs into counts of INFO, WARNING, ERROR, unique users, top errors."""
    summary = {}
    summary['Total log count'] = len(parsed_data['Date'])

    messages = parsed_data['Message']
    message_types = ['INFO', 'WARNING', 'ERROR']
    for type in message_types:
        summary[f'Total {type} count'] = sum([1 if type in message else 0 
                                        for message in messages])
    
    unique_ids = set()
    for message in messages:
        if 'user' in message.lower():
            parts = message.lower().split('user')
            unique_ids.add(parts[1].strip().split()[0])

    summary['Count of Unique Users: '] = len(unique_ids)

    error_count = Counter([message for message in parsed_data['Message'] 
                                    if 'ERROR' in message])
    summary['Most frequent error messages:'] = ', '.join([msg for msg, _ in error_count.most_common(2)])

 
    return summary
def save_report(summary):
    """Save the summary report to CSV."""
    data = pd.DataFrame(summary, index = [0])
    data.to_csv('log_summary.csv')

def main():
    """runs all the function"""
    log_dir = 'logs'
    files = get_log_files(log_dir)
    
    info = {'Date':[], 'Time': [], 'Message': []}
    for file in files:
        file_path = os.path.join(log_dir, file)
        info = parse_log(file_path, info)
    
    
    summary = summarize_logs(info)
   # print(summary)

    save_report(summary)
    print('Report generated: log_summary.csv')
    data = pd.read_csv('log_summary.csv')
    print(data)
    

if __name__ == '__main__':
    """this is main"""
    main()
