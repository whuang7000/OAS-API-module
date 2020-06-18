# Vysioneer Takehome Challenge (Attempt 2)

### Setup
1. Clone this repository
2. Create a virtual environment
3. Run `pip install requirements.txt`
4. run `python myapp.py`
5. In a separate terminal and in the same directory, run `pytest tests`
6. You can use curl or an application like Postman to test different URL endpoints.

### Notes and Design Choices
First off, thank you for providing me with skeleton code and guidance. Before your help, I think I was struggling the most with thinking of a way to route all requests through a central function. I did not know you could use `app.route('/<path:req_path>'` for that. For my design choices, I changed some things about the skeleton code. First, I commented out some lines and changed a few to get the server to actually run and for testing purposes. Initially, you provided me with 5 TODO functions: `path_to_regex`, `parse_body`, `parse_parameters`, `validate_response`, and `validate_request`. I decided to split up `validate_request` into `validate_body` and `validate_parameters` and got rid of the parsing functions because Flask requests automatically parse them into Python dictionaries for you. I also included two util functions to help validate the OAS components: `validate_component` and `get_component`. The hardest part of this entire implementation was definitely handling nested components (Pet objects can have Tag objects) and figuring out the regex for handling in-path parameters.

For testing purposes, I return early from the handler if `validate_body` and `validate_parameters` pass because the business logic python functions that the endpoints route to aren't implemented, so it will throw an error, which hinders my validation testing. Consequently, I could not test `validate_response` very thorougly. I refactored the tests from my last attempt, but due to time constraints, they aren't completely thorough, but they do ensure basic correctness. (All of them should pass)

### Improvements and Flaws
I couldn't figure out how to pick which response error code to return, so I always return error code 400 when a validation error occurs. This is because each method in the YAML file returns a different status code for different errors (i.e it's not very consistent), so I don't think it is very possible to dynamically choose which error code to return. Also, I didn't implement the `default` OAS field checking because my implementation would not have been very elegant: it would've been a long series of nested `if` statements. Also, for simplicity purposes, I only implemented `integer`, `string`, `array`, `bool`, and `number` in the OAS type specification even though there are more such as `datetime` and `binary`.

### Conclusion
Sorry for misunderstanding the takehome challenge. Although it is unfortunate that I got it wrong the first time, I actually leaned a lot more this time through, and hopefully it is correct. Thank you for taking the time to review my takehome challenge!