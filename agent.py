import os 
import yaml
import json
import requests
import pandas as pd
from requests.exceptions import RequestException
import math
import re
from termcolor import colored
from search import WebSearcher
from urllib.parse import urlparse
from collections import OrderedDict
from prompts import query_agent_prompt, equipment_agent_prompt, application_agent_prompt, region_agent_prompt, planning_agent_prompt, \
    vendor_agent_prompt, length_agent_prompt, criteria_agent_prompt, resource_agent_prompt, integration_agent_prompt

#Default varables
equipment_item = None
application = "pharmaceutical"
valid_application = None
valid_equipment_item = None
#length = 1
#excelfile = None

#North America, Europe, Asia-Pacific (APAC), Middle East & Africa (MEA), Latin America, and Russia & CIS
region_list = ["North America", "Europe", "Asia-Pacific (APAC)", "Middle East & Africa (MEA)", "Latin America", "Russia & CIS"]
region = region_list[1]

Market_sectors = ["Pharmaceutical & Biotechnology", "Life Sciences & Medical Devices", "Food & Beverage Processing", "Chemical & Petrochemical", 
                  "Semiconductor & Electronics", "Energy & Environmental", "Aerospace & Automotive", "Academic & Research Laboratories"]

#Project data may contain project name, facility type, product type, and location
project_name = None #"Lonza Eden Project"
facility_type = None #"Biopharmaceutical Manufacturing Facility"
product_type = None #"Antibody Drug Conjugate"
facility_location = None #"Visp, Switzerland"
project = [project_name, facility_type, product_type, facility_location]

# User data may contain user name, company, title and location
user_name = None #"David Tomsik"
user_company = None #"CRB Group"
user_title = None #"Process Engineer"
user_location = None #"Basel, Switzerland"
user = [user_name, user_company, user_title, user_location]

def load_config(file_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
        for key, value in config.items():
            os.environ[key] = value

class Agent:
    def __init__(self, model, tool, temperature=0, max_tokens=1000, query_agent_prompt=None, equipment_agent_prompt=None, application_agent_prompt=None, region_agent_prompt=None, \
        planning_agent_prompt=None, vendor_agent_prompt=None, length_agent_prompt=None, criteria_agent_prompt=None, resource_agent_prompt=None, integration_agent_prompt=None, verbose=False):
        load_config('config.yaml')
        self.api_key = os.getenv("OPENAI_API_KEY")
#for chat-based interactions, continue using https://api.openai.com/v1/chat/completions. For instruction-based tasks, consider using the 
#gpt-3.5-turbo-instruct model with the /v1/completions endpoint
        self.url = 'https://api.openai.com/v1/chat/completions'
        #self.api_key = os.getenv("DEEPSEEK_API_KEY")
        #self.url = 'https://api.deepseek.com/v1/chat/completions'
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.tool = tool
        self.tool_specs = tool.__doc__
        self.query_agent_prompt = query_agent_prompt
        self.equipment_agent_prompt = equipment_agent_prompt        
        self.application_agent_prompt = application_agent_prompt
        self.region_agent_prompt = region_agent_prompt
        self.planning_agent_prompt = planning_agent_prompt
        self.vendor_agent_prompt = vendor_agent_prompt
        self.length_agent_prompt = length_agent_prompt
        self.criteria_agent_prompt = criteria_agent_prompt
        self.resource_agent_prompt = resource_agent_prompt
        self.integration_agent_prompt = integration_agent_prompt
        self.model = model
        self.verbose = verbose
#query = user input from terminal
#project = [project_name, facility_type, product_type, facility_location]
#user = [user_name, user_company, user_title, user_location]
#
#
    def run_query_agent(self, query, project, user, outputs):

        system_prompt = self.query_agent_prompt.format(
            query=query,
            project=project,
            user=user,
            outputs=outputs 
        )

        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": query},
                         {"role": "system", "content": system_prompt}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

        json_data = json.dumps(data)
        response = requests.post(self.url, headers=self.headers, data=json_data, timeout=180)
        response_dict = response.json()
        print("Query Agent API Response:", response_dict)  # Debugging step
        content = response_dict['choices'][0]['message']['content']
        print(colored(f"Query Agent Content: {content}", 'yellow'))
#return content as output (typical)
        return content
#entry = query agent output = self.run_query_agent(query, project=project, user=user, outputs=outputs)
#
#
    def run_equipment_agent(self, entry, outputs):

        system_prompt = self.equipment_agent_prompt.format(
            entry=entry,
            outputs=outputs
        )

        example_json = {
          "eqitem": [
            {
              "valid_equipment_item": "Bioreactor",
              "equipment_item_comment": "Valid entry for biopharmaceutical use."
            }  
          ]
        }

        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": entry},
                         {"role": "system", "content": system_prompt + json.dumps(example_json)}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

        json_data = json.dumps(data)
        response = requests.post(self.url, headers=self.headers, data=json_data, timeout=180)
        response_dict = response.json()
        print("Equipment Agent API Response:", response_dict)  # Debugging step
        content = response_dict['choices'][0]['message']['content']
        print(colored(f"Equipment Agent Content: {content}", 'yellow'))    

        return content
#entry = query agent output = self.run_query_agent(query, project=project, user=user, outputs=outputs)   
#
#
    def run_application_agent(self, entry, outputs):

        system_prompt = self.application_agent_prompt.format(
            entry=entry,
            outputs=outputs
        )

        example_json = {
          "applic": [
            {
              "valid_application": "Biopharmaceutical Manufacturing Facility",
              "application_comment": "Default application was used since entry did not include one."
            }  
          ]
        }
        
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": entry},
                         {"role": "system", "content": system_prompt + json.dumps(example_json)}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

        json_data = json.dumps(data)
        response = requests.post(self.url, headers=self.headers, data=json_data, timeout=180)
        response_dict = response.json()
        print("Application Agent API Response:", response_dict)  # Debugging step
        content = response_dict['choices'][0]['message']['content']
        print(colored(f"Application Agent Content: {content}", 'yellow'))

        return content
#entry = query agent output = self.run_query_agent(query, project=project, user=user, outputs=outputs)
#
#
    def run_region_agent(self, entry, region_list, outputs):

        system_prompt = self.region_agent_prompt.format(
            entry=entry,
            region_list=region_list,
            outputs=outputs
        )

        example_json = {
          "reout": [
            {
              "valid_region": "Europe",
              "region_comment": "Corrected to Europe based on geographical location."
            }
          ]
        }

        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": entry},
                         {"role": "system", "content": system_prompt + json.dumps(example_json)}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

        json_data = json.dumps(data)
        response = requests.post(self.url, headers=self.headers, data=json_data, timeout=180)
        response_dict = response.json()
        print("Region Agent API Response:", response_dict)  # Debugging step
        content = response_dict['choices'][0]['message']['content']
        print(colored(f"Region Agent Content: {content}", 'red'))

        return content    
#
#
    def run_planning_agent(self, query, eqitem, applic, region, plan=None, outputs=None, feedback=None):

        system_prompt = self.planning_agent_prompt.format(
            outputs=outputs,
            eqitem=eqitem,
            applic=applic,
            region=region,
            query=query,
            plan=plan,
            feedback=feedback,
            tool_specs=self.tool_specs
        )

        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": "equipment item = " + eqitem + "; application = " + applic + "; region = " + region},
                         {"role": "system", "content": system_prompt}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

        json_data = json.dumps(data)
        response = requests.post(self.url, headers=self.headers, data=json_data, timeout=180)
        response_dict = response.json()
#        print(response_dict)
        content = response_dict['choices'][0]['message']['content']
        print(colored(f"Planning Agent: {content}", 'green'))

        return content
#
#

    def run_vendor_agent(self, eqitem, domain, outputs):

        system_prompt = self.vendor_agent_prompt.format(
            eqitem=eqitem,
            domain=domain,
            outputs=outputs
        )

        example_jsons = [
            {
                "vendor": {
                    "name": "WALDNER Process Systems",
                    "website": "waldner.de",
                    "founded": "1908 by Hermann Waldner",
                    "headquarters": "Wangen im Allgäu, Germany",
                    "employees": "Approximately 1,400",
                    "divisions": "Process Systems, Dosomat (packaging machines), Water Technology, Laboratory Furniture",
                    "industries_served": "Pharmaceutical, food, chemical, and healthcare",
                    "product_offerings": "Custom isolators, vessels, CIP/SIP units, full containment systems, and complete process lines",
                    "specialties": "N/A",
                    "certifications": "ISO 9001, ISO 14001",
                    "compliance": "PED, AD2000, DIN EN 13445, ASME, China License, TR certificates",
                    "snippet": "WALDNER specializes in modular, GMP-compliant process systems, including isolators for sterile and high-containment applications. They have delivered over 25,000 custom solutions worldwide.",
                    "agent_comment": "Waldner is a leading supplier of custom made isolators according to their website and several other sources."
                }
            },
            {
                "vendor": {
                    "name": "Dec Group",
                    "website": "dec-group.net",
                    "founded": "1987",
                    "headquarters": "Ecublens, Vaud, Switzerland",
                    "employees": "501-1,000",
                    "divisions": "Powder Handling, Particle Sizing, Filling Solutions, Containment Solutions, Continuous Processing Technologies",
                    "industries_served": "Pharmaceutical and chemical sectors",
                    "product_offerings": "High-containment equipment, powder handling systems, aseptic manufacturing solutions, microdosing, jet milling, blending, sampling, barrier systems, process isolators, and liquids handling",
                    "specialties": "High-containment equipment for pharmaceutical and chemical manufacturing, powder handling equipment, aseptic manufacturing solutions, microdosing, jet milling, bulk solids handling, blending and sampling, barrier systems and process isolators, and liquids handling",
                    "certifications": "N/A",
                    "compliance": "N/A",
                    "snippet": "Dec Group offers integrated process solutions, including isolators for sterile and high-containment applications. Their products are designed to enhance productivity while adhering to regulatory standards.",
                    "agent_comment": "DEC is a prominent supplier of various isolator types, including those for process and pharmaceutical manufacturing according to their website and other sources."            
                }
            },
            {
                "vendor": {
                    "name": "Wikipedia",
                    "website": "en.wikipedia.org",
                    "founded": "N/A",
                    "headquarters": "N/A",
                    "employees": "N/A",
                    "divisions": "N/A",
                    "industries_served": "N/A",
                    "product_offerings": "Not a vendor",
                    "specialties": "N/A",
                    "certifications": "N/A",
                    "compliance": "N/A",
                    "snippet": "N/A",
                    "agent_comment": "Wikipedia doesn't provide the relevent equipment based to their website which doesn't include this type of product."        
                }
            }
        ]

        system_prompt += "\n\n# Example format only (do not copy this):\n" + json.dumps(example_jsons, indent=2)


        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": "valid equipment item = " + eqitem + "domain = " + domain},
                        {"role": "system", "content": system_prompt + json.dumps(example_jsons, indent=2)}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }


        json_data = json.dumps(data)
        response = requests.post(self.url, headers=self.headers, data=json_data, timeout=180)
        response_dict = response.json()
        #print(colored(f"response_dict: {response_dict}", 'yellow'))
        #print()
        content = response_dict['choices'][0]['message']['content']
        #print(colored(f"Vendor Agent: {content}", 'yellow'))
        #print()

        return content

#
#
    def format_results(self, organic_results):

        result_strings = []
        for result in organic_results:
            title = result.get('title', 'No Title')
            link = result.get('link', '#')
            snippet = result.get('snippet', 'No snippet available.')
            result_strings.append(f"Title: {title}\nLink: {link}\nSnippet: {snippet}\n---")
        
        return '\n'.join(result_strings)
    
    def search_equipment_vendors(self, search_query: str):

        search_url = "https://google.serper.dev/search"
        headers = {
            'Content-Type': 'application/json',
            'X-API-KEY': os.environ['SERPER_DEV_API_KEY']  # Ensure this environment variable is set with your API key
        }
#        payload = json.dumps({"q": search_query})

        country = "de"
        language = "de"

        all_results = []

        for page in range(1, 2):
            payload = {
                "q": search_query,
                "gl": country,
                "hl": language,
                "autocorrect": False,
                "num": 20,
                "page": page
            }

            print(colored(f"Fetching page {page}...", 'cyan'))
            response = requests.post(search_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            # Optionally print or save one of the responses
            if page == 1:
                with open("serper_output.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

            # Extract from 'organic'
            for item in data.get("organic", []):
                name = item.get("title", "")
                snippet = item.get("snippet", "")
                link = item.get("link", "")
                parsed_url = urlparse(link)
                domain = parsed_url.netloc.lower().removeprefix("www.")

#                make = next((m for m in makes if m.lower() in (name + " " + snippet).lower()), "Unknown")

                all_results.append({
                    "name": name,
                    "snippet": snippet,
                    "domain": domain,
                    "url": link
                })

            # Extract from 'places'
            for place in data.get("places", []):
                name = place.get("title", "")
                snippet = place.get("snippet", "")
                all_results.append({
                    "name": name,
                    "snippet": snippet,
                    "domain": domain,
                    "url": ""
                })

#        return all_results
# Remove duplicates by domain
        unique_results = OrderedDict()
        for entry in all_results:
            if entry['domain'] not in unique_results:
                unique_results[entry['domain']] = entry

        return list(unique_results.values())

#
    def run_length_agent(self, vendors_out, outputs=None):

        system_prompt = self.length_agent_prompt.format(
            vendors_out=vendors_out,
            outputs=outputs
        )

        example_json = {
          "lnout": [
            {
              "length": 7,
              "length_comment": "Total vendors: 7"
            }
          ]
        }

        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": vendors_out},
                         {"role": "system", "content": system_prompt + json.dumps(example_json)}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

        json_data = json.dumps(data)
        response = requests.post(self.url, headers=self.headers, data=json_data, timeout=180)
        response_dict = response.json()
#        print(response_dict)
        print(f"response_dict: {response_dict}")
        content = response_dict['choices'][0]['message']['content']
#        print(colored(f"Length Agent: {content}", 'red'))

        return content
#
#
    def run_criteria_agent(self, entry, eqitem, applic, vendor, outputs=None):

        system_prompt = self.criteria_agent_prompt.format(
            entry=entry,
            eqitem=eqitem,
            applic=applic,
            vendor=vendor,
            outputs=outputs
        )

        example_json = {
        "criteria": [
            {
              "category": "Vendor Identification",
              "items": [
                "Official company name",
                "Contact details",
                "Regions served",
                "Manufacturing facilities",
                "Industry certifications"
              ]
            },
            {
              "category": "Technical Specifications",
              "items": [
                "Model types",
                "Range of sizes",
                "Materials of construction",
                "Flow rates",
                "Pressure ratings",
                "Packing technologies"
              ]
            },
            {
              "category": "Key Capabilities",
              "items": [
                "Scale production experience",
                "Customization options",
                "Turnaround time for manufacturing and delivery"
              ]
            },
            {
              "category": "Reputation and References",
              "items": [
                "Case studies",
                "Testimonials",
                "References for similar projects",
                "Past experience with the user"
              ]
            },
            {
              "category": "Support Services",
              "items": [
                "Installation services",
                "Qualification services (IQ/OQ/PQ)",
                "Commissioning services",
                "After-sales support (maintenance, spare parts, technical service)"
              ]
            }
          ]
        }

        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": "entry = " + entry + "valid equipment item = " + eqitem + "; valid application = " + applic},
                         {"role": "system", "content": system_prompt + json.dumps(example_json, indent=2)}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

        json_data = json.dumps(data)
        response = requests.post(self.url, headers=self.headers, data=json_data, timeout=180)
        response_dict = response.json()
#        print(response_dict)
        content = response_dict['choices'][0]['message']['content']
#        print(colored(f"Criteria Agent: {content}", 'red'))

        return content
#
#
    def run_resource_agent(self, eqitem, vendor, criteria, plan, outputs=None, feedback=None):

        system_prompt = self.resource_agent_prompt.format(
            eqitem=eqitem,
            vendor=vendor,
            criteria=criteria,
            plan=plan,
            feedback=feedback,
            outputs=outputs,
            tool_specs=self.tool_specs
        )

        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": eqitem},
                        {"role": "system", "content": system_prompt}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

        json_data = json.dumps(data)
        response = requests.post(self.url, headers=self.headers, data=json_data, timeout=180)
        response_dict = response.json()
        content = response_dict['choices'][0]['message']['content']
        return content
#
#
    def run_integration_agent(self, plan, outputs):
        system_prompt = self.integration_agent_prompt.format(
            outputs=outputs,
            plan=plan
        )

        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": plan},
                         {"role": "system", "content": system_prompt}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

        json_data = json.dumps(data)
        response = requests.post(self.url, headers=self.headers, data=json_data, timeout=180)
        response_dict = response.json()
        content = response_dict['choices'][0]['message']['content']
#        print(colored(f"Integration Agent: {content}", 'red'))
        # print("Integration Agent:", content)

        return content
    
    #response format
#
#
    def check_response(self, response, query):
        
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "response_checker",
                    "description": "Check if the response meets the requirements",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "meets_requirements": {
                                "type": "string",
                                "description": """Check if the response meets the requirements of the query based on the following:
                                1. The response should be relevant to the query.
                                2. The response should be coherent and well-structured with citations.
                                3. The response should be comprehensive and address the query in its entirety.
                                Return 'yes' if the response meets the requirements and 'no' otherwise.
                                """
                            },
                        },
                        "required": ["meets_requirements"]
                    }
                }
            }
        ]

        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": f"Response: {response} \n Query: {query}"},],
            "temperature": 0,
            "tools": tools,
            "tool_choice": "required"
        }

        json_data = json.dumps(data)
        response = requests.post(self.url, headers=self.headers, data=json_data, timeout=180)
        response_dict = response.json()

        tool_calls = response_dict['choices'][0]['message']['tool_calls'][0]
        arguments_json = json.loads(tool_calls['function']['arguments'])
        response = arguments_json['meets_requirements']

        if response == 'yes':
            return True
        else:
            return False
#
#
    def execute(self, iterations=5):
        query = input("Enter equipment description: ")
        tool = self.tool(model=self.model, verbose=self.verbose)
        meets_requirements = False
        plan = None
        entry = None
        eqitem = None
        applic = None
        region = None
        vendor = None
        vendors_out = None        
        length = 1
        criteria = None
        criteria_dict = None
        outputs = None
        response = None
        code = "run"
        iterations = 0

        entry = self.run_query_agent(query, project=project, user=user, outputs=outputs)
        print(colored(f"Entry: {entry}", 'cyan'))
        print()

        data = self.run_equipment_agent(entry=entry, outputs=outputs)
        clean_data = re.sub(r"```[a-zA-Z]*", "", data).strip()
        eqdata = json.loads(clean_data)
        eqitem = eqdata['valid_equipment_item']
        eqcomm = eqdata['equipment_item_comment']
        #print(colored(f"Valid Equipment Item: {eqitem}", 'cyan'))
        #print(colored(f"Equipment Item Comment: {eqcomm}", 'cyan'))
        #print()
        if eqitem == "invalid entry":
            code = "stop"
            print("code:",code)
            print(colored(f"Valid Equipment Item: {eqitem}", 'cyan'))
            print(colored(f"Equipment Item Comment: {eqcomm}", 'cyan'))
            print()
        if code == "run":
            data = self.run_application_agent(entry=entry, outputs=outputs)
            clean_data = re.sub(r"```[a-zA-Z]*", "", data).strip()
            #apdata = json.loads(clean_data)
            if clean_data and clean_data.strip():
                apdata = json.loads(clean_data)
            else:
                print("clean_data is empty or invalid")
                apdata = {}
    #
    #
            applic = apdata['valid_application']
            apcomm = apdata['application_comment']
            #print(colored(f"Valid Application: {applic}", 'cyan'))
            #print(colored(f"Application Comment: {apcomm}", 'cyan'))
        if applic == "invalid entry":
            code = "stop"
            print("code:",code)
            print(colored(f"Valid Application: {applic}", 'cyan'))
            print(colored(f"Application Comment: {apcomm}", 'cyan'))
            print()
#
#
        if code == "run":
            reout = self.run_region_agent(entry=entry, region_list=region_list, outputs=outputs)
            clean_data = re.sub(r"```[a-zA-Z]*", "", reout).strip()
            redata = json.loads(clean_data)
            region = redata['region']
            recomm = redata['region_comment']
            print(colored(f"Valid Region: {region}", 'cyan'))
            print(colored(f"Region Comment: {recomm}", 'cyan'))


        if code == "run":
            vendors = self.search_equipment_vendors(eqitem)
    #        print()            
    #        print("Vendors data:", vendors)
            domains = [vendor['domain'] for vendor in vendors]
    #        print()
    #        print(colored(f"Domains: {domains}", 'cyan'))


            def export_to_xlsx(vendors, filename="vendor_list_dev.xlsx"):
                df = pd.DataFrame(vendors)
                df.to_excel(filename, index=False)
                print()
                print("Saving to:", os.path.abspath(filename))
    #            print(f"Exported {len(df)} results to {filename}")
                return len(df), filename

            length, excelfile = export_to_xlsx(vendors)
            print()
            print(f"Exported {length} results to {excelfile}")

            # Define outside the loop to avoid redeclaring every time
            def print_vendor_parameters(vendor_list, vendor_number):
                for vendor in vendor_list:
                    name = vendor['name']
                    website = vendor['website']
                    founded = vendor['founded']
                    headquarters = vendor['headquarters']
                    employees = vendor['employees']
                    divisions = vendor['divisions']
                    industries_served = vendor['industries_served']
                    product_offerings = vendor['product_offerings']
                    specialties = vendor['specialties']
                    certifications = vendor['certifications']
                    compliance = vendor['compliance']
                    snippet = vendor['snippet']
                    agent_comment = vendor['agent_comment']
                    print()
                    print("Number:", vendor_number)
                    print("Company Name:", name)
                    print("Company Website:", website)
                    print("Founded:", founded)
                    print("Headquarters:", headquarters)
                    print("Employees:", employees)
                    print("Divisions:", divisions)
                    print("Industries Served:", industries_served)
                    print("Product Offerings:", product_offerings)
                    print("Specialties:", specialties)
                    print("Certifications:", certifications)
                    print("Compliance:", compliance)
                    print("Snippet:", snippet)
                    print("Agent Comment:", agent_comment)

        # Initialize loop
        vendor_number = 1
        iterations = 1
        iterations_max = length
        all_vendors = []

        while code == "run" and iterations <= iterations_max:
            print()
            print("ITERATIONS:", iterations)
            print("LENGTH:", length)
            print("MEETS REQUIREMENTS:", meets_requirements)
            print("ITERATIONS MAX:", iterations_max)

            print(colored(f"Vendor Snippet: {vendors[iterations-1]['snippet']}", 'cyan'))
            domain = vendors[iterations-1]['domain']
            print("Current Vendor Domain:", domain)

            vendor_output = self.run_vendor_agent(eqitem, domain, outputs)

            print("RAW vendor_output:")
            print(vendor_output)

            vendors_list = []

            if vendor_output:
                try:
                    vendors_dict = json.loads(vendor_output)
                except json.JSONDecodeError:
                    match = re.search(r'```json\s*(\{.*?\})\s*```', vendor_output, re.DOTALL)
                    if match:
                        try:
                            vendors_dict = json.loads(match.group(1))
                        except json.JSONDecodeError as e:
                            print("JSON decode failed:", e)
                            vendors_dict = {}
                    else:
                        print("No valid JSON found.")
                        vendors_dict = {}

                # ✅ Handle both 'vendor' and 'vendors_list'
                if "vendors_list" in vendors_dict:
                    vendors_list = vendors_dict["vendors_list"]
                elif "vendor" in vendors_dict:
                    vendors_list = [vendors_dict["vendor"]]
                else:
                    print("No vendor or vendors_list key found.")

                if vendors_list:
                    all_vendors.extend(vendors_list)
                    print_vendor_parameters(vendors_list, vendor_number)
                else:
                    print("No vendor list found in output.")
            else:
                print("No output from vendor agent.")

            vendor_number += 1
            iterations += 1

        # ✅ Export all vendors to Excel after the loop
        if code == "run":
            if all_vendors:
                df = pd.DataFrame(all_vendors)
                output_path = "vendor_parameters_output.xlsx"
                df.to_excel(output_path, index=False)
                print(f"\nExported vendor data to: {output_path}")
            else:
                print("\nNo vendors were collected to export.")

#
#
if __name__ == '__main__':
    agent = Agent(model="gpt-4-turbo",

                  tool=WebSearcher, 
                  query_agent_prompt=query_agent_prompt, 
                  equipment_agent_prompt=equipment_agent_prompt, 
                  application_agent_prompt=application_agent_prompt, 
                  region_agent_prompt=region_agent_prompt, 
                  planning_agent_prompt=planning_agent_prompt, 
                  vendor_agent_prompt=vendor_agent_prompt, 
                  length_agent_prompt=length_agent_prompt, 
                  criteria_agent_prompt=criteria_agent_prompt, 
                  resource_agent_prompt=resource_agent_prompt, 
                  integration_agent_prompt=integration_agent_prompt,
                  verbose=True
                  )
    agent.execute()
