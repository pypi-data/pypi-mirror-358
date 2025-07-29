import pytest
import numpy as np
import SimpleITK as sitk
from pyRadPlan.cst import OAR, Target, HelperVOI, ExternalVOI, create_voi


def test_create_voi_no_args():
    with pytest.raises(ValueError):
        create_voi()


def test_target_constructor_empty_args():
    with pytest.raises(ValueError):
        Target()


def test_oar_constructor_empty_args():
    with pytest.raises(ValueError):
        OAR()


def test_helper_voi_constructor_empty_args():
    with pytest.raises(ValueError):
        HelperVOI()


def test_target_constructor_3d(generic_input_3d):
    name, ct, mask, alpha_x, beta_x = generic_input_3d
    target = Target(name=name, ct_image=ct, mask=mask)
    assert target.ct_image == ct
    assert isinstance(target.mask, sitk.Image)
    assert target.voi_type == "TARGET"
    assert target.mask.GetOrigin() == target.ct_image.cube_hu.GetOrigin()
    assert target.mask.GetSpacing() == target.ct_image.cube_hu.GetSpacing()
    assert target.mask.GetDirection() == target.ct_image.cube_hu.GetDirection()

    # test non default alpha_x and beta_x
    target_2 = Target(name=name, ct_image=ct, mask=mask, alpha_x=alpha_x, beta_x=beta_x)
    assert target_2.alpha_x == alpha_x
    assert target_2.beta_x == beta_x


def test_target_constructor_4d(generic_input_4d):
    name, ct, mask, alpha_x, beta_x = generic_input_4d
    target = Target(name=name, ct_image=ct, mask=mask)
    assert target.ct_image == ct
    assert isinstance(target.mask, sitk.Image)
    assert target.voi_type == "TARGET"

    # test non default alpha_x and beta_x
    target_2 = Target(name=name, ct_image=ct, mask=mask, alpha_x=alpha_x, beta_x=beta_x)
    assert target_2.alpha_x == alpha_x
    assert target_2.beta_x == beta_x


def test_target_constructor_4d_np(generic_input_4d):
    name, ct, mask, alpha_x, beta_x = generic_input_4d
    target = Target(name=name, ct_image=ct, mask=sitk.GetArrayFromImage(mask))
    assert target.ct_image == ct
    assert isinstance(target.mask, sitk.Image)
    assert target.voi_type == "TARGET"

    # test non default alpha_x and beta_x
    target_2 = Target(name=name, ct_image=ct, mask=mask, alpha_x=alpha_x, beta_x=beta_x)
    assert target_2.alpha_x == alpha_x
    assert target_2.beta_x == beta_x


def test_mixed_constructors(generic_input_3d, generic_input_4d):
    name_3d, ct_3d, mask_3d, _, _ = generic_input_3d
    name_4d, ct_4d, mask_4d, _, _ = generic_input_4d
    with pytest.raises(ValueError):
        target = Target(name=name_3d, ct_image=ct_3d, mask=mask_4d)

    with pytest.raises(ValueError):
        target = Target(name=name_4d, ct_image=ct_4d, mask=mask_3d)


def test_oar_constructor(generic_input_3d):
    name, ct, mask, alpha_x, beta_x = generic_input_3d
    oar = OAR(name=name, ct_image=ct, mask=mask)
    assert oar.ct_image == ct
    assert isinstance(oar.mask, sitk.Image)
    assert oar.voi_type == "OAR"

    # test non default alpha_x and beta_x
    oar_2 = OAR(name=name, ct_image=ct, mask=mask, alpha_x=alpha_x, beta_x=beta_x)
    assert oar_2.alpha_x == alpha_x
    assert oar_2.beta_x == beta_x


def test_helper_voi_constructor(generic_input_3d):
    name, ct, mask, alpha_x, beta_x = generic_input_3d
    helper_voi = HelperVOI(name=name, ct_image=ct, mask=mask)
    assert helper_voi.ct_image == ct
    assert isinstance(helper_voi.mask, sitk.Image)
    assert helper_voi.voi_type == "HELPER"

    # test non default alpha_x and beta_x
    helper_voi_2 = HelperVOI(name=name, ct_image=ct, mask=mask, alpha_x=alpha_x, beta_x=beta_x)
    assert helper_voi_2.alpha_x == alpha_x
    assert helper_voi_2.beta_x == beta_x


def tet_external_voi_constructor(generic_input_3d):
    name, ct, mask, alpha_x, beta_x = generic_input_3d
    helper_voi = ExternalVOI(name=name, ct_image=ct, mask=mask)
    assert helper_voi.ct_image == ct
    assert isinstance(helper_voi.mask, sitk.Image)
    assert helper_voi.voi_type == "HELPER"

    # test non default alpha_x and beta_x
    helper_voi_2 = ExternalVOI(name=name, ct_image=ct, mask=mask, alpha_x=alpha_x, beta_x=beta_x)
    assert helper_voi_2.alpha_x == alpha_x
    assert helper_voi_2.beta_x == beta_x


def test_voi_idx_wrong_shape(generic_input_3d):
    name, ct, _, _, _ = generic_input_3d
    with pytest.raises(ValueError):
        Target(name=name, ct_image=ct, mask=np.array([[1], [1], [1]]))


def test_voi_idx_wrong_dim(generic_input_3d):
    name, ct, _, _, _ = generic_input_3d
    with pytest.raises(ValueError):
        Target(name=name, ct_image=ct, mask=np.array([1]))

    with pytest.raises(ValueError):
        Target(name=name, ct_image=ct, mask=np.array([1] * 5)[:, None])


def test_voi_idx_non_int_idx(generic_input_3d):
    name, ct, _, _, _ = generic_input_3d
    with pytest.raises(ValueError):
        Target(name=name, ct_image=ct, mask=[[1.2, 3, 4]])


def test_voi_idx_wrong_dtype(generic_input_3d):
    name, ct, mask, _, _ = generic_input_3d
    mask_float = mask.astype("float32")
    mask_float = sitk.GetImageFromArray(mask_float)
    with pytest.raises(ValueError):
        Target(name=name, ct_image=ct, mask=mask_float)

    mask = np.zeros_like(mask) * 3.0
    with pytest.raises(ValueError):
        Target(name=name, ct_image=ct, mask=mask)


def test_voi_idx_wrong_input(generic_input_3d):
    name, ct, _, _, _ = generic_input_3d
    with pytest.raises(ValueError):
        Target(name=name, ct_image=ct, mask=[[2], [3], [4]])


def test_create_voi_target_from_dict(generic_input_3d):
    name, ct, mask, _, _ = generic_input_3d
    voi = create_voi(data={"voi_type": "TARGET", "name": name, "ct_image": ct, "mask": mask})
    assert isinstance(voi, Target)
    assert voi.ct_image == ct
    assert isinstance(voi.mask, sitk.Image)
    assert voi.voi_type == "TARGET"


def test_create_voi_oar_from_dict(generic_input_3d):
    name, ct, mask, _, _ = generic_input_3d
    voi = create_voi(data={"voi_type": "OAR", "name": name, "ct_image": ct, "mask": mask})
    assert isinstance(voi, OAR)
    assert voi.ct_image == ct
    assert isinstance(voi.mask, sitk.Image)
    assert voi.voi_type == "OAR"


def test_create_voi_helper_from_dict(generic_input_3d):
    name, ct, mask, _, _ = generic_input_3d
    voi = create_voi(data={"voi_type": "HELPER", "name": name, "ct_image": ct, "mask": mask})
    assert isinstance(voi, HelperVOI)
    assert voi.ct_image == ct
    assert isinstance(voi.mask, sitk.Image)
    assert voi.voi_type == "HELPER"


def test_create_voi_invalid_voi_type(generic_input_3d):
    name, ct, mask, _, _ = generic_input_3d
    with pytest.raises(ValueError):
        create_voi(data={"voi_type": "invalid", "name": name, "ct_image": ct, "mask": mask})


def test_create_voi_no_voi_type(generic_input_3d):
    name, ct, mask, _, _ = generic_input_3d
    with pytest.raises(ValueError):
        create_voi(data={"name": name, "ct_image": ct, "mask": mask})


def test_create_voi_no_data():
    with pytest.raises(ValueError):
        create_voi()


def test_create_voi_from_VOI(generic_input_3d):
    name, ct, mask, _, _ = generic_input_3d
    voi = create_voi(data={"voi_type": "HELPER", "name": name, "ct_image": ct, "mask": mask})
    voi_2 = create_voi(voi)
    assert voi == voi_2


def test_create_target_from_kwargs(generic_input_3d):
    name, ct, mask, _, _ = generic_input_3d
    voi = create_voi(voi_type="TARGET", name=name, ct_image=ct, mask=mask)
    assert isinstance(voi, Target)
    assert voi.ct_image == ct
    assert isinstance(voi.mask, sitk.Image)
    assert voi.voi_type == "TARGET"


def test_create_oar_from_kwargs(generic_input_3d):
    name, ct, mask, _, _ = generic_input_3d
    voi = create_voi(voi_type="OAR", name=name, ct_image=ct, mask=mask)
    assert isinstance(voi, OAR)
    assert voi.ct_image == ct
    assert isinstance(voi.mask, sitk.Image)
    assert voi.voi_type == "OAR"


def test_create_helper_from_kwargs(generic_input_3d):
    name, ct, mask, _, _ = generic_input_3d
    voi = create_voi(voi_type="HELPER", name=name, ct_image=ct, mask=mask)
    assert isinstance(voi, HelperVOI)
    assert voi.ct_image == ct
    assert isinstance(voi.mask, sitk.Image)
    assert voi.voi_type == "HELPER"


def test_create_voi_invalid_voi_type_kwargs(generic_input_3d):
    name, ct, mask, _, _ = generic_input_3d
    with pytest.raises(ValueError):
        create_voi(voi_type="invalid", name=name, ct_image=ct, mask=mask)


def test_create_voi_no_voi_type_kwargs(generic_input_3d):
    name, ct, mask, _, _ = generic_input_3d
    with pytest.raises(ValueError):
        create_voi(name=name, ct_image=ct, mask=mask)


def test_voi_indices(generic_input_3d, generic_input_4d):
    name_3d, ct_3d, mask_3d, _, _ = generic_input_3d
    name_4d, ct_4d, mask_4d, _, _ = generic_input_4d
    voi_3d = create_voi(voi_type="TARGET", name=name_3d, ct_image=ct_3d, mask=mask_3d)
    voi_4d = create_voi(voi_type="TARGET", name=name_4d, ct_image=ct_4d, mask=mask_4d)
    assert (voi_3d.indices == np.array([5000])).all()
    assert (sitk.GetArrayViewFromImage(voi_3d.mask).ravel(order="F")[voi_3d.indices] == 1).all()
    assert (voi_4d.indices == np.array([103, 10000])).all()
    assert (sitk.GetArrayViewFromImage(voi_4d.mask).ravel(order="F")[voi_4d.indices] == 1).all()


def test_voi_indices_np(generic_input_3d, generic_input_4d):
    name_3d, ct_3d, mask_3d, _, _ = generic_input_3d
    name_4d, ct_4d, mask_4d, _, _ = generic_input_4d
    voi_3d = create_voi(voi_type="TARGET", name=name_3d, ct_image=ct_3d, mask=mask_3d)
    voi_4d = create_voi(voi_type="TARGET", name=name_4d, ct_image=ct_4d, mask=mask_4d)
    assert (voi_3d.indices_numpy == np.array([1])).all()
    assert (
        sitk.GetArrayViewFromImage(voi_3d.mask).ravel(order="C")[voi_3d.indices_numpy] == 1
    ).all()
    assert (voi_4d.indices_numpy == np.array([1, 510100])).all()
    assert (
        sitk.GetArrayViewFromImage(voi_4d.mask).ravel(order="C")[voi_4d.indices_numpy] == 1
    ).all()


def test_voi_get_indices_by_order(generic_input_3d, generic_input_4d):
    name_3d, ct_3d, mask_3d, _, _ = generic_input_3d
    name_4d, ct_4d, mask_4d, _, _ = generic_input_4d
    voi_3d = create_voi(voi_type="TARGET", name=name_3d, ct_image=ct_3d, mask=mask_3d)
    voi_4d = create_voi(voi_type="TARGET", name=name_4d, ct_image=ct_4d, mask=mask_4d)
    assert (voi_3d.get_indices(order="numpy") == voi_3d.indices_numpy).all()
    assert (voi_4d.get_indices(order="numpy") == voi_4d.indices_numpy).all()
    assert (voi_3d.get_indices(order="sitk") == voi_3d.indices).all()
    assert (voi_4d.get_indices(order="sitk") == voi_4d.indices).all()


def test_voi_numpy_mask(generic_input_3d, generic_input_4d):
    name_3d, ct_3d, mask_3d, _, _ = generic_input_3d
    name_4d, ct_4d, mask_4d, _, _ = generic_input_4d
    voi_3d = create_voi(voi_type="TARGET", name=name_3d, ct_image=ct_3d, mask=mask_3d)
    voi_4d = create_voi(voi_type="TARGET", name=name_4d, ct_image=ct_4d, mask=mask_4d)
    assert (voi_3d._numpy_mask == mask_3d).all()
    assert (voi_4d._numpy_mask == sitk.GetArrayViewFromImage(mask_4d)).all()


def test_scenario_indices(generic_input_3d, generic_input_4d):
    name_3d, ct_3d, mask_3d, _, _ = generic_input_3d
    name_4d, ct_4d, mask_4d, _, _ = generic_input_4d
    voi_3d = create_voi(voi_type="TARGET", name=name_3d, ct_image=ct_3d, mask=mask_3d)
    voi_4d = create_voi(voi_type="TARGET", name=name_4d, ct_image=ct_4d, mask=mask_4d)
    assert (voi_3d.scenario_indices() == np.array([1])).all()
    assert (voi_3d.scenario_indices("sitk") == np.array([5000])).all()
    assert voi_4d.scenario_indices() == [np.array([1]), np.array([10100])]
    assert voi_4d.scenario_indices("sitk") == [np.array([5000]), np.array([51])]
    with pytest.raises(ValueError):
        voi_3d.scenario_indices("invalid")
    with pytest.raises(ValueError):
        voi_4d.scenario_indices("invalid")


def test_masked_ct(generic_input_3d, generic_input_4d):
    name_3d, ct_3d, mask_3d, _, _ = generic_input_3d
    name_4d, ct_4d, mask_4d, _, _ = generic_input_4d
    voi_3d = create_voi(voi_type="TARGET", name=name_3d, ct_image=ct_3d, mask=mask_3d)
    voi_4d = create_voi(voi_type="TARGET", name=name_4d, ct_image=ct_4d, mask=mask_4d)
    with pytest.raises(ValueError):
        voi_3d.masked_ct("invalid")
    with pytest.raises(ValueError):
        voi_4d.masked_ct("invalid")

    masked_ct_3d_sitk = voi_3d.masked_ct("sitk")
    assert isinstance(masked_ct_3d_sitk, sitk.Image)
    assert (sitk.GetArrayFromImage(masked_ct_3d_sitk) == mask_3d.astype(np.float32) * 1000).all()

    masked_ct_3d_np = voi_3d.masked_ct("numpy")
    assert (masked_ct_3d_np == mask_3d.astype(np.float32) * 1000).all()

    masked_ct_4d_sitk = voi_4d.masked_ct("sitk")
    assert isinstance(masked_ct_4d_sitk, sitk.Image)
    assert (
        sitk.GetArrayFromImage(masked_ct_4d_sitk)
        == sitk.GetArrayViewFromImage(mask_4d).astype(np.float32) * 1000
    ).all()

    masked_ct_4d_np = voi_4d.masked_ct("numpy")
    assert (masked_ct_4d_np == sitk.GetArrayViewFromImage(mask_4d).astype(np.float32) * 1000).all()


def test_scenario_ct_data(generic_input_3d, generic_input_4d):
    name_3d, ct_3d, mask_3d, _, _ = generic_input_3d
    name_4d, ct_4d, mask_4d, _, _ = generic_input_4d
    voi_3d = create_voi(voi_type="TARGET", name=name_3d, ct_image=ct_3d, mask=mask_3d)
    voi_4d = create_voi(voi_type="TARGET", name=name_4d, ct_image=ct_4d, mask=mask_4d)
    assert isinstance(voi_4d.scenario_ct_data, list)
    assert len(voi_4d.scenario_ct_data) == 2
    assert (voi_3d.scenario_ct_data == np.array([1000])).all()
    assert (voi_4d.scenario_ct_data[0] == np.array([1000])).all()
    assert (voi_4d.scenario_ct_data[1] == np.array([1000])).all()


def test_create_target_camel_case(generic_input_3d):
    name, ct, mask, alpha_x, beta_x = generic_input_3d

    voi = create_voi(
        data={
            "voiType": "TARGET",
            "name": name,
            "ctImage": ct,
            "mask": mask,
            "alphaX": alpha_x,
            "betaX": beta_x,
        }
    )
    assert isinstance(voi, Target)
    assert voi.ct_image == ct
    assert isinstance(voi.mask, sitk.Image)
    assert voi.voi_type == "TARGET"
    assert voi.alpha_x == alpha_x
    assert voi.beta_x == beta_x


def test_create_oar_camel_case(generic_input_3d):
    name, ct, mask, alpha_x, beta_x = generic_input_3d
    voi = create_voi(
        data={
            "voiType": "OAR",
            "name": name,
            "ctImage": ct,
            "mask": mask,
            "alphaX": alpha_x,
            "betaX": beta_x,
        }
    )
    assert isinstance(voi, OAR)
    assert voi.ct_image == ct
    assert isinstance(voi.mask, sitk.Image)
    assert voi.voi_type == "OAR"
    assert voi.alpha_x == alpha_x
    assert voi.beta_x == beta_x


def test_create_helper_camel_case(generic_input_3d):
    name, ct, mask, alpha_x, beta_x = generic_input_3d
    voi = create_voi(
        data={
            "voiType": "HELPER",
            "name": name,
            "ctImage": ct,
            "mask": mask,
            "alphaX": alpha_x,
            "betaX": beta_x,
        }
    )
    assert isinstance(voi, HelperVOI)
    assert voi.ct_image == ct
    assert isinstance(voi.mask, sitk.Image)
    assert voi.voi_type == "HELPER"
    assert voi.alpha_x == alpha_x
    assert voi.beta_x == beta_x


def test_create_voi_invalid_voi_type_camel_case(generic_input_3d):
    name, ct, mask, _, _ = generic_input_3d
    with pytest.raises(ValueError):
        create_voi(voi_type="invalid", name=name, ctImage=ct, mask=mask)


# def test_valildate_voi(generic_input_3d):
#     name, ct, mask, _, _=  generic_input_3d
#     voi = create_voi(voi_type="TARGET", name=name, ct_image=ct, mask=mask)
#     voivalidate_voi()
#     voi_2 = create_voi(voi_type="OAR", name=name, ct_image=ct, mask=mask)
#     voi_2.validate_voi()
#     voi_3 = create_voi(voi_type="HELPER", name=name, ct_image=ct, mask=mask)
#     voi_3.validate_voi()
