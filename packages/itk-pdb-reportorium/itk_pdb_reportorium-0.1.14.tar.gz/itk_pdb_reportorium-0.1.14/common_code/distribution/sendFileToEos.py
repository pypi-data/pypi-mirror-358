### example script to send files to EOS
# usage: python sendFileToEos.py --files my_report.html --projCode T --type TEST -w 2.9.9 -l thing
# assume EOS user_name (eos_usr) and password (eos_pwd) in environment
# NB: replace YOUR_EOS_FILEPATH with appropriate
import os
import sys
import argparse
### if functions file in same directory
#from functions import *
from .functions import *
from datetime import datetime
import argparse
import json
from common_code.credentials import CheckCredential
from common_code.distribution.functions import UseLinkList
from common_code.distribution.functions import SendToEos

### if functions file in sub-directory, e.g. commonCode
# sys.path.insert(1, os.getcwd()+'/commonCode')
# from commonFunctions import *
### other
cwd = os.getcwd()

#################
### useful functions
#################
### map project code to name
projMap={'P':"pixels", 'S':"strips", 'CE':"common_electronics", 'CM':"common_mechanics", 'G':"general", 'T':"test"}



# ---------- Loading the JSON file from metadata directory ----------
script_dir = os.path.dirname(os.path.abspath(__file__))

# ✅ Corrected path: go up one level to common_code/, then into metadata/
json_file_path = os.path.abspath(os.path.join(script_dir, "..", "metadata", "reportTypeMap.json"))

print(f"Looking for file at: {json_file_path}")

with open(json_file_path, "r") as file:
    data = json.load(file)

# ---------- Extract dictionaries based on the structure in the JSON file ----------
general_data = next((item for item in data if "general" in item), {})
reportTypeMap = general_data.get("general", {}).get("reportTypeMap", {})
general_subtypes = general_data.get("general", {}).get("subtypes", [])

# Extract the data for specific WBS_code
wbs_mappings = {}
for item in data:
    for wbs_code, wbs_data in item.items():
        if wbs_code not in ["general", "ext"]:
            report_type_key = f"reportTypeMap_WBS{wbs_code.replace('.', '')}"
            wbs_mappings[wbs_code] = {
                "reportTypeMap": wbs_data.get(report_type_key, {}),
                "subtypes": wbs_data.get("subtypes", [])
            }

# Collect all valid WBS codes
valid_wbs_codes = list(wbs_mappings.keys())

def GetArgs(descStr=None):
    my_parser = argparse.ArgumentParser(description=descStr)
    # -------------------------------------------------
    my_parser.add_argument('--files', '-f', nargs='+', help='paths to files', default=[])
    my_parser.add_argument('--fileDir', '-fd', type=str, help='paths to directory with (html/pdf) files', default=None)
    my_parser.add_argument('--projCode', '-p', type=str, help='project: CE, CM, S, P', required=True)
    my_parser.add_argument('--type', '-t', type=str, help='type of report: DI, PQ, SS, TEST', required=True)
    my_parser.add_argument('--link', '-l', type=str, help='link to code', required=True)
    my_parser.add_argument('--date', '-d', type=str, help="report date (YYYY_mm_dd), will use today's date if not supplied", default=None)
    my_parser.add_argument('--author', '-a', type=str, help='report author, will use EOS username if not supplied', default=None)
    my_parser.add_argument('--wbsCode', '-w', type=str, help=f'WBS code: {", ".join(valid_wbs_codes)}', default=None)
    my_parser.add_argument('--Type_of_Sub_category', '-tsc', type=str, help='Type sub-category for the specified WBS code', default=None)

    args = my_parser.parse_args()
    # -------------------------------------------------
    # **Final validation**: Ensure selected type matches WBS_code (if given)
    if args.type and args.wbsCode and args.wbsCode in wbs_mappings:
        valid_types_for_wbs = wbs_mappings[args.wbsCode]["reportTypeMap"].keys()
        if args.type not in valid_types_for_wbs:
            print(f"Invalid type '{args.type}' for WBS {args.wbsCode}. \nAvailable options: {valid_types_for_wbs}")
            exit(-1)
    # -------------------------------------------------
    return args

### get files form directory (keep pdf & html)
def GetFilesFromDir(dirPath, extList=["pdf","html"]):
    # check directory exists
    print(f"Checking directory: {dirPath}")
    if not os.path.isdir(dirPath):
        print(" - directory not found :( exiting")
        # quit if not file
        return []
    else:
        print("  - directory found :)")
    # collect file paths
    print(f"  - checking for: {', '.join(extList)}")
    keepList=[]
    for ld in os.listdir(dirPath):
        if ld.split('.')[-1] in extList:
            print(f"    - found report: {ld}")
            keepList.append( (dirPath+"/"+ld).replace('//','/') )

    print(f" Found total {len(keepList)} report-like files")
    return keepList


#################
### main
#################
def main(args):
    ### get EOS stuff from environment
    eos_usr=CheckCredential("eos_usr")
    eos_pwd=CheckCredential("eos_pwd")
    # stop if eos info. missing
    if eos_pwd==None or eos_usr==None:
        print("EOS info. missing. Stop here.")
        return -1
    else:
        print("Found EOS info. :)")

    ### check optional arguments
    if args.date==None:
        args.date= datetime.now().strftime("%Y-%m-%d_%H:%M")
    if args.author==None:
        args.author= eos_usr

    ### check project code
    if args.projCode not in list(projMap.keys()):
        print(f"Project code {args.projCode} not recognised. \nPlease select from: \t{projMap.keys()}")
        return -1

    #-------------------------------------------------------------------------------------
    # If wbsCode is not found in wbs_mappings, then the general will be used reportTypeMap
    if args.wbsCode:
        wbs_data = wbs_mappings.get(args.wbsCode, {})
        if not wbs_data:
            print(f"WBS code '{args.wbsCode}' not found in mappings. Using general report types.")
            wbs_data = {"reportTypeMap": reportTypeMap, "subtypes": []}  # Fall back to general mapping

        valid_type = list(wbs_data["reportTypeMap"].keys())
        valid_subcategories = wbs_data["subtypes"]

        if args.type and args.type not in valid_type:
            print(f"Invalid type '{args.type}' for WBS {args.wbsCode}. \n" f"Available options: {valid_type}")
            exit(-1)

        if args.Type_of_Sub_category and args.Type_of_Sub_category not in valid_subcategories:
            print(f"Invalid Type sub-category '{args.Type_of_Sub_category}' for WBS {args.wbsCode}. \n" f"Available options: {valid_subcategories}")
            exit(-1)

        # Proceed with the rest of the script
        print("Validation successful. Proceeding with file upload...")
    #-------------------------------------------------------------------------------------
    # set-meta-data prefix
    print(f"DEBUG: Author: {args.author}, Date: {args.date}")
    #-------------------------------------------------------------------------------------
    metaPrefix = f"{args.projCode}@{args.type}@{args.author}@{args.date}"
    metaPrefix += f"@{args.wbsCode or 'None'}"
    #metaPrefix += f"@{args.Type_of_Sub_category or 'None'}"
    if args.Type_of_Sub_category:
        metaPrefix += f"@{args.Type_of_Sub_category}"
    else:
        metaPrefix += ""  # Remove None from report for Sub_category in case it's not assigned
    #-------------------------------------------------------------------------------------

    ### add link metadata if supplied
    if args.link!=None:
        linkDict=UseLinkList(eos_usr, eos_pwd, args.link)
        metaPrefix+=f"@{linkDict}"
        print(f"{linkDict} link to {metaPrefix}")
    else:
        metaPrefix+=f"@{None}"

    # Loop over files
    count = 0
    print(f"Checking files...")
    for aFile in args.files:
        print(f" - Checking: {aFile}")
        ## check filepaths
        if not os.path.isfile(aFile):
            print("   - file not found :( exiting")
            # quit if not file
            continue
        else:
            print("   - file found :)")

        ### construct EOS filename with metadata
        file_rename= metaPrefix+"@"+aFile.split('/')[-1]

        print(f"   - use file_rename {file_rename}")

        #-------------------------------------------------------------------------------------
        ### Define EOS destination directory
        destDir = f"{projMap[args.projCode]}-reports/"
        eosPath = "/eos/atlas/atlascerngroupdisk/det-itk/prod-db/reports/"
        print(f"   - Destination directory: {destDir}")

        ### Send file to EOS
        if SendToEos(eos_usr, eos_pwd, f"{eosPath}{destDir}", aFile, file_rename):
            print("  ✅ Report successfully sent to eos.")
            count += 1
        else:
            print("  ❌ Failed to send report to eos.")

    return count
#--------------------------------------------------------------------------
if __name__ == "__main__":

    print(f"### In {__file__}")
    args=GetArgs('Send to EOS')

    ### print arguments
    print(vars(args))

    ### check some source is defined
    if args.files==None or len(args.files)<1 and args.fileDir==None:
        print("No files defined. Please use --files argument to define file paths")
#----------------------------------------------------------------------------

    fileList=[]
    ### get files from directory if required
    if args.fileDir!=None:
        fileList=GetFilesFromDir(args.fileDir)

        ## if files found
        if len(fileList)>0:
            ## list found reports for user
            print("######################\n### Reports to upload to eos:\n######################")
            for e,fl in enumerate(fileList,1):
                print(f"{e}. {fl}")
            print("----------------------")

            ## get confirmation
            user_reply= input(f"Upload {len(fileList)} reports? (yes/y/Y) ")
            if user_reply[0].lower()=="y":
                print("### Uploading reports")
                args.files=fileList
            else:
                print("### No uploads.")

        ## if no files found
        else:
            print(f"No files found in {args.fileDir}")

    ### upload reports (if found)
    upCount=0
    if len(args.files)<1:
        print("No reports found to upload.")
    else:
        upCount=main(args)

    print(f"Uploaded reports: {upCount}")
    print("All done.")
