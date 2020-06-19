import requests


def test_api(address, params):

    response_a = requests.get(address, params=params)

    if response_a.status_code == 200:

        return response_a.content

    else:

        return response_a.status_code


if __name__ == '__main__':

    # Change api_ip accordingly

    api_ip = 'http://34.87.87.72:5000/api/v1/resources/'
    api_ip = 'http://127.0.0.1:5000/api/v1/resources/'

    api_a = api_ip + 'query'
    api_a_param = [('sql', 'select * from category limit 3')]

    api_b = api_ip + 'outdated'
    api_b_param = [('category', 'American_people_stubs')]

    result_a = test_api(api_a, api_a_param)
    print(result_a)

    result_b = test_api(api_b, api_b_param)
    print(result_b)
