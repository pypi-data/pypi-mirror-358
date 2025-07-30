# -*- coding: utf-8 -*-

__author__ = "Robert Denham"
__copyright__ = "Robert Denham"
__license__ = "mit"

import os
from fractionalcover3.compute_fractionalcover import fractional_cover_surface_reflectance as cfc
from fractionalcover3.qv_fractionalcover_sentinel2 import unmix_sentinel as qvs2
from fractionalcover3 import data
from pathlib import Path
import pkg_resources
import pytest
from click.testing import CliRunner
# these are going to require qvf, rsc etc
# so only do those if the rsc module is available



def test_compute_fractionalcover(tmp_path):
    """
    Test the console script "compute_fractionalcover.py"
    """
    pytest.importorskip("rsc")
    inimage = data.landsat7_refimage()
    outimage = Path(tmp_path) / 'l7tmre_sub_20190511_dp0m3.img'
    args = ["-i", inimage, "-o", outimage.as_posix(), '--allow-missing-metadata']
    runner = CliRunner()
    result = runner.invoke(cfc, args)
    assert result.exit_code == 0


    # specify a model by file
    example_model = Path(pkg_resources.resource_filename('fractionalcover3', 'pkgdata/fcModel_32x32x32.tflite'))
    outimage = Path(tmp_path) / 'l7tmre_sub_20190511_dp0m3.img'
    args = ["--fc_model", str(example_model),  "-i", inimage, "-o", outimage.as_posix(), '--allow-missing-metadata']
    result = runner.invoke(cfc, args)
    assert result.exit_code == 0

    # specify a model by number
    example_model = Path(pkg_resources.resource_filename('fractionalcover3', 'pkgdata/fcModel_32x32x32.tflite'))
    outimage = Path(tmp_path) / 'l7tmre_sub_20190511_dp0m3.img'
    args = ["--fc_model", 1 ,  "-i", inimage, "-o", outimage.as_posix(), '--allow-missing-metadata']
    result = runner.invoke(cfc, args)
    assert result.exit_code == 0


def test_qv_fractionalcover_sentinel2(tmp_path, capsys):
    """
    Test the console script "compute_fractionalcover.py"
    """
    pytest.importorskip("rsc")
    inimage = data.sentinel2_refimage()[0]
    outimage = "test.img"
    runner = CliRunner()
    with runner.isolated_filesystem():
        args = ['-i', inimage, '-o', outimage, '-vv', '--allow-missing-metadata']
        result = runner.invoke(qvs2, args)
        assert result.exit_code == 0
        # specify a model by file
        example_model = Path(pkg_resources.resource_filename('fractionalcover3', 'pkgdata/fcModel_32x32x32.tflite'))
        args = ['-i', inimage, "--fc_model", str(example_model), '--allow-missing-metadata', '-vv']
        result = runner.invoke(qvs2, args)
        assert result.exit_code == 0

        # specify a model by number
        args = ['-i', inimage, "--fc_model", "2", '--allow-missing-metadata', '-vv']
        result = runner.invoke(qvs2, args)
        assert result.exit_code == 0


