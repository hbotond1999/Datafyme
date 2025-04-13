from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

from common.ai.model import get_llm_model


class PythonCode(BaseModel):
        code: str = Field(description="Your working and safe code")

def dataframe_cleaner_agent():
        prompt_str ="""
### Context
You are a helpfully professional data engineer, who specialized to cleaning data with python and pandas.

###Task
Please create Python code to clean and prepare a pandas DataFrame for database storage and efficient visualization. The code should include the following functionalities:

Here is the dataframe dataframe preview: 

{dataframe}

1. Proper conversion and standardization of data types:
   - Converting dates to a consistent datetime format
   - Converting numeric values to appropriate types (int, float)
   - Cleaning text data (removing unnecessary whitespace, standardizing case)

2. Handling special values:
   - Splitting currencies into separate columns (e.g., "$5000" into a "currency" column with "$" and an "amount" column with 5000)
   - Separating units from values (e.g., "10kg" → "value": 10, "unit": "kg")
   
Please create Python code to clean and prepare a pandas DataFrame (referenced as 'df') for database storage and efficient visualization. The code must adhere to these requirements:

1. Only use pandas functionality (already imported as 'pd')
2. Do NOT include any import statements
3. Always reference the DataFrame as 'df'
4. The code should be executable with Python's exec() function
5. All operations should modify the 'df' variable in place when possible


### Example
For example:
df.select_dtypes(include=['object']).columns.tolist()
for col in df.select_dtypes(include=['object']).columns.tolist():
df[col] = df[col].str.lower()

"""
        prompt = PromptTemplate(template=prompt_str, input_variables=["dataframe"])

        return prompt | get_llm_model().with_structured_output(PythonCode)