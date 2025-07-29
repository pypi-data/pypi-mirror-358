import os
import sys
import shutil
import argparse
from dotenv import dotenv_values
import json
from alm.__version__ import __version__
import requests
import time
from alm.utils import print_job_info, read_token_from_file, update_file_keys_in_json, zip_current_directory
import yaml
from alm.model import settings
import getpass

from alm.alo_llm_cli import ALC

settings.update()
experimental_plan = settings.experimental_plan
LCC_URL = experimental_plan.setting.ai_logic_deployer_url

# def read_yaml(file_path):
#     with open(file_path, 'r', encoding='utf-8') as file:
#         data = yaml.safe_load(file)
#     return data

def check_ws(workspace_name):
    if workspace_name == None :
        default_workspace_name = read_token_from_file('default_ws')
        workspace_id = read_token_from_file(default_workspace_name)
    else :
        workspace_id = read_token_from_file(workspace_name)  # 주어진 workspace_name으로 workspace_id를 읽어옴
    return workspace_id

# def __api(args):
#     from alo_llm.alo_llm import Alo
#     from alo_llm.model import settings
#     settings.computing= 'api'
#     alo = Alo()
#     alo.run()

# def __login(args): #0522 수정 완
#     ### access token 발급
#     login_url = f"{LCC_URL}/api/v1/auth/login"
#     args.id = input("Please enter your AI Conductor ID: ")
#     args.password = getpass.getpass("Please enter your AI Conductor password: ")
#     login_data = {
#         "username": args.id,
#         "password": args.password
#     }
#     response = requests.post(login_url, data=login_data)
#     if response.status_code == 200:
#         tokens = response.json()
#         print(tokens)
#         access_token = tokens['access_token']
#         # 여기서 .token 파일 초기화함
#         update_file_keys_in_json('access_token', access_token, initialize =True)
#         print("Login success")
#         workspace_return = tokens['user']['workspace']

#         workspace_list = []
#         for i in range (len(workspace_return)):
#             workspace_list.append(workspace_return[i]['name'])
#             update_file_keys_in_json(workspace_return[i]['name'], workspace_return[i]['id'])
#         print(f'You can acess these workspaces: {workspace_list}')

#         # WS가 하나인 경우 default WS로 잡음
#         if len(workspace_list) == 1 :
#             update_file_keys_in_json('default_ws', workspace_list[0])
#             print(f"Default workspace: {workspace_list[0]}")

#         # WS가 여러개인 경우 입력으로 받음
#         else :
#             default_workspace_name = input("please input default workspace")
#             update_file_keys_in_json('default_ws', default_workspace_name)

#             if default_workspace_name in workspace_list :
#                 print(f"Default workspace: {default_workspace_name}")
#             else :
#                 raise ValueError("Please check default workspace name !!")

#     else:
#         print("Failed to obtain access token:", response.status_code, response.text)

def __register(args): # 0522 수정 완
    workspace_id = check_ws(args.workspace)

    token = read_token_from_file('access_token')

    headers = {
        "Authorization": f'Bearer {token}'
    }

    # alm register -list todo: version 들도 보여줘야되나?
    if args.list and not args.delete:
        apilist_url = f"{LCC_URL}/api/v1/workspaces/{workspace_id}/aipacks"

        response = requests.get(apilist_url, headers=headers)

        if response.status_code == 200:
            response_data = response.json()
            api_names = [solution['name'] for solution in response_data['solutions']]
            print(response_data['solutions'])
            title = "API Names"
            max_length = max(len(name) for name in api_names)
            box_width = max(len(title), max_length) + 4

            print(f"┌{'─' * (box_width - 2)}┐")
            print(f"│ {title.center(box_width - 4)} │")
            print(f"├{'─' * (box_width - 2)}┤")
            for api_name in api_names:
                print(f"│ {api_name.ljust(box_width - 4)} │")
            print(f"└{'─' * (box_width - 2)}┘")
        else:
            print("Failed:", response.status_code, response.text)

        return

    # alm register delete
    elif args.delete and not args.list :
        register_list_url = f"{LCC_URL}/api/v1/workspaces/{workspace_id}/aipacks"

        headers = {
            "Authorization": f'Bearer {token}',
            "Content-Type": "application/json"
        }
        response = requests.get(register_list_url, headers=headers)

        if response.status_code == 200:
            response_data = response.json()
            api_names = [[solution['name'], solution['id']] for solution in response_data['solutions']]

            solution_id = None
            for i in range(len(api_names)):
                print(api_names[i][0])
                if args.name==api_names[i][0]:
                    solution_id = api_names[i][1]
            if solution_id == None :
                raise ValueError("Please check service api name !!")

        ### register delete url ###
        url = f"{LCC_URL}/api/v1/workspaces/{workspace_id}/aipacks/{solution_id}"

        response = requests.delete(url, headers=headers)
        if response.status_code == 200:
            print(response.json())
            response_data = response.json()
            result = (
                f"Registration Deleted!\n"
                f"Name: {args.name}\n"
                f"Versions: {version_num}\n"
            )

            print(result)

        else:
            raise Exception(f"Request failed: {response.status_code}, {response.text}")

    else :
        register_apply_uri = f"{LCC_URL}/api/v1/workspaces/{workspace_id}/aipacks"
        api_name = input("Service API name: ")
        api_overview = input("Service API description overview: ")

        # ZIP 파일 생성
        zip_current_directory(f'{api_name}.zip', exclude_files=['.env', '.token', '.venv'])  # 현재 디렉토리 압축
        from alm.__version__ import VERSION  # 버전 정보 가져오기
        # todo base_service_api_rui에 사용자가 입력하는 python 버전으로 바꾸기 대신, python이 아니라 FAISS 이런 버전이면?? python-3.12-FAISS 이런식이라면..
        data = {
            "metadata_json": json.dumps({
                "metadata_version": "1.2",
                "name": api_name,
                "description": {
                    "title": api_name,
                    "alo_version": str(VERSION),
                    "contents_name": api_name,
                    "contents_version": "1.0.0",
                    "inference_build_type": "amd64",
                    "overview": api_overview,
                    "detail": [
                        {
                            "title": "title001",
                            "content": "content001"
                        },
                        {
                            "title": "title002",
                            "content": "content002"
                        }
                    ]
                },
                "ai_pack" : {
                    #"base_service_api_uri" : "339713051385.dkr.ecr.ap-northeast-2.amazonaws.com/mellerikat/release/ai-packs/base/python:python-3.12",
                    "base_service_api_tag": "python-3.12",
                    "logic_code_uri": f"logic/{api_name}.zip"
                }
            })
        }

        token = read_token_from_file('access_token')  # 토큰 읽기
        headers = {
            "Authorization": f"Bearer {token}"
        }

        # `with` 문을 사용하여 파일을 열고 닫기
        zip_filename = f'{api_name}.zip'
        with open(zip_filename, 'rb') as file:
            files = {'aipack_file': (zip_filename, file, 'application/zip')}

            response = requests.post(register_apply_uri, data=data, files=files, headers=headers)

            if response.status_code == 200:
                response_data = response.json()
                name = response_data['name']
                creator = response_data['creator']
                created_at_raw = response_data['created_at']

                versions = response_data['versions']
                version_info = []
                for version in versions:
                    version_num = version['version_num']

                result = (
                    f"Registration Successful!\n"
                    "------------------------------------"
                    f"Name: {name}\n"
                    f"Creator: {creator}\n"
                    f"Created At: {created_at_raw}\n"
                    f"Versions: {version_num}\n"
                    "------------------------------------"
                )

                print(result)

                medatadata_path = os.path.join(settings.workspace, 'metadata.json')

                with open(medatadata_path, 'w') as f:
                    json.dump(data, f, indent=4)

            else:
                raise Exception(f"Request failed: {response.status_code}, {response.text}")

def __update(args): # body 부분 수정필요
    workspace_id = check_ws(args.workspace)

    ### service ID 읽기 ###
    register_list_url = f"{LCC_URL}/api/v1/workspaces/{workspace_id}/aipacks"
    token = read_token_from_file('access_token')

    headers = {
        "Authorization": f'Bearer {token}',
        "Content-Type": "application/json"
    }
    response = requests.get(register_list_url, headers=headers)

    if response.status_code == 200:
        response_data = response.json()
        print(response_data)
        api_names = [[solution['name'], solution['id'], solution['last_version']] for solution in response_data['solutions']]
        #api_versions = [ solution['versions'] for solution in response_data['solutions']]
        solution_id = None
        for i in range(len(api_names)):
            if args.name==api_names[i][0]:
                solution_id = api_names[i][1]
                ai_pack_version = api_names[i][2]
        if solution_id == None :
            raise ValueError("Please check service api name !!")

        zip_current_directory(f'{args.name}_v{ai_pack_version}.zip', exclude_files=['.env', '.token', '.venv'])
        files = {'files': open(f'{args.name}_v{ai_pack_version}.zip', 'rb')}

        solution_version_creation_info = {
            "data": files
        }

        ### todo 수정 ###
        update_url = f"{LCC_URL}/api/v1/workspaces/{workspace_id}/aipacks/{solution_id}/versions"
        response = requests.post(update_url, json=files, headers=headers)

        if response.status_code == 200:
            print(response.json())
        else:
            raise Exception(f"Request failed: {response.status_code}, {response.text}")

    else:
        print("Failed:", response.status_code, response.text)

################# deploy #################

def __deploy(args):
    # 최신 버전을 default로 하고 입력으로 받는 경우에만 최신 버전 사용
    workspace_id = check_ws(args.workspace)
    token = read_token_from_file('access_token')
    headers = {
        "Authorization": f'Bearer {token}',
        "Content-Type": "application/json"
    }
    deployments = "deployments"

    medatadata_path = os.path.join(settings.workspace, 'metadata.json')
    with open(medatadata_path, 'r') as f:
        data = json.load(f)
        metadata_dict = json.loads(data["metadata_json"])

    # alm deploy list
    if args.list and not any([args.get, args.update, args.delete]):
        deploy_list_url = f"{LCC_URL}/api/v1/{workspace_id}/{deployments}"

        # POST 요청 보내기
        response = requests.get(deploy_list_url, headers=headers)
        # 결과 출력
        if response.status_code == 200:
            print('Deployed API List:', response.json())
        else:
            print('Failed to get the API list:', response.status_code, response.text)

    # alm deploy get
    elif args.get and not any([args.list, args.update, args.delete]):

        deploy_get_url = f"{LCC_URL}/api/v1/{workspace_id}/{deployments}"
        headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
        }

        # POST 요청 보내기
        stream_list = requests.get(deploy_get_url, headers=headers)

        #todo 여기서 stream_list 처리하기 args.name으로 받아서 stream_id 얻어와야할듯

        deploy_get_aipack_url = f"{LCC_URL}/api/v1/{workspace_id}/{deployments}{stream_id}"
        response = requests.get(deploy_get_aipack_url, headers=headers)
        # 응답 처리
        if response.status_code == 200:
            print("Success:", response.json())
        else:
            print("Error:", response.status_code, response.text)

    # alm deploy update
    elif args.update and not any([args.list, args.get, args.delete]):
        print("deploy_update hello")

    # alm deploy delete
    elif args.delete and not any([args.list, args.get, args.update]):
        deploy_list_url = f"{LCC_URL}/api/v1/{workspace_id}/{deployments}"

        # POST 요청 보내기
        stream_list = requests.get(deploy_list_url, headers=headers)

        #todo 여기서 stream_list 처리하기 args.name으로 받아서 stream_id 얻어와야할듯

        deploy_get_aipack_url = f"{LCC_URL}/api/v1/{workspace_id}/{deployments}/{stream_id}"
        response = requests.delete(deploy_get_aipack_url, headers=headers)
        # 응답 처리
        if response.status_code == 200:
            print("Success:", response.json())
        else:
            print("Error:", response.status_code, response.text)

    # alm deploy
    else :
        register_list_url = f"{LCC_URL}/api/v1/workspaces/{workspace_id}/aipacks"
        response = requests.get(register_list_url, headers=headers)
        # todo default 버전을 1로? 아니면 가장 마지막 버전으로?
        if response.status_code == 200:
            response_data = response.json()
            api_names = [[solution['name'], solution['id']] for solution in response_data['solutions']]
            api_versions = [ solution['versions'] for solution in response_data['solutions']]

            sol_version_id = None
            solution_id = None
            for i in range(len(api_names)):
                # 현재 등록한 이름과 비교
                if api_names[i][0] == args.name:
                    solution_id = api_names[i][1]
                    sol_version_id = api_versions[i][0]['id']
                    solution_version = 'v' + str(api_versions[i][0]['version_num'])
            if solution_id == None :
                raise ValueError("Please check service api name !!")

        else :
            print("Error:", response.status_code, response.text)

        #todo solution version 불러오기
        deploy_create_url = f"{LCC_URL}/api/v1/{workspace_id}/{deployments}"

        # todo version id 잡기
        data = {
            "name": args.name,
            "version_name" : solution_version,
            "solution_version_id": sol_version_id
        }
        response = requests.post(deploy_create_url, headers=headers, json=data)

        # 응답 처리
        if response.status_code == 200:
            print("Success:", response.json())
        else:
            print("Error:", response.status_code, response.text)
            ### register delete url ###

##################### Activate #####################
def __activate(args):
    workspace_id = check_ws(args.workspace)

    # Bearer 토큰이 필요할 경우 헤더에 추가
    token = read_token_from_file('access_token')
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    medatadata_path = os.path.join(settings.workspace, 'metadata.json')
    with open(medatadata_path, 'r') as f:
        data = json.load(f)
        metadata_dict = json.loads(data["metadata_json"])

    deployments = "deployments"
    # activate list
    if args.list and not any([args.get]):
        deploy_create_url = f"{LCC_URL}/api/v1/{workspace_id}/{deployments}"
        # Bearer 토큰이 필요할 경우 헤더에 추가
        response = requests.get(deploy_create_url, headers=headers)

        # todo stream id 찾도록 수정
        if response.status_code == 200:
            response_data = response.json()
            api_names = [[solution['name'], solution['id']] for solution in response_data['stream']]

            stream_id = None
            for i in range(len(api_names)):
                if args.service_api_name==api_names[i][0]:
                    stream_id = api_names[i][1]
            if solution_id == None :
                raise ValueError("Please check service api name !!")

        activate_list_url = f"{LCC_URL}/api/v1/{workspace_id}/{deployments}/{stream_id}/aactivation"

        # POST 요청 보내기
        response = requests.get(activate_list_url, headers=headers)
        # 응답 처리
        if response.status_code == 200:
            print("Success:", response.json())
        else:
            print("Error:", response.status_code, response.text)

    # activate gets
    elif args.get and not any([args.list]):
        deploy_create_url = f"{LCC_URL}/api/v1/{workspace_id}/{deployments}"
        response = requests.get(deploy_create_url, headers=headers)

        # todo stream id 찾도록 수정
        if response.status_code == 200:
            response_data = response.json()
            api_names = [[solution['name'], solution['id']] for solution in response_data['stream']]

            stream_id = None
            for i in range(len(api_names)):
                if args.service_api_name==api_names[i][0]:
                    stream_id = api_names[i][1]
            if solution_id == None :
                raise ValueError("Please check service api name !!")

        activate_list_url = f"{LCC_URL}/api/v1/{workspace_id}/{deployments}/{stream_id}/aactivation"

        # POST 요청 보내기
        response_stream_his = requests.get(activate_list_url, headers=headers)
        # 응답 처리
        if response_stream_his.status_code == 200:
            response_stream_hi_data = response_stream_his.json()
            # todo stream_his 구하는 로직 필요
            stream_his_id = "jj"
            activate_get_url = f"{LCC_URL}/api/v1/activations/{stream_his_id}"
            # POST 요청 보내기
            response = requests.get(activate_get_url, headers=headers)
            # 응답 처리
            if response.status_code == 200:
                print("Success:", response.json())
            else:
                print("Error:", response.status_code, response.text)

        else:
            print("Error:", response_stream_his.status_code, response_stream_his.text)
    # activate
    else :
        deploy_create_url = f"{LCC_URL}/api/v1/{workspace_id}/{deployments}"
        # Bearer 토큰이 필요할 경우 헤더에 추가
        response = requests.get(deploy_create_url, headers=headers)

        # todo stream id 찾도록 수정
        if response.status_code == 200:
            response_data = response.json()
            print(response_data)
            api_names = [[solution['name'], solution['id'], solution['solution_version_id']] for solution in response_data['streams']]

            solution_id = None
            stream_id = None
            for i in range(len(api_names)):
                print(args.name, api_names[i][0])
                if args.name==api_names[i][0]:
                    stream_id = api_names[i][1]
                    solution_id = api_names[i][2]
                    # ㅎ해당 내용 찾으면 break
                    break
            if stream_id == None :
                raise ValueError("Please check service api name !!")
        else :
            print("Error:", response.status_code, response.text)

        activate_url = f"{LCC_URL}/api/v1/{workspace_id}/deployments/{stream_id}/activations"
        env_dict = dotenv_values('.env') # type: OrderedDict

        # todo data 구조 확인하기
        streamhistory_info = {
            "stream_history_creation_info" : {
                "train_resource_name" : "standard",
                "metadata_json" : metadata_dict,

            },
            "replica": 1,
            "secret" : json.dumps(env_dict)

        }

        # POST 요청 보내기
        response = requests.post(activate_url, headers=headers, json = streamhistory_info)
        # 응답 처리
        if response.status_code == 200:
            print("Success:", response.json())
        else:
            print("Error:", response.status_code, response.text)

def __deactivate(args):
    workspace_id = check_ws(args.workspace)

    # Bearer 토큰이 필요할 경우 헤더에 추가
    token = read_token_from_file('access_token')
    print(f'Successfully authenticated. Token: {token}')
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    deploy_create_url = f"{LCC_URL}/api/v1/{workspace_id}/{deployments}"
    # Bearer 토큰이 필요할 경우 헤더에 추가
    response = requests.get(deploy_create_url, headers=headers)

    # todo stream id 찾도록 수정
    if response.status_code == 200:
        response_data = response.json()
        api_names = [[solution['name'], solution['id']] for solution in response_data['stream']]

        solution_id = None
        for i in range(len(api_names)):
            if args.service_api_name==api_names[i][0]:
                stream_id = api_names[i][1]
        if solution_id == None :
            raise ValueError("Please check service api name !!")

    activate_list_url = f"{LCC_URL}/api/v1/{workspace_id}/{deployments}/{stream_id}/aactivation"

    # POST 요청 보내기
    response_stream_his = requests.get(activate_list_url, headers=headers)
    # 응답 처리
    if response_stream_his.status_code == 200:
        response_stream_hi_data = response_stream_his.json()
        # todo stream_his 구하는 로직 필요
        stream_his_id = "jj"
        activate_delete_url = f"{LCC_URL}/api/v1/activations/{stream_his_id}"
        # POST 요청 보내기
        response = requests.get(activate_delete_url, headers=headers)
        # 응답 처리
        if response.status_code == 200:
            print("Success:", response.json())
        else:
            print("Error:", response.status_code, response.text)

    else:
        print("Error:", response_stream_his.status_code, response_stream_his.text)

##################### get info #####################

def __get_info(args):
    # alm get workspace_info
    # alm get image_info
    # alm get version

    token = read_token_from_file('access_token')
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # workspace info
    if args.workspace_info and not any([args.image_info, args.version]):
        workspace_id = check_ws(args.workspace_name)

        workspace_info_url = f"{LCC_URL}/api/v1/workspaces/{workspace_id}/info"

        # POST 요청 보내기
        workspace_info = requests.get(workspace_info_url, headers=headers)

        # 응답 처리
        if workspace_info.status_code == 200:
            print("Workspace info:", workspace_info.json())
        else:
            print("Error:", workspace_info.status_code, workspace_info.text)

    # image list
    elif args.image_info and not any([args.workspace_info, args.version]):
        version_rul = f"{LCC_URL}/api/v1/images/info"
        # Bearer 토큰이 필요할 경우 헤더에 추가

        # POST 요청 보내기
        images_list = requests.get(version_rul, headers=headers)

        if images_list.status_code == 200:
            print("Base images:", images_list.json())
        else:
            print("Error:", images_list.status_code, images_list.text)

    # version check
    else :
        version_rul = f"{LCC_URL}/api/v1/version"
        # POST 요청 보내기
        aic_version = requests.get(version_rul, headers=headers)
        if aic_version.status_code == 200:
            aic_version = aic_version.json()
            print("AIC Version: ", aic_version['aic']['versions'][0]['ver_str'])
        else:
            print("Error:", aic_version.status_code, aic_version.text)

def main():

    acli = ALC(LCC_URL, settings)

    if len(sys.argv) > 1:
        if sys.argv[-1] in ['-v', '--version']:
            print(__version__)
            return
        if sys.argv[1] in ['-h', '--help']:
            pass
        elif sys.argv[1] not in ['api', 'login', 'register', 'update', 'deploy', 'activate', 'deactivate', 'get']:  # v1 호환
            # ['run', 'history', 'register', 'update', 'delete', 'template', 'example', 'api', 'provision_create', 'login', 'apilist', 'provision_description', 'provision_delete']:  # v1 호환
            sys.argv.insert(1, 'api')
    else:
        sys.argv.insert(1, 'api')

    parser = argparse.ArgumentParser('alm', description='ALO(AI Learning Organizer)')
    parser.add_argument('-v', '--version', action='version', version=__version__)
    subparsers = parser.add_subparsers(dest='command')

    # ALO-LLM
    cmd_api = subparsers.add_parser('api', description='')

    # Auth
    cmd_login = subparsers.add_parser('login', description='Login')
    cmd_login.add_argument('--id', help='User id')
    cmd_login.add_argument('--password', help='User password')

    # Register (Solution)
    cmd_register = subparsers.add_parser('register', description='Register Service API')
    cmd_register.add_argument('-n', '--name', default = None, help='Service API name')
    cmd_register.add_argument('-w', '--workspace', default = None, help='Workspace name')
    cmd_register.add_argument('-i', '--image', default="python 3.12", help='Image info')
    cmd_register.add_argument('-v', '--version', default=None, help='Service API version')
    cmd_register.add_argument('-l', '--list', action="store_true", default = None, help='register list flag')
    cmd_register.add_argument('-u', '--update', type=str, default=None, help='register delete flag')
    # cmd_register.add_argument('-d', '--delete', action="store_true", default = None, help='register delete flag')
    cmd_register.add_argument('-d', '--delete', type=str, default=None, help='register delete flag')

    # cmd_register_list = subparsers.add_parser('register_list', description='Get list of Service API')
    # cmd_register_list.add_argument('-w', '--workspace' , default = None, help='Workspace name')

    cmd_register_update = subparsers.add_parser('update', description='Describe provision status')
    cmd_register_update.add_argument('-n', '--name', default=None, help='workspace name')
    cmd_register_update.add_argument('-w', '--workspace', default=None, help='workspace name')

    # cmd_register_delete = subparsers.add_parser('register_delete', description='Delete registered Service API')
    # cmd_register_delete.add_argument('-n', '--name', required=True, help='Service API name')
    # cmd_register_delete.add_argument('-w', '--workspace', default=None, help='workspace name')

    # cmd_register_version_delete = subparsers.add_parser('register_version_delete', description='Delete registered Service API')
    # cmd_register_version_delete.add_argument('-n', '--name', required=True, help='Service API name')
    # cmd_register_version_delete.add_argument('-w', '--workspace', default=None, help='workspace name')
    # cmd_register_version_delete.add_argument('-v', '--version', default=None, help='workspace name')

    # Deploy (Stream)
    cmd_deploy = subparsers.add_parser('deploy', description='Provision and deploy Service API')
    cmd_deploy.add_argument('-n', '--name', default=None, help='Service API name')
    cmd_deploy.add_argument('-w', '--workspace', default=None, help='workspace name')
    cmd_deploy.add_argument('-v', '--version', default=None, help='version name')
    cmd_deploy.add_argument('-l', '--list', action="store_true", default = None, help='register list flag')
    cmd_deploy.add_argument('-g', '--get', action="store_true", default = None, help='register list flag')
    cmd_deploy.add_argument('-d', '--delete', type=str, default=None, help='register delete flag')
    # cmd_deploy.add_argument('-d', '--delete', action="store_true", default = None, help='register list flag')
    cmd_deploy.add_argument('-u', '--update', action="store_true", default = None, help='register list flag')

    # cmd_deploy_create = subparsers.add_parser('deploy_create', description='Provision and deploy Service API')
    # cmd_deploy_create.add_argument('-n', '--name', required=True, help='Service API name')
    # cmd_deploy_create.add_argument('-w', '--workspace', default=None, help='workspace name')
    # cmd_deploy_create.add_argument('-v', '--version', default=None, help='version name')

    # cmd_deploy_list = subparsers.add_parser('deploy_list', description='Get list of Service API')
    # cmd_deploy_list.add_argument('-w', '--workspace', default=None, help='workspace name')

    # cmd_deploy_get = subparsers.add_parser('deploy_get', description='Get list of Service API')
    # cmd_deploy_get.add_argument('-w', '--workspace', default=None, help='workspace name')
    # cmd_deploy_get.add_argument('-n', '--name', default=None, help='Service API name')

    # cmd_deploy_delete = subparsers.add_parser('deploy_delete', description='Delete provision of Service API')
    # cmd_deploy_delete.add_argument('-n', '--name', required=True, help='Service API name')
    # cmd_deploy_delete.add_argument('-w', '--workspace', default=None, help='workspace name')

    # cmd_deploy_update = subparsers.add_parser('deploy_update', description='Delete provision of Service API')
    # cmd_deploy_update.add_argument('-n', '--name', required=True, help='Service API name')
    # cmd_deploy_update.add_argument('-w', '--workspace', default=None, help='workspace name')

    # Activate (StreamHistory)
    cmd_activate = subparsers.add_parser('activate', description='Describe provision status')
    cmd_activate.add_argument('-n', '--name', default=None,help='Service API name')
    cmd_activate.add_argument('-w', '--workspace', default=None, help='workspace name')
    cmd_activate.add_argument('-s', '--spec', default=None, help='spec info')
    cmd_activate.add_argument('-r', '--replicas', default=None, help='number of replicas')
    cmd_activate.add_argument('-l', '--list', action="store_true", default = None, help='register list flag')
    cmd_activate.add_argument('-g', '--get', action="store_true", default = None, help='register list flag')

    cmd_deactivate = subparsers.add_parser('deactivate', description='Describe provision status')
    cmd_deactivate.add_argument('-n', '--name', default=None,help='Service API name')
    cmd_deactivate.add_argument('-w', '--workspace', default=None, help='workspace name')

    # cmd_activate_list = subparsers.add_parser('activate_list', description='Describe provision status')
    # cmd_activate_list.add_argument('-n', '--name', required=True, help='Service API name')
    # cmd_activate_list.add_argument('-w', '--workspace', default=None, help='workspace name')

    # cmd_activate_get = subparsers.add_parser('activate_get', description='Describe provision status')
    # cmd_activate_get.add_argument('-n', '--name', required=True, help='Service API name')
    # cmd_activate_get.add_argument('-w', '--workspace', default=None, help='workspace name')

    # cmd_deactivate = subparsers.add_parser('deactivate', description='Describe provision status')
    # cmd_deactivate.add_argument('-n', '--name', required=True, help='Service API name')
    # cmd_deactivate.add_argument('-w', '--workspace', default=None, help='workspace name')

    cmd_get = subparsers.add_parser('get', description='Describe provision status')
    cmd_get.add_argument('-wn', '--workspace_name', default=None, help='workspace name')
    cmd_get.add_argument('-w', '--workspace_info', action="store_true", default=None, help='number of replicas')
    cmd_get.add_argument('-i', '--image_info', action="store_true", default = None, help='register list flag')
    cmd_get.add_argument('-v', '--version', action="store_true", default = None, help='register list flag')
    # # Workspace
    # cmd_workspaces_info = subparsers.add_parser('workspace_info', description='Describe provision status')
    # cmd_workspaces_info.add_argument('-w', '--workspace', default=None, help='workspace name')

    # # Misc
    # cmd_images = subparsers.add_parser('image_info', description='init of ALO-LLM')

    # cmd_version = subparsers.add_parser('version', description='init of ALO-LLM')

    args = parser.parse_args()
    # alm register
    # alm register -l, --list
    # register -d, --delete, -v
    # update
    # deploy -n, -v
    # deploy -l, --list
    # deploy -g, --get
    # deploy -d, --delete
    # activate
    # activate -l, --list
    # activate -g, --get
    # deactivate
    # alm get workspace_info
    # alm get image_info
    # alm get version
    commands = {
                'api': acli.api,
                'login' : acli.login,
                'register' : acli.register,
                'update': __update,
                'deploy': acli.deploy,
                'activate': acli.activate,
                'deactivate': acli.deactivate,
                'get': __get_info
                }
    commands[args.command](args)

