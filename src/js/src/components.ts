import { DjangoFormProps, HttpRequestProps } from "./types";
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

export function HttpRequest({ method, url, body, callback }: HttpRequestProps) {
  React.useEffect(() => {
    fetch(url, {
      method: method,
      body: body,
    })
      .then((response) => {
        response
          .text()
          .then((text) => {
            callback(response.status, text);
          })
          .catch(() => {
            callback(response.status, "");
          });
      })
      .catch(() => {
        callback(520, "");
      });
  }, []);

  return null;
}
