import time

import requests
import os

from token_yielder.errors import ErrorObjects



class CreateRequestTask:
    '''
        Base class to initiate pre-requisites and send request to
        external api. base_url, consumer_id and consumer_secret are mandatory fields
        whereas others are optional and mapped to default value.
        User can seperate base_url and router of the api end point and pass them as arguments
        or the whole url as base_url, which gives more dynamic options.
        timeout is configured to 5 seconds as default which can be overidden by run time parameter
        headers are default and payload will be formed in the constructor.
    '''
    def __init__(self, base_url: str, router: str, consumer_id: str, consumer_secret: str, timeout: int = 5):
        self.url = base_url
        self.router = router if router else ""
        self.consumer_id = consumer_id
        self.consumer_secret = consumer_secret
        self.accept_header = {'Content-Type': 'application/x-www-form-urlencoded'}
        self.payload = {
            "client_id": self.consumer_id,
            "client_secret": self.consumer_secret,
            "grant_type": "client_credentials"
        }
        self.timeout = timeout

    async def rotate_function(self, variable_name: str='Token', interval: int=36000, token_name: str='access_token'):
        '''
            async rotate_function is used to generate token in specified interval.
            by default it's configured to 10 hours (60 * 60 * 10) which can be
            overidden by user if needed. Similarly variable name for the token
            is set to Token which also can be overridden by user so the token can
            be accessed by application through environment variable.
            this has exception handlers which captures if there's any abnormality
            and raises custom error object with more info which makes it easy to interpret.

            Run this function using asyncio.run() method so it runs in the backend.
            Sample: asyncio.run(rotate_function)
        '''
        start = True
        while start:
            try:
                response = requests.post(self.url+self.router, headers=self.accept_header, data=self.payload, timeout=self.timeout)
                if response.status_code == 200:
                    data = response.json()
                    os.environ[variable_name] = data[token_name]
                else:
                    start = False
                    raise ErrorObjects(response.content, response.status_code)
                time.sleep(interval)
            except Exception as e:
                raise ErrorObjects(data=str(e))
            except ErrorObjects as e:
                start = False
                raise e


    def generate_token(self, variable_name: str='Token', store: bool=False, token_name: str='access_token'):
        '''
            generate_token function is used to just generate token, but it has two options
            User can use this either store the token in environment variable or just return the token
            by default this function returns the token which is tracked by store boolean.
            If user wants to store in environment then this boolean needs to be set to True
            which can be done in runtime. Similar to rotate_function this also has custom error
            object handles unexpected errors.
        '''
        try:
            response = requests.post(self.url+self.router, headers=self.accept_header, data=self.payload, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                if not store:
                    return data[token_name]
                os.environ[variable_name] = data[token_name]
            else:
                raise ErrorObjects(response.content, response.status_code)
        except Exception as e:
            raise ErrorObjects(data=str(e))
        except ErrorObjects as e:
            raise e