import pytest
import responses
from fig2q.downloadImage import download_image, get_file_id, get_artboard_id

@pytest.mark.usefixtures("mock_figma_token")
class TestDownloadImage:

    @responses.activate
    def test_download_image_success(self, sample_figma_url, tmp_path):
        # Mock Figma API response
        responses.add(
            responses.GET,
            "https://api.figma.com/v1/images/qiY7mWWSxQjrSG2d50wxFv",
            json={"images": {"45:11": "https://fake-image-url.com/image.png"}},
            status=200
        )

        # Mock image download
        responses.add(
            responses.GET,
            "https://fake-image-url.com/image.png",
            body=b"fake image data",
            status=200
        )

        output_path = tmp_path / "test.png"
        download_image(sample_figma_url, str(output_path))

        assert output_path.exists()
        assert output_path.read_bytes() == b"fake image data"

    def test_get_file_id(self, sample_figma_url):
        assert get_file_id(sample_figma_url) == "qiY7mWWSxQjrSG2d50wxFv"

    def test_get_artboard_id(self, sample_figma_url):
        assert get_artboard_id(sample_figma_url) == "45:11"
