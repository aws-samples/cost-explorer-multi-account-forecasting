##############################

import boto3
import json
import random
from datetime import datetime, timedelta

def put_results_in_s3(bucket, key, body):
    s3_client = boto3.client('s3')
    s3_client.put_object(Bucket=bucket, Key=key, Body=body)
    return
    
def format_filter(account, region):
    f_filter = "{{\"And\": [{{\"Dimensions\": {{\"Key\": \"LINKED_ACCOUNT\",\"Values\": [\"{}\"]}}}},{{\"Dimensions\": {{\"Key\": \"REGION\",\"Values\": [\"{}\"]}}}}]}}".format(account,region)
    return json.loads(f_filter)

def get_active_regions():
    ec2_client = boto3.client('ec2')
    region_list = ec2_client.describe_regions(AllRegions=False)
    active_regions = []
    for regions in  region_list['Regions']:
       active_regions.append(regions['RegionName'])

    return active_regions

def get_active_accounts():
    org_client = boto3.client('organizations')
    acct_list = org_client.list_accounts()
    active_accts = []
    for accts in  acct_list['Accounts']:
        if accts['Status'] == 'ACTIVE':     
           active_accts.append(accts['Id'])
    return active_accts

def get_forecasts(filter, forecast_interval_days):
    ce_client = boto3.client('ce')

    startMonth = str(datetime.now().month+1).zfill(2)
    startYear = str(datetime.now().year)
    startDay = "01"
    startDate = startYear + "-" + startMonth + "-" + startDay

    endTime = datetime.now() + timedelta(days = forecast_interval_days)

    endMonth = str(endTime.month+1).zfill(2)
    endYear = str(endTime.year)
    endDay = "01"
    endDate = endYear + "-" + endMonth + "-" + endDay

    timeperiod = "{{\"Start\": \"{}\",\"End\": \"{}\"}}".format(startDate, endDate)

    #print(timeperiod)

    try:
       forecast = ce_client.get_cost_forecast( 
                                              #TimePeriod={'Start': '2022-08-01','End': '2022-11-01'},
                                              TimePeriod=json.loads(timeperiod),
                                              Metric = 'UNBLENDED_COST',
                                              Granularity='MONTHLY',
                                              Filter = filter
                                             )	
    except:
       print("NO DATA AVAILABLE...")

    return forecast

def get_output_as_quicksight(forecast_interval_days):

    ## Initialize Forecast Results
    #forecast_results = "Account,Date,Region,Forecast\n"
    forecast_results = ""

    ## Get Active Regions and Active Accounts in AWS Organizations
    active_regions = get_active_regions()
    active_accts = get_active_accounts()

    for acct in active_accts:
       for region in active_regions:
          filter = format_filter(acct,region)
          print("\nGetting Data For ", acct, " ", region)

          try:
             #print("\nFORECAST: \n", get_forecasts(filter))
             forecasts = get_forecasts(filter, forecast_interval_days)

             for forecast in forecasts["ForecastResultsByTime"]:
               MV = int(round( float(forecast["MeanValue"])))

               ## Remove Zero and Null Mean Values.
               if MV > 1 :
                  forecast_results += acct + ","
                  forecast_results += forecast["TimePeriod"]["Start"] + ","
                  forecast_results += region + ","
                  forecast_results += str(MV) + "\n"	 	    	    		        
          except:
             print("Error - Forecast Data Not Available")

    print("FINAL OUTPUT....\n")
    print(forecast_results)

    return forecast_results

def get_time_periods(forecast):
    output = ","

    for tp in forecast["ForecastResultsByTime"] :
       output += "," 
       st_time = tp["TimePeriod"]["Start"]
       output += str(st_time)

    output += "\n" 

    return output  


def get_output_as_excel(forecast_interval_days):

    ##Initialize Forecast Results
    forecast_results = ""
    ITR = "0"

    ## Get Active Regions and Active Accounts in AWS Organizations
    active_regions = get_active_regions()
    active_accts = get_active_accounts()

    for acct in active_accts:
       for region in active_regions:
         filter = format_filter(acct,region)
         print("\nGetting Data For ", acct, " ", region)

         try:
            #print("\nFORECAST: \n", get_forecasts(filter))
            forecasts = get_forecasts(filter,forecast_interval_days)
            if ITR == "0" :
               forecast_results += get_time_periods(forecasts)
               print("TIME PERIODS = ", forecast_results, "\n" )
               ITR = "1"

            #forecast_results += region + "," + acct

            mean_values = ""

            for forecast in forecasts["ForecastResultsByTime"]:	            
              MV = int(round( float(forecast["MeanValue"])))
              ## Remove Zero and Null Mean Values.
              if MV > 1 :	            
                 mean_values += "," + str(MV)
              else:
                 ## Populate with test data temporarily. Remove this for real data
                 MV = random.randint(500,5000)
                 #mean_values += "," + str(MV)
            if mean_values != "" :
               regn_acct = region + "," + "a-" + acct
               forecast_results += regn_acct + mean_values + "\n"

         except:
            print("Error")
    
       forecast_results += ",,,,\n" 

    print("FINAL OUTPUT....\n")
    print(forecast_results)

    return forecast_results	    

def lambda_handler(event, context):
    # TODO implement

    s3_bucket = event['S3Bucket']
    s3_key = event['S3FolderPath'] + "ce_forcasts.csv"
    forecast_interval_days = event['ForecastMonths'] * 30
    DEFAULT_FORECAST_INTERVAL_DAYS = forecast_interval_days

    ## Output results as CSV for Quicksight
    forecast_results = get_output_as_quicksight(forecast_interval_days)      

    ## Upload results in S3
    put_results_in_s3(s3_bucket, s3_key, forecast_results)

    ## Output results as CSV for MS Excel
    forecast_results = get_output_as_excel(forecast_interval_days)

    ## Upload results in S3
    #s3_key = "CostExplorerForecast/forecast-data-excel.csv"
    #put_results_in_s3(s3_bucket, s3_key, forecast_results)

    return {
              'statusCode': 200
    }

   ##############################
 
