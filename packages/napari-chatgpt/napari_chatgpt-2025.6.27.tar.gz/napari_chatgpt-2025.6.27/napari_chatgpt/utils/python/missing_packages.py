import sys

from arbol import aprint, asection
from langchain.chains import LLMChain
from langchain.llms import BaseLLM
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from napari_chatgpt.chat_server.callbacks.callbacks_arbol_stdout import \
    ArbolCallbackHandler
from napari_chatgpt.utils.openai.default_model import \
    get_default_openai_model_name

_required_packages_prompt = f"""
**Context:**
You are an expert Python coder with extensive knowledge of all python libraries, and their different versions.

**Task:**
Find the list of "pip installable" packages (packages that can be installed using the 'pip install' command) required to run the Python code provided below. The code is written against Python version {sys.version.split()[0]}.
Please only include packages that are absolutely necessary for running the code. Do not include any other packages. Exclude any dependencies that are already included in the listed packages.
The answer should be a space-delimited list of packages, without any additional text or explanations before or after the list.
For example, if the code requires the packages 'numpy', 'scipy', and 'magicgui', the answer should be a single line: 'numpy scipy magicgui'.
If no additional packages are required to run this code, just return an empty string.
Make sure we have the right answer.

**Code:**

```python
{'{code}'}
```

**Space Separated List of Packages:**
"""


def required_packages(code: str,
                      llm: BaseLLM = None,
                      verbose: bool = False):
    with(asection(
            f'Automatically determines missing packages for code of length: {len(code)}')):
        # Cleanup code:
        code = code.strip()

        # If code is empty, nothing is missing!
        if len(code) == 0:
            return []

        aprint(f'Input code:\n{code}')

        # Instantiates LLM if needed:
        llm = llm or ChatOpenAI(model_name=get_default_openai_model_name(),
                                temperature=0)

        # Make prompt template:
        prompt_template = PromptTemplate(template=_required_packages_prompt,
                                         input_variables=["code"])

        # Instantiate chain:
        chain = LLMChain(
            prompt=prompt_template,
            llm=llm,
            verbose=verbose,
            callbacks=[ArbolCallbackHandler('Required libraries')]
        )

        # Variable for prompt:
        variables = {"code": code}

        # call LLM:
        list_of_packages_str = chain.invoke(variables)['text']

        # Cleanup:
        list_of_packages_str = list_of_packages_str.strip()

        # Sometimes some models insist on having some text before:
        if ':' in list_of_packages_str:
            list_of_packages_str = list_of_packages_str.split(':')[-1].strip()

        # If the string contains commas:
        if ',' in list_of_packages_str:
            list_of_packages_str = list_of_packages_str.replace(',', ' ')

        # If the string contains new lines:
        if '\n' in list_of_packages_str:
            list_of_packages_str = list_of_packages_str.replace('\n', ' ')

        if len(list_of_packages_str) > 0:

            # Parse the list:
            list_of_packages = list_of_packages_str.split()

            # Remove duplicates:
            list_of_packages = list(set(list_of_packages))

            # Strip each package name of white spaces:
            list_of_packages = [p.strip() for p in list_of_packages]

            # Remove empty strings:
            list_of_packages = [p for p in list_of_packages if len(p) > 0]

            aprint(f'List of required packages:\n{list_of_packages}')

        else:
            aprint(f'No packages to run this code!')
            return []

    return list_of_packages



