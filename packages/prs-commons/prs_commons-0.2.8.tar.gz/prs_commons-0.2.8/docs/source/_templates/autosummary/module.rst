{{ fullname | escape | underline}}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}
   :members:
   :show-inheritance:
   :special-members: __new__, __init__
   :undoc-members:
   :exclude-members: __weakref__

   {% block methods %}
   .. automethod:: __init__
   {% if methods %}
   .. rubric:: {{ _('Methods') }}

   .. autosummary::
      :toctree:
      {% for item in methods %}
      ~{{ name }}.{{ item }}
      {%- endfor %}
   {% endif %}
   {% endblock %}
