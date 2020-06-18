import re
import yaml
import logging
import json
from flask import request, make_response

TYPES = {
  'integer': int,
  'string': str,
  'boolean': bool,
  'number': float,
  'array': list
}

class MyOpenAPI:
  operation_dict = {}
  def __init__(self, flask, spec_path):
    self.app = flask(__name__)
    spec_str = ""
    with open(spec_path, 'r') as fp:
      spec_str = fp.read()
    spec_dict = yaml.load(spec_str)

    @self.app.route('/<path:req_path>', methods=['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    def request_handler(req_path):
      for (path_pattern, path_spec) in spec_dict['paths'].items():
        regex = re.compile(path_to_regex(path_pattern))
        match = regex.search(request.path)
        if match is None:
          continue
        method = request.method.lower()
        if method not in path_spec:
          return ("Method not allowed", 405)
        method_spec = path_spec[method]
        operationId = method_spec['operationId']
        # if operationId not in self.operation_dict:
        #   return ("Not implemented", 501)
        parameters, param_validation = validate_parameters(method_spec, path_pattern, request)
        if param_validation is not None:
          return param_validation


        body, body_validation = validate_body(method_spec, spec_dict, request)
        if body_validation is not None:
          return body_validation

        return make_response("Success.", 200)

        implementation = self.operation_dict[operationId]

        response = implementation(request, body, parameters)

        response_validation = validate_response(method_spec, spec_dict, response)
        if response_validation is not None:
          return response_validation

        return response


  def operationId(self, operationId):
    def decorator(fn):
      self.operation_dict[operationId] = fn
    return decorator

def path_to_regex(path_pattern):
  '''
  This function will take a YAML path and return regex.
  Example:
    path_pattern: pet/{petId}/uploadImage?param1=arg1&param2=arg2
    returned regex: pet/(\\S)/uploadImage$
  '''
  # Remove query parameters
  stripped = path_pattern.split("?")[0]

  # Replace curly braces with regex expression for any alphanumeric
  regex = re.sub(r"\s*{.*}\s*", r'(\\S)', stripped)

  # Add $ to match at end of path
  return regex + '$'

def validate_body(method_spec, spec_dict, request):
  '''
  This function is split up into two sections. One section deals with application/json bodies and the other deals
  with other forms of data such as multipart/form-data and x-www-form-urlencoded. All JSON bodies contained a ref in the given YAML file.
  This function is written under the assumption that all JSON requests must have an object ref.

  Returns the parsed body and a response.
  '''
  spec_body = method_spec.get('requestBody')
  request_body = request.get_data()
  
  if spec_body is None:
    if not request_body:
      return None, None
    else:
      # Request has body when it shouldn't
      return None, make_response("Invalid extra parameters.", 400)

  if request.is_json and "application/json" not in spec_body['content'] or request.is_json == False and "application/json" in spec_body['content']:
    return None, make_response("Datatype mismatch.", 400)

  # application/json data
  if request.is_json:
    # json requests always have object refs in the given yaml
    ref = spec_body['content']['application/json']['schema'].get('$ref')
    component = get_component(spec_dict, ref)
    if component is None:
      return None, make_response("Schema does not exist.", 400)
    
    request_dict = request.get_json()
    err = validate_component(spec_dict, component, request_dict)
    if err is not None:
      return None, err

  # other data forms
  else:
    # ref in body
    temp = spec_body['content']
    ref = spec_body['content'][list(temp.keys())[0]]['schema'].get('$ref')
    if ref:
      component = get_component(spec_dict, ref)
      if component is None:
        return None, make_response("Schema does not exist.", 400)
      
      request_dict = request.form
      err = validate_component(spec_dict, component, request_dict)
      if err is not None:
        return None, err

    # no ref in body
    else:
      temp = spec_body['content']
      fields = spec_body['content'][list(temp.keys())[0]]['schema']['properties']
      request_dict = request.form
      for name, props in fields.items():
        arg = request_dict.get(name)
        if arg is None:
          if props.get('required', False) == True:
            return None, make_response("Missing field.", 400)
          else:
            continue
        cast = TYPES[props['type']]
        try:
          casted_param = cast(arg)
        except ValueError:
          return None, make_response("Invalid field type.", 400)

        #Enforce enum
        enum = props.get('enum')
        if enum is not None and casted_param not in enum:
          return None, make_response("Enumeration error.", 400)

  #request_dict is already a python dict, no extra parsing needed.
  return request_dict, None

def validate_parameters(method_spec, path_pattern, request):
  '''
  This function is split up into two sections. The first section handles in-path parameters and the second section
  handles query parameters.
  '''
  spec_params = method_spec.get('parameters')
  if spec_params is None:
    if len(request.args) == 0:
      return None, None
    else:
      #Request has parameters when it shouldn't
      return None, make_response("Invalid extra parameters.", 400)

  replaced = re.sub(r"\s*{.*}\s*", r'(\\S)', path_pattern)
  search = re.search(replaced, request.path)
  in_path_params = ()
  if search:
    in_path_params = iter(search.groups()) #search.groups() is a tuple of the in-path params created from regex searching the request path

  query_params = request.args
  in_path_params_dict = {}

  #in-path parameter handling
  for param in spec_params:
    if param['in'] == 'path':
      try:
        arg = next(in_path_params)
      except StopIteration:
        #No more in-path parameters in the iterator
        if param.get('required', False) == True:
          return None, make_response("Missing parameters.", 400)
        else:
          continue #continue the loop if the parameter is not found AND not required
      
      cast = TYPES[param['schema']['type']]
      try:
        casted_param = cast(arg)
      except ValueError:
        return None, make_response("Invalid parameter type.", 400)
      in_path_params_dict[param['name']] = casted_param
      #insert some business logic with the casted param

    #query parameter handling
    elif param['in'] == 'query':
      arg = query_params.get(param['name'])
      if arg is None and param.get('required', False) == True:
        return None, make_response("Missing parameters.", 400)
      cast = TYPES[param['schema']['type']]
      try:
        casted_param = cast(arg)
        #Enforce array validation by validating each item
        if cast == list:
          arg = query_params.getlist(param['name'])
          casted_param = cast(arg) 
          item_cast = TYPES[param['schema']['items']['type']]
          for i in range(len(casted_param)):
            casted_param[i] = item_cast(casted_param[i])

            #Enforce enum
            enum = param['schema']['items'].get('enum')
            if enum is not None and casted_param[i] not in enum:
              return None, make_response("Enumeration error.", 400)

      except ValueError:
        return None, make_response("Invalid parameter type.", 400)
      #Do some business logic with the casted param

    combined_args = {**in_path_params_dict, **query_params} #Python 3.5 syntax to combine two dictionaries
    return combined_args, None

def validate_response(method_spec, spec_dict, response):
  '''
  Validates a response object. All response objects in the YAML had JSON content if it had any content. This
  function is written under that assumption. All JSON bodies contained a ref in the given YAML file.
  This function is written under the assumption that all JSON responses must have an object ref.
  '''
  spec_body = method_spec['responses'][response.status_code]

  # No content, no validation needed
  if len(spec_body['content']) == 0:
    return None

  response_dict = response.get_json()
  ref = spec_body['content']['application/json']['schema'].get('$ref')
  component = get_component(spec_dict, ref)
  if component is None:
    return make_response("Schema does not exist.", 400)

  err = validate_component(spec_dict, component, response_dict)
  if err is not None:
    return err

  return None

def validate_component(spec, component, request_dict):
  '''
  Validates an object ref to a component in the YAML file. 
  '''
  required_fields = component.get('required', [])
  for name, props in component['properties'].items():
    arg = request_dict.get(name)
    if arg is None:
      if name in required_fields:
        return make_response("Missing field.", 400)
      else:
        continue

    # Nested ref handling. For example, a Pet object can have a Tag object associated with it.
    ref = props.get('$ref')
    if ref:
      nested_component = get_component(spec, ref)
      err = validate_component(spec, nested_component, arg) #recursive call 
      if err is not None:
        return make_response("Validation error.", 400)
    
    cast = TYPES[props['type']]

    #Python allows you to cast floats as ints, so need special case
    if cast == int and type(arg) == float:
      return make_response("Invalid field type.", 400)

    try:
      casted_param = cast(arg)
    except ValueError:
      return make_response("Invalid field type.", 400)

    if cast == list:
      ref = props['items'].get('$ref')    
      for i in range(len(casted_param)):
        # item type of array is an object ref
        if ref:
          nested_component = get_component(spec, ref)
          err = validate_component(spec, nested_component, casted_param[i]) #recursive call
          if err is not None:
            return make_response("Validation error.", 400)

        # item type of array is a primitive type
        else:
          item_cast = TYPES[param['schema']['items']['type']]
          casted_param[i] = item_cast(casted_param[i])

          enum = param['schema']['items'].get('enum')
          if enum is not None and casted_param[i] not in enum:
            return None, make_response("Enumeration error.", 400)

    return None

def get_component(spec, ref_str):
  '''
  Gets a component from the YAML spec.
  '''
  spl = ref_str.split("/")[1:] # example: ref_str='#/components/schemas/Pet' ----> spl=['components','schemas','Pet']
  for s in spl:
    spec = spec.get(s)
    if spec is None: # Schema doesn't exist
      return None
  return spec

