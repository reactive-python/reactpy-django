# type: ignore
# TODO: Almost everything in this module should be moved to `reactpy.utils._mutate_vdom()`.
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from reactpy.core.events import EventHandler, to_event_handler_function

if TYPE_CHECKING:
    from reactpy.core.types import VdomDict


def convert_html_props_to_reactjs(vdom_tree: VdomDict) -> VdomDict:
    """Transformation that standardizes the prop names to be used in the component."""
    # On each node, replace the 'attributes' key names with the standardized names.
    if "attributes" in vdom_tree:
        vdom_tree["attributes"] = {_normalize_prop_name(k): v for k, v in vdom_tree["attributes"].items()}

    return vdom_tree


def convert_textarea_children_to_prop(vdom_tree: VdomDict) -> VdomDict:
    """Transformation that converts the text content of a <textarea> to the 'value' prop."""
    # If the current tag is <textarea>, move the text content to the 'value' prop.
    if vdom_tree["tagName"] == "textarea" and "children" in vdom_tree and vdom_tree["children"]:
        vdom_tree.setdefault("attributes", {})
        text_content = vdom_tree.pop("children")
        text_content = "".join([child for child in text_content if isinstance(child, str)])
        default_value = vdom_tree["attributes"].pop("defaultValue", "")
        vdom_tree["attributes"]["defaultValue"] = text_content or default_value

    return vdom_tree


def set_value_prop_on_select_element(vdom_tree: VdomDict) -> VdomDict:
    """Use the `value` prop on <select> instead of setting `selected` on <option>."""
    # If the current tag is <select>, remove 'selected' prop from any <option> children and
    # instead set the 'value' prop on the <select> tag.
    if vdom_tree["tagName"] == "select" and "children" in vdom_tree:
        vdom_tree.setdefault("attributes", {})
        selected_options = _find_selected_options(vdom_tree)
        multiple_choice = vdom_tree["attributes"]["multiple"] = bool(vdom_tree["attributes"].get("multiple"))
        if selected_options and not multiple_choice:
            vdom_tree["attributes"]["defaultValue"] = selected_options[0]
        if selected_options and multiple_choice:
            vdom_tree["attributes"]["defaultValue"] = selected_options

    return vdom_tree


def transform_value_prop_on_input_element(vdom_tree: VdomDict) -> VdomDict:
    """Adds an onChange handler on form <input> elements, since ReactJS doesn't like uncontrolled inputs."""
    if vdom_tree["tagName"] == "input":
        vdom_tree.setdefault("attributes", {})
        vdom_tree["attributes"].setdefault("defaultValue", vdom_tree["attributes"].pop("value", ""))

    return vdom_tree


def intercept_anchor_links(vdom_tree: VdomDict) -> VdomDict:
    """Intercepts anchor links and prevents the default behavior.
    This allows ReactPy-Router to handle the navigation instead of the browser."""
    if vdom_tree["tagName"] == "a":
        vdom_tree.setdefault("eventHandlers", {})
        vdom_tree["eventHandlers"]["onClick"] = EventHandler(
            to_event_handler_function(_do_nothing_event), prevent_default=True
        )

    return vdom_tree


def infer_key_from_attributes(vdom_tree: VdomDict) -> VdomDict:
    """Infer the node's 'key' by looking at any attributes that should be unique."""
    attributes = vdom_tree.get("attributes", {})

    # Infer 'key' from 'id'
    key = attributes.get("id")

    # Fallback: Infer 'key' from 'name'
    if not key and vdom_tree["tagName"] in {"input", "select", "textarea"}:
        key = attributes.get("name")

    if key:
        vdom_tree["key"] = key

    return vdom_tree


def _find_selected_options(vdom_node: Any) -> list[str]:
    """Recursively iterate through the tree to find all <option> tags with the 'selected' prop.
    Removes the 'selected' prop and returns a list of the 'value' prop of each selected <option>."""
    if not isinstance(vdom_node, dict):
        return []

    selected_options = []
    if vdom_node["tagName"] == "option" and "attributes" in vdom_node:
        value = vdom_node["attributes"].setdefault("value", vdom_node["children"][0])

        if "selected" in vdom_node["attributes"]:
            vdom_node["attributes"].pop("selected")
            selected_options.append(value)

    for child in vdom_node.get("children", []):
        selected_options.extend(_find_selected_options(child))

    return selected_options


def _normalize_prop_name(prop_name: str) -> str:
    """Standardizes the prop name to be used in the component."""
    return REACT_PROP_SUBSTITUTIONS.get(prop_name, prop_name)


def _parse_react_props(string: str) -> set[str]:
    """Extracts the props from a string of React props (copy-pasted from ReactJS docs)."""
    lines = string.strip().split("\n")
    props = set()

    for line in lines:
        parts = line.split(":", maxsplit=1)
        if len(parts) == 2 and parts[0] not in {"children", "ref", "aria-*", "data-*"}:
            key, value = parts
            key = key.strip()
            value = value.strip()
            props.add(key)

    return props


def _do_nothing_event(*args, **kwargs):
    """A placeholder event function that does nothing."""


# TODO: Create a script that will auto-generate this into a file dump.
# The current implementation of manually copy-pasting it isn't ideal.
# https://react.dev/reference/react-dom/components/common#common-props
SPECIAL_PROPS = r"""
children: A React node (an element, a string, a number, a portal, an empty node like null, undefined and booleans, or an array of other React nodes). Specifies the content inside the component. When you use JSX, you will usually specify the children prop implicitly by nesting tags like <div><span /></div>.
dangerouslySetInnerHTML: An object of the form { __html: '<p>some html</p>' } with a raw HTML string inside. Overrides the innerHTML property of the DOM node and displays the passed HTML inside. This should be used with extreme caution! If the HTML inside isn't trusted (for example, if it's based on user data), you risk introducing an XSS vulnerability. Read more about using dangerouslySetInnerHTML.
ref: A ref object from useRef or createRef, or a ref callback function, or a string for legacy refs. Your ref will be filled with the DOM element for this node. Read more about manipulating the DOM with refs.
suppressContentEditableWarning: A boolean. If true, suppresses the warning that React shows for elements that both have children and contentEditable={true} (which normally do not work together). Use this if you're building a text input library that manages the contentEditable content manually.
suppressHydrationWarning: A boolean. If you use server rendering, normally there is a warning when the server and the client render different content. In some rare cases (like timestamps), it is very hard or impossible to guarantee an exact match. If you set suppressHydrationWarning to true, React will not warn you about mismatches in the attributes and the content of that element. It only works one level deep, and is intended to be used as an escape hatch. Don't overuse it. Read more about suppressing hydration errors.
style: An object with CSS styles, for example { fontWeight: 'bold', margin: 20 }. Similarly to the DOM style property, the CSS property names need to be written as camelCase, for example fontWeight instead of font-weight. You can pass strings or numbers as values. If you pass a number, like width: 100, React will automatically append px (“pixels”) to the value unless it's a unitless property. We recommend using style only for dynamic styles where you don't know the style values ahead of time. In other cases, applying plain CSS classes with className is more efficient. Read more about applying CSS with className and styles.
"""

STANDARD_PROPS = r"""
accessKey: A string. Specifies a keyboard shortcut for the element. Not generally recommended.
aria-*: ARIA attributes let you specify the accessibility tree information for this element. See ARIA attributes for a complete reference. In React, all ARIA attribute names are exactly the same as in HTML.
autoCapitalize: A string. Specifies whether and how the user input should be capitalized.
className: A string. Specifies the element's CSS class name. Read more about applying CSS styles.
contentEditable: A boolean. If true, the browser lets the user edit the rendered element directly. This is used to implement rich text input libraries like Lexical. React warns if you try to pass React children to an element with contentEditable={true} because React will not be able to update its content after user edits.
data-*: Data attributes let you attach some string data to the element, for example data-fruit="banana". In React, they are not commonly used because you would usually read data from props or state instead.
dir: Either 'ltr' or 'rtl'. Specifies the text direction of the element.
draggable: A boolean. Specifies whether the element is draggable. Part of HTML Drag and Drop API.
enterKeyHint: A string. Specifies which action to present for the enter key on virtual keyboards.
htmlFor: A string. For <label> and <output>, lets you associate the label with some control. Same as for HTML attribute. React uses the standard DOM property names (htmlFor) instead of HTML attribute names.
hidden: A boolean or a string. Specifies whether the element should be hidden.
id: A string. Specifies a unique identifier for this element, which can be used to find it later or connect it with other elements. Generate it with useId to avoid clashes between multiple instances of the same component.
is: A string. If specified, the component will behave like a custom element.
inputMode: A string. Specifies what kind of keyboard to display (for example, text, number or telephone).
itemProp: A string. Specifies which property the element represents for structured data crawlers.
lang: A string. Specifies the language of the element.
onAnimationEnd: An AnimationEvent handler function. Fires when a CSS animation completes.
onAnimationEndCapture: A version of onAnimationEnd that fires in the capture phase.
onAnimationIteration: An AnimationEvent handler function. Fires when an iteration of a CSS animation ends, and another one begins.
onAnimationIterationCapture: A version of onAnimationIteration that fires in the capture phase.
onAnimationStart: An AnimationEvent handler function. Fires when a CSS animation starts.
onAnimationStartCapture: onAnimationStart, but fires in the capture phase.
onAuxClick: A MouseEvent handler function. Fires when a non-primary pointer button was clicked.
onAuxClickCapture: A version of onAuxClick that fires in the capture phase.
onBeforeInput: An InputEvent handler function. Fires before the value of an editable element is modified. React does not yet use the native beforeinput event, and instead attempts to polyfill it using other events.
onBeforeInputCapture: A version of onBeforeInput that fires in the capture phase.
onBlur: A FocusEvent handler function. Fires when an element lost focus. Unlike the built-in browser blur event, in React the onBlur event bubbles.
onBlurCapture: A version of onBlur that fires in the capture phase.
onClick: A MouseEvent handler function. Fires when the primary button was clicked on the pointing device.
onClickCapture: A version of onClick that fires in the capture phase.
onCompositionStart: A CompositionEvent handler function. Fires when an input method editor starts a new composition session.
onCompositionStartCapture: A version of onCompositionStart that fires in the capture phase.
onCompositionEnd: A CompositionEvent handler function. Fires when an input method editor completes or cancels a composition session.
onCompositionEndCapture: A version of onCompositionEnd that fires in the capture phase.
onCompositionUpdate: A CompositionEvent handler function. Fires when an input method editor receives a new character.
onCompositionUpdateCapture: A version of onCompositionUpdate that fires in the capture phase.
onContextMenu: A MouseEvent handler function. Fires when the user tries to open a context menu.
onContextMenuCapture: A version of onContextMenu that fires in the capture phase.
onCopy: A ClipboardEvent handler function. Fires when the user tries to copy something into the clipboard.
onCopyCapture: A version of onCopy that fires in the capture phase.
onCut: A ClipboardEvent handler function. Fires when the user tries to cut something into the clipboard.
onCutCapture: A version of onCut that fires in the capture phase.
onDoubleClick: A MouseEvent handler function. Fires when the user clicks twice. Corresponds to the browser dblclick event.
onDoubleClickCapture: A version of onDoubleClick that fires in the capture phase.
onDrag: A DragEvent handler function. Fires while the user is dragging something.
onDragCapture: A version of onDrag that fires in the capture phase.
onDragEnd: A DragEvent handler function. Fires when the user stops dragging something.
onDragEndCapture: A version of onDragEnd that fires in the capture phase.
onDragEnter: A DragEvent handler function. Fires when the dragged content enters a valid drop target.
onDragEnterCapture: A version of onDragEnter that fires in the capture phase.
onDragOver: A DragEvent handler function. Fires on a valid drop target while the dragged content is dragged over it. You must call e.preventDefault() here to allow dropping.
onDragOverCapture: A version of onDragOver that fires in the capture phase.
onDragStart: A DragEvent handler function. Fires when the user starts dragging an element.
onDragStartCapture: A version of onDragStart that fires in the capture phase.
onDrop: A DragEvent handler function. Fires when something is dropped on a valid drop target.
onDropCapture: A version of onDrop that fires in the capture phase.
onFocus: A FocusEvent handler function. Fires when an element lost focus. Unlike the built-in browser focus event, in React the onFocus event bubbles.
onFocusCapture: A version of onFocus that fires in the capture phase.
onGotPointerCapture: A PointerEvent handler function. Fires when an element programmatically captures a pointer.
onGotPointerCaptureCapture: A version of onGotPointerCapture that fires in the capture phase.
onKeyDown: A KeyboardEvent handler function. Fires when a key is pressed.
onKeyDownCapture: A version of onKeyDown that fires in the capture phase.
onKeyPress: A KeyboardEvent handler function. Deprecated. Use onKeyDown or onBeforeInput instead.
onKeyPressCapture: A version of onKeyPress that fires in the capture phase.
onKeyUp: A KeyboardEvent handler function. Fires when a key is released.
onKeyUpCapture: A version of onKeyUp that fires in the capture phase.
onLostPointerCapture: A PointerEvent handler function. Fires when an element stops capturing a pointer.
onLostPointerCaptureCapture: A version of onLostPointerCapture that fires in the capture phase.
onMouseDown: A MouseEvent handler function. Fires when the pointer is pressed down.
onMouseDownCapture: A version of onMouseDown that fires in the capture phase.
onMouseEnter: A MouseEvent handler function. Fires when the pointer moves inside an element. Does not have a capture phase. Instead, onMouseLeave and onMouseEnter propagate from the element being left to the one being entered.
onMouseLeave: A MouseEvent handler function. Fires when the pointer moves outside an element. Does not have a capture phase. Instead, onMouseLeave and onMouseEnter propagate from the element being left to the one being entered.
onMouseMove: A MouseEvent handler function. Fires when the pointer changes coordinates.
onMouseMoveCapture: A version of onMouseMove that fires in the capture phase.
onMouseOut: A MouseEvent handler function. Fires when the pointer moves outside an element, or if it moves into a child element.
onMouseOutCapture: A version of onMouseOut that fires in the capture phase.
onMouseUp: A MouseEvent handler function. Fires when the pointer is released.
onMouseUpCapture: A version of onMouseUp that fires in the capture phase.
onPointerCancel: A PointerEvent handler function. Fires when the browser cancels a pointer interaction.
onPointerCancelCapture: A version of onPointerCancel that fires in the capture phase.
onPointerDown: A PointerEvent handler function. Fires when a pointer becomes active.
onPointerDownCapture: A version of onPointerDown that fires in the capture phase.
onPointerEnter: A PointerEvent handler function. Fires when a pointer moves inside an element. Does not have a capture phase. Instead, onPointerLeave and onPointerEnter propagate from the element being left to the one being entered.
onPointerLeave: A PointerEvent handler function. Fires when a pointer moves outside an element. Does not have a capture phase. Instead, onPointerLeave and onPointerEnter propagate from the element being left to the one being entered.
onPointerMove: A PointerEvent handler function. Fires when a pointer changes coordinates.
onPointerMoveCapture: A version of onPointerMove that fires in the capture phase.
onPointerOut: A PointerEvent handler function. Fires when a pointer moves outside an element, if the pointer interaction is cancelled, and a few other reasons.
onPointerOutCapture: A version of onPointerOut that fires in the capture phase.
onPointerUp: A PointerEvent handler function. Fires when a pointer is no longer active.
onPointerUpCapture: A version of onPointerUp that fires in the capture phase.
onPaste: A ClipboardEvent handler function. Fires when the user tries to paste something from the clipboard.
onPasteCapture: A version of onPaste that fires in the capture phase.
onScroll: An Event handler function. Fires when an element has been scrolled. This event does not bubble.
onScrollCapture: A version of onScroll that fires in the capture phase.
onSelect: An Event handler function. Fires after the selection inside an editable element like an input changes. React extends the onSelect event to work for contentEditable={true} elements as well. In addition, React extends it to fire for empty selection and on edits (which may affect the selection).
onSelectCapture: A version of onSelect that fires in the capture phase.
onTouchCancel: A TouchEvent handler function. Fires when the browser cancels a touch interaction.
onTouchCancelCapture: A version of onTouchCancel that fires in the capture phase.
onTouchEnd: A TouchEvent handler function. Fires when one or more touch points are removed.
onTouchEndCapture: A version of onTouchEnd that fires in the capture phase.
onTouchMove: A TouchEvent handler function. Fires one or more touch points are moved.
onTouchMoveCapture: A version of onTouchMove that fires in the capture phase.
onTouchStart: A TouchEvent handler function. Fires when one or more touch points are placed.
onTouchStartCapture: A version of onTouchStart that fires in the capture phase.
onTransitionEnd: A TransitionEvent handler function. Fires when a CSS transition completes.
onTransitionEndCapture: A version of onTransitionEnd that fires in the capture phase.
onWheel: A WheelEvent handler function. Fires when the user rotates a wheel button.
onWheelCapture: A version of onWheel that fires in the capture phase.
role: A string. Specifies the element role explicitly for assistive technologies. nt.
slot: A string. Specifies the slot name when using shadow DOM. In React, an equivalent pattern is typically achieved by passing JSX as props, for example <Layout left={<Sidebar />} right={<Content />} />.
spellCheck: A boolean or null. If explicitly set to true or false, enables or disables spellchecking.
tabIndex: A number. Overrides the default Tab button behavior. Avoid using values other than -1 and 0.
title: A string. Specifies the tooltip text for the element.
translate: Either 'yes' or 'no'. Passing 'no' excludes the element content from being translated.
"""

FORM_PROPS = r"""
onReset: An Event handler function. Fires when a form gets reset.
onResetCapture: A version of onReset that fires in the capture phase.
onSubmit: An Event handler function. Fires when a form gets submitted.
onSubmitCapture: A version of onSubmit that fires in the capture phase.
"""

DIALOG_PROPS = r"""
onCancel: An Event handler function. Fires when the user tries to dismiss the dialog.
onCancelCapture: A version of onCancel that fires in the capture phase. capture-phase-events)
onClose: An Event handler function. Fires when a dialog has been closed.
onCloseCapture: A version of onClose that fires in the capture phase.
"""

DETAILS_PROPS = r"""
onToggle: An Event handler function. Fires when the user toggles the details.
onToggleCapture: A version of onToggle that fires in the capture phase. capture-phase-events)
"""

IMG_IFRAME_OBJECT_EMBED_LINK_IMAGE_PROPS = r"""
onLoad: An Event handler function. Fires when the resource has loaded.
onLoadCapture: A version of onLoad that fires in the capture phase.
onError: An Event handler function. Fires when the resource could not be loaded.
onErrorCapture: A version of onError that fires in the capture phase.
"""

AUDIO_VIDEO_PROPS = r"""
onAbort: An Event handler function. Fires when the resource has not fully loaded, but not due to an error.
onAbortCapture: A version of onAbort that fires in the capture phase.
onCanPlay: An Event handler function. Fires when there's enough data to start playing, but not enough to play to the end without buffering.
onCanPlayCapture: A version of onCanPlay that fires in the capture phase.
onCanPlayThrough: An Event handler function. Fires when there's enough data that it's likely possible to start playing without buffering until the end.
onCanPlayThroughCapture: A version of onCanPlayThrough that fires in the capture phase.
onDurationChange: An Event handler function. Fires when the media duration has updated.
onDurationChangeCapture: A version of onDurationChange that fires in the capture phase.
onEmptied: An Event handler function. Fires when the media has become empty.
onEmptiedCapture: A version of onEmptied that fires in the capture phase.
onEncrypted: An Event handler function. Fires when the browser encounters encrypted media.
onEncryptedCapture: A version of onEncrypted that fires in the capture phase.
onEnded: An Event handler function. Fires when the playback stops because there's nothing left to play.
onEndedCapture: A version of onEnded that fires in the capture phase.
onError: An Event handler function. Fires when the resource could not be loaded.
onErrorCapture: A version of onError that fires in the capture phase.
onLoadedData: An Event handler function. Fires when the current playback frame has loaded.
onLoadedDataCapture: A version of onLoadedData that fires in the capture phase.
onLoadedMetadata: An Event handler function. Fires when metadata has loaded.
onLoadedMetadataCapture: A version of onLoadedMetadata that fires in the capture phase.
onLoadStart: An Event handler function. Fires when the browser started loading the resource.
onLoadStartCapture: A version of onLoadStart that fires in the capture phase.
onPause: An Event handler function. Fires when the media was paused.
onPauseCapture: A version of onPause that fires in the capture phase.
onPlay: An Event handler function. Fires when the media is no longer paused.
onPlayCapture: A version of onPlay that fires in the capture phase.
onPlaying: An Event handler function. Fires when the media starts or restarts playing.
onPlayingCapture: A version of onPlaying that fires in the capture phase.
onProgress: An Event handler function. Fires periodically while the resource is loading.
onProgressCapture: A version of onProgress that fires in the capture phase.
onRateChange: An Event handler function. Fires when playback rate changes.
onRateChangeCapture: A version of onRateChange that fires in the capture phase.
onResize: An Event handler function. Fires when video changes size.
onResizeCapture: A version of onResize that fires in the capture phase.
onSeeked: An Event handler function. Fires when a seek operation completes.
onSeekedCapture: A version of onSeeked that fires in the capture phase.
onSeeking: An Event handler function. Fires when a seek operation starts.
onSeekingCapture: A version of onSeeking that fires in the capture phase.
onStalled: An Event handler function. Fires when the browser is waiting for data but it keeps not loading.
onStalledCapture: A version of onStalled that fires in the capture phase.
onSuspend: An Event handler function. Fires when loading the resource was suspended.
onSuspendCapture: A version of onSuspend that fires in the capture phase.
onTimeUpdate: An Event handler function. Fires when the current playback time updates.
onTimeUpdateCapture: A version of onTimeUpdate that fires in the capture phase.
onVolumeChange: An Event handler function. Fires when the volume has changed.
onVolumeChangeCapture: A version of onVolumeChange that fires in the capture phase.
onWaiting: An Event handler function. Fires when the playback stopped due to temporary lack of data.
onWaitingCapture: A version of onWaiting that fires in the capture phase.
"""

INPUT_PROPS = r"""
checked: A boolean. For a checkbox input or a radio button, controls whether it is selected.
value: A string. For a text input, controls its text. (For a radio button, specifies its form data.)
defaultChecked: A boolean. Specifies the initial value for type="checkbox" and type="radio" inputs.
defaultValue: A string. Specifies the initial value for a text input.
accept: A string. Specifies which filetypes are accepted by a type="file" input.
alt: A string. Specifies the alternative image text for a type="image" input.
capture: A string. Specifies the media (microphone, video, or camera) captured by a type="file" input.
autoComplete: A string. Specifies one of the possible autocomplete behaviors.
autoFocus: A boolean. If true, React will focus the element on mount.
dirname: A string. Specifies the form field name for the element's directionality.
disabled: A boolean. If true, the input will not be interactive and will appear dimmed.
children: <input> does not accept children.
form: A string. Specifies the id of the <form> this input belongs to. If omitted, it's the closest parent form.
formAction: A string. Overrides the parent <form action> for type="submit" and type="image".
formEnctype: A string. Overrides the parent <form enctype> for type="submit" and type="image".
formMethod: A string. Overrides the parent <form method> for type="submit" and type="image".
formNoValidate: A string. Overrides the parent <form noValidate> for type="submit" and type="image".
formTarget: A string. Overrides the parent <form target> for type="submit" and type="image".
height: A string. Specifies the image height for type="image".
list: A string. Specifies the id of the <datalist> with the autocomplete options.
max: A number. Specifies the maximum value of numerical and datetime inputs.
maxLength: A number. Specifies the maximum length of text and other inputs.
min: A number. Specifies the minimum value of numerical and datetime inputs.
minLength: A number. Specifies the minimum length of text and other inputs.
multiple: A boolean. Specifies whether multiple values are allowed for <type="file" and type="email".
name: A string. Specifies the name for this input that's submitted with the form.
onChange: An Event handler function. Required for controlled inputs. Fires immediately when the input's value is changed by the user (for example, it fires on every keystroke). Behaves like the browser input event.
onChangeCapture: A version of onChange that fires in the capture phase.
onInput: An Event handler function. Fires immediately when the value is changed by the user. For historical reasons, in React it is idiomatic to use onChange instead which works similarly.
onInputCapture: A version of onInput that fires in the capture phase.
onInvalid: An Event handler function. Fires if an input fails validation on form submit. Unlike the built-in invalid event, the React onInvalid event bubbles.
onInvalidCapture: A version of onInvalid that fires in the capture phase.
onSelect: An Event handler function. Fires after the selection inside the <input> changes. React extends the onSelect event to also fire for empty selection and on edits (which may affect the selection).
onSelectCapture: A version of onSelect that fires in the capture phase.
pattern: A string. Specifies the pattern that the value must match.
placeholder: A string. Displayed in a dimmed color when the input value is empty.
readOnly: A boolean. If true, the input is not editable by the user.
required: A boolean. If true, the value must be provided for the form to submit.
size: A number. Similar to setting width, but the unit depends on the control.
src: A string. Specifies the image source for a type="image" input.
step: A positive number or an 'any' string. Specifies the distance between valid values.
type: A string. One of the input types.
width: A string. Specifies the image width for a type="image" input.
"""

SELECT_PROPS = r"""
value: A string (or an array of strings for multiple={true}). Controls which option is selected. Every value string match the value of some <option> nested inside the <select>.
defaultValue: A string (or an array of strings for multiple={true}). Specifies the initially selected option.
autoComplete: A string. Specifies one of the possible autocomplete behaviors.
autoFocus: A boolean. If true, React will focus the element on mount.
children: <select> accepts <option>, <optgroup>, and <datalist> components as children. You can also pass your own components as long as they eventually render one of the allowed components. If you pass your own components that eventually render <option> tags, each <option> you render must have a value.
disabled: A boolean. If true, the select box will not be interactive and will appear dimmed.
form: A string. Specifies the id of the <form> this select box belongs to. If omitted, it's the closest parent form.
multiple: A boolean. If true, the browser allows multiple selection.
name: A string. Specifies the name for this select box that's submitted with the form.
onChange: An Event handler function. Required for controlled select boxes. Fires immediately when the user picks a different option. Behaves like the browser input event.
onChangeCapture: A version of onChange that fires in the capture phase.
onInput: An Event handler function. Fires immediately when the value is changed by the user. For historical reasons, in React it is idiomatic to use onChange instead which works similarly.
onInputCapture: A version of onInput that fires in the capture phase.
onInvalid: An Event handler function. Fires if an input fails validation on form submit. Unlike the built-in invalid event, the React onInvalid event bubbles.
onInvalidCapture: A version of onInvalid that fires in the capture phase.
required: A boolean. If true, the value must be provided for the form to submit.
size: A number. For multiple={true} selects, specifies the preferred number of initially visible items.
"""

TEXTAREA_PROPS = r"""
autoComplete: Either 'on' or 'off'. Specifies the autocomplete behavior.
autoFocus: A boolean. If true, React will focus the element on mount.
children: <textarea> does not accept children. To set the initial value, use defaultValue.
cols: A number. Specifies the default width in average character widths. Defaults to 20.
disabled: A boolean. If true, the input will not be interactive and will appear dimmed.
form: A string. Specifies the id of the <form> this input belongs to. If omitted, it's the closest parent form.
maxLength: A number. Specifies the maximum length of text.
minLength: A number. Specifies the minimum length of text.
name: A string. Specifies the name for this input that's submitted with the form.
onChange: An Event handler function. Required for controlled text areas. Fires immediately when the input's value is changed by the user (for example, it fires on every keystroke). Behaves like the browser input event.
onChangeCapture: A version of onChange that fires in the capture phase.
onInput: An Event handler function. Fires immediately when the value is changed by the user. For historical reasons, in React it is idiomatic to use onChange instead which works similarly.
onInputCapture: A version of onInput that fires in the capture phase.
onInvalid: An Event handler function. Fires if an input fails validation on form submit. Unlike the built-in invalid event, the React onInvalid event bubbles.
onInvalidCapture: A version of onInvalid that fires in the capture phase.
onSelect: An Event handler function. Fires after the selection inside the <textarea> changes. React extends the onSelect event to also fire for empty selection and on edits (which may affect the selection).
onSelectCapture: A version of onSelect that fires in the capture phase.
placeholder: A string. Displayed in a dimmed color when the text area value is empty.
readOnly: A boolean. If true, the text area is not editable by the user.
required: A boolean. If true, the value must be provided for the form to submit.
rows: A number. Specifies the default height in average character heights. Defaults to 2.
wrap: Either 'hard', 'soft', or 'off'. Specifies how the text should be wrapped when submitting a form.
"""

LINK_PROPS = r"""
disabled: a boolean. Disables the stylesheet.
onError: a function. Called when the stylesheet fails to load.
onLoad: a function. Called when the stylesheet finishes being loaded.
as: a string. The type of resource. Its possible values are audio, document, embed, fetch, font, image, object, script, style, track, video, worker.
imageSrcSet: a string. Applicable only when as="image". Specifies the source set of the image.
imageSizes: a string. Applicable only when as="image". Specifies the sizes of the image.
sizes: a string. The sizes of the icon.
href: a string. The URL of the linked resource.
crossOrigin: a string. The CORS policy to use. Its possible values are anonymous and use-credentials. It is required when as is set to "fetch".
referrerPolicy: a string. The Referrer header to send when fetching. Its possible values are no-referrer-when-downgrade (the default), no-referrer, origin, origin-when-cross-origin, and unsafe-url.
fetchPriority: a string. Suggests a relative priority for fetching the resource. The possible values are auto (the default), high, and low.
hrefLang: a string. The language of the linked resource.
integrity: a string. A cryptographic hash of the resource, to verify its authenticity.
type: a string. The MIME type of the linked resource.
"""

META_PROPS = r"""
name: a string. Specifies the kind of metadata to be attached to the document.
charset: a string. Specifies the character set used by the document. The only valid value is "utf-8".
httpEquiv: a string. Specifies a directive for processing the document.
itemProp: a string. Specifies metadata about a particular item within the document rather than the document as a whole.
content: a string. Specifies the metadata to be attached when used with the name or itemProp props or the behavior of the directive when used with the httpEquiv prop.
"""

SCRIPT_PROPS = r"""
async: a boolean. Allows the browser to defer execution of the script until the rest of the document has been processed — the preferred behavior for performance.
crossOrigin: a string. The CORS policy to use. Its possible values are anonymous and use-credentials.
fetchPriority: a string. Lets the browser rank scripts in priority when fetching multiple scripts at the same time. Can be "high", "low", or "auto" (the default).
integrity: a string. A cryptographic hash of the script, to verify its authenticity.
noModule: a boolean. Disables the script in browsers that support ES modules — allowing for a fallback script for browsers that do not.
nonce: a string. A cryptographic nonce to allow the resource when using a strict Content Security Policy.
referrer: a string. Says what Referer header to send when fetching the script and any resources that the script fetches in turn.
type: a string. Says whether the script is a classic script, ES module, or import map.
"""

KNOWN_REACT_PROPS = _parse_react_props(
    SPECIAL_PROPS
    + STANDARD_PROPS
    + FORM_PROPS
    + DETAILS_PROPS
    + IMG_IFRAME_OBJECT_EMBED_LINK_IMAGE_PROPS
    + AUDIO_VIDEO_PROPS
    + INPUT_PROPS
    + SELECT_PROPS
    + TEXTAREA_PROPS
    + LINK_PROPS
    + META_PROPS
    + SCRIPT_PROPS
)

# Old Prop (Key) : New Prop (Value)
# Also includes some special cases like 'class' -> 'className'
REACT_PROP_SUBSTITUTIONS = {prop.lower(): prop for prop in KNOWN_REACT_PROPS} | {
    "for": "htmlFor",
    "class": "className",
    "checked": "defaultChecked",
}
