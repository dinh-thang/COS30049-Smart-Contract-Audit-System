from fastapi import UploadFile, HTTPException, status
import os
import re
import subprocess

UPLOADS_DIR = "uploads"

def save_uploaded_file(contract: UploadFile):
    """
    Saves the uploaded file to the 'uploads' directory.

    Params:
        contract (UploadFile): The uploaded file to be saved.

    Returns:
        str: The file path where the file is saved.
    """
    try: 
        # ensure that the 'uploads' directory exists, exist_ok to True to specify existing dir w/o error
        os.makedirs(UPLOADS_DIR, exist_ok=True)

        # file path within the 'uploads' directory
        file_path = os.path.join(UPLOADS_DIR, contract.filename)

        # write the contents of the uploaded file to the specified file path
        with open(file_path, "wb") as f:
            f.write(contract.file.read())

        # return the file path where the file is saved
        return file_path
    except Exception as e:
        #  HTTPException with a 500 status code
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error occurred while saving the file. Please try again.")


def extract_solidity_version(file_content: str):
    """
    Extracts the Solidity version from the given file content.

    Params:
        file_content (str): The content of the file.

    Returns:
        str or None: The Solidity version if found, None otherwise.
    """
    try: 
        # regexp match "pragma solidity x.y.z;" or "pragma solidity ^x.y.z;"
        version_pattern = re.search(r"pragma solidity \^?(?P<version>\d+\.\d+\.\d+);", file_content)

        # raise an exception if no version is found
        if not version_pattern:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solidity version not found in the file.",
            )

        # return the version if found
        return version_pattern.group('version')
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error occurred while extracting the Solidity version. Please try again.")


def analyze_contract(file_path: str, solidity_version: str):
    """
    Analyses uploaded contract by running Slither commands with the specified Solidity version.

    Params:
        file_path (str): The path to the contract file.
        solidity_version (str): The version of Solidity used in the uploaded contract.

    Returns:
        str: The path to the generated Markdown file.
    """
    try:
        # run Slither commands with the specified Solidity version using subprocess
        install_cmd = ['solc-select', 'install', solidity_version]
        use_cmd = ['solc-select', 'use', solidity_version]
        slither_cmd = ['slither', file_path, '--checklist']
        
        subprocess.run(install_cmd, check=True)
        subprocess.run(use_cmd, check=True)
        
        with open(f"{file_path}.md", "w") as output_file:
            subprocess.run(slither_cmd, stdout=output_file)
        
        # return the path to the generated Markdown file
        return f"{file_path}.md"
    except subprocess.CalledProcessError as e:
        # HTTPException with a 500 status code and the error details
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error running Slither. Please try again.")
    except Exception as e:
        # HTTPException with a 500 status code and the error details
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error analyzing contract. Please try again.")

def filter_report(file_path: str):
    """
    Reads the contents of a markdown file located at the given `file_path` and extracts the vulnerabilities and their details.

    Params:
        file_path (str): The path to the markdown file.

    Returns:
        list: A list of dictionaries containing information about each vulnerability found in the markdown file. Each dictionary has the following keys:
            - vulnerability_type (str): The type of vulnerability.
            - impact (str): The impact of the vulnerability.
            - confidence (str): The confidence level of the vulnerability.
            - recommendation (str): The recommendation for fixing the vulnerability.
            - results (list): A list of dictionaries containing information about each result of the vulnerability. Each dictionary has the following keys:
                - ID (int): The ID of the result.
                - description (str): The description of the result.
                - location (str): The location of the result within the contract.
    """
    try:
        with open(file_path, "r") as f:
            md_content = f.read()

            # patterns to match vulnerability types, impact, confidence, and results. 
            # ! result_pattern no ok yet, 90% ok
            vulnerability_pattern = r"##\s*(?P<vulnerability_type>[\w-]+)\nImpact:\s*(?P<impact>\w+)\nConfidence:\s*(?P<confidence>\w+)(?P<results>[\s\S]+?)(?=\n##|$)"
            # one vuln can have many results with different locations within the contract
            result_pattern = r'- \[ \] ID-(?P<id>\d+)\n(?P<description>[^\n]+)\n(?:.+\n)*\t[^\n]+\n\n[^\n]*?(?P<location>#\S+)'

            matches = re.finditer(vulnerability_pattern, md_content)

            vulnerabilities = []

            for match in matches:
                result_dict = match.groupdict()
                vulnerability_info = {
                    "vulnerability_type": result_dict["vulnerability_type"],
                    "impact": result_dict["impact"],
                    "confidence": result_dict["confidence"],
                    "recommendation": None,  # initialise recommendation
                    "results": []
                }

                # find matches for each result within the vulnerability
                results_matches = re.finditer(result_pattern, result_dict["results"])
                for result_match in results_matches:
                    result = result_match.groupdict()
                    vulnerability_info["results"].append({
                        "ID": int(result["id"]),
                        "description": result["description"].strip(),
                        "location": result["location"]
                    })

                # find recommendation for the vulnerability type
                vulnerability_info["recommendation"] = find_recommendation(vulnerability_info["vulnerability_type"])

                # append the vulnerability info to the list
                vulnerabilities.append(vulnerability_info)

            # return the list of vulnerabilities
            return vulnerabilities
    except Exception as e:
        # HTTPException with a 500 status code and the error details
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error occurred while filtering the report. Please try again.")

def upload_report(report: dict):
    # debug
    # print("Uploading report to the database:")
    # print(report)
    return report

    # return a status code/msg
    # return "Report uploaded successfully"

def find_recommendation(check_name: str):
    """
    Find recommendation for a given check name.
    
    Params:
        check_name (str): The name of the vulnerability to find the recommendation for.
    
    Returns:
        str: The recommendation for the given vulnerability name.
    """
    try:
        # the file path to slither wiki, basically .md file that contains recommendation for the given vulnerability
        # this file clone from Slither github page: https://github.com/crytic/slither/wiki/Detector-Documentation
        file_path = './slither.wiki/Detector-Documentation.md'
        
        # open the wiki file
        with open(file_path, 'r') as file:
            # read the file
            content = file.read()

        # regexp pattern with named group for extracting recommendation
        # DOTALL to match \n character
        pattern = re.compile(
            fr'##\s.*?###\sConfiguration\n\* Check: `{check_name}`.*?###\sRecommendation\n(?P<recommendation>.*?)(?=\n##\s|\Z)',
            re.DOTALL
        )

        # search for the pattern in the content
        match = re.search(pattern, content)

        # return the recommendation if has a match
        if match:
            recommendation = match.group('recommendation').strip()
            return recommendation
        else:
            return f'Recommendation not found for: {check_name}'
    except Exception as e:
        # HTTPException with a 500 status code and the error details
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching recommendation. Please try again.")

# # func get current date and time as a string
# def get_current_datetime():
#     return datetime.now().strftime("%d-%m-%Y %I:%M %p")