from pathlib import Path
from typing import Optional

import streamlit as st
import streamlit.components.v1 as components

_USE_WEB_DEV_SERVER = False

if _USE_WEB_DEV_SERVER:
    _component_func = components.declare_component(
        "st_joystick", url="http://localhost:1234"
    )
else: #use build folder
    # Tell streamlit that there is a component called st_joystick,
    # and that the code to display that component is in the "frontend" folder
    frontend_dir = (Path(__file__).parent / "frontend/build").absolute()
    _component_func = components.declare_component(
        "st_joystick", path=str(frontend_dir)
    )

# Create the python function that will be called
def st_joystick(
    options: Optional[dict] = {
        'zone': None,
        'size': 100,
        'color': 'white',
        'mode':'static',
        'position': {'top': '50%', 'left': '50%'}
    },
    id: Optional[int] = 0
):
    """
    This function enables streamlit to create and receive Joystick events
    """
    component_value = _component_func(
       options = options,
       id = id
    )
    return component_value

@st.fragment
def left_joystick():
    value = st_joystick(options={'size': 200})
    #st.write(value)

def main():
    left_joystick()


if __name__ == "__main__":
    main()
