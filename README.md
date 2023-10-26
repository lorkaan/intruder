# Intruder
A Implementation of Burp Intruder that allows for script based automated testing on web parameters

This is an experiment to learn about HTTP Request Automation methods and Dictionary Attacks in the Cybersecurity field.

Ideally, this project can be used in conjunction with the [HTTPSpider](https://www.github.com/lorkaan/httpspider) project to improve the discovery process involving links with query parameters.

# Disclaimer
Please do not use this against websites that you do not own or do not have permission to test/attack.

# Testing
Due to the potential legal issues when testing this project, I have provided a [Test Server](https://www.github.com/lorkaan/testenvintruder) to use instead.

# Notes
Currently, only type that is supported is Sniper (0 in the command as noted in the example). Additionally, Post parameters are not available as yet.

This project is designed primarily as a toolbox third party library to be extended. The ability to use commands via terminals is generally for testing purposes and as a template for more specific usage in the future (eg customizing a test for a given website). This is necessary as the feedback from different websites as to a good or bad command can differ and be independent for each website. The [Test Server](https://www.github.com/lorkaan/testenvintruder) is designed to operate with the current default for "bad" response, which is just an empty string as an HTTP Response.

# Required 
Pipenv
Python 3.9

All subsequent commands listed are assumed to run from the cloned repo

# Setup

```
pipenv shell
pip install
```

This will create a virtual environment and download the required packages

# Run
`pipenv shell` if not already done to change your terminal into the virtual evnironment created during setup

Assuming that the [Test Server](https://www.github.com/lorkaan/testenvintruder) project is running,an Example command is the following:
`python run_injection.py 0 --wordlists ./example/wordlist.txt --delimiter \n --target http://127.0.0.1:5000/gtest?name=pear --get name`

Notes:
- `0` is the type of attack, in this case its a Sniper attack (only one query parameter is to be tested)
- `--wordlists` is a list of files that hold the query values to try, seperated by an optional delimiter (default is newline)
- `--delimiter` is the delimiter to use when reading wordlist files. This example has it set to the default of \n and thus can be omitted safely
- `--target` is the website address to perform the test on
- `--get` is the get parameters to test with (sniper requires just one)
