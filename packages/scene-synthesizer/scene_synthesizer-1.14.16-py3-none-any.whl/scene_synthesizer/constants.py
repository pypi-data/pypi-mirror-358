# Copyright (c) 2021-2024, NVIDIA CORPORATION & AFFILIATES.  All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0

# constants.py

# This is used for loading URDF and USD files
DEFAULT_JOINT_LIMIT_LOWER = -10.0
DEFAULT_JOINT_LIMIT_UPPER = 10.0
DEFAULT_JOINT_LIMIT_VELOCITY = 10.0
DEFAULT_JOINT_LIMIT_EFFORT = 10.0
DEFAULT_JOINT_STIFFNESS = None
DEFAULT_JOINT_DAMPING = None

# This is used when 'up' and 'front' vectors are specified
DEFAULT_TOLERANCE_UP_FRONT_ORTHOGONALITY = 1e-7

# This is the key in the scene graph edge data where e.g. joint information is stored
EDGE_KEY_METADATA = 'metadata'
