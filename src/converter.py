import json
import os
from jinja2 import Template
from templates import JMETER_TEMPLATE

class Converter:
    def __init__(self):
        self.template = JMETER_TEMPLATE

    def parse_postman(self, collection_path, env_path=None):
        with open(collection_path, 'r', encoding='utf-8') as f:
            collection = json.load(f)
            
        variables = []
        if env_path:
            with open(env_path, 'r', encoding='utf-8') as f:
                env = json.load(f)
                variables = [{'name': v['key'], 'value': v['value']} 
                           for v in env.get('values', [])]
                
        requests = []
        def process_items(items, folder_name=""):
            for item in items:
                if 'item' in item:  # 这是一个文件夹
                    new_folder = f"{folder_name}/{item['name']}" if folder_name else item['name']
                    process_items(item['item'], new_folder)
                elif 'request' in item:  # 这是一个请求
                    req = item['request']
                    url = req['url']
                    
                    # 处���URL
                    if isinstance(url, dict):
                        protocol = url.get('protocol', 'http')
                        if isinstance(url.get('host'), list):
                            domain = '.'.join(url['host'])
                        else:
                            domain = url.get('host', '')
                        port = url.get('port', '')
                        if isinstance(url.get('path'), list):
                            path = '/'.join(url['path'])
                        else:
                            path = url.get('path', '')
                    else:
                        from urllib.parse import urlparse
                        parsed = urlparse(url)
                        protocol = parsed.scheme or 'http'
                        domain = parsed.hostname or ''
                        port = str(parsed.port) if parsed.port else ''
                        path = parsed.path or ''
                    
                    # 处理请求体
                    body = ''
                    if 'body' in req:
                        if req['body'].get('mode') == 'raw':
                            body = req['body'].get('raw', '')
                        elif req['body'].get('mode') == 'formdata':
                            form_data = []
                            for form_item in req['body'].get('formdata', []):
                                form_data.append(f"{form_item['key']}={form_item.get('value', '')}")
                            body = '&'.join(form_data)
                    
                    request_name = item['name']
                    request_data = {
                        'name': request_name,
                        'folder': folder_name,  # 添加文件夹信息
                        'protocol': protocol,
                        'domain': domain,
                        'port': port,
                        'path': path,
                        'method': req['method'],
                        'headers': [{'name': h['key'], 'value': h['value']} 
                                  for h in req.get('header', [])],
                        'body': body
                    }
                    requests.append(request_data)
        
        process_items(collection['item'])
        return {'variables': variables, 'requests': requests}

    def parse_apipost(self, collection_path):
        with open(collection_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("Data structure:", data.keys())
        
        requests = []
        variables = []
        folders = {}  # 存储文件夹信息
        
        def build_folder_structure(items):
            # 先构建文件夹映射
            for item in items:
                if item.get('target_type') == 'folder':
                    folders[item['target_id']] = {
                        'name': item['name'],
                        'parent_id': item.get('parent_id', '0'),
                        'children': []
                    }
        
        def get_folder_path(folder_id):
            # 递归获取完整的文件夹路径
            if folder_id not in folders:
                return ''
            folder = folders[folder_id]
            parent_path = get_folder_path(folder['parent_id'])
            return f"{parent_path}/{folder['name']}" if parent_path else folder['name']
        
        def process_items(items):
            for item in items:
                print(f"Processing item: {item.get('name', 'Unknown')} of type {item.get('target_type', 'Unknown')}")
                
                # 处理 API
                if item.get('target_type') == 'api':
                    try:
                        request = item.get('request', {})
                        parent_id = item.get('parent_id', '0')
                        folder_path = get_folder_path(parent_id)
                        
                        # 处理请求头
                        headers = []
                        if request and 'header' in request:
                            header_params = request['header'].get('parameter', [])
                            for header in header_params:
                                if isinstance(header, dict) and header.get('is_checked', 1) == 1:
                                    headers.append({
                                        'name': header.get('key', ''),
                                        'value': header.get('value', '')
                                    })

                        # 处理请求体
                        body = ''
                        if request and 'body' in request:
                            body_params = request['body'].get('parameter', [])
                            if body_params:
                                body_data = {}
                                for param in body_params:
                                    if isinstance(param, dict) and param.get('is_checked', 1) == 1:
                                        body_data[param.get('key', '')] = param.get('value', '')
                                if body_data:
                                    body = json.dumps(body_data)

                        # 处理 URL
                        url = item.get('url', '')
                        if not url.startswith('http'):
                            url = f"http://localhost{url if url.startswith('/') else f'/{url}'}"
                        
                        from urllib.parse import urlparse
                        parsed = urlparse(url)
                        protocol = parsed.scheme or 'http'
                        domain = parsed.hostname or 'localhost'
                        port = str(parsed.port) if parsed.port else ''
                        path = parsed.path or ''

                        request_name = item['name']
                        request_data = {
                            'name': request_name,
                            'folder': folder_path,  # 使用完整的文件夹路径
                            'method': item.get('method', 'GET'),
                            'protocol': protocol,
                            'domain': domain,
                            'port': port,
                            'path': path,
                            'body': body,
                            'headers': headers
                        }
                        print(f"Adding request: {request_name} in folder: {folder_path}")
                        requests.append(request_data)
                    except Exception as e:
                        print(f"Error processing request {item.get('name', '')}: {str(e)}")

                # 递归处理子项目
                if 'children' in item and item['children']:
                    process_items(item['children'])
                if 'apis' in item and item['apis']:
                    process_items(item['apis'])

        # 开始处理
        if 'apis' in data:
            print(f"Processing {len(data['apis'])} APIs from root")
            # 先构建文件夹结构
            build_folder_structure(data['apis'])
            # 然后处理所有请求
            process_items(data['apis'])
        else:
            print("No 'apis' field found in root")
            process_items(data)
        
        print(f"Total requests processed: {len(requests)}")
        return {'variables': variables, 'requests': requests}

    def convert_to_jmx(self, data, test_plan_name, output_path):
        print(f"Converting {len(data['requests'])} requests to JMX")  # 添加调试信息
        
        # 导入 groupby 过滤器
        from jinja2 import Environment, BaseLoader
        env = Environment(loader=BaseLoader())
        template = env.from_string(self.template)
        
        # 按文件夹分组处理请求
        requests_by_folder = {}
        for request in data['requests']:
            folder = request.get('folder', '')
            if folder not in requests_by_folder:
                requests_by_folder[folder] = []
            requests_by_folder[folder].append(request)
        
        # 渲染模板
        jmx_content = template.render(
            test_plan_name=test_plan_name,
            variables=data['variables'],
            folders=requests_by_folder.items()  # 传递分组后的数据
        )
        
        output_file = os.path.join(output_path, f"{test_plan_name}.jmx")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(jmx_content)
        
        print(f"JMX file saved to: {output_file}")  # 添加调试信息
        return output_file

    def parse_request(self, request):
        # 处理请求体
        body = ''
        if 'body' in request:
            if request['body'].get('mode') == 'raw':
                body = request['body'].get('raw', '')
            elif request['body'].get('mode') == 'formdata':
                form_data = []
                for form_item in request['body'].get('formdata', []):
                    form_data.append(f"{form_item['key']}={form_item.get('value', '')}")
                body = '&'.join(form_data)

    def parse_url(self, url):
        if isinstance(url, dict):
            protocol = url.get('protocol', 'http')
            domain = '.'.join(url['host']) if isinstance(url.get('host'), list) else url.get('host', '')
            port = url.get('port', '')
            path = '/'.join(url['path']) if isinstance(url.get('path'), list) else url.get('path', '')
            return protocol, domain, port, path
        else:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.scheme, parsed.hostname, parsed.port, parsed.path

def convert_to_jmx(source_type, collection_path, env_path, test_plan_name, output_path):
    converter = Converter()
    
    if source_type == 'postman':
        data = converter.parse_postman(collection_path, env_path)
    else:
        data = converter.parse_apipost(collection_path)
        
    return converter.convert_to_jmx(data, test_plan_name, output_path)
