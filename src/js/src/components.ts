import type { DjangoFormProps, HttpRequestProps } from "./types";
import { useEffect } from "preact/hooks";
import { type ComponentChildren, render, createElement } from "preact";
/**
 * Interface used to bind a ReactPy node to React.
 */
export function bind(node: HTMLElement | Element | Node) {
  return {
    create: (
      type: string,
      props: Record<string, unknown>,
      children: ComponentChildren[],
    ) => createElement(type, props, ...children),
    render: (element: HTMLElement | Element | Node) => {
      render(element, node);
    },
    unmount: () => render(null, node),
  };
}

export function DjangoForm({
  onSubmitCallback,
  formId,
}: DjangoFormProps): null {
  useEffect(() => {
    const form = document.getElementById(formId) as HTMLFormElement;

    // Submission event function
    const onSubmitEvent = (event: Event) => {
      event.preventDefault();
      const formData = new FormData(form);

      // Convert the FormData object to a plain object by iterating through it
      // If duplicate keys are present, convert the value into an array of values
      const entries = formData.entries();
      const formDataArray = Array.from(entries);
      const formDataObject = formDataArray.reduce<Record<string, unknown>>(
        (acc, [key, value]) => {
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
        },
        {},
      );

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
  useEffect(() => {
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
