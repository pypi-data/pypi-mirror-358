from fractionalcover3 import data
from pathlib import Path


def test_default_model():
    """
    Does the model exist?
    """
    modelfile = data.get_model()
    # how to test this?
    #assert Path(modelfile).exists()

def test_image():
    """
    Does the test image exist?
    """
    assert Path(data.landsat7_refimage()).exists()
    s2paths = data.sentinel2_refimage()
    for img in s2paths:
        assert Path(img).exists()
