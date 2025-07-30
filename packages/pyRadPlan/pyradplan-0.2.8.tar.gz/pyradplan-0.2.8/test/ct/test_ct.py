import pytest
import SimpleITK as sitk
import os
import numpy as np
from pathlib import Path
from pydantic import ValidationError

from pyRadPlan.ct import CT, create_ct, validate_ct, ct_from_file


@pytest.fixture
def sample_image(tmp_path):
    """Create a sample SimpleITK image for testing."""
    sample_array = np.random.rand(50, 100, 100) * 1000  # Random HU values
    image = sitk.GetImageFromArray(sample_array)
    image.SetOrigin((0, 0, 0))
    image.SetSpacing((1, 1, 2))
    image.SetDirection((1, 0, 0, 0, 1, 0, 0, 0, 1))

    """Save it for testing ct_from_file method"""
    writer = sitk.ImageFileWriter()
    writer.SetUseCompression(True)
    writer.SetImageIO("NiftiImageIO")

    file_path = os.path.join(tmp_path, "DummyCT.nii.gz")

    writer.SetFileName(file_path)
    writer.Execute(image)

    return image, file_path


def test_ct_creation(sample_image):
    """Test creation of a CT object from a SimpleITK image."""
    ct = create_ct(cube_hu=sample_image[0])
    assert isinstance(ct, CT)
    assert ct.size == (100, 100, 50)  # reverse order of axes
    assert ct.resolution == {"x": 1, "y": 1, "z": 2}
    assert ct.origin == (0, 0, 0)
    assert ct.direction == (1, 0, 0, 0, 1, 0, 0, 0, 1)


def test_ct_from_dict(sample_image):
    """Test creation of a CT object from a dictionary."""
    ct_dict = {
        "cube_hu": sample_image[0],
        "origin": (1, 2, 3),
        "direction": (1, 0, 0, 0, 1, 0, 0, 0, 1),
        "resolution": {"x": 2, "y": 2, "z": 4},
    }
    ct = create_ct(ct_dict)
    assert ct.origin == (1, 2, 3)
    assert ct.resolution == {"x": 2, "y": 2, "z": 4}


def test_ct_to_matrad_dict(sample_image):
    """Test conversion of CT object to matRad dictionary format."""
    ct = create_ct(cube_hu=sample_image[0])
    matrad_dict = ct.to_matrad()
    assert "cubeHU" in matrad_dict
    assert "cubeDim" in matrad_dict
    assert matrad_dict["cubeDim"].tolist() == [100.0, 100.0, 50.0]  # reverse order of axes
    assert matrad_dict["cubeHU"].shape == (1,)
    assert matrad_dict["cubeHU"][0].shape == (100, 100, 50)  # reverse order of axes


def test_ct_from_file(sample_image):
    """Test creation of a CT object from a .nii.gz file."""
    sample_file = Path(sample_image[1])
    if sample_file.exists():
        ct = ct_from_file(sample_file)
        assert isinstance(ct, CT)
    else:
        pytest.skip("Sample DICOM file not available")


def test_validate_ct(sample_image):
    """Test validation of CT objects."""
    ct = create_ct(cube_hu=sample_image[0])
    validated_ct = validate_ct(ct)
    assert ct is validated_ct

    validated_ct = validate_ct(cube_hu=sample_image[0])
    assert isinstance(validated_ct, CT)


def test_invalid_input():
    """Test handling of invalid input."""
    with pytest.raises(ValueError):
        create_ct(cube_hu="invalid input")


@pytest.mark.parametrize(
    "size,spacing",
    [((5, 5, 5), (2, 2, 2)), ((20, 30, 40), (0.5, 0.5, 1)), ((100, 100, 100), (0.1, 0.1, 0.1))],
)
def test_various_image_sizes(size, spacing):
    """Test CT creation with various image sizes and spacings."""
    # Numpy axis order is z,y,x and SimpleITK axis order is x,y,z. Need to flip size before assertion
    sample_array = np.random.rand(*size) * 1000
    image = sitk.GetImageFromArray(sample_array)
    image.SetSpacing(spacing)
    ct = create_ct(cube_hu=image)
    assert ct.size == size[::-1]
    assert ct.resolution == {"x": spacing[0], "y": spacing[1], "z": spacing[2]}


def test_ct_property_change(sample_image):
    """Test changing properties of an existing CT object."""
    ct = create_ct(cube_hu=sample_image[0])
    new_origin = (5, 5, 1)
    ct.cube_hu.SetOrigin(new_origin)
    assert ct.origin == new_origin


def test_check_dict_convert_sitk_image():
    """Test the check_dict_convert_sitk_image method."""
    sample_array = np.random.rand(100, 200, 200) * 1000
    ct_dict = {
        "cube_hu": sample_array,
        "origin": (1, 2, 3),
        "direction": (1, 0, 0, 0, 1, 0, 0, 0, 1),
        "resolution": {"x": 2, "y": 2, "z": 4},
    }

    ct = CT.model_validate(ct_dict)
    assert isinstance(ct.cube_hu, sitk.Image)
    assert ct.origin == (1, 2, 3)
    assert ct.resolution == {"x": 2, "y": 2, "z": 4}


def test_check_multiple_scenarios_from_numpy():
    """Test the conversion to 4D image."""
    sample_array = np.ndarray((2,), dtype=object)
    sample_array[0] = np.random.rand(100, 200, 200) * 1000
    sample_array[1] = np.random.rand(100, 200, 200) * 1000
    ct_dict = {
        "cube_hu": sample_array,
        "origin": (1, 2, 3, 0),
        "direction": (1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1),
        "resolution": {"x": 2, "y": 2, "z": 4},
    }

    ct = CT.model_validate(ct_dict)
    assert isinstance(ct.cube_hu, sitk.Image)
    assert ct.origin == (1, 2, 3)
    assert ct.resolution == {"x": 2, "y": 2, "z": 4}


def test_missing_hu_cube():
    """Test handling of missing HU cube."""
    with pytest.raises(ValidationError):
        CT.model_validate({})


# WET
@pytest.fixture
def sample_ct(sample_image):
    """Create a sample CT object for testing."""
    return create_ct(cube_hu=sample_image[0])


def test_compute_wet_valid_hlut(sample_ct):
    """Test compute_wet with a valid HLUT."""
    hlut = np.array(
        [[-1000, 0, 3000], [0, 1, 2]]  # HU values  # Corresponding WET values
    ).transpose()
    wet_image = sample_ct.compute_wet(hlut)
    assert isinstance(wet_image, sitk.Image)
    assert wet_image.GetSize() == sample_ct.size
    assert wet_image.GetSpacing() == (
        sample_ct.resolution["x"],
        sample_ct.resolution["y"],
        sample_ct.resolution["z"],
    )
    assert wet_image.GetOrigin() == sample_ct.origin
    assert wet_image.GetDirection() == sample_ct.direction


def test_compute_wet_invalid_hlut(sample_ct):
    """Test compute_wet with an invalid HLUT."""
    hlut = np.array([[-1000, 0, 1000]])  # Invalid HLUT with only one row
    with pytest.raises(ValueError):
        sample_ct.compute_wet(hlut)


def test_compute_wet_edge_cases(sample_ct):
    """Test compute_wet with edge cases in HLUT."""
    hlut = np.array(
        [[-1000, 0, 1000], [0, 1, 2]]  # HU values  # Corresponding WET values
    ).transpose()
    # Test with minimum HU value
    sample_ct.cube_hu = sitk.GetImageFromArray(np.full((50, 100, 100), -1000))
    wet_image = sample_ct.compute_wet(hlut)
    assert np.all(sitk.GetArrayFromImage(wet_image) == 0)

    # Test with maximum HU value
    sample_ct.cube_hu = sitk.GetImageFromArray(np.full((50, 100, 100), 1000))
    wet_image = sample_ct.compute_wet(hlut)
    assert np.all(sitk.GetArrayFromImage(wet_image) == 2)


def test_hlut_unsorted(sample_ct):
    """Test compute_wet with an unsorted HLUT."""
    hlut_unsorted = np.array(
        [[0, -1000, 3000], [1, 0, 3]]  # HU values  # Corresponding WET values
    ).transpose()

    hlut_sorted = np.array(
        [[-1000, 0, 3000], [0, 1, 3]]  # HU values  # Corresponding WET values
    ).transpose()

    wet_image_unsorted = sample_ct.compute_wet(hlut_unsorted)
    wet_image_sorted = sample_ct.compute_wet(hlut_sorted)
    assert np.all(
        sitk.GetArrayViewFromImage(wet_image_unsorted)
        == sitk.GetArrayViewFromImage(wet_image_sorted)
    )
