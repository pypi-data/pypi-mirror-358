import openai
import pandas as pd

class DataQualitySummery:
    def __init__(self,api_key: str,base_url: str, model:str, temprature, max_token):
        self.api_key= api_key
        self.base_url= base_url
        self.model= model
        self.temprature= temprature
        self.max_token= max_token

    def create_connection(self):
        try:
            if 'pwc' in self.base_url:
                # print(self.api_key,self.base_url)
                client= openai.OpenAI(
                        api_key=self.api_key,
                        base_url=self.base_url
                    )
                if client:
                        return client
                else:
                        return "Connection establish unsuccessful"
            else:
                 return "Connection establish not possible"
        
                
        except Exception as e:
            return f"Error: {e}"
        
    def data_quality_details(self, data: pd.DataFrame, response:str=None)-> str:

        system_prompt= """
        You are an expert in data quality and data analytics who understand data impact on business
        Based on Gartener Data Quality Metrics, please assess dataset and return a report that includes:
        - Defination for each metrics (Completeness, Uniqueness, Accuracy, Consistency, Timeleness, Validity)
        - Score (out of 100) per matric (or N/A if not applicable)
        - Area for Imporvement per metric
        - Summery table
        - Overall data quality score
        Here is the dataset:
        """+(data.to_string(index=False)[:3000] if data is not None else '') # truncate to avoid token limit
        client= self.create_connection()
        if data is not None:
            message= [{"role":"user", "content": system_prompt}]
            llm_response= client.chat.completions.create(
                model=self.model,
                messages= message,
                temperature= self.temprature,
                max_tokens= 1000
            )

            gratner_output= llm_response.choices[0].message.content
            print(gratner_output)
            return gratner_output
    
    def data_quality_summery(self, response):

        sys_promt=  """
        Based on the user response summerise the content and present it within 150 words
        """+{response}

        client= self.create_connection()
        if response is not None:
            message= [{"role":"user", "content": response}]
            llm_response= client.chat.completions.create(
                model=self.model,
                messages= message,
                temperature= self.temprature,
                max_tokens= 1000
            )

            gratner_output_summery= llm_response.choices[0].message.content
            print(gratner_output_summery)
            return gratner_output_summery


        
    