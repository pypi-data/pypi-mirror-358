// The `Streamlit` object exists because our html file includes
// `streamlit-component-lib.js`.
// If you get an error about "Streamlit" not being defined, that
// means you're missing that file.
import { Streamlit } from "streamlit-component-lib";
import nipplejs from "nipplejs";

const joyDiv = document.body.appendChild(document.createElement("div"));

function sendValue(value) {
  Streamlit.setComponentValue(value)
}

/**
 * The component's render function. This will be called immediately after
 * the component is initially loaded, and then again every time the
 * component gets new data from Python.
 */
function onRender(event) {
  // Only run the render code the first time the component is loaded.
  if (!window.rendered) {
    const {options, divId} = event.detail.args;
    joyDiv.setAttribute('id', String('joyDiv') + divId);
    options['zone'] = joyDiv;

    if(!('mode' in options))
      options['mode'] = 'static'
    if(!('position' in options))
      options['position'] = {'top': '50%', 'left': '50%'}
    
    //console.log('Creating Joystick with: ', options);
    var joystick = nipplejs.create(options);

    var styleStr = 'height:' + String(options['size'] * 1.5) + 'px;';
    styleStr += 'min-width: ' +  String(options['size'] * 1.5) + 'px;';
    joyDiv.setAttribute('style', styleStr);
    Streamlit.setFrameHeight(options['size'] * 1.56);

    joystick.on('start', function (evt, data) {
        sendValue({'type':  evt.type, 'id': data.id, 'identifier': data.identifier, 'frontPosition': data.frontPosition});
    });

    joystick.on('end', function (evt, data) {
        sendValue({'type':  evt.type, 'id': data.id, 'identifier': data.identifier, 'frontPosition': data.frontPosition});
    });

    joystick.on('move', function (evt, data) {
        data['type'] = evt.type;
        delete data.instance;
        sendValue(data);
    });
    window.rendered = true
  }
}

// Render the component whenever python send a "render event"
Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender)
// Tell Streamlit that the component is ready to receive events
Streamlit.setComponentReady()

