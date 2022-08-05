## Cost Forecasting in a Multi-Account Organization

This solution enables users to get cost forecast data from a multi-account organization, and visualize it in a single pane of glass, in AWS QuickSight, MS Excel, or any compatible 3rd party BI tool. 

Using the Cost Explorer console to get cost forecasting data across all accounts, and their corresponding regions, in a multi-account organization, is a cumbersome and error prone process. For a multi-account organization, users do not have the ability to get cost forecasts data from Cost Explorer, in a single query, and “group by” any attribute, such as, accounts, regions, forecast month, etc. 

Once deployed, this solution automatically collects all cost forecasting data at a predefined schedule (daily/weekly) from cost explorer, transforms the output to be easily queried or “grouped by” in Athena, visualized in QuickSight or any compatible 3rd party BI tool, or very simply visualized as clustered, stacked charts in MS Excel. 

## Solution Architecture
![image](./CE-Forecasts-Solution-Architecture.PNG)


## How it works

1.	An EventBridge rule is configured to invoke a Lambda function at a pre-configured schedule. For example, daily, weekly or monthly. Defaults to 7 days.
2.	EventBridge invokes the Lambda function and passes the desired forecast months, and the target S3 location for storing cost forecast results as arguments to the Lambda function. The JSON input to the Lambda function looks something like this,              
   	{ <b />
      "S3Bucket": "mybucket",<b />
      "S3FolderPath": "CostExplorerForecast/", <b />
      "ForecastMonths": 6 <b />
    } 
3.	The Lambda function does the following,
    -	Gets the list of accounts from AWS Organization. 
    -	Get a list of active regions within each account from EC2.
    -	Gets cost forecast data from Cost Explorer, for each active region within the account.
-	Filters accounts and/or regions with no historical cost. 
-	Extracts relevant fields from the output from Cost Explorer, transforms and outputs the results as a CSV file in S3. This file can now be consumed by Amazon Quicksight, and other 3rd party BI tools, like Tableau or Power BI to be graphically visualized.  
-	Optionally, creates a transformation for MS Excel to be viewed as clustered, stacked charts.
4.	The schema for the forecast data is defined and stored in AWS Glue data catalog.
5.	Amazon Quicksight, or any 3rd Party BI tool such as Tableau or Power BI that is compatible with Athena can be used to query and visualize cost forecasting data across accounts and regions.
6.	To view the data in MS Excel, as clustered, stacked charts, uncomment a couple of lines of code in the Lambda function, to get the same forecast data, but transformed to be compatible with MS Excel charts.
For example, uncomment the following lines in the python code,
#s3_key_excel = event['S3FolderPath'] + "Excel/ce_forcasts_excel.csv"
#put_results_in_s3(s3_bucket, s3_key_excel, forecast_results) 


See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

