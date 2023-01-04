import pytest
from api import create_app
import json
from api.utils.db_management import db_cleanup


TEST_USERNAME = "test_username"
NEW_TEST_USERNAME = "test_username_2"
TEST_URL = "https://youtube.com"
NEW_TEST_URL = "http://youtube.com/"
INVALID_YT_URL = "https://youtube.com/test_video_url"
TEST_DATE = "2000-01-01"
TEST_DESCRIPTION = "test description"
TEST_COMMENT = "test comment body"
NEW_TEST_COMMENT = "new test comment body"
current_api_key = ""
second_current_api_key = ""


def convert_response_data(response):
    return json.loads(response.data.decode('utf-8'))


def set_current_api_key(response):
    global current_api_key
    data = convert_response_data(response)
    current_api_key = data.get("key", "")


def set_second_current_api_key(response):
    global second_current_api_key
    data = convert_response_data(response)
    second_current_api_key = data.get("key", "")


@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    db_cleanup()

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def client_with_user(client):
    new_user = {"username": TEST_USERNAME}
    response = client.post("/Users/", json=new_user)
    set_current_api_key(response)
    return client


@pytest.fixture()
def client_with_two_users(client_with_user):
    second_user = {"username": NEW_TEST_USERNAME}
    response = client_with_user.post("/Users/", json=second_user)
    set_second_current_api_key(response)
    return client_with_user


@pytest.fixture()
def client_with_video(client_with_user):
    video = {"url": TEST_URL, "user_id": 1}
    response = client_with_user.post('/Videos/', json=video)
    return client_with_user


@pytest.fixture()
def client_with_comment(client_with_video):
    comment = {"user_id": 1, "video_id": 1, "body": TEST_COMMENT}
    response = client_with_video.post('/Comments/', json=comment)
    return client_with_video


def test_get_empty_users(client):
    response = client.get("/Users/")
    res = convert_response_data(response)
    assert res == []


def test_user_get(client_with_user):
    user = {"username": TEST_USERNAME}
    response = client_with_user.get('/Users/', query_string=user)
    assert response.status == "200 OK"
    data = convert_response_data(response)
    assert len(data) == 1
    assert data[0]["username"] == TEST_USERNAME


def test_wrong_user_get(client_with_user):
    wrong_user = {"username": NEW_TEST_USERNAME}
    response = client_with_user.get('/Users/', query_string=wrong_user)
    assert response.status == "404 NOT FOUND"
    data = convert_response_data(response)
    assert len(data) == 0


def test_add_user(client):
    new_user = {"username": TEST_USERNAME}
    response = client.post("/Users/", json=new_user)
    assert response.status == "200 OK"
    data = convert_response_data(response)
    assert len(data) == 3
    assert data["username"] == TEST_USERNAME
    assert data["id"] == 1
    assert data["key"] != ""
    users_res = client.get("/Users/")
    users_data = convert_response_data(users_res)
    assert len(users_data) == 1


def test_add_duplicate_user(client_with_user):
    user = {"username": TEST_USERNAME}
    response = client_with_user.post("/Users/", json=user)
    assert response.status == "400 BAD REQUEST"


def test_get_user_by_id(client_with_user):
    response = client_with_user.get('/Users/1')
    assert response.status == "200 OK"
    data = convert_response_data(response)
    assert len(data) == 2
    assert data["username"] == TEST_USERNAME
    assert data["id"] == 1


def test_get_nonexistent_user_by_id(client_with_user):
    response = client_with_user.get('/Users/2')
    assert response.status == "404 NOT FOUND"


def test_put_no_api_key(client_with_user):
    user_data = {"username": NEW_TEST_USERNAME}
    response = client_with_user.put('/Users/1', json=user_data)
    assert response.status_code == 400


def test_patch_no_api_key(client_with_user):
    user_data = {"username": NEW_TEST_USERNAME}
    response = client_with_user.patch('/Users/1', json=user_data)
    assert response.status_code == 400


def test_delete_no_api_key(client_with_user):
    user_data = {"username": NEW_TEST_USERNAME}
    response = client_with_user.delete('/Users/1', json=user_data)
    assert response.status_code == 400


def test_put_empty_api_key(client_with_user):
    user_data = {"username": NEW_TEST_USERNAME, "api_key": ""}
    response = client_with_user.put('/Users/1', json=user_data)
    assert response.status_code == 400


def test_patch_empty_api_key(client_with_user):
    user_data = {"username": NEW_TEST_USERNAME, "api_key": ""}
    response = client_with_user.patch('/Users/1', json=user_data)
    assert response.status_code == 400


def test_delete_empty_api_key(client_with_user):
    user_data = {"username": NEW_TEST_USERNAME, "api_key": ""}
    response = client_with_user.delete('/Users/1', json=user_data)
    assert response.status_code == 400


def test_put_new_username(client_with_user):
    new_user_data = {"username": NEW_TEST_USERNAME, "api_key": current_api_key}
    response = client_with_user.put('/Users/1', json=new_user_data)
    data = convert_response_data(response)
    assert response.status == "200 OK"
    assert len(data) == 2
    assert data["username"] == NEW_TEST_USERNAME
    assert data["id"] == 1


def test_wrong_client_put(client_with_two_users):
    wrong_user = {"username": NEW_TEST_USERNAME, "api_key": current_api_key}
    response = client_with_two_users.put('/Users/1', json=wrong_user)
    assert response.status == "400 BAD REQUEST"


def test_patch_new_username(client_with_user):
    new_user_data = {"username": NEW_TEST_USERNAME, "api_key": current_api_key}
    response = client_with_user.patch('/Users/1', json=new_user_data)
    assert response.status == "200 OK"
    data = convert_response_data(response)
    assert len(data) == 2
    assert data["username"] == NEW_TEST_USERNAME
    assert data["id"] == 1


def test_wrong_client_patch(client_with_two_users):
    wrong_user = {"username": NEW_TEST_USERNAME, "api_key": current_api_key}
    response = client_with_two_users.patch('/Users/1', json=wrong_user)
    assert response.status == "400 BAD REQUEST"


def test_user_delete(client_with_user):
    user_data = {"api_key": current_api_key}
    del_response = client_with_user.delete('/Users/1', json=user_data)
    assert del_response.status == "200 OK"
    get_response = client_with_user.get('/Users/')
    data = convert_response_data(get_response)
    assert len(data) == 0


def test_wrong_user_delete(client_with_user):
    user_data = {"api_key": current_api_key}
    del_response = client_with_user.delete('/Users/2', json=user_data)
    assert del_response.status == "404 NOT FOUND"
    get_response = client_with_user.get('/Users/')
    data = convert_response_data(get_response)
    assert len(data) == 1


def test_get_empty_videos(client):
    response = client.get('/Videos/')
    data = convert_response_data(response)
    assert response.status_code == 200
    assert data == []


def test_add_video(client_with_user):
    video = {"url": TEST_URL, "user_id": 1}
    response = client_with_user.post('/Videos/', json=video)
    assert response.status_code == 200
    get_response = client_with_user.get('/Videos/')
    get_response_data = convert_response_data(get_response)
    assert get_response.status_code == 200
    assert len(get_response_data) == 1


def test_video_get(client_with_video):
    video_data = {"url": TEST_URL}
    response = client_with_video.get('/Videos/', query_string=video_data)
    assert response.status_code == 200
    data = convert_response_data(response)
    assert len(data) == 1
    assert data[0]["url"] == TEST_URL


def test_wrong_video_get(client_with_video):
    video_data = {"url": NEW_TEST_URL}
    response = client_with_video.get('/Videos/', query_string=video_data)
    assert response.status_code == 404
    data = convert_response_data(response)
    assert len(data) == 0


def test_add_duplicate_video(client_with_video):
    video_data = {"url": TEST_URL}
    response = client_with_video.post('/Videos/', json=video_data)
    assert response.status_code == 400


def test_add_invalid_url(client_with_video):
    video_data = {"url": "www.wrong_url.com"}
    response = client_with_video.post('/Videos/', json=video_data)
    assert response.status_code == 400


def test_get_video_by_id(client_with_video):
    response = client_with_video.get('/Videos/1')
    data = convert_response_data(response)
    assert response.status_code == 200
    assert data["url"] == TEST_URL
    assert data["user"] == TEST_USERNAME


def test_get_nonexistent_user_by_id(client_with_video):
    response = client_with_video.get('/Videos/2')
    assert response.status_code == 404


def test_put_new_url(client_with_video):
    new_video_data = {"url": NEW_TEST_URL,
                      "user_id": 1, "api_key": current_api_key}
    response = client_with_video.put('/Videos/1', json=new_video_data)
    assert response.status_code == 200
    data = convert_response_data(response)
    assert data["url"] == NEW_TEST_URL


def test_get_no_video_with_date(client_with_video):
    data = {"date": TEST_DATE}
    response = client_with_video.get('/Videos/', query_string=data)
    assert response.status_code == 404


def test_get_video_with_date(client_with_user):
    video_data = {"url": TEST_URL, "user_id": 1, "date": TEST_DATE}
    post_response = client_with_user.post('/Videos/', json=video_data)
    get_data = {"date": TEST_DATE}
    get_response = client_with_user.get('/Videos/', query_string=get_data)
    get_response_data = convert_response_data(get_response)
    assert get_response.status_code == 200
    assert len(get_response_data) == 1
    assert get_response_data[0]["date"] == TEST_DATE


def test_post_invalid_youtube_url(client_with_user):
    video_data = {"url": INVALID_YT_URL, "user_id": 1}
    response = client_with_user.post('/Videos/', json=video_data)
    assert response.status_code == 400


def test_put_invalid_youtube_url(client_with_video):
    video_data = {"url": INVALID_YT_URL, "user_id": 1}
    response = client_with_video.put('/Videos/1', json=video_data)
    assert response.status_code == 400


def test_patch_video(client_with_video):
    video_data = {"url": NEW_TEST_URL, "user_id": 1,
                  "date": TEST_DATE, "description": TEST_DESCRIPTION, "api_key": current_api_key}

    response = client_with_video.patch('/Videos/1', json=video_data)
    assert response.status_code == 200
    data = convert_response_data(response)
    assert data["url"] == NEW_TEST_URL
    assert data["date"] == TEST_DATE
    assert data["description"] == TEST_DESCRIPTION


def test_patch_invalid_youtube_url(client_with_video):
    video_data = {"url": INVALID_YT_URL, "user_id": 1,
                  "date": TEST_DATE, "description": TEST_DESCRIPTION, "api_key": current_api_key}

    response = client_with_video.patch('/Videos/1', json=video_data)
    assert response.status_code == 400


def test_delete_video(client_with_video):
    video_data = {"api_key": current_api_key}
    response = client_with_video.delete('/Videos/1', json=video_data)
    assert response.status_code == 200
    video_list_response = client_with_video.get('/Videos/')
    video_list_data = convert_response_data(video_list_response)
    assert len(video_list_data) == 0


def test_get_empty_comment(client):
    response = client.get('/Comments/')
    assert response.status_code == 200
    data = convert_response_data(response)
    assert len(data) == 0


def test_add_comment(client_with_video):
    comment = {"user_id": 1, "video_id": 1, "body": TEST_COMMENT}
    response = client_with_video.post('/Comments/', json=comment)
    assert response.status_code == 200
    get_response = client_with_video.get('/Comments/')
    get_data = convert_response_data(get_response)
    assert len(get_data) == 1


def test_comment_get_by_video_id(client_with_comment):
    comment_data = {"video_id": 1}
    response = client_with_comment.get('/Comments/', query_string=comment_data)
    data = convert_response_data(response)
    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["body"] == TEST_COMMENT


def test_comment_get_by_user_id(client_with_comment):
    comment_data = {"user_id": 1}
    response = client_with_comment.get('/Comments/', query_string=comment_data)
    data = convert_response_data(response)
    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["body"] == TEST_COMMENT


def test_get_comment_by_id(client_with_comment):
    response = client_with_comment.get('/Comments/1')
    assert response.status_code == 200
    data = convert_response_data(response)
    assert data["body"] == TEST_COMMENT


def test_put_comment(client_with_comment):
    new_comment = {"user_id": 1, "video_id": 1,
                   "body": NEW_TEST_COMMENT, "api_key": current_api_key}
    response = client_with_comment.put('/Comments/1', json=new_comment)
    assert response.status_code == 200
    get_response = client_with_comment.get('/Comments/1')
    get_data = convert_response_data(get_response)
    assert get_data["body"] == NEW_TEST_COMMENT


def test_patch_comment(client_with_comment):
    new_comment = {"user_id": 1, "video_id": 1,
                   "body": NEW_TEST_COMMENT, "api_key": current_api_key}
    response = client_with_comment.patch('/Comments/1', json=new_comment)
    assert response.status_code == 200
    get_response = client_with_comment.get('/Comments/1')
    get_data = convert_response_data(get_response)
    assert get_data["body"] == NEW_TEST_COMMENT


def test_delete_comment(client_with_comment):
    comment_data = {"api_key": current_api_key}
    response = client_with_comment.delete('/Comments/1', json=comment_data)
    assert response.status_code == 200
    get_response = client_with_comment.get('/Comments/')
    get_data = convert_response_data(get_response)
    assert len(get_data) == 0
