"""
Sqlalchemy type decorator for float or numpy values
SPDX - License - Identifier: LGPL - 3.0 - or -later
Copyright © 2024 Concordia CERC group
Project Coder Connor Brackley Connor.Brackley@concordia.ca
"""

import numpy as np
from sqlalchemy import TypeDecorator, Float


class FloatOrNpfloat(TypeDecorator):
  """
  Custom SQLAlchemy type decorator to convert np.float types to float.
  """
  impl = Float

  def process_bind_param(self, value, dialect):
    if value is not None:
      if isinstance(value, (float, np.floating)):
        value = float(value)
      else:
        raise TypeError(f"Expected float, np.float64, or None, got {type(value).__name__}")

    return value
