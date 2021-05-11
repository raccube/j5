"""Tests for orientation class."""

from numpy import allclose  # type: ignore
from pyquaternion import Quaternion

from j5.vision.orientation import Orientation


def test_orientation_quaternion() -> None:
    """Test the quaternion property of the Orientation class."""
    q = Quaternion.random()
    assert q == Orientation(q).quaternion


def test_orientation_matrix() -> None:
    """Test the matrix property of the Orientation class."""
    q = Quaternion.random()
    assert allclose(q.rotation_matrix, Orientation(q).rotation_matrix)


def test_orientation_yaw_pitch_roll() -> None:
    """Test the yaw_pitch_roll property of the Orientation class."""
    q = Quaternion.random()
    assert q.yaw_pitch_roll == Orientation(q).yaw_pitch_roll


def test_orientation_yaw() -> None:
    """Test the yaw property of the Orientation class."""
    q = Quaternion.random()
    assert q.yaw_pitch_roll[0] == Orientation(q).yaw


def test_orientation_pitch() -> None:
    """Test the pitch property of the Orientation class."""
    q = Quaternion.random()
    assert q.yaw_pitch_roll[1] == Orientation(q).pitch


def test_orientation_roll() -> None:
    """Test the roll property of the Orientation class."""
    q = Quaternion.random()
    assert q.yaw_pitch_roll[2] == Orientation(q).roll


def test_orientation_rot_x() -> None:
    """Test the rot_x property of the Orientation class."""
    q = Quaternion.random()
    assert q.yaw_pitch_roll[1] == Orientation(q).rot_x


def test_orientation_rot_y() -> None:
    """Test the rot_y property of the Orientation class."""
    q = Quaternion.random()
    assert q.yaw_pitch_roll[0] == Orientation(q).rot_y


def test_orientation_rot_z() -> None:
    """Test the rot_z property of the Orientation class."""
    q = Quaternion.random()
    assert q.yaw_pitch_roll[2] == Orientation(q).rot_z


def test_orientation_repr() -> None:
    """Test the __repr__ method of the Orientation class."""
    o = Orientation(Quaternion.random())
    assert repr(o) == f"Orientation(" \
                      f"rot_x={o.rot_x}, " \
                      f"rot_y={o.rot_y}, " \
                      f"rot_z={o.rot_z}" \
                      f")"
