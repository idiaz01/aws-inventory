# AWS Inventory
This is a simple python script that uses the AWS SDK to list all the resources in an AWS account. The script is written in Python 3 and uses the boto3 library to interact with AWS.
It can be used to list all the resources in an AWS account and export the list of resources to an Excel file.
## Features
- List all the resources in an AWS account
- Export the list of resources to an Excel file

## Requirements
- Python 3 installed

## Installation
1. Clone the repository
2. Install the required libraries using pip
```bash
pip install -r requirements.txt
```
3. Configure your AWS credentials in the file 'aws_credentials.yml':
```yaml
AWS_ACCESS_KEY_ID: YOUR_ACCESS_KEY
AWS_SECRET_ACCESS_KEY: YOUR_SECRET_ACCESS_KEY
```

## Usage
In order to run the script, you need to provide the name of the output Excel file as an argument. For example:
```bash
python aws_inventory.py output.xlsx
```
