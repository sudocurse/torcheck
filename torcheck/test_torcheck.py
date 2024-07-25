from ipaddress import ip_address
from unittest.mock import patch
from flask import url_for
from torcheck import database, create_app
import pytest

class Test:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.nodes = [ip_address(x) for x in ['41.10.5.127', '94.23.148.66',
                 '95.216.107.105', '145.40.194.172',
                 '45.83.106.225', '131.188.40.189',
                 '131.188.40.188', '2a0b:f4c2:1::138',
                 '2a0b:f4c2:1::139', '152.67.84.62']]

    def test_match_ipv6(self):
        # test with a valid but weirdly formatted ipv6 address
        test_ipv6 = "2a0b:F4C2:1:0000:00:0::138   "
        assert database.match_ip(test_ipv6, self.nodes)

    @pytest.fixture()
    def app(self):
        app = create_app()
        app.config['TESTING'] = True
        return app

    def test_delete_node(self, app):
        app.config["SERVICES"]["tor"]["nodes"] = self.nodes

        delete_target = "45.83.106.225"
        client = app.test_client()

        response = client.get(f'/node/{delete_target}')
        assert response.json['tor'] == True

        response = client.delete(f'/node/{delete_target}')
        assert response.status_code == 200
        assert response.json["status"] == "success"
        response = client.get(f'/node/{delete_target}')
        assert response.json['tor'] == False


if __name__ == '__main__':
    pytest.main()


