import { DjangoFormProps, OnlyOnceProps } from "./types";
import React from "react";
import ReactDOM from "react-dom";
/**
 * Interface used to bind a ReactPy node to React.
 */
export function bind(node) {
  return {
    create: (type, props, children) =>
      React.createElement(type, props, ...children),
    render: (element) => {
      ReactDOM.render(element, node);
    },
    unmount: () => ReactDOM.unmountComponentAtNode(node),
  };
}

export function DjangoForm({
  onSubmitCallback,
  formId,
}: DjangoFormProps): null {
  React.useEffect(() => {
    const form = document.getElementById(formId) as HTMLFormElement;

    // Submission event function
    const onSubmitEvent = (event) => {
      event.preventDefault();
      const formData = new FormData(form);

      // Convert the FormData object to a plain object by iterating through it
      // If duplicate keys are present, convert the value into an array of values
      const entries = formData.entries();
      const formDataArray = Array.from(entries);
      const formDataObject = formDataArray.reduce((acc, [key, value]) => {
        if (acc[key]) {
          if (Array.isArray(acc[key])) {
            acc[key].push(value);
          } else {
            acc[key] = [acc[key], value];
          }
        } else {
          acc[key] = value;
        }
        return acc;
      }, {});

      onSubmitCallback(formDataObject);
    };

    // Bind the event listener
    if (form) {
      form.addEventListener("submit", onSubmitEvent);
    }

    // Unbind the event listener when the component dismounts
    return () => {
      if (form) {
        form.removeEventListener("submit", onSubmitEvent);
      }
    };
  }, []);

  return null;
}

export function LoadOnlyOnce({
  path,
  nodeName,
  autoRemove,
}: OnlyOnceProps): null {
  React.useEffect(() => {
    // Check if the element already exists
    let el: null | HTMLElement = null;
    if (nodeName === "script") {
      el = document.head.querySelector(
        "script.reactpy-staticfile[src='" + path + "']",
      );
    } else if (nodeName === "link") {
      el = document.head.querySelector(
        "link.reactpy-staticfile[href='" + path + "']",
      );
    } else {
      throw new Error("Invalid nodeName provided to LoadOnlyOnce");
    }

    // Create a new element, if needed
    if (el === null) {
      el = document.createElement(nodeName);
      el.className = "reactpy-staticfile";
      if (nodeName === "script") {
        el.setAttribute("src", path);
      } else if (nodeName === "link") {
        el.setAttribute("href", path);
        el.setAttribute("rel", "stylesheet");
      }
      document.head.appendChild(el);
    }

    // If requested, auto remove the element when it is no longer needed
    if (autoRemove) {
      // Keep track of the number of ReactPy components that are dependent on this script
      let count = Number(el.getAttribute("data-count"));
      count += 1;
      el.setAttribute("data-count", count.toString());

      // Remove the element when the last dependent component is unmounted
      return () => {
        count -= 1;
        if (count === 0) {
          el.remove();
        } else {
          el.setAttribute("data-count", count.toString());
        }
      };
    }
  }, []);

  return null;
}
