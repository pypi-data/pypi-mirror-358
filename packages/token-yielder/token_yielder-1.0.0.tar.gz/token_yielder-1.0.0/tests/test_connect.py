import os
from token_yielder.connect import CreateRequestTask

base_url="http://localhost:8000"
router="/postmethod"
consumer_id="125486"
consumer_secret="Nothing"
consumer_secret_wrong="123443"

def test_generate_token():
    test_object = CreateRequestTask(base_url, router, consumer_id, consumer_secret)
    token_obtained = test_object.generate_token()
    assert token_obtained == 'story of black water'

def test_generate_and_store_token():
    test_object = CreateRequestTask(base_url,router,consumer_id,consumer_secret)
    test_object.generate_token(store=True)
    assert os.environ['Token'] == 'story of black water'

def test_failure_generate_token():
    try:
        test_object = CreateRequestTask(base_url=base_url, router=router, consumer_id=consumer_id, consumer_secret=consumer_secret_wrong)
        token_obtained = test_object.generate_token()
        pass
    except Exception as arg:
        assert arg.status == 400